import re
import sys, traceback

from collections import namedtuple
from can_lexer import getCtxByLine, Pos
from util.infoprinter import ErrorPrinter

error = namedtuple("layer", ["lineno", "filename"])

def error_catch(e, line_ctx):

    def show(ty, info):
        if ty == 'NameError':
            return re.sub(r"name '(.*)' is not defined", r"唔知`\1`係咩", info)
        return f"{ty}:{info}"

    exc_type, exc_value, tback = sys.exc_info()
    tback = traceback.extract_tb(tback)
    infos = list(map(lambda x: error(x.lineno, x.filename), tback))[1:]
    err_ty = e.__class__.__name__
    print(f"\033[0;31m濑嘢!!!\033[0m: {show(err_ty, str(e))}")
    for info in infos:
        line_loc = line_ctx[info.lineno]
        ctx = getCtxByLine(line_loc)
        p = ErrorPrinter(info=" 喺runtime察覺到錯誤!",
                        pos=Pos(line_loc,0), tips=" 暫時未諗唔到:(", 
                        ctx=ctx,
                        _file=info.filename,
                        _len=len(ctx.encode("gbk")))

        p.show(arrow_char="^")
    exit()