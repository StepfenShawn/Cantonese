from can_lexer import TokenType, can_token, getCtxByLine
from infoprinter import ErrorPrinter

# The root(father) of all Parser classes.
class ParserBase:

    def __init__(self, token_list : list, file = "") -> None:
        self.pos = 0
        self.tokens = token_list
        self.file = file

    def look_ahead(self, step: int) -> can_token:
        return self.tokens[self.pos + step]

    def current(self) -> can_token:
        return self.look_ahead(0)

    def get_next_token_of_kind(self, k: TokenType, step: int) -> can_token:
        tk = self.look_ahead(step)
        err = ""
        if k != tk.typ:
            err = f"\033[0;31m濑嘢!!!\033[0m: {tk.value}附近睇唔明啊大佬!!! Excepted: {str(k)}"
            self.error(tk, err)
        self.pos += 1
        return tk
    
    def get_next_token_of(self, expectation, step: int) -> can_token:
        tk = self.look_ahead(step)
        err = ""
        if isinstance(expectation, list):
            if tk.value not in expectation:
                err = f"\033[0;31m濑嘢!!!\033[0m: 睇唔明嘅语法: `{tk.value}`"
                self.error(tk, err, f" 係咪`\033[5;33m{', '.join(expectation)}\033[0m` ??")
            self.pos += 1
            return tk
        else:
            if expectation != tk.value:
                err = f"Line {tk.lineno}: 睇唔明嘅语法: `{tk.value}`"
                self.error(tk, err, f" 係咪`\033[5;33m{expectation}\033[0m` ??")
            self.pos += 1
            return tk

    def skip(self, step: int):
        self.pos += step

    def get_line(self) -> int:
        return self.tokens[self.pos].lineno

    def error(self, tk, info, tips):
        ctx = getCtxByLine(tk.lineno)
        p = ErrorPrinter(info=info, pos=tk.pos, 
            ctx=ctx, tips=tips, _file=self.file, _len=len(tk.value.encode("gbk")))
        p.show()
        exit()