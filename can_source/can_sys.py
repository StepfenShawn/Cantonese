import sys, traceback, os

from collections import namedtuple
from can_source.can_error import error_stdout
from can_source.can_lexer import getCtxByLine, Pos
from can_source.can_utils.infoprinter import ErrorPrinter


def set_work_env(file: str):
    pa = os.path.dirname(file)  # Return the last file Path
    pa = "./" if len(pa) == 0 else pa
    sys.path.insert(0, pa)


class CanContext:
    """
    A class to hold global values in `compile-time`
    """

    def __init__(self):
        pass

    def set_token_ctx(self, token_ctx: tuple):
        """
        we need a buffer_tokens in lazy parser.
        because the first token maybe not case in `look_ahead` mode.
        """
        self.tokens, self.buffer_tokens = token_ctx

    def get_token_ctx(self) -> tuple:
        return (self.tokens, self.buffer_tokens)


class CanMacrosContext:
    """
    A class to hold macros in `compile-time`
    """

    def __init__(self):
        self.macros = {}

    def update(self, name, o):
        self.macros.update({name: o})

    def get(self, name):
        return self.macros.get(name)


can_context = CanContext()
can_macros_context = CanMacrosContext()

error = namedtuple("layer", ["lineno", "filename"])


def error_catch(e):
    exc_type, exc_value, tback = sys.exc_info()
    tback = traceback.extract_tb(tback)
    infos = list(map(lambda x: error(x.lineno, x.filename), tback))[1:]

    err_ty = e.__class__.__name__

    print(f"\033[0;31m濑嘢!!!\033[0m: {error_stdout(err_ty, str(e))}")

    for info in infos:
        from can_source.can_compile import line_map

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

            p.show(arrow_char="^")
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
