"""
    Created at 2021/1/16 16:23
    The interpreter for Cantonese    
"""

import cmd
import sys, os
import argparse
import traceback

from collections import defaultdict
from typing import Callable
import textwrap

sys.path.append(os.getcwd())
sys.dont_write_bytecode = True

from cantonese_rs import parse_to_ast

from py_cantonese.can_utils.show.infoprinter import format_color
from py_cantonese.can_utils.show.helper import show_more
from py_cantonese.can_error.compile_time import *

from py_cantonese.can_compiler.compiler import Codegen
import py_cantonese.can_sys as can_sys
import py_cantonese.can_import

from py_cantonese.can_libs import *
from py_cantonese.web_core.can_web_parser import *
from py_cantonese.can_const import _version_, logo
from py_cantonese.can_ast.can_ast_converter import convert_program

def include_eval(dispatch, file, is_to_py) -> None:
    if dispatch == "cantonese":
        with open(file, encoding="utf-8") as f:
            code = f.read()
            start_cantonese(lambda: cantonese_run(code, is_to_py, str(file)))
    elif dispatch == "sh":
        os.system(f"./{file}")
    else:
        raise Exception("Unreachable!")

class Options:
    dump_ast = False
    dump_lex = False
    mkfile = False
    _to_llvm = False
    debug = False


def create_cli():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", nargs="?", default="")
    arg_parser.add_argument("others", nargs="?", default="")
    arg_parser.add_argument(
        "-to_py", action="store_true", help="Translate Cantonese to Python"
    )
    arg_parser.add_argument(
        "-讲翻py", action="store_true", help="Translate Cantonese to Python"
    )
    arg_parser.add_argument("-to_web", action="store_true")
    arg_parser.add_argument("-倾偈", action="store_true")
    arg_parser.add_argument("-allow_pyc", action="store_true")
    arg_parser.add_argument("-compile", action="store_true")
    arg_parser.add_argument("-讲白啲", action="store_true")
    arg_parser.add_argument("-build", action="store_true")
    arg_parser.add_argument("-ast", action="store_true")
    arg_parser.add_argument("-z", action="store_true")
    arg_parser.add_argument("-lex", action="store_true")
    arg_parser.add_argument("-debug", action="store_true")
    arg_parser.add_argument(
        "-v", "--version", action="store_true", help="Print the version"
    )
    arg_parser.add_argument("-mkfile", action="store_true")
    arg_parser.add_argument("-l", action="store_true")
    arg_parser.add_argument("-llvm", action="store_true")

    return arg_parser.parse_args()


TO_PY_CODE = ""


def start_cantonese(run_fn: Callable):
    """
    啓動 `Cantonese` !!!
    """
    global args
    try:
        return run_fn()
    except CompTimeException as e:
        print("!!編譯期間瀨嘢:(\n")
        print(e)
        exit()
    except Exception as e:
        if args.z:
            traceback.print_exc()
        else:
            tb = traceback.extract_tb(e.__traceback__)
            filename, lineno, funcname, _ = tb[-1]
            print(
                f"!!編譯器內部瀨嘢:(\n\n -> `{funcname}`函數\n -> 喺編譯器源代碼 '{filename}' 嘅{lineno}行:\n ->   {_}\n 發生 {e}\n\n 用 `-z` 查看完整錯誤信息."
            )
            exit()


def show_pretty_lex(tokens):
    lines_tracker = defaultdict(list)
    for token in tokens:
        lines_tracker[f"line {token.pos.line}"].append(str(token))
    show_more(list(lines_tracker.items()))


def show_pretty_ast(stats):
    show_more(stats)


def cantonese_run(
    code: str, is_to_py: bool, file: str, REPL=False, get_py_code=False, use_rust=True
) -> None:

    global TO_PY_CODE
    global lib_env

    os.environ["CUR_FILE"] = file

    # 使用Rust解析器生成AST的dict表示
    ast_dict = parse_to_ast(code)
    
    if isinstance(ast_dict, list):
        # 将dict表示转换为can_ast对象
        stats = convert_program(ast_dict)
        # 如果需要显示AST，则在转换后显示
        if Options.dump_ast:
            show_pretty_ast(stats)
            
        # 使用转换后的can_ast对象生成Python代码
        code_gen = Codegen(stats, path=file)
        TO_PY_CODE = code_gen.to_py()
    else:
        # 处理解析错误
        if "error" in ast_dict:
            error_msg = ast_dict["error"]
            raise CompTimeException(f"解析错误: {error_msg}")
        else:
            raise CompTimeException("未知解析错误")
    
    if Options._to_llvm:
        import llvm_core.can_llvm_build as can_llvm_build
        import llvm_core.llvm_evaluator as llvm_evaluator

        evaluator = llvm_evaluator.LLvmEvaluator(file)
        for i, stat in enumerate(stats):
            if i != len(stats) - 1:
                evaluator.evaluate(stat, llvmdump=Options.debug)
            else:
                evaluator.evaluate(stat, llvmdump=Options.debug, endMainBlock=True)
        exit()

    cantonese_lib_init()

    if is_to_py:
        print("-> To python:")
        out_format = textwrap.indent(format_color(TO_PY_CODE, "Python"), "  ")
        print(out_format)
        print("->")

    if Options.mkfile:
        f = open(file[: len(file) - 10] + ".py", "w", encoding="utf-8")
        f.write("###########################################\n")
        f.write("#        Generated by Cantonese           #\n")
        f.write("###########################################\n")
        f.write(
            "# Run it by "
            + "'cantonese "
            + file[: len(file) - 10]
            + ".py"
            + " -build' \n"
        )
        f.write(TO_PY_CODE)

    if Options.debug:
        import dis

        print(dis.dis(TO_PY_CODE))
    else:
        try:
            c = TO_PY_CODE
            if REPL:
                TO_PY_CODE = ""  # reset the global lib_env in REPL mode
            if get_py_code:
                return c
            code = compile(TO_PY_CODE, file, "exec")
            exec(code, lib_env)
        except Exception as e:
            can_sys.error_catch(e)


class 交互(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = "> "

    def var_def(self, key):
        pass

    def run(self, code):
        if code in lib_env.keys():
            print(lib_env[code])
        try:
            exec(code, lib_env)
        except Exception as e:
            can_sys.error_catch(e)

    def default(self, code):
        os.environ["REPL_CONTEXT"] = code
        if code is not None:
            if code == ".quit":
                sys.exit(1)
            c = start_cantonese(
                lambda: cantonese_run(
                    code, False, "【標準輸入】", REPL=True, get_py_code=True
                ),
            )
            self.run(c)


def 开始交互():
    import time

    print(_version_)

    交互().cmdloop(
        "本地時間: " + str(time.asctime(time.localtime(time.time()))) + ", 天氣唔知點"
    )


def main():
    global _version_

    args = create_cli()

    if args.version:
        print(_version_, logo)
        sys.exit(1)

    if not args.file:
        sys.exit(开始交互())

    if not os.path.exists(args.file):
        print("Error occurred when checking the path of file!")
        print(f" File {args.file}")
        print("      " + "^" * len(args.file.encode("gbk")))
        print("\033[0;31m濑嘢!!!\033[0m: 揾唔到你嘅文件 :(")
    else:

        can_sys.set_work_env(args.file)
        sys.path.insert(0, "./")

        is_to_py = False
        code = ""

        with open(args.file, encoding="utf-8") as f:
            code = f.read()

        if args.build:
            cantonese_lib_init()
            exec(code, lib_env)
            exit()
        if args.to_py or args.讲翻py:
            is_to_py = True
        if args.to_web or args.倾偈:
            if args.compile or args.讲白啲:
                cantonese_web_run(code, args.file, False)
            else:
                cantonese_web_run(code, args.file, True)
        if args.ast:
            Options.dump_ast = True
        if args.lex:
            Options.dump_lex = True
        if args.debug:
            Options.debug = True
        if args.mkfile:
            Options.mkfile = True
        if args.llvm or args.l:
            Options._to_llvm = True
        if args.allow_pyc:
            sys.dont_write_bytecode = False

        start_cantonese(lambda: cantonese_run(code, is_to_py, args.file))


if __name__ == "__main__":
    # Support colorful fonts on windows
    if os.name == "nt":
        os.system("")

    main()
