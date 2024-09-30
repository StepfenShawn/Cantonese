"""
    Inner library: Some global const value for cantonese
"""

from can_source.can_ast import AST, can_exp
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

    @staticmethod
    def from_ast(ast: AST):
        if isinstance(ast, can_exp.IdExp):
            name = ast.name
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
        raise Exception("Can not into FragSpec")
