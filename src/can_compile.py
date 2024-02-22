import can_parser
import can_lexer
import os
import re

from libraries.can_lib import cantonese_lib_import, cantonese_model_new,\
    cantonese_turtle_init
from collections import defaultdict

class CanPyCompile:
    def __init__(self):
        pass

    @staticmethod
    def cantonese_lib_run(lib_name : str, path : str) -> str:
        pa = os.path.dirname(path) # Return the last file Path
        tokens = []
        code = ""
        found = False
        for dirpath,dirnames,files in os.walk(pa):
            if lib_name + '.cantonese' in files:
                code = open(pa + '/' + lib_name + '.cantonese', encoding = 'utf-8').read()
                found = True
        if found == False:
            raise ImportError(lib_name + '.cantonese not found.')
                
        tokens = can_lexer.cantonese_token(path, code)
        stats = can_parser.StatParser(tokens).parse_stats()
        code_gen = Codegen(stats, path)
        code = ''
        for stat in stats:
            code += code_gen.codegen_stat(stat)
        
        return code

class Codegen(object):
    def __init__(self, nodes : list, path : str):
        self.nodes = nodes
        self.path = path
        self.tab = ''
        self.line = 1
        self.line_mmap = defaultdict(int) # Python line mapping to Cantonese line

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

        elif isinstance(exp, can_parser.can_ast.SpecificIdExp):
            s = ''
            p_corr = re.match(r'(.*)同(.*)有幾襯', exp.id, re.M|re.I)
            if p_corr:
                s = " corr(" + p_corr.group(1) +", " + p_corr.group(2) + ") "
            return s
        else:
            return ''

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

    def codegen_lib_list(self, lib_list : list) -> tuple:
        s = ''
        user_lib = []
        for lib in lib_list:
            import_res = cantonese_lib_import(self.codegen_expr(lib))
            if import_res != "Not found":
                s += ', ' + import_res
            else:
                user_lib.append(self.codegen_expr(lib))

        return s[2 : ], user_lib

    def codegen_build_in_method_or_id(self, exp : can_parser.can_ast) -> str:
        list_build_in_method = {
            "加啲" : "append",
            "摞走" : "remove",
            "散水" : "clear"
        }

        if (isinstance(exp, can_parser.can_ast.IdExp)):
            if exp.name in list_build_in_method:
                return list_build_in_method[exp.name]
            else:
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
            if stat.args_type != [] and\
                stat.ret_type != []:
                # remove the '<*>'
                stat.args_type = list(filter(lambda x : not isinstance(x, can_parser.can_ast.VarArgExp), stat.args_type))
                assert stat.args.__len__() == stat.args_type.__len__()
                s = ''
                arg_decl = ''
                for arg, arg_ty in zip(stat.args, stat.args_type):
                    arg_decl += self.codegen_expr(arg) + " : " + '"'  + self.codegen_expr(arg_ty) + '"' + ','
                s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + arg_decl + ') -> ' + '"'  + self.codegen_args(stat.ret_type) + '"' \
                     + ':\n'
                s += self.codegen_block(stat.blocks)

                self.update_line_map(stat, s)
                return s

            else:
                s = ''
                s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + self.codegen_args(stat.args) + '):\n'
                s += self.codegen_block(stat.blocks)
                
                self.update_line_map(stat, s)
                return s

        elif isinstance(stat, can_parser.can_ast.MatchModeFuncDefStat):
            s = ''
            s += self.tab + 'def ' + self.codegen_expr(stat.func_name) + '(*args):\n'
            for args, blocks in zip(stat.args_list, stat.block_list):
                # TODO: support more args
                if len(args) == 1:
                    if isinstance(args[0], (can_parser.can_ast.NumeralExp, can_parser.can_ast.StringExp, 
                                        can_parser.can_ast.ListExp)):
                        s += self.tab + '\t' + 'if args[0] == '+ self.codegen_expr(args[0])  + ':\n';
                        s += self.tab + '\t\t' + 'return ' + self.codegen_expr(blocks) + '\n'
                    elif isinstance(args[0], can_parser.can_ast.IdExp):
                        # TODO: use re.sub here
                        s += self.tab + '\t' +'return ' + self.codegen_expr(blocks).replace(args[0].name, "args[0]") + '\n'
            
            self.update_line_map(stat, s)
            return s


        elif isinstance(stat, can_parser.can_ast.FuncCallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.func_name) + '(' + self.codegen_args(stat.args) + ')' + '\n'
            self.update_line_map(stat, s)
            return s

        elif isinstance(stat, can_parser.can_ast.ImportStat):
            s = ''
            libs, user_lib = self.codegen_lib_list(stat.idlist)
            if len(libs):
                s += self.tab + 'import ' + libs + '\n'
            if len(user_lib):
                for l in user_lib:
                    s += self.tab + CanPyCompile.cantonese_lib_run(l, self.path)
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