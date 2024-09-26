import can_source.can_parser as can_parser
import can_source.can_lexer as can_lexer
import sys, os
from typing import Generator

from can_source.libraries.can_lib import (
    fix_lib_name,
    cantonese_model_new,
    cantonese_turtle_init,
)
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

line_map = {}


class Codegen:
    def __init__(self, nodes: Generator, path: str):
        self.nodes = nodes
        self.path = path
        self.tab = ""
        self.line = 1
        self.line_mmap = defaultdict(list)  # Python line mapping to Cantonese line
        self.code = ""

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
            for can_lineno in range(stat.pos.line, stat.pos.end_line + 1):
                self.line_mmap[py_lineno].append(can_lineno)

    def emit(self, s, stat):
        s = self.tab + s
        self.update_line_map(stat, s)
        self.code += s

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
            s = "["
            if len(exp.elem_exps):
                for elem in exp.elem_exps:
                    s += self.codegen_expr(elem) + ", "
                s = s[:-2] + "]"
                return s
            else:
                return s + "]"

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

        elif isinstance(stat, can_parser.can_ast.ModelNewStat):
            s = ""
            model = self.codegen_expr(stat.model)
            dataset = self.codegen_expr(stat.dataset)
            s += cantonese_model_new(model, dataset, self.tab, s)

            self.emit(s, stat)

        elif isinstance(stat, can_parser.can_ast.TurtleStat):
            cantonese_turtle_init()
            for item in stat.exp_blocks:
                self.emit(self.codegen_expr(item) + "\n", stat)

    def codegen_block(self, blocks):
        save = self.tab
        self.tab += "\t"
        if len(blocks) == 0:
            self.emit("pass", stat=None)
        else:
            for block in blocks:
                self.codegen_stat(block)
        self.tab = save
