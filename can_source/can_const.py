"""
    Inner library: Some global const value for cantonese
"""

from can_source.can_lexer.can_lexer import TokenType, can_token
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
        raise Exception(
            f"case meta var's token type {tk}: it's value `{tk.value}` can not into FragSpec"
        )


_version_ = "Cantonese\033[5;33m 1.0.9\033[0m Copyright (C) 2020-2024\033[5;35m StepfenShawn\033[0m"
logo = (
    "\033[0;34m"
    + r"""
   ______            __                           
  / ________ _____  / /_____  ____  ___  ________ 
 / /   / __ `/ __ \/ __/ __ \/ __ \/ _ \/ ___/ _ \
/ /___/ /_/ / / / / /_/ /_/ / / / /  __(__  /  __/
\____/\__,_/_/ /_/\__/\____/_/ /_/\___/____/\___/ 
         
"""
    + "\033[0m"
    + "Keep cantonese alive!\nSource: https://github.com/StepfenShawn/Cantonese\n鐘意嘅話star埋我啊! Thank you!"
)
