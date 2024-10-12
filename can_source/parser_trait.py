import os
from can_source.can_error import NoTokenException
from can_source.can_lexer import TokenType, can_token, getCtxByLine, Pos
from can_source.can_utils.infoprinter import ErrorPrinter
from collections import namedtuple


def pos_tracker(func):
    """
    追踪Token位置
    """

    def wrapper(self, *args, **kwargs):
        start_pos = self.Fn.next_lexer_pos
        ast = func(self, *args, **kwargs)
        if ast == "EOF":
            return
        end_pos = self.Fn.last_tk.pos
        ast.pos = Pos(
            line=start_pos.line,
            offset=start_pos.offset,
            end_line=end_pos.end_line,
            end_offset=end_pos.end_offset,
        )
        return ast

    return wrapper


def new_token_context(tokens):
    cls = namedtuple("TokenContext", ["tokens", "buffer_tokens"])
    return cls(tokens=tokens, buffer_tokens=[])


class ParserFn:
    def __init__(self, ctx) -> None:
        self.last_tk = None
        self.ctx = ctx

    def _next(self):
        try:
            return next(self.ctx.tokens)
        except StopIteration as e:
            raise NoTokenException("No tokens...")

    def no_tokens(self):
        if self.ctx.buffer_tokens:
            return False
        else:
            try:
                self.ctx.buffer_tokens.append(self._next())
            except NoTokenException as e:
                return True
            return False

    def look_ahead(self) -> can_token:
        if self.ctx.buffer_tokens:
            return self.ctx.buffer_tokens.pop(0)

        next_tk = self._next()
        self.last_tk = next_tk
        return next_tk

    def try_look_ahead(self) -> can_token:
        if self.ctx.buffer_tokens:
            return self.ctx.buffer_tokens[0]
        next_tk = self._next()
        self.ctx.buffer_tokens.append(next_tk)
        return next_tk

    def skip_once(self) -> None:
        if self.ctx.buffer_tokens:
            self.last_tk = self.ctx.buffer_tokens.pop(0)
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

    # strict match
    def match_tk(self, expect_tk: can_token) -> bool:
        tk = self.try_look_ahead()
        return tk.value == expect_tk.value and tk.typ == expect_tk.typ

    def match(self, v) -> bool:
        if self.no_tokens():
            return False
        tk = self.try_look_ahead()
        if isinstance(v, TokenType):
            return tk.typ == v
        elif isinstance(v, list):
            for x in v:
                if self.match(x):
                    return True
            return False
        else:
            return tk.value == v

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
                self.error(
                    tk, err, f" 係咪`\033[5;33m{', '.join(expectation)}\033[0m` ??"
                )
            return tk
        else:
            if expectation != tk.value:
                err = f"Line {tk.lineno}: 睇唔明嘅语法: `{tk.value}`"
                self.error(tk, err, f" 係咪`\033[5;33m{expectation}\033[0m` ??")
            return tk

    def error(self, tk, info, tips):
        ctx = getCtxByLine(os.environ["CUR_FILE"], tk.lineno)
        p = ErrorPrinter(
            info=f'{info}\n 畀 parser 不經意"莊"到:',
            pos=tk.pos,
            ctx=ctx,
            tips=tips,
            _file=os.environ["CUR_FILE"],
            _len=len(tk.value.encode("gbk")),
        )
        p.show()
        exit()

    def many(self, other_parse_fn, util_cond) -> list:
        result = []
        while not util_cond():
            result.append(other_parse_fn())
        return result

    def oneplus(self, other_parse_fn, util_cond) -> list:
        result = [other_parse_fn()]
        while not util_cond():
            result.append(other_parse_fn())
        return result

    def maybe(self, other_parse_fn, case_cond) -> object:
        if not case_cond():
            return None
        self.skip_once()
        return other_parse_fn()
