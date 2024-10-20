from dataclasses import fields
from typing import Any, Dict, List, Union, Tuple

from can_source.can_error.compile_time import MacroCanNotExpand
from can_source.can_ast import TokenTree
from can_source.can_macros.match_state import MatchState
from can_source.can_macros.meta_var import MetaVar
from can_source.can_macros.pat_matcher import match
from can_source.can_parser import *
from can_source.can_const import *
from can_source.can_parser.parser_trait import ParserFn, new_token_context

from can_source.can_macros.macro import Macros


class CanMacro(Macros):
    def __init__(self, name, patterns, bodys) -> None:
        self.name = name
        self.patterns = patterns
        self.bodys = bodys

    def try_expand(self, tokentrees: TokenTree):
        for pat, block in zip(self.patterns, self.bodys):
            init_match_state = MatchState(
                ParserFn(new_token_context((token for token in tokentrees.val))), {}
            )
            match_res, result = match(pat, init_match_state)
            if result:
                return match_res.meta_vars, block
        raise MacroCanNotExpand(f"展開唔到Macro: {self.name} ...")

    def ensure_repetition(
        self, rep_exp: can_ast.MacroMetaRepExp, meta_vars: Dict[str, MetaVar]
    ) -> Tuple[bool, int]:

        if isinstance(rep_exp.token_trees, can_ast.MetaIdExp):
            return True, meta_vars.get(rep_exp.token_trees.name).get_repetition_times()

        ensure = False
        times = 0  # 元变量出现次数

        for child in fields(rep_exp.token_trees):
            value = getattr(rep_exp.token_trees, child.name)
            if isinstance(value, can_ast.MetaIdExp):
                ensure = True
                times = meta_vars.get(value.name).get_repetition_times()
            elif isinstance(value, can_ast.MacroMetaRepExp):
                _ensure, _times = self.ensure_repetition(value, meta_vars)
                ensure = _ensure and ensure and (times == _times)
        return ensure, times

    def yield_repetition(
        self, rep: can_ast.MacroMetaRepExp, meta_vars: Dict[str, MetaVar]
    ) -> Union[Any, List[Any]]:
        ensure, times = self.ensure_repetition(rep, meta_vars)
        if ensure:
            if rep.rep_op == RepOp.PLUS_CLOSE.value:
                return self.expand_meta_vars(rep.token_trees, meta_vars)
            elif rep.rep_op == RepOp.OPRIONAL.value:
                return (
                    None
                    if times == 0
                    else self.expand_meta_vars(rep.token_trees, meta_vars)
                )
            elif rep.rep_op == RepOp.CLOSURE.value:
                return (
                    None
                    if times == 0
                    else self.expand_meta_vars(rep.token_trees, meta_vars)
                )
            else:
                raise Exception("Unreachable!!!")
        else:
            raise MacroCanNotExpand("repetition")

    def modify_body(self, body, meta_vars: Dict[str, MetaVar]):
        for child in fields(body):
            value = getattr(body, child.name)
            if isinstance(value, can_ast.MetaIdExp):
                setattr(body, child.name, meta_vars.get(value.name).value)
            elif isinstance(value, (can_ast.Stat, can_ast.Exp)):
                self.modify_body(value, meta_vars)
            elif isinstance(value, (list, set)):
                after_expand = []
                for sub_value in value:
                    if isinstance(sub_value, can_ast.MetaIdExp):
                        vv = meta_vars.get(sub_value.name).value
                        if isinstance(vv, list):
                            after_expand.extend(vv)
                        else:
                            after_expand.append(vv)
                    elif isinstance(sub_value, can_ast.MacroMetaRepExp):
                        vv = self.yield_repetition(sub_value, meta_vars)
                        after_expand.extend(vv)
                    else:
                        self.modify_body(sub_value, meta_vars)
                        after_expand.append(sub_value)
                setattr(body, child.name, after_expand)
        return body

    def expand_meta_vars(self, body, matched_meta_vars):
        # 单个`metaIdExp`
        if isinstance(body, can_ast.MetaIdExp):
            return matched_meta_vars.get(body.name).value
        # 其它情况
        return self.modify_body(body, matched_meta_vars)

    def expand(self, tokentrees: TokenTree):
        matched_meta_vars, body = self.try_expand(tokentrees)
        return self.expand_meta_vars(body, matched_meta_vars)
