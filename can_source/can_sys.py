import re
import sys, traceback, os

from collections import namedtuple
from can_source.can_lexer import getCtxByLine, Pos
from can_source.util.infoprinter import ErrorPrinter

error = namedtuple("layer", ["lineno", "filename"])

def set_work_env(file: str):
    pa = os.path.dirname(file) # Return the last file Path
    pa = "./" if len(pa) == 0 else pa
    sys.path.insert(0, pa)

def error_catch(e):
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
        ctx = getCtxByLine(info.filename, info.lineno)
        p = ErrorPrinter(info=" 喺runtime察覺到錯誤!",
                        pos=Pos(info.lineno, 0, info.lineno, 0), tips="  幫緊你只不過有心無力:(", 
                        ctx=ctx,
                        _file=info.filename,
                        _len=len(ctx.encode("gbk")))

        p.show(arrow_char="^")
    exit()