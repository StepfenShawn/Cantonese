from dataclasses import dataclass
from typing import List
from .can_exp import Exp

class Stat:
    pass

@dataclass
class FuncCallStat(Stat):
    func_name: Exp
    args: List[Exp]
    pos: object

@dataclass
class IfStat(Stat):
    if_exp: Exp
    if_block: List[Stat]
    elif_exps: List[Exp]
    elif_blocks: List[Stat]
    else_blocks: List[Stat]
    pos: object
    
@dataclass
class PrintStat(Stat):
    args: List[Exp]
    pos: object

@dataclass
class PassStat(Stat):
    pos: object

@dataclass
class AssignStat(Stat):
    var_list: List[Exp]
    exp_list: List[Exp]
    pos: object

@dataclass
class AssignBlockStat(Stat):
    var_list: List[List[Exp]]
    exp_list: List[List[Exp]]
    pos: object

@dataclass
class ForStat(Stat):
    var: Exp
    from_exp: Exp
    to_exp: Exp
    blocks: List[Exp]
    pos: object

@dataclass
class ForEachStat(Stat):
    id_list: List[Exp]
    exp_list: List[Exp]
    blocks: List[Stat]
    pos: object

@dataclass
class WhileStat(Stat):
    cond_exp: Exp
    blocks: List[Stat]
    pos: object

@dataclass
class ListInitStat(Stat):
    pos: object

@dataclass
class FunctionDefStat(Stat):
    name_exp: Exp
    args: List[Exp]
    blocks: List[Stat]
    pos: object

@dataclass
class FuncTypeDefStat(Stat):
    func_name: Exp
    args_type: List[Exp]
    return_type: List[Exp]
    pos: object

@dataclass
class MethodDefStat(Stat):
    name_exp: Exp
    args: List[Exp]
    class_blocks: List[Stat]
    pos: object

@dataclass
class AttrDefStat(Stat):
    class_var_list: List[Exp]
    class_exp_list: List[Exp]
    pos: object

@dataclass
class ClassInitStat(Stat):
    class_var_list: List[Exp]
    pos: object

@dataclass
class ClassDefStat(Stat):
    class_name: Exp
    class_extend: List[Exp]
    class_blocks: List[Stat]
    pos: object

@dataclass
class ImportStat(Stat):
    idlist: List[Exp]
    pos: object

@dataclass
class RaiseStat(Stat):
    name_exp: Exp
    pos: object

@dataclass
class TryStat(Stat):
    try_blocks: List[Stat]
    except_exps: List[Exp]
    except_blocks: List[Stat]
    finally_blocks: List[Stat]
    pos: object

@dataclass
class GlobalStat(Stat):
    idlist: List[Exp]
    pos: object

@dataclass
class BreakStat(Stat):
    pos: object

@dataclass
class ContinueStat(Stat):
    pos: object

@dataclass
class TypeStat(Stat):
    exps: List[Exp]
    pos: object

@dataclass
class AssertStat(Stat):
    exps: Exp
    pos: object

@dataclass
class ReturnStat(Stat):
    exps: List[Exp]
    pos: object

@dataclass
class DelStat(Stat):
    exps: List[Exp]
    pos: object

@dataclass
class CmdStat(Stat):
    args: List[Exp]
    pos: object

@dataclass
class MethodCallStat(Stat):
    name_exp: Exp
    method: Exp
    args: List[Exp]
    pos: object


@dataclass
class CallStat(Stat):
    exp: Exp
    pos: object

@dataclass
class MatchStat(Stat):
    match_id: Exp
    match_val: Exp
    match_block_exp: Exp
    default_match_block: List[Stat]
    pos: object

@dataclass
class ExtendStat(Stat):
    code: str
    pos: object

@dataclass
class ModelNewStat(Stat):
    model: Exp
    dataset: Exp
    pos: object

@dataclass
class TurtleStat(Stat):
    exp_blocks: List[Exp]
    pos: object

@dataclass
class ExitStat(Stat):
    pos: object