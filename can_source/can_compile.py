import can_source.can_parser as can_parser
import can_source.can_lexer as can_lexer
from can_source.parser_base import new_token_context
import sys, os
from typing import Generator

from collections import defaultdict
from can_source.can_libs import fix_lib_name

line_map = {}


class Codegen:
    def __init__(self, nodes: Generator, path: str):
        self.nodes = nodes
        self.path = path
        self.tab = ""
        self.line = 1
        self.line_mmap = defaultdict(list)  # Python line mapping to Cantonese line
        self.code = ""
        self.macro_meta_vars = {}

    def to_py(self):
        for node in self.nodes:
            self.codegen_stat(node)
        line_map[os.environ["CUR_FILE"]] = self.line_mmap
        return self.code

    def update_line_map(self, stat: can_parser.can_ast.Stat, s: str):
        start = self.line
        self.line += s.count("\n")
        end = self.line
        for py_lineno in range(start, end):
            if stat.pos:
                for can_lineno in range(stat.pos.line, stat.pos.end_line + 1):
                    self.line_mmap[py_lineno].append(can_lineno)

    def emit(self, s, stat):
        s = self.tab + s
        self.update_line_map(stat, s)
        self.code += s

    def codegen_expr(self, exp) -> str:
        if isinstance(exp, can_parser.can_ast.StringExp):
            return "Str(" + exp.s + ")"

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
            return (
                "("
                + self.codegen_expr(exp.exp1)
                + exp.op
                + self.codegen_expr(exp.exp2)
                + ")"
            )

        elif isinstance(exp, can_parser.can_ast.MappingExp):
            return self.codegen_expr(exp.exp1) + ":" + self.codegen_expr(exp.exp2)

        elif isinstance(exp, can_parser.can_ast.ObjectAccessExp):
            return (
                self.codegen_expr(exp.prefix_exp) + "." + self.codegen_expr(exp.key_exp)
            )

        elif isinstance(exp, can_parser.can_ast.ListAccessExp):
            return (
                self.codegen_expr(exp.prefix_exp)
                + "["
                + self.codegen_expr(exp.key_exp)
                + "]"
            )

        elif isinstance(exp, can_parser.can_ast.UnopExp):
            return "(" + exp.op + " " + self.codegen_expr(exp.exp) + ")"

        elif isinstance(exp, can_parser.can_ast.FuncCallExp):
            return (
                self.codegen_expr(exp.prefix_exp)
                + "("
                + self.codegen_args(exp.args)
                + ")"
            )

        elif isinstance(exp, can_parser.can_ast.LambdaExp):
            return (
                "(lambda "
                + self.codegen_args(exp.id_list)
                + " : "
                + self.codegen_args(exp.blocks)
                + ")"
            )

        elif isinstance(exp, can_parser.can_ast.IfElseExp):
            return (
                "("
                + self.codegen_expr(exp.if_exp)
                + " if "
                + self.codegen_expr(exp.if_cond_exp)
                + " else "
                + self.codegen_expr(exp.else_exp)
                + ")"
            )

        elif isinstance(exp, can_parser.can_ast.ListExp):
            s = "List(["
            if len(exp.elem_exps):
                for elem in exp.elem_exps:
                    s += self.codegen_expr(elem) + ", "
                s = s[:-2] + "])"
                return s
            else:
                return s + "])"

        elif isinstance(exp, can_parser.can_ast.MapExp):
            s = "{"
            if len(exp.elem_exps):
                for elem in exp.elem_exps:
                    s += self.codegen_expr(elem) + ", "
                s = s[:-2] + "}"
                return s
            else:
                return s + "}"

        elif isinstance(exp, can_parser.can_ast.AssignExp):
            s = self.codegen_expr(exp.exp1) + " = " + self.codegen_expr(exp.exp2)
            return s

        elif isinstance(exp, can_parser.can_ast.MetaIdExp):
            return self.codegen_expr(self.macro_meta_vars[exp.name])

        elif isinstance(exp, can_parser.can_ast.MacroResult):
            self.macro_meta_vars = exp.meta_var
            s = ""
            for node in exp.results:
                if isinstance(node, can_parser.can_ast.Stat):
                    self.codegen_stat(node)
                elif isinstance(node, can_parser.can_ast.Exp):
                    s += self.codegen_expr(node)
            # clear the meta vars
            self.macro_meta_vars = {}
            return s if s else ""

    def codegen_args(self, args: list) -> str:
        s = ""
        for arg in args:
            s += ", " + self.codegen_expr(arg)
        return s[2:]

    def codegen_lib_list(self, lib_list: list) -> str:
        res = []
        for _ in lib_list:
            name, need_load = fix_lib_name(self.codegen_expr(_))
            if need_load:
                for pa in sys.path:
                    if os.path.exists(f"{pa}/{name}.cantonese"):
                        with open(f"{pa}/{name}.cantonese", encoding="utf-8") as f:
                            os.environ[f"{pa}/{name}.cantonese_SOURCE"] = f.read()
            res.append(name)
        return ",".join(res)

    def codegen_build_in_method_or_id(self, exp: can_parser.can_ast) -> str:
        if isinstance(exp, can_parser.can_ast.IdExp):
            return exp.name
        else:
            return self.codegen_expr(exp)

    def codegen_varlist(self, lst: list) -> str:
        s = ""
        for l in lst:
            s += ", " + self.codegen_expr(l)
        return s[2:]

    def codegen_stat(self, stat):
        if isinstance(stat, can_parser.can_ast.PrintStat):
            self.emit("print(" + self.codegen_args(stat.args) + ")\n", stat)

        elif isinstance(stat, can_parser.can_ast.AssignStat):
            self.emit(
                self.codegen_args(stat.var_list)
                + " = "
                + self.codegen_args(stat.exp_list)
                + "\n",
                stat,
            )

        elif isinstance(stat, can_parser.can_ast.AssignBlockStat):
            for i in range(len(stat.var_list)):
                self.emit(
                    self.codegen_expr(stat.var_list[i])
                    + " = "
                    + self.codegen_expr(stat.exp_list[i])
                    + "\n",
                    stat,
                )

        elif isinstance(stat, can_parser.can_ast.ExitStat):
            self.emit("exit()\n", stat)

        elif isinstance(stat, can_parser.can_ast.PassStat):
            self.emit("pass\n", stat)

        elif isinstance(stat, can_parser.can_ast.BreakStat):
            self.emit("break\n", stat)

        elif isinstance(stat, can_parser.can_ast.ContinueStat):
            self.emit("continue\n", stat)

        elif isinstance(stat, can_parser.can_ast.IfStat):
            self.emit("if " + self.codegen_expr(stat.if_exp) + ":\n", stat)
            self.codegen_block(stat.if_block)

            for i in range(len(stat.elif_exps)):
                self.emit("elif " + self.codegen_expr(stat.elif_exps[i]) + ":\n", stat)
                self.codegen_block(stat.elif_blocks[i])

            if len(stat.else_blocks):
                self.emit("else:\n", stat)
                self.codegen_block(stat.else_blocks)

        elif isinstance(stat, can_parser.can_ast.TryStat):
            self.emit("try: \n", stat)
            self.codegen_block(stat.try_blocks)

            for i in range(len(stat.except_exps)):
                self.emit(
                    "except " + self.codegen_expr(stat.except_exps[i]) + ":\n", stat
                )
                self.codegen_block(stat.except_blocks[i])

            if len(stat.finally_blocks):
                self.emit("finally:\n", stat)
                self.codegen_block(stat.finally_blocks)

        elif isinstance(stat, can_parser.can_ast.RaiseStat):
            self.emit("raise " + self.codegen_expr(stat.name_exp) + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.WhileStat):
            self.emit("while " + self.codegen_expr(stat.cond_exp) + ":\n", stat)
            self.codegen_block(stat.blocks)

        elif isinstance(stat, can_parser.can_ast.ForStat):
            self.emit(
                "for "
                + self.codegen_expr(stat.var)
                + " in range("
                + self.codegen_expr(stat.from_exp)
                + ", "
                + self.codegen_expr(stat.to_exp)
                + "):\n",
                stat,
            )
            self.codegen_block(stat.blocks)

        elif isinstance(stat, can_parser.can_ast.FunctionDefStat):
            self.emit(
                "def "
                + self.codegen_expr(stat.name_exp)
                + "("
                + self.codegen_args(stat.args)
                + "):\n",
                stat,
            )
            self.codegen_block(stat.blocks)

        elif isinstance(stat, can_parser.can_ast.FuncCallStat):
            self.emit(
                self.codegen_expr(stat.func_name)
                + "("
                + self.codegen_args(stat.args)
                + ")"
                + "\n",
                stat,
            )

        elif isinstance(stat, can_parser.can_ast.ImportStat):
            libs = self.codegen_lib_list(stat.idlist)
            self.emit("import " + libs + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.ReturnStat):
            self.emit("return " + self.codegen_args(stat.exps) + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.DelStat):
            self.emit("del " + self.codegen_args(stat.exps) + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.TypeStat):
            self.emit("print(type(" + self.codegen_expr(stat.exps) + "))\n", stat)

        elif isinstance(stat, can_parser.can_ast.AssertStat):
            self.emit("assert " + self.codegen_expr(stat.exps) + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.ClassDefStat):
            extend_classes = ""
            if stat.class_extend != None:
                extend_classes = self.codegen_args(stat.class_extend)
            self.emit(
                "class "
                + self.codegen_expr(stat.class_name)
                + "("
                + extend_classes
                + "):\n",
                stat,
            )
            self.codegen_block(stat.class_blocks)

        elif isinstance(stat, can_parser.can_ast.MethodDefStat):
            self.emit(
                "def "
                + self.codegen_expr(stat.name_exp)
                + "("
                + self.codegen_args(stat.args)
                + "):\n",
                stat,
            )
            self.codegen_block(stat.class_blocks)

        elif isinstance(stat, can_parser.can_ast.AttrDefStat):
            names = list(map(lambda x: x.exp.name, stat.attrs_list))
            args_str = ",".join([name + "=None" for name in names])
            attr_str = ";".join([("self." + name + "=" + name) for name in names])
            self.emit(f"def __init__(self, {args_str}):{attr_str}\n", stat)

        elif isinstance(stat, can_parser.can_ast.MethodCallStat):
            self.emit(
                self.codegen_expr(stat.name_exp)
                + "."
                + self.codegen_build_in_method_or_id(stat.method)
                + "("
                + self.codegen_args(stat.args)
                + ")\n",
                stat,
            )

        elif isinstance(stat, can_parser.can_ast.CmdStat):
            self.emit("os.system(" + self.codegen_args(stat.args) + ")\n", stat)

        elif isinstance(stat, can_parser.can_ast.CallStat):
            self.emit(self.codegen_expr(stat.exp) + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.GlobalStat):
            self.emit("global " + self.codegen_args(stat.idlist) + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.ExtendStat):
            for s in stat.code.split("\n"):
                self.emit(s + "\n", stat)

        elif isinstance(stat, can_parser.can_ast.MatchStat):
            for i in range(len(stat.match_val)):
                if i == 0:
                    elif_or_if = "if "
                else:
                    elif_or_if = "elif "
                self.emit(
                    elif_or_if
                    + self.codegen_expr(stat.match_id)
                    + " == "
                    + self.codegen_expr(stat.match_val[i])
                    + ":\n",
                    stat,
                )
                self.codegen_block(stat.match_block_exp[i])

            if len(stat.default_match_block):
                self.emit("else:\n", stat)
                self.codegen_block(stat.default_match_block)

        elif isinstance(stat, can_parser.can_ast.ForEachStat):
            self.emit(
                "for "
                + self.codegen_args(stat.id_list)
                + " in "
                + self.codegen_args(stat.exp_list)
                + ":\n",
                stat,
            )
            self.codegen_block(stat.blocks)

    def codegen_block(self, blocks):
        save = self.tab
        self.tab += "\t"
        if len(blocks) == 0:
            self.emit("pass", stat=None)
        else:
            for block in blocks:
                self.codegen_stat(block)
        self.tab = save
