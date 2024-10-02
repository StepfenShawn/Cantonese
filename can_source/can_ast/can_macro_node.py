from dataclasses import dataclass
from typing import List

from can_source.can_ast.can_exp import Exp
from can_source.can_ast.can_stat import Stat
from can_source.can_const import RepOp


@dataclass
class MetaIdExp(Exp):
    """
    meta var in `macro-blocks`
    """

    name: str


@dataclass
class MetaRepExp(Exp):
    """
    meta repetitions in `macro-blocks`
    """

    token_trees: List[object]
    sep: str
    rep_op: RepOp


@dataclass
class MacroDefStat(Stat):
    match_pats: List[Exp]
    match_block: List[Stat]
    pos: object = None


@dataclass
class MacroMetaId(Exp):
    """
    meta id in `macro-patterns`
    """

    _id: Exp
    frag_spec: Exp


@dataclass
class MacroMetaRepExp(Exp):
    """
    meta exp in `macro-patterns`
    """

    token_trees: List[object]
    rep_sep: Exp
    rep_op: Exp


@dataclass
class MacroResult:
    """
    inner-result before expand
    """

    meta_var: dict
    results: list


@dataclass
class TokenTree:
    val: List[object]
