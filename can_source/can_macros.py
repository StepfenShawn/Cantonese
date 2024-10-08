from dataclasses import dataclass
from typing import Optional

from can_source.can_error import NoTokenException, MacroCanNotExpand
from can_source.can_utils.option import Option
from can_source.can_ast import MacroResult, TokenTree, MacroMetaRepExp, MacroMetaId
from can_source.can_parser import *
from can_source.can_const import *
from can_source.parser_base import ParserFn, new_token_context


@dataclass
class MatchState:
    parser_fn: ParserFn
    meta_vars: dict
    meta_rep: dict


def match_token(excepted: can_token, state: MatchState) -> Optional[MatchState]:
    """
    匹配一个token
    """
    try:
        if state.parser_fn.match_tk(excepted):
            state.parser_fn.skip_once()
            return state
        else:
            return None
    except NoTokenException:
        return None


def match_macro_meta_id(pat: MacroMetaId, state: MatchState) -> Optional[MatchState]:
    """
    匹配元变量
    """
    meta_var_name = pat._id.value
    spec = FragSpec.from_can_token(pat.frag_spec)
    if spec == FragSpec.IDENT:
        ast_node = can_ast.can_exp.IdExp(
            name=state.parser_fn.eat_tk_by_kind(TokenType.IDENTIFIER).value
        )
        state.meta_vars.update({meta_var_name: ast_node})
    elif spec == FragSpec.STMT:
        ast_node = StatParser(from_=state.curF).parse()
        state.meta_vars.update({meta_var_name: ast_node})
    elif spec == FragSpec.EXPR:
        ast_node = ExpParser.from_ParserFn(state.parser_fn).parse_exp()
        state.meta_vars.update({meta_var_name: ast_node})
    elif spec == FragSpec.STR:
        ast_node = can_ast.can_exp.StringExp(
            s=state.parser_fn.eat_tk_by_kind(TokenType.STRING).value
        )
        state.meta_vars.update({meta_var_name: ast_node})
    else:
        return None
    return state


def match_macro_meta_repexp(
    pat: MacroMetaRepExp, state: MatchState
) -> Optional[MatchState]:
    if pat.rep_op == RepOp.CLOSURE.value:  # *
        try:
            try_match = match(pat.token_trees, state)
            if pat.rep_sep:
                state.parser_fn.eat_tk_by_value(pat.rep_sep)
            while try_match.is_some():
                try_match = match(pat.token_trees, state)
                if pat.rep_sep:
                    state.parser_fn.eat_tk_by_value(pat.rep_sep)
        except NoTokenException:
            return None
    elif pat.rep_op == RepOp.OPRIONAL.value:  # ?
        try_match = match(pat.token_trees, state)
    elif pat.rep_op == RepOp.PLUS_CLOSE.value:  # +
        try_match = match(pat.token_trees, state)
    else:
        return None
    return state


def match(pattern, state: MatchState) -> Option:
    # if no pattern?
    if len(pattern) == 0:
        return Option(state) if state.parser_fn.no_tokens() else Option(None)
    for pat in pattern:
        if isinstance(pat, MacroMetaId):
            state = match_macro_meta_id(pat, state)
        elif isinstance(pat, MacroMetaRepExp):
            state = match_macro_meta_repexp(pat, state)
        else:
            state = match_token(pat, state)

        # matches are considered failed when the status is `None`
        if state == None:
            return Option(None)

    return Option(state)


class CanMacro:
    def __init__(self, name, patterns, bodys) -> None:
        self.name = name
        self.patterns = patterns
        self.bodys = bodys

    def try_expand(self, tokentrees: TokenTree):
        for pat, block in zip(self.patterns, self.bodys):
            init_match_state = MatchState(
                ParserFn(new_token_context((token for token in tokentrees.val))), {}, []
            )
            match_res = match(pat, init_match_state)
            if match_res.is_some():
                meta_vars = match_res.unwrap().meta_vars
                return meta_vars, block
        raise MacroCanNotExpand(f"Can not expand macro: {self.name}")

    def eval(self, tokentrees: TokenTree) -> MacroResult:
        matched_meta_vars, block = self.try_expand(tokentrees)
        parse_res = MacroResult(matched_meta_vars, block)
        return parse_res
