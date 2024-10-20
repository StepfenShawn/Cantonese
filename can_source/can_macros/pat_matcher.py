from typing import Tuple
from can_source.can_macros.match_state import MatchState
from can_source.can_error.compile_time import NoParseException, NoTokenException
from can_source.can_ast import TokenTree, MacroMetaRepExp, MacroMetaId
from can_source.can_parser import *
from can_source.can_const import *


def match_token(excepted: can_token, state: MatchState) -> Tuple[MatchState, bool]:
    """
    匹配一个token
    """
    state.parser_fn.start_record()
    try:
        if state.parser_fn.match_tk(excepted):
            state.parser_fn.skip_once()
            return state, True
        else:
            state.parser_fn.roll_back()
            return state, False
    except NoTokenException:
        state.parser_fn.roll_back()
        return state, False


def match_macro_meta_id(pat: MacroMetaId, state: MatchState) -> Tuple[MatchState, bool]:
    """
    匹配元变量
    """

    meta_var_name = pat._id.value
    spec = FragSpec.from_can_token(pat.frag_spec)
    try:
        if spec == FragSpec.IDENT and state.parser_fn.match(TokenType.IDENTIFIER):
            ast_node = can_ast.can_exp.IdExp(
                name=state.parser_fn.eat_tk_by_kind(TokenType.IDENTIFIER).value
            )
            state.update_meta_vars(meta_var_name, ast_node)
        elif spec == FragSpec.STMT:
            state.parser_fn.start_record()
            try:
                ast_node = StatParser(from_=state.curF).parse()
            except (NoTokenException, NoParseException) as e:
                state.parser_fn.roll_back()
                return state, False
            else:
                state.update_meta_vars(meta_var_name, ast_node)
        elif spec == FragSpec.EXPR:
            state.parser_fn.start_record()
            try:
                ast_node = ExpParser.from_ParserFn(state.parser_fn).parse_exp()
            except (NoTokenException, NoParseException) as e:
                state.parser_fn.roll_back()
                return state, False
            else:
                state.update_meta_vars(meta_var_name, ast_node)
        elif spec == FragSpec.STR and state.parser_fn.match(TokenType.STRING):
            ast_node = can_ast.can_exp.StringExp(
                s=state.parser_fn.eat_tk_by_kind(TokenType.STRING).value
            )
            state.update_meta_vars(meta_var_name, ast_node)
        elif spec == FragSpec.LITERAL and (
            state.parser_fn.match(TokenType.STRING)
            or state.parser_fn.match(TokenType.NUM)
        ):
            if state.parser_fn.match(TokenType.STRING):
                ast_node = can_ast.can_exp.StringExp(
                    s=state.parser_fn.eat_tk_by_kind(TokenType.STRING).value
                )
            elif state.parser_fn.match(TokenType.NUM):
                ast_node = can_ast.can_exp.NumeralExp(
                    val=state.parser_fn.eat_tk_by_kind(TokenType.NUM).value
                )
            state.update_meta_vars(meta_var_name, ast_node)
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
        if result and pat.rep_sep:
            state.parser_fn.eat_tk_by_value(pat.rep_sep)
        while result:
            try:
                for tk_node in pat.token_trees:
                    state, result = match_pattern(tk_node, state)
                if result and pat.rep_sep:
                    state.parser_fn.eat_tk_by_value(pat.rep_sep)
            except NoTokenException as e:
                break
        return state, True
    elif pat.rep_op == RepOp.OPRIONAL.value:  # ?
        for tk_node in pat.token_trees:
            state, result = match_pattern(tk_node, state)
        if result and pat.rep_sep:
            state.parser_fn.eat_tk_by_value(pat.rep_sep)
        return state, True
    elif pat.rep_op == RepOp.PLUS_CLOSE.value:  # +
        result = True
        state.parser_fn.start_record()
        for tk_node in pat.token_trees:
            state, r = match_pattern(tk_node, state)
            result &= r
        if result and pat.rep_sep:
            state.parser_fn.eat_tk_by_value(pat.rep_sep)
            while result:
                try:
                    for tk_node in pat.token_trees:
                        state, result = match_pattern(tk_node, state)
                        if not result:
                            break
                    if result and pat.rep_sep:
                        state.parser_fn.eat_tk_by_value(pat.rep_sep)
                except NoTokenException as e:
                    break
        else:
            state.parser_fn.roll_back()
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
