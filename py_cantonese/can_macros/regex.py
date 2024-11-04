from typing import TypeVar, Tuple, Any

from py_cantonese.can_const import FragSpec
from py_cantonese.can_lexer.can_token import can_token

Self = TypeVar("Self")


class Regex:
    pass


class Atom(Regex):
    def __init__(self, token: can_token) -> None:
        self.token = token

    def __repr__(self) -> str:
        return "atom(token(" + self.token.value + ")"


class Var(Regex):
    def __init__(self, var: can_token, spec: FragSpec) -> None:
        self.var = var
        self.spec = spec

    def __repr__(self) -> str:
        return "meta_var(" + self.var.value + ":" + self.spec.value + ")"


class Empty(Regex):
    def __repr__(self) -> str:
        return "Empty"


class Concat(Regex):
    def __init__(self, left: Regex, right: Regex) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        s = "concat:\n"
        if self.left:
            s += "\tleft: " + repr(self.left) + "\n"
        if self.right:
            s += "\tright: " + repr(self.right) + "\n"
        return s


# *
class Star(Regex):
    def __init__(self, v: Regex) -> None:
        self.v = v

    def __repr__(self) -> str:
        return "Star:\n" + repr(self.v)


# ?
class Optional(Regex):
    def __init__(self, v: Regex) -> None:
        self.v = v

    def __repr__(self) -> str:
        return "Optional:\n" + repr(self.v)
