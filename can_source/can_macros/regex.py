from typing import TypeVar, Tuple, Any

from can_source.can_const import FragSpec
from can_source.can_lexer.can_token import can_token

Self = TypeVar("Self")


class Regex:
    pass


class Atom(Regex):
    def __init__(self, token: can_token) -> None:
        self.token = token


class Var(Regex):
    def __init__(self, var: can_token, spec: FragSpec) -> None:
        self.var = var
        self.spec = spec


class Empty(Regex):
    pass


class Concat(Regex):
    def __init__(self, left: Regex, right: Regex) -> None:
        self.left = left
        self.right = right


# *
class Star(Regex):
    def __init__(self, v: Regex) -> None:
        self.v = v


# +
class Plus(Regex):
    def __init__(self, v: Regex) -> None:
        self.v = v


# ?
class Optional(Regex):
    def __init__(self, v: Regex) -> None:
        self.v = v
