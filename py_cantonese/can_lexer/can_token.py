from py_cantonese.can_lexer.pos import Pos
from py_cantonese.can_lexer.can_keywords import TokenType


class can_token:
    """
    经过 Lexer 后嘅 Token
    """

    __slots__ = ("pos", "typ", "value")

    def __init__(self, pos: Pos, typ: TokenType, value: str):
        self.pos = pos
        self.typ = typ
        self.value = value

    @property
    def lineno(self):
        return self.pos.line

    @property
    def offset(self):
        return self.pos.offset

    def __repr__(self) -> str:
        return f"{self.value} ({self.typ.name})"
