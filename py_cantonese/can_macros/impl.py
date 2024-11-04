from typing import Any, Dict, List, Union, Tuple

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
from copy import deepcopy

from py_cantonese.can_error.compile_time import MacroCanNotExpand
from py_cantonese.can_ast import TokenTree, MacroMetaId, MacroMetaRepExpInPat
from py_cantonese.can_lexer.can_token import can_token
from py_cantonese.can_macros.match_state import MatchState
from py_cantonese.can_macros.meta_var import MetaVar
from py_cantonese.can_macros.pat_matcher import PatRuler
import py_cantonese.can_ast as can_ast
from py_cantonese.can_const import *
from py_cantonese.can_macros.regex import *

from py_cantonese.can_macros.macro import Macros
from py_cantonese.can_context import can_parser_context


class TokenTreeHelper:
    @staticmethod
    def tree_to_list(tree: TokenTree):
        ys = [tree.open_ch]
        for leaf in tree.child:
            if isinstance(leaf, TokenTree):
                ys.extend(TokenTreeHelper.tree_to_list(leaf))
            else:
                ys.append(leaf)
        ys.append(tree.close_ch)
        return ys


def flatten(xs):
    ys = []
    if isinstance(xs, Iterable):
        for x in xs:
            ys.extend(flatten(x))
    else:
        ys.append(xs)
    return ys


def build_regex(l: list) -> Regex:
    if not l:
        return Empty()
    x = l.pop(0)
    node = None
    if isinstance(x, can_token):
        node = Atom(x)
    elif isinstance(x, MacroMetaId):
        node = Var(x._id, x.frag_spec)
    elif isinstance(x, MacroMetaRepExpInPat):
        if x.rep_op == RepOp.CLOSURE.value:
            node = Star(build_regex(x.token_trees + [x.rep_sep]))
        elif x.rep_op == RepOp.OPRIONAL.value:
            node = Concat(
                Optional(build_regex(x.token_trees)), Optional(Atom(x.rep_sep))
            )
        elif x.rep_op == RepOp.PLUS_CLOSE.value:
            node = Concat(
                build_regex(x.token_trees + [x.rep_sep]),
                Star(build_regex(x.token_trees + [x.rep_sep])),
            )
    return Concat(node, build_regex(l))


class CanMacro(Macros):
    def __init__(self, name, patterns, bodys) -> None:
        self.name = name
        self.patterns = patterns
        self.bodys = bodys

    def try_expand(self, tokentrees: TokenTree):
        for pat, block in zip(self.patterns, self.bodys):
            init_match_state = MatchState({})
            matcher = PatRuler().with_state(init_match_state)
            if matcher.matches(
                build_regex(deepcopy(pat)),
                TokenTreeHelper.tree_to_list(tokentrees)[1:-1],
            ):
                return matcher.get_state().meta_vars, block
        raise MacroCanNotExpand(f"展開唔到Macro: {self.name} ...")

    def ensure_repetition(
        self, rep_exp: can_ast.MacroMetaRepExpInBlock, meta_vars: Dict[str, MetaVar]
    ) -> Tuple[bool, int]:

        if isinstance(rep_exp.token_trees, can_ast.MetaIdExp):
            return True, meta_vars.get(rep_exp.token_trees.name).get_repetition_times()

        ensure = False
        times = 0  # 元变量出现次数
        for value in rep_exp.token_trees.child:
            if isinstance(value, can_ast.MetaIdExp):
                ensure = True
                v = meta_vars.get(value.name)
                times = v.get_repetition_times() if v else 0
            elif isinstance(value, can_ast.MacroMetaRepExpInBlock):
                _ensure, _times = self.ensure_repetition(value, meta_vars)
                ensure = _ensure and ensure and (times == _times)
        return ensure, times

    def yield_repetition(
        self, rep: can_ast.MacroMetaRepExpInBlock, meta_vars: Dict[str, MetaVar]
    ) -> Union[Any, List[Any]]:
        ensure, times = self.ensure_repetition(rep, meta_vars)
        if ensure:
            if rep.rep_op == RepOp.PLUS_CLOSE.value:
                res = []
                for time in range(times):
                    res.extend(self.modify_body(rep.token_trees, meta_vars))
                    if time != times - 1 and rep.rep_sep:
                        res.append(rep.rep_sep)
                return res

            elif rep.rep_op == RepOp.OPRIONAL.value:
                if times == 0:
                    return []
                else:
                    return self.modify_body(rep.token_trees, meta_vars)
            elif rep.rep_op == RepOp.CLOSURE.value:
                if times == 0:
                    return []
                else:
                    res = []
                    for time in range(times):
                        res.extend(self.modify_body(rep.token_trees, meta_vars))
                        if time != times - 1 and rep.rep_sep:
                            res.append(rep.rep_sep)
                    return res
            else:
                raise Exception("Unreachable!!!")
        else:
            raise MacroCanNotExpand("repetition")

    def apply_meta_op(
        self,
        meta_vars: Any,
        token: Union[
            can_token,
            can_ast.MetaIdExp,
            can_ast.CallMacro,
            can_ast.MacroMetaRepExpInBlock,
        ],
    ):
        if isinstance(token, can_token):
            return token
        elif isinstance(token, can_ast.MetaIdExp):
            return meta_vars.get(token.name).value
        elif isinstance(token, can_ast.MacroMetaRepExpInBlock):
            x = self.yield_repetition(token, meta_vars)
            return x
        elif isinstance(token, TokenTree):
            x = list(
                map(
                    lambda tk: self.apply_meta_op(meta_vars, tk),
                    TokenTreeHelper.tree_to_list(token),
                )
            )
            return x

    def modify_body(self, body: TokenTree, meta_vars: Any):
        return flatten(map(lambda tk: self.apply_meta_op(meta_vars, tk), body.child))

    def expand(self, tokentrees: TokenTree):
        matched_meta_vars, body = self.try_expand(tokentrees)
        body = self.modify_body(body, matched_meta_vars)
        ast_result = (
            can_parser_context.with_name("stat").with_tokens(deepcopy(body)).parse()
        )
        return ast_result
