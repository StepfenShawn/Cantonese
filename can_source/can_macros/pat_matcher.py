from copy import deepcopy
from typing import List, TypeVar

from can_source.can_macros.regex import *
from can_source.can_macros.match_state import MatchState
from can_source.can_ast import TokenTree
from can_source.can_parser import *
from can_source.can_const import *
from can_source.can_context import can_parser_context


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
                self.state.update_meta_vars(meta_var_name, tokens)
                return True

        elif spec == FragSpec.STR:
            if len(tokens) == 1 and tokens[-1].typ == TokenType.STRING:
                self.state.update_meta_vars(meta_var_name, tokens)
                return True

        elif spec == FragSpec.LITERAL:
            if len(tokens) == 1 and tokens[-1].typ in [
                TokenType.STRING,
                TokenType.NUM,
            ]:
                self.state.update_meta_vars(meta_var_name, tokens)
                return True

        elif spec == FragSpec.STMT:
            try:
                can_parser_context.with_name("stat").with_tokens(
                    deepcopy(tokens)
                ).parse()
            except (NoParseException, NoTokenException):
                return False
            else:
                self.state.update_meta_vars(meta_var_name, tokens)
                return True

        elif spec == FragSpec.EXPR:
            try:
                (
                    can_parser_context.with_name("exp")
                    .with_tokens(deepcopy(tokens))
                    .parse(name="parse_exp")
                )
            except (NoParseException, NoTokenException):
                return False
            else:
                self.state.update_meta_vars(meta_var_name, tokens)
                return True

        return False

    def matches(self, regex: Regex, tokens: List[can_token]) -> bool:
        if isinstance(regex, Empty):
            return tokens == []
        elif isinstance(regex, Atom):
            return len(tokens) == 1 and tokens[-1].value == regex.token.value
        elif isinstance(regex, Var):
            return self.match_var(regex, tokens)
        elif isinstance(regex, Concat):
            for prefix, suffix in split(tokens):
                if self.matches(regex.left, prefix) and self.matches(regex.right, suffix):
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
