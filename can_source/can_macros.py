from dataclasses import dataclass, fields
from typing import Tuple

from can_source.can_error.compile_time import NoTokenException, MacroCanNotExpand
from can_source.can_ast import MacroResult, TokenTree, MacroMetaRepExp, MacroMetaId
from can_source.can_parser import *
from can_source.can_const import *
from can_source.parser_trait import ParserFn, new_token_context

from can_source.macros.macro import Macros

class MetaVarTracker:
    """
    A class to track every meta vars.
    Used for `meta repetitions` feature.
    """

    def __init__(self, tracker: dict):
        self.tracker = tracker

    def update(self, vars: dict):
        for name in vars:
            if name in self.tracker:
                self.tracker[name].append(vars.get(name))
            else:
                self.tracker[name] = [vars.get(name)]

    def get_rep_times(self, name):
        return len(self.tracker.get(name, []))


@dataclass
class MatchState:
    parser_fn: ParserFn
    meta_vars: dict
    meta_rep: MetaVarTracker


def match_token(excepted: can_token, state: MatchState) -> Tuple[MatchState, bool]:
    """
    匹配一个token
    """
    try:
        if state.parser_fn.match_tk(excepted):
            state.parser_fn.skip_once()
            return state, True
        else:
            return state, False
    except NoTokenException:
        return state, False


def match_macro_meta_id(pat: MacroMetaId, state: MatchState) -> Tuple[MatchState, bool]:
    """
    匹配元变量
    """

    meta_var_name = pat._id.value
    spec = FragSpec.from_can_token(pat.frag_spec)
    try:
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
        elif spec == FragSpec.LITERAL:
            next_tk = state.parser_fn.try_look_ahead()
            if next_tk.typ == TokenType.STRING:
                ast_node = can_ast.can_exp.StringExp(
                    s=state.parser_fn.eat_tk_by_kind(TokenType.STRING).value
                )
            elif next_tk.typ == TokenType.NUM:
                ast_node = can_ast.can_exp.NumeralExp(
                    val=state.parser_fn.eat_tk_by_kind(TokenType.NUM).value
                )
            else:
                return state, False
            state.meta_vars.update({meta_var_name: ast_node})
        else:
            return state, False
    except NoTokenException:
        return state, False
    return state, True


def match_macro_meta_repexp(
    pat: MacroMetaRepExp, state: MatchState
) -> Tuple[MatchState, bool]:
    if state.parser_fn.no_tokens():
        return state, False

    if pat.rep_op == RepOp.CLOSURE.value:  # *
        for tk_node in pat.token_trees:
            state, result = match_pattern(tk_node, state)
        if pat.rep_sep:
            state.parser_fn.eat_tk_by_value(pat.rep_sep)
        state.meta_rep.update(state.meta_vars)
        while result:
            try:
                for tk_node in pat.token_trees:
                    state, result = match_pattern(tk_node, state)
                    if pat.rep_sep:
                        state.parser_fn.eat_tk_by_value(pat.rep_sep)
                    state.meta_rep.update(state.meta_vars)
            except NoTokenException as e:
                break
    elif pat.rep_op == RepOp.OPRIONAL.value:  # ?
        for tk_node in pat.token_trees:
            state, result = match(pat.token_trees, state)
        if result:
            if pat.rep_sep:
                state.parser_fn.eat_tk_by_value(pat.rep_sep)
            state.meta_rep.update(state.meta_vars)
        else:
            return state, True
    elif pat.rep_op == RepOp.PLUS_CLOSE.value:  # +
        for tk_node in pat.token_trees:
            state, result = match(pat.token_trees, state)
        if result:
            if pat.rep_sep:
                state.parser_fn.eat_tk_by_value(pat.rep_sep)
            state.meta_rep.update(state.meta_vars)
            while result:
                try:
                    for tk_node in pat.token_trees:
                        state, result = match_pattern(tk_node, state)
                        if pat.rep_sep:
                            state.parser_fn.eat_tk_by_value(pat.rep_sep)
                        state.meta_rep.update(state.meta_vars)
                except NoTokenException as e:
                    break
        else:
            return state, False
    else:
        return state, False
    return state, True


def match_pattern(pat, state: MatchState) -> Tuple[MatchState, bool]:
    if isinstance(pat, MacroMetaId):
        state, result = match_macro_meta_id(pat, state)
    elif isinstance(pat, MacroMetaRepExp):
        state, result = match_macro_meta_repexp(pat, state)
    else:
        state, result = match_token(pat, state)
    return state, result


def match(pattern, state: MatchState) -> Tuple[MatchState, bool]:
    # if no pattern? (Epsilon)
    if len(pattern) == 0:
        return (state, True) if state.parser_fn.no_tokens() else (state, False)

    for pat in pattern:
        state, result = match_pattern(pat, state)
        if not result:
            return state, False

    # all pattern has been matched, it's should be `no_tokens` state
    if state.parser_fn.no_tokens():
        return state, True
    else:
        return state, False


class CanMacro(Macros):
    def __init__(self, name, patterns, bodys) -> None:
        self.name = name
        self.patterns = patterns
        self.bodys = bodys

    def try_expand(self, tokentrees: TokenTree):
        for pat, block in zip(self.patterns, self.bodys):
            init_match_state = MatchState(
                ParserFn(new_token_context((token for token in tokentrees.val))),
                {},
                MetaVarTracker({}),
            )
            match_res, result = match(pat, init_match_state)
            if result:
                return match_res.meta_vars, match_res.meta_rep, block
        raise MacroCanNotExpand(f"Can not expand macro: {self.name}")
    
    def modify_body(self, body, meta_vars: dict):
        for child in fields(body):
            value = getattr(body, child.name)
            if isinstance(value, can_ast.MetaIdExp):
                setattr(body, child.name, meta_vars.get(value.name))
            elif isinstance(value, (can_ast.Stat, can_ast.Exp)):
                self.modify_body(value, meta_vars)
            elif isinstance(value, (list, set)):
                for v in value:
                    self.modify_body(v, meta_vars)
            
        return body
        
    def expand(self, tokentrees: TokenTree) -> MacroResult:
        matched_meta_vars, matched_meta_rep, body = self.try_expand(tokentrees)
        return self.modify_body(body, matched_meta_vars)
