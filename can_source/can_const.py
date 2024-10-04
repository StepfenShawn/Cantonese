"""
    Inner library: Some global const value for cantonese
"""

from can_source.can_lexer import TokenType, can_token
from enum import Enum


class RepOp(Enum):
    CLOSURE = "*"
    PLUS_CLOSE = "+"
    OPRIONAL = "?"


class FragSpec(Enum):
    BLOCK = 0
    EXPR = 1
    IDENT = 2
    LITERAL = 3
    STMT = 4
    STR = 5
    TT = 6

    @staticmethod
    def from_can_token(tk: can_token):
        if tk.typ == TokenType.IDENTIFIER:
            name = tk.value
            if name == "id" or name == "ident":
                return FragSpec.IDENT
            elif name == "expr":
                return FragSpec.EXPR
            elif name == "lit":
                return FragSpec.LITERAL
            elif name == "stmt":
                return FragSpec.STMT
            elif name == "block":
                return FragSpec.BLOCK
            elif name == "str":
                return FragSpec.STR
            elif name == "tt":
                return FragSpec.TT
        raise Exception(f"case meta var's token type {tk}: Can not into FragSpec")
