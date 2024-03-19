import can_source.can_parser as can_parser
import can_source.can_lexer as can_lexer
import re
import sys, os
import ast

from can_source.libraries.can_lib import fix_lib_name, cantonese_model_new,\
    cantonese_turtle_init
from collections import defaultdict
from can_source.libraries.can_lib import fix_lib_name

import importlib

importlib.machinery.SOURCE_SUFFIXES.insert(0, ".cantonese")
_py_source_to_code = importlib.machinery.SourceFileLoader.source_to_code

def _can_source_to_code(self, data, path, _optimize=-1):

    source = data.decode("utf-8")
    if not path.endswith(".cantonese"):
        return _py_source_to_code(self, source, path, _optimize=_optimize)
    
    cur_file = os.environ["CUR_FILE"]
    os.environ["CUR_FILE"] = path

    tokens = can_lexer.cantonese_token(path, source)
    stats = can_parser.StatParser((tokens, [])).parse_stats()
    code_gen = Codegen(stats, path=path)
    _code = code_gen.to_py()

    os.environ["CUR_FILE"] = cur_file
    return _py_source_to_code(self, _code, path, _optimize=_optimize)

importlib.machinery.SourceFileLoader.source_to_code = _can_source_to_code

class Codegen:
    def __init__(self, nodes : list, path : str):
        self.nodes = nodes
        self.path = path
        self.tab = ''
        self.line = 1
        self.line_mmap = defaultdict(int) # Python line mapping to Cantonese line

    def to_py(self):
        code = ''
        for node in self.nodes:
            code += self.codegen_stat(node)
        return code

    def build_ast(self):
        tree = ast.parse(self.to_py())
        tree.body = list(map(self.fix_lineno, tree.body))
        return tree

    def fix_lineno(self, _node: ast.AST):
        if not isinstance(_node, ast.AST):
            if isinstance(_node, (list, set)):
                for _ in _node:
                    self.fix_lineno(_)        
            return

        if hasattr(_node, "lineno"):
            py_line = _node.lineno
            _node.lineno = self.line_mmap[py_line]
            _node.col_offset = 0
            _node.end_lineno = _node.lineno
            _node.end_col_offset = 0

        for attr in dir(_node):
            self.fix_lineno(getattr(_node, attr))

        return _node

    def update_line_map(self, stat: can_parser.can_ast.Stat, s: str):
        start = self.line
        self.line += s.count('\n')
        end = self.line
        for lno in range(start, end):
            self.line_mmap[lno] = stat.pos.line

    def codegen_expr(self, exp) -> str:
        if isinstance(exp, can_parser.can_ast.StringExp):
            return exp.s
        
        elif isinstance(exp, can_parser.can_ast.NumeralExp):
            return exp.val
        
        elif isinstance(exp, can_parser.can_ast.IdExp):
            return exp.name

        elif isinstance(exp, can_parser.can_ast.FalseExp):
            return "False"
        
        elif isinstance(exp, can_parser.can_ast.TrueExp):
            return "True"
        
        elif isinstance(exp, can_parser.can_ast.NullExp):
            return "None"
        
        elif isinstance(exp, can_parser.can_ast.AnnotationExp):
            return self.codegen_expr(exp.exp) + ":" + exp.tyid.name

        elif isinstance(exp, can_parser.can_ast.BinopExp):
            return '(' + self.codegen_expr(exp.exp1) + exp.op + self.codegen_expr(exp.exp2) + ')'

        elif isinstance(exp, can_parser.can_ast.MappingExp):
            return self.codegen_expr(exp.exp1) + ':' + self.codegen_expr(exp.exp2)

        elif isinstance(exp, can_parser.can_ast.ObjectAccessExp):
            return self.codegen_expr(exp.prefix_exp) + '.' + self.codegen_expr(exp.key_exp)

        elif isinstance(exp, can_parser.can_ast.ListAccessExp):
            return self.codegen_expr(exp.prefix_exp) + '[' + self.codegen_expr(exp.key_exp) + ']'
        
        elif isinstance(exp, can_parser.can_ast.UnopExp):
            return '(' + exp.op + ' ' + self.codegen_expr(exp.exp) + ')'
        
        elif isinstance(exp, can_parser.can_ast.FuncCallExp):
            return self.codegen_expr(exp.prefix_exp) + '(' + self.codegen_args(exp.args) + ')'

        elif isinstance(exp, can_parser.can_ast.LambdaExp):
            return ' lambda ' + self.codegen_args(exp.id_list) + ' : ' + self.codegen_args(exp.blocks)

        elif isinstance(exp, can_parser.can_ast.IfElseExp):
            return '(' + self.codegen_expr(exp.if_exp) + ' if ' + self.codegen_expr(exp.if_cond_exp) + ' else ' + self.codegen_expr(exp.else_exp) + ')'

        elif isinstance(exp, can_parser.can_ast.ListExp):
            s = '['
            if len(exp.elem_exps):
                for elem in exp.elem_exps:
                    s += self.codegen_expr(elem) + ', '
                s = s[ : -2] + ']'
                return s
            else:
                return s + ']'

        elif isinstance(exp, can_parser.can_ast.MapExp):
            s = '{'
            if len(exp.elem_exps):
                for elem in exp.elem_exps:
                    s += self.codegen_expr(elem) + ', '
                s = s[ : -2] + '}'
                return s
            else:
                return s + '}'

        elif isinstance(exp, can_parser.can_ast.ClassSelfExp):
            s = 'self.' + self.codegen_expr(exp.exp)
            return s

        elif isinstance(exp, can_parser.can_ast.AssignExp):
            s = self.codegen_expr(exp.exp1) + ' = ' + self.codegen_expr(exp.exp2)
            return s

    def codegen_args(self, args : list) -> str:
        s = ''
        for arg in args:
            s += ', ' + self.codegen_expr(arg)
        return s[2 : ]

    def codegen_method_args(self, args : list) -> str:
        s = ''
        for arg in args:
            s += ', ' + self.codegen_expr(arg)
        return "self, " + s[2 : ]

    def codegen_lib_list(self, lib_list : list) -> str:
        res = []
        for _ in lib_list:
            name, need_load = fix_lib_name(self.codegen_expr(_))
            if need_load:
                for pa in sys.path:
                    if os.path.exists(f'{pa}/{name}.cantonese'):
                        with open(f"{pa}/{name}.cantonese", encoding="utf-8") as f:
                            os.environ[f"{pa}/{name}.cantonese_SOURCE"] = f.read()
            res.append(name)
        return ','.join(res)

    def codegen_build_in_method_or_id(self, exp: can_parser.can_ast) -> str:
        if (isinstance(exp, can_parser.can_ast.IdExp)):
                return exp.name
        else:
            return self.codegen_expr(exp)

    def codegen_varlist(self, lst : list) -> str:
        s = ''
        for l in lst:
            s += ', ' + self.codegen_expr(l)
        return s[2 : ]

    def codegen_stat(self, stat):
        if isinstance(stat, can_parser.can_ast.PrintStat):
            s = self.tab + 'print(' + self.codegen_args(stat.args) + ')\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.AssignStat):
            s = ''
            s += self.tab + self.codegen_args(stat.var_list) + ' = ' + self.codegen_args(stat.exp_list) + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.AssignBlockStat):
            s = ''
            for i in range(len(stat.var_list)):
                s += self.tab + self.codegen_expr(stat.var_list[i]) + ' = ' + self.codegen_expr(stat.exp_list[i]) + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ExitStat):
            s = self.tab + 'exit()\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.PassStat):
            s = self.tab + 'pass\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.BreakStat):
            s = self.tab + 'break\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ContinueStat):
            s = self.tab + 'continue\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.IfStat):
            s = ''
            s += self.tab + 'if ' + self.codegen_expr(stat.if_exp) + ':\n'
            s += self.codegen_block(stat.if_block)
            
            for i in range(len(stat.elif_exps)):
                s += self.tab + 'elif ' + self.codegen_expr(stat.elif_exps[i]) + ':\n'
                s += self.codegen_block(stat.elif_blocks[i])

            if len(stat.else_blocks):
                s += self.tab + 'else:\n'
                s += self.codegen_block(stat.else_blocks)
            
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.TryStat):
            s = ''
            s += self.tab + 'try: \n'
            s += self.codegen_block(stat.try_blocks)

            for i in range(len(stat.except_exps)):
                s += self.tab + 'except ' + self.codegen_expr(stat.except_exps[i]) + ':\n'
                s += self.codegen_block(stat.except_blocks[i])

            if len(stat.finally_blocks):
                s += self.tab + 'finally:\n'
                s += self.codegen_block(stat.finally_blocks)

            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.RaiseStat):
            s = ''
            s += self.tab + 'raise ' + self.codegen_expr(stat.name_exp) + '\n'
            
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.WhileStat):
            s = ''
            s += self.tab + 'while ' + self.codegen_expr(stat.cond_exp) + ':\n'
            s += self.codegen_block(stat.blocks)

            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ForStat):
            s = ''
            s += self.tab + 'for ' + self.codegen_expr(stat.var) + ' in range('+ self.codegen_expr(stat.from_exp) \
                        + ', ' + self.codegen_expr(stat.to_exp) + '):\n'
            s += self.codegen_block(stat.blocks)

            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.FunctionDefStat):
            s = ''
            s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + self.codegen_args(stat.args) + '):\n'
            s += self.codegen_block(stat.blocks)
            
            self.update_line_map(stat, s)
            return s


        elif isinstance(stat, can_parser.can_ast.FuncCallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.func_name) + '(' + self.codegen_args(stat.args) + ')' + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ImportStat):
            s = ''
            libs = self.codegen_lib_list(stat.idlist)
            s += self.tab + 'import ' + libs + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ReturnStat):
            s = ''
            s += self.tab + 'return ' + self.codegen_args(stat.exps) + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.DelStat):
            s = ''
            s += self.tab + 'del ' + self.codegen_args(stat.exps) + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.TypeStat):
            s = ''
            s += self.tab + 'print(type(' + self.codegen_expr(stat.exps) + '))\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.AssertStat):
            s = ''
            s += self.tab + 'assert ' + self.codegen_expr(stat.exps) + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ClassDefStat):
            s = ''
            s += self.tab + 'class ' + self.codegen_expr(stat.class_name) + '(' + self.codegen_args(stat.class_extend) + '):\n'
            s += self.codegen_block(stat.class_blocks)
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.MethodDefStat):
            s = ''
            s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + self.codegen_method_args(stat.args) + '):\n'
            s += self.codegen_block(stat.class_blocks)
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.MethodCallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.name_exp) + '.' + self.codegen_build_in_method_or_id(stat.method) + \
                 '(' + self.codegen_args(stat.args) + ')\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.CmdStat):
            s = ''
            s += self.tab + 'os.system(' + self.codegen_args(stat.args) + ')\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.CallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.exp) + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.GlobalStat):
            s = ''
            s += self.tab + 'global ' + self.codegen_args(stat.idlist) + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ExtendStat):
            s = ''
            s += self.tab + stat.code + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.MatchStat):
            s = ''
            enum = ['if ', 'elif ']
            for i in range(len(stat.match_val)):
                if i == 0:
                    elif_or_if = 'if '
                else:
                    elif_or_if = 'elif '
                s += self.tab + elif_or_if + self.codegen_expr(stat.match_id) + ' == ' + \
                     self.codegen_expr(stat.match_val[i]) + ':\n'
                s += self.codegen_block(stat.match_block_exp[i])

            if len(stat.default_match_block):
                s += self.tab + 'else:\n'
                s += self.codegen_block(stat.default_match_block)

            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ForEachStat):
            s = ''
            s += self.tab + 'for ' + self.codegen_args(stat.id_list) + ' in ' + self.codegen_args(stat.exp_list) + ':\n'
            s += self.codegen_block(stat.blocks)

            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ModelNewStat):
            s = ''
            model = self.codegen_expr(stat.model)
            dataset = self.codegen_expr(stat.dataset)
            s += cantonese_model_new(model, dataset, self.tab, s)
            
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.TurtleStat):
            s = ''
            cantonese_turtle_init()
            for item in stat.exp_blocks:
                s += self.tab + self.codegen_expr(item) + '\n'
            
            self.update_line_map(stat, s)
            return s

    def codegen_block(self, blocks):
        save = self.tab
        self.tab += '\t'
        s = ''
        for block in blocks:
            s += self.codegen_stat(block)
        self.tab = save
        return s