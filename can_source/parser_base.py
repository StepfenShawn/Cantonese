import os
from can_source.can_lexer import TokenType, can_token, getCtxByLine, Pos
from can_source.util.infoprinter import ErrorPrinter

def pos_tracker(func):
    def wrapper(self, *args, **kwargs):
        start_pos = self.next_lexer_pos
        ast = func(self, *args, **kwargs)
        if ast == "EOF":
            return
        end_pos = self.last_tk.pos
        ast.pos = Pos(line=start_pos.line,
                      offset=start_pos.offset,
                      end_line=end_pos.end_line,
                      end_offset=end_pos.end_offset)
        return ast
    return wrapper

# The root(father) of all Parser classes.
class ParserBase():
    __slots__ = ("tokens", "buffer_tokens")
    def __init__(self, token_ctx: tuple) -> None:
        self.tokens, self.buffer_tokens = token_ctx
        self.last_tk = None

    def get_token_ctx(self) -> tuple:
        return (self.tokens, self.buffer_tokens)

    def _next(self):
        try:
            return next(self.tokens)
        except StopIteration as e:
            pass

    def look_ahead(self) -> can_token:
        if self.buffer_tokens:
            return self.buffer_tokens.pop(0)
            
        next_tk = self._next()
        self.last_tk = next_tk
        return next_tk

    def try_look_ahead(self) -> can_token:
        if self.buffer_tokens:
            return self.buffer_tokens[0]
        next_tk = self._next()
        self.buffer_tokens.append(next_tk)
        return next_tk

    def skip_once(self) -> None:
        if self.buffer_tokens:
            self.last_tk = self.buffer_tokens.pop(0)
        else:
            self.last_tk = self._next()

    @property
    def next_lexer_pos(self) -> Pos:
        return self.try_look_ahead().pos

    def eats(self, tk_list):
        for v in tk_list:
            if isinstance(v, str):
                self.eat_tk_by_value(v)
            else:
                self.eat_tk_by_kind(v)
        
    def eat_tk_by_kind(self, k: TokenType) -> can_token:
        tk = self.look_ahead()
        err = ""
        if k != tk.typ:
            err = f"\033[0;31m濑嘢!!!\033[0m: `{tk.value}`好似有D唔三唔四"
            self.error(tk, err, f" 不妨嘗試下`{k.name}`類型??")
        return tk
    
    def eat_tk_by_value(self, expectation) -> can_token:
        tk = self.look_ahead()
        err = ""
        if isinstance(expectation, list):
            if tk.value not in expectation:
                err = f"\033[0;31m濑嘢!!!\033[0m: 睇唔明嘅语法: `{tk.value}`"
                self.error(tk, err, f" 係咪`\033[5;33m{', '.join(expectation)}\033[0m` ??")
            return tk
        else:
            if expectation != tk.value:
                err = f"Line {tk.lineno}: 睇唔明嘅语法: `{tk.value}`"
                self.error(tk, err, f" 係咪`\033[5;33m{expectation}\033[0m` ??")
            return tk

    def error(self, tk, info, tips):
        ctx = getCtxByLine(os.environ["CUR_FILE"], tk.lineno)
        p = ErrorPrinter(info=f'{info}\n 畀 parser 不經意"莊"到:', pos=tk.pos, 
            ctx=ctx, tips=tips, _file=os.environ["CUR_FILE"], _len=len(tk.value.encode("gbk")))
        p.show()
        exit()