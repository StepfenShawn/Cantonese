import sys, traceback, os, re
from typing import Generator, List, Any
from pathlib import Path
from collections import namedtuple

from py_cantonese.can_error.compile_time import LexerException
from py_cantonese.can_error.runtime import error_stdout
from py_cantonese.can_lexer.can_lexer import getCtxByLine, Pos
from py_cantonese.can_lexer import cantonese_token_from_file
from py_cantonese.can_utils.show.infoprinter import ErrorPrinter
from py_cantonese.can_utils.depend_tree import DependTree, depend_to_url, get_trace
from py_cantonese.can_context import CanTokenContext
from py_cantonese.can_parser.exp.names_parser import NamesParser
from py_cantonese.can_parser import ParserFn


def set_work_env(file: str):
    pa = os.path.dirname(file)  # Return the last file Path
    pa = "./" if len(pa) == 0 else pa
    sys.path.insert(0, pa)


def get_lib_std_dir():
    src_dir = os.path.dirname(os.path.abspath(__file__))
    return Path(src_dir) / "can_libs" / "std"


def get_all_base_macros_env():
    return (get_lib_std_dir() / "macros").glob("*.cantonese")


def eval_pre_script(code: str, file: str, apply_f: callable) -> str:
    """
    预处理 `{% ... %}`
    """

    def lexer(script: str) -> Generator:
        try:
            tokens = cantonese_token_from_file(file, script, False)
        except LexerException as e:
            print(e.message)
            exit()
        return tokens

    def parse(token_ctx: CanTokenContext) -> DependTree:
        depend_tree = NamesParser.from_ParserFn(ParserFn(token_ctx)).parse()
        return depend_tree

    def pre_eval(trace: List[List[Any]]) -> None:
        for each_chain in trace:
            path = depend_to_url(each_chain, str(get_lib_std_dir()))
            if os.path.exists(str(path) + ".cantonese"):
                apply_f("cantonese", path + ".cantonese")
            elif os.path.exists(str(path) + ".sh"):
                apply_f("sh", path + ".sh")
            elif os.path.exists(str(path) + ".py"):
                apply_f("py", path + ".py")

    pre_script_pattern = re.compile(r"\{%.*?%\}", re.S)
    match_search = re.search(pre_script_pattern, code)

    while match_search:
        case_script = match_search.group()[2:-2]
        cnt_newline = case_script.count("\n")
        code = code.replace(match_search.group(), "\n" * cnt_newline)

        tokens = lexer(case_script)
        cur_token_ctx = CanTokenContext()
        cur_token_ctx.set_token_ctx((tokens, []))

        trace = get_trace(parse(cur_token_ctx))
        pre_eval(trace)

        # continue to match
        match_search = re.search(pre_script_pattern, code)
    return code


error = namedtuple("layer", ["lineno", "filename"])


def error_catch(e):
    exc_type, exc_value, tback = sys.exc_info()
    tback = traceback.extract_tb(tback)
    infos = list(map(lambda x: error(x.lineno, x.filename), tback))[1:]

    err_ty = e.__class__.__name__

    print(f"\033[0;31m濑嘢!!!\033[0m: {error_stdout(err_ty, str(e))}")

    for info in infos:
        from py_cantonese.can_compiler.compiler import line_map

        lines = line_map[info.filename][info.lineno]

        if len(lines) <= 1:
            lineno = lines[0]
            ctx = getCtxByLine(info.filename, lineno)
            p = ErrorPrinter(
                info=" 喺runtime察覺到錯誤!",
                pos=Pos(lineno, 0, lineno, 0),
                tips="  幫緊你只不過有心無力:(",
                ctx=ctx,
                _file=info.filename,
                _len=len(ctx.encode("gbk")),
            )

            print(p.err_msg(arrow_char="^"))
        else:
            start_line = lines[0]
            end_line = lines[-1]
            ctx = (getCtxByLine(info.filename, lineno) + "\n" for lineno in lines)
            p = ErrorPrinter(
                info=" 喺runtime察覺到錯誤!",
                pos=Pos(start_line, 0, end_line, 0),
                tips="  幫緊你只不過有心無力:(",
                ctx=ctx,
                _file=info.filename,
            )

            p.show_multline()

    exit()
