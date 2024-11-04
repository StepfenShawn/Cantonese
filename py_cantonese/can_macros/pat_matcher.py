from copy import deepcopy
from typing import List, TypeVar

from py_cantonese.can_macros.regex import *
from py_cantonese.can_macros.match_state import MatchState
from py_cantonese.can_ast import TokenTree
from py_cantonese.can_parser import *
from py_cantonese.can_const import *
from py_cantonese.can_context import can_parser_context


def split(xs: list):
    if len(xs) == 1:
        return [(xs, [])]
    return [(xs[:i], xs[i:]) for i in range(0, len(xs))] + [(xs, [])]


def prefix_split(xs: list):
    return [(xs[:i], xs[i:]) for i in range(1, len(xs))] + [(xs, [])]


Self = TypeVar("Self")


class PatRuler:

    def with_state(self, state: MatchState) -> Self:
        self.state = state
        return self

    def match_var(self, regex: Var, tokens: List[can_token]) -> bool:
        meta_var_name = regex.var.value
        spec = FragSpec.from_can_token(regex.spec)
        if spec == FragSpec.IDENT:
            if len(tokens) == 1 and tokens[-1].typ == TokenType.IDENTIFIER:
                return True

        elif spec == FragSpec.STR:
            if len(tokens) == 1 and tokens[-1].typ == TokenType.STRING:
                return True

        elif spec == FragSpec.LITERAL:
            if len(tokens) == 1 and tokens[-1].typ in [
                TokenType.STRING,
                TokenType.NUM,
            ]:
                return True

        elif spec == FragSpec.STMT:
            try:
                if (
                    can_parser_context.with_name("stat")
                    .with_tokens(deepcopy(tokens))
                    .can_be_parse_able(name="parse")
                ):
                    return True
            except (NoParseException, NoTokenException):
                return False

        elif spec == FragSpec.EXPR:
            try:
                if (
                    can_parser_context.with_name("exp")
                    .with_tokens(deepcopy(tokens))
                    .can_be_parse_able(name="parse_exp")
                ):
                    return True
            except (NoParseException, NoTokenException):
                return False

        return False

    def matches(self, regex: Regex, tokens: List[can_token]) -> bool:
        if isinstance(regex, Empty):
            return tokens == []
        elif isinstance(regex, Atom):
            return len(tokens) == 1 and tokens[-1].value == regex.token.value
        elif isinstance(regex, Var):
            return self.match_var(regex, tokens)
        elif isinstance(regex, Optional):
            print(regex.v, tokens)
            return self.matches(regex.v, tokens) or tokens == []
        elif isinstance(regex, Concat):
            for prefix, suffix in split(tokens):
                if self.matches(regex.left, prefix) and self.matches(
                    regex.right, suffix
                ):
                    if isinstance(regex.left, Var):
                        self.state.update_meta_vars(regex.left.var.value, prefix)
                    if isinstance(regex.right, Var):
                        self.state.update_meta_vars(regex.right.var.value, suffix)
                    return True
            return False
        elif isinstance(regex, Star):
            if tokens == []:
                return True
            for prefix, suffix in prefix_split(tokens):
                if self.matches(regex.v, prefix) and self.matches(regex, suffix):
                    return True
            return False

    def get_state(self):
        return self.state
