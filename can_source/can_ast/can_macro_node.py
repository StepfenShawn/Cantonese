from dataclasses import dataclass
from typing import List, Any

from can_source.can_ast.can_exp import Exp
from can_source.can_ast.can_stat import Stat


@dataclass
class MetaIdExp(Exp):
    """
    meta var in `macro-blocks`
    """

    name: str


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
class TokenTree:
    val: List[Any]


@dataclass
class CallMacro:
    name: str
    token_trees: List[object]
