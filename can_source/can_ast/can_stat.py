from dataclasses import dataclass
from typing import List
from .can_exp import Exp


class Stat:
    pass


@dataclass
class FuncCallStat(Stat):
    func_name: Exp
    args: List[Exp]
    pos: object = None


@dataclass
class IfStat(Stat):
    if_exp: Exp
    if_block: List[Stat]
    elif_exps: List[Exp]
    elif_blocks: List[Stat]
    else_blocks: List[Stat]
    pos: object = None


@dataclass
class PrintStat(Stat):
    args: List[Exp]
    pos: object = None


@dataclass
class PassStat(Stat):
    pos: object = None


@dataclass
class AssignStat(Stat):
    var_list: List[Exp]
    exp_list: List[Exp]
    pos: object = None


@dataclass
class AssignBlockStat(Stat):
    var_list: List[List[Exp]]
    exp_list: List[List[Exp]]
    pos: object = None


@dataclass
class ForStat(Stat):
    var: Exp
    from_exp: Exp
    to_exp: Exp
    blocks: List[Exp]
    pos: object = None


@dataclass
class ForEachStat(Stat):
    id_list: List[Exp]
    exp_list: List[Exp]
    blocks: List[Stat]
    pos: object = None


@dataclass
class WhileStat(Stat):
    cond_exp: Exp
    blocks: List[Stat]
    pos: object = None


@dataclass
class ListInitStat(Stat):
    pos: object = None


@dataclass
class FunctionDefStat(Stat):
    name_exp: Exp
    args: List[Exp]
    blocks: List[Stat]
    pos: object = None


@dataclass
class FuncTypeDefStat(Stat):
    func_name: Exp
    args_type: List[Exp]
    return_type: List[Exp]
    pos: object = None


@dataclass
class MethodDefStat(Stat):
    name_exp: Exp
    args: List[Exp]
    class_blocks: List[Stat]
    pos: object = None


@dataclass
class AttrDefStat(Stat):
    attrs_list: List[Exp]
    pos: object = None

@dataclass
class ClassDefStat(Stat):
    class_name: Exp
    class_extend: List[Exp]
    class_blocks: List[Stat]
    pos: object = None


@dataclass
class ImportStat(Stat):
    idlist: List[Exp]
    pos: object = None


@dataclass
class RaiseStat(Stat):
    name_exp: Exp
    pos: object = None


@dataclass
class TryStat(Stat):
    try_blocks: List[Stat]
    except_exps: List[Exp]
    except_blocks: List[Stat]
    finally_blocks: List[Stat]
    pos: object = None


@dataclass
class GlobalStat(Stat):
    idlist: List[Exp]
    pos: object = None


@dataclass
class BreakStat(Stat):
    pos: object = None


@dataclass
class ContinueStat(Stat):
    pos: object = None


@dataclass
class TypeStat(Stat):
    exps: List[Exp]
    pos: object = None


@dataclass
class AssertStat(Stat):
    exps: Exp
    pos: object = None


@dataclass
class ReturnStat(Stat):
    exps: List[Exp]
    pos: object = None


@dataclass
class DelStat(Stat):
    exps: List[Exp]
    pos: object = None


@dataclass
class CmdStat(Stat):
    args: List[Exp]
    pos: object = None


@dataclass
class MethodCallStat(Stat):
    name_exp: Exp
    method: Exp
    args: List[Exp]
    pos: object = None


@dataclass
class CallStat(Stat):
    exp: Exp
    pos: object = None


@dataclass
class MatchStat(Stat):
    match_id: Exp
    match_val: Exp
    match_block_exp: Exp
    default_match_block: List[Stat]
    pos: object = None


@dataclass
class MacroDefStat(Stat):
    match_pats: List[Exp]
    match_block: List[Stat]
    pos: object = None


@dataclass
class ExtendStat(Stat):
    code: str
    pos: object = None


@dataclass
class ExitStat(Stat):
    pos: object = None
