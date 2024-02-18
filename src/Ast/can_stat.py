from dataclasses import dataclass
from typing import List
from .can_exp import Exp

class Stat:
    pass

@dataclass
class FuncCallStat(Stat):
    func_name: Exp
    args: List[Exp]

@dataclass
class IfStat(Stat):
    if_exp: Exp
    if_block: List[Stat]
    elif_exps: List[Exp]
    elif_blocks: List[Stat]
    else_blocks: List[Stat]

@dataclass
class PrintStat(Stat):
    args: List[Exp]

@dataclass
class PassStat(Stat):
    pass

@dataclass
class AssignStat(Stat):
    var_list: List[Exp]
    exp_list: List[Exp]

@dataclass
class AssignBlockStat(Stat):
    var_list: List[List[Exp]]
    exp_list: List[List[Exp]]

@dataclass
class ForStat(Stat):
    var: Exp
    from_exp: Exp
    to_exp: Exp
    blocks: List[Exp]

@dataclass
class ForEachStat(Stat):
    id_list: List[Exp]
    exp_list: List[Exp]
    blocks: List[Stat]

@dataclass
class WhileStat(Stat):
    cond_exp: Exp
    blocks: List[Stat]

@dataclass
class ListInitStat(Stat):
    pass

@dataclass
class FunctionDefStat(Stat):
    name_exp: Exp
    args: List[Exp]
    blocks: List[Stat]
    args_type: List[Exp] = None
    ret_type: List[Exp] = None

@dataclass
class FuncTypeDefStat(Stat):
    func_name: Exp
    args_type: List[Exp]
    return_type: List[Exp]

@dataclass
class MethodDefStat(Stat):
    name_exp: Exp
    args: List[Exp]
    class_blocks: List[Stat]

@dataclass
class AttrDefStat(Stat):
    class_var_list: List[Exp]
    class_exp_list: List[Exp]

@dataclass
class ClassInitStat(Stat):
    class_var_list: List[Exp]

@dataclass
class ClassDefStat(Stat):
    class_name: Exp
    class_extend: List[Exp]
    class_blocks: List[Stat]

@dataclass
class MatchModeFuncDefStat(Stat):
    func_name: Exp
    args_list: List[Exp]
    block_list: List[Stat]

@dataclass
class ImportStat(Stat):
    idlist: List[Exp]

@dataclass
class RaiseStat(Stat):
    name_exp: Exp

@dataclass
class TryStat(Stat):
    try_blocks: List[Stat]
    except_exps: List[Exp]
    except_blocks: List[Stat]
    finally_blocks: List[Stat]

@dataclass
class GlobalStat(Stat):
    idlist: List[Exp]

@dataclass
class BreakStat(Stat):
    pass

@dataclass
class ContinueStat(Stat):
    pass

@dataclass
class TypeStat(Stat):
    exps: List[Exp]

@dataclass
class AssertStat(Stat):
    exps: Exp

@dataclass
class ReturnStat(Stat):
    exps: List[Exp]

@dataclass
class DelStat(Stat):
    exps: List[Exp]

@dataclass
class CmdStat(Stat):
    args: List[Exp]

@dataclass
class MethodCallStat(Stat):
    name_exp: Exp
    method: Exp
    args: List[Exp]

@dataclass
class CallStat(Stat):
    exp: Exp

@dataclass
class MatchStat(Stat):
    match_id: Exp
    match_val: Exp
    match_block_exp: Exp
    default_match_block: List[Stat]

@dataclass
class ExtendStat(Stat):
    code: str

@dataclass
class ModelNewStat(Stat):
    model: Exp
    dataset: Exp

@dataclass
class TurtleStat(Stat):
    exp_blocks: List[Exp]

@dataclass
class ExitStat(Stat):
    pass