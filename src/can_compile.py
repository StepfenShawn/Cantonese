import can_parser

from can_lib import cantonese_lib_import

class Codegen(object):
    def __init__(self, nodes : list, path : str):
        self.nodes = nodes
        self.path = path
        self.tab = ''

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

    def codegen_lib_list(self, lib_list : list) -> str:
        s = ''
        for lib in lib_list:
            import_res = cantonese_lib_import(self.codegen_expr(lib))
            if import_res != "Not found":
                s += ', ' + import_res

        return s[2 : ]
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
            return self.tab + 'print(' + self.codegen_args(stat.args) + ')\n'
        
        elif isinstance(stat, can_parser.can_ast.AssignStat):
            return self.tab + self.codegen_varlist(stat.var_list) + ' = ' + self.codegen_args(stat.exp_list) + '\n'

        elif isinstance(stat, can_parser.can_ast.ExitStat):
            return self.tab + 'exit()\n'

        elif isinstance(stat, can_parser.can_ast.PassStat):
            return self.tab + 'pass\n'

        elif isinstance(stat, can_parser.can_ast.BreakStat):
            return self.tab + 'break\n'

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

            return s

        elif isinstance(stat, can_parser.can_ast.RaiseStat):
            s = ''
            s += self.tab + 'raise ' + self.codegen_expr(stat.name_exp) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.WhileStat):
            s = ''
            s += self.tab + 'while not ' + self.codegen_expr(stat.cond_exp) + ':\n'
            s += self.codegen_block(stat.blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.ForStat):
            s = ''
            s += self.tab + 'for ' + self.codegen_expr(stat.var) + ' in range('+ self.codegen_expr(stat.from_exp) \
                        + ', ' + self.codegen_expr(stat.to_exp) + '):\n'
            s += self.codegen_block(stat.blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.FunctoinDefStat):
            s = ''
            s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + self.codegen_args(stat.args) + '):\n'
            s += self.codegen_block(stat.blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.FuncCallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.func_name) + '(' + self.codegen_args(stat.args) + ')' + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.ImportStat):
            return self.tab + 'import ' + self.codegen_lib_list(stat.idlist) + '\n'

        elif isinstance(stat, can_parser.can_ast.ReturnStat):
            s = ''
            s += self.tab + 'return ' + self.codegen_args(stat.exps) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.DelStat):
            s = ''
            s += self.tab + 'del ' + self.codegen_args(stat.exps) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.TypeStat):
            s = ''
            s += self.tab + 'print(type(' + self.codegen_expr(stat.exps) + '))\n'
            return s

        elif isinstance(stat, can_parser.can_ast.AssertStat):
            s = ''
            s += self.tab + 'assert ' + self.codegen_expr(stat.exps) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.ClassDefStat):
            s = ''
            s += self.tab + 'class ' + self.codegen_expr(stat.class_name) + '(' + self.codegen_args(stat.class_extend) + '):\n'
            s += self.codegen_block(stat.class_blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.MethodDefStat):
            s = ''
            s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + self.codegen_method_args(stat.args) + '):\n'
            s += self.codegen_block(stat.class_blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.MethodCallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.name_exp) + '.' + self.codegen_build_in_method_or_id(stat.method) + \
                 '(' + self.codegen_args(stat.args) + ')\n'
            return s

        elif isinstance(stat, can_parser.can_ast.CmdStat):
            s = ''
            s += self.tab + 'os.system(' + self.codegen_args(stat.args) + ')\n'
            return s

        elif isinstance(stat, can_parser.can_ast.ClassInitStat):
            s = ''
            s += self.tab + 'def __init__(self, ' + self.codegen_args(stat.class_var_list) + '):\n'
            for i in range(len(stat.class_var_list)):
                s += self.tab + 'self.' + self.codegen_expr(stat.class_var_list[i]) + ' = ' + \
                    self.codegen_expr(stat.class_var_list[i]) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.CallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.exp) + '\n'
            return s

    def codegen_block(self, blocks):
        save = self.tab
        self.tab += '\t'
        s = ''
        for block in blocks:
            s += self.codegen_stat(block)
        self.tab = save
        return s