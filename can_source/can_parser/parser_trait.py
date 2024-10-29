import os
from can_source.can_error.compile_time import NoTokenException, NoParseException
from can_source.can_lexer.can_lexer import TokenType, can_token, getCtxByLine, Pos
from can_source.can_utils.show.infoprinter import ErrorPrinter
from collections import namedtuple
from typing import List, Union, Any, Callable


def pos_tracker(func):
    """
    追踪Token位置
    """

    def wrapper(self, *args, **kwargs):
        start_pos = self.Fn.next_lexer_pos
        ast = func(self, *args, **kwargs)
        if ast == "EOF":
            return
        if self.Fn.last_tk:
            end_pos = self.Fn.last_tk.pos
            ast.pos = Pos(
                line=start_pos.line,
                offset=start_pos.offset,
                end_line=end_pos.end_line,
                end_offset=end_pos.end_offset,
            )
        return ast

    return wrapper


def new_token_context(tokens: List[can_token]):
    cls = namedtuple("TokenContext", ["tokens", "buffer_tokens"])
    return cls(tokens=tokens, buffer_tokens=[])


class ParserFn:
    """
    A class that embedded in every `Parser` class.
    """

    def __init__(self, ctx) -> None:
        self.last_tk = None
        self.ctx = ctx

    def start_record(self):
        """
        开始记录Token (!用于backtrace)
        """
        self.record = True
        self.cache = []

    def close_record(self):
        """
        停止记录Token (!用于backtrace)
        """
        self.record = False
        self.cache = []

    def roll_back(self):
        """
        Used for implementing `backtrace` for parser.
        """
        if not hasattr(self, "record") or not self.record:
            raise Exception("Unreachable!!!")
        self.cache.reverse()
        for tk in self.cache:
            self.ctx.buffer_tokens.insert(0, tk)
        self.close_record()

    def get_record(self):
        return self.cache

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
            next_tk = self.ctx.buffer_tokens.pop(0)
        else:
            next_tk = self._next()
            self.last_tk = next_tk
        if hasattr(self, "record") and self.record:
            self.cache.append(next_tk)
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
        if hasattr(self, "record") and self.record:
            self.cache.append(self.last_tk)

    @property
    def next_lexer_pos(self) -> Pos:
        return self.try_look_ahead().pos

    def eats(self, tk_list: List[Union[str, TokenType]]):
        for v in tk_list:
            if isinstance(v, str):
                self.eat_tk_by_value(v)
            else:
                self.eat_tk_by_kind(v)

    # strict match
    def match_tk(self, expect_tk: can_token) -> bool:
        tk = self.try_look_ahead()
        return tk.value == expect_tk.value and tk.typ == expect_tk.typ

    def match(self, v: Union[TokenType, List, str]) -> bool:
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

    def eat_tk_by_value(self, expectation: Union[List, str]) -> can_token:
        tk = self.look_ahead()
        if hasattr(self, "record") and self.record:
            self.cache.append(tk)
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

    def error(self, tk: can_token, info: str, tips: str):
        ctx = getCtxByLine(os.environ["CUR_FILE"], tk.lineno)
        raise NoParseException(
            ErrorPrinter(
                info=f'{info}\n 畀 parser 不經意"莊"到:',
                pos=tk.pos,
                ctx=ctx,
                tips=tips,
                _file=os.environ["CUR_FILE"],
                _len=len(tk.value.encode("gbk")),
            ).err_msg()
        )

    def many(
        self, other_parse_fn: Callable[[], Any], util_cond: Callable[[], bool]
    ) -> list:
        result = []
        while not util_cond():
            result.append(other_parse_fn())
        return result

    def oneplus(
        self, other_parse_fn: Callable[[], Any], util_cond: Callable[[], bool]
    ) -> list:
        result = [other_parse_fn()]
        while not util_cond():
            result.append(other_parse_fn())
        return result

    def maybe(
        self, other_parse_fn: Callable[[], Any], case_cond: Callable[[], bool]
    ) -> object:
        if not case_cond():
            return None
        self.skip_once()
        return other_parse_fn()
