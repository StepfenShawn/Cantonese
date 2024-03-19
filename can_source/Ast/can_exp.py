from dataclasses import dataclass
from typing import List

class Exp:
    pass

# null
@dataclass
class NullExp(Exp):
    pass

# True
@dataclass
class TrueExp(Exp):
    pass

# False
@dataclass
class FalseExp(Exp):
    pass

# <*>
@dataclass
class VarArgExp(Exp):
    pass

# Number
@dataclass
class NumeralExp(Exp):
    val: int

# <->
@dataclass
class ConcatExp(Exp):
    exps: list

# Literal String
@dataclass
class StringExp(Exp):
    s: str

# List Expr
@dataclass
class ListExp(Exp):
    elem_exps: List[Exp]

# Map Expr
@dataclass
class MapExp(Exp):
    elem_exps: List[Exp]

# unop exp
@dataclass
class UnopExp(Exp):
    op: str
    exp: Exp

# exp1 op exp2
@dataclass
class BinopExp(Exp):
    op: str
    exp1: Exp
    exp2: Exp

# exp1 = exp2
@dataclass
class AssignExp(Exp):
    exp1: Exp
    exp2: Exp

# exp1: tyid
@dataclass
class AnnotationExp(Exp):
    exp: Exp
    tyid: Exp

# exp1 ==> exp2
@dataclass
class MappingExp(Exp):
    exp1: Exp
    exp2: Exp

@dataclass
class IdExp(Exp):
    name: str

# '(' exp ')'
@dataclass
class ParensExp(Exp):
    exp: Exp

@dataclass
class ObjectAccessExp(Exp):
    prefix_exp: Exp
    key_exp: Exp

@dataclass
class ListAccessExp(Exp):
    prefix_exp: Exp
    key_exp: Exp

@dataclass
class AttrAccessExp(Exp):
    key_exp: Exp

@dataclass
class FuncCallExp(Exp):
    prefix_exp: Exp
    args: List[Exp]

@dataclass
class LambdaExp(Exp):
    id_list: List[Exp]
    blocks: List[Exp]

@dataclass
class ClassSelfExp(Exp):
    exp: Exp

@dataclass
class IfElseExp(Exp):
    if_cond_exp: Exp
    if_exp: Exp
    else_exp: Exp