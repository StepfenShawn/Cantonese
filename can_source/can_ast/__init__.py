# This file exports all AST nodes to parser
from typing import Union
from .can_exp import *
from .can_stat import *
from dataclasses import dataclass

AST = Union[Stat, Exp]

@dataclass
class MacroResult:
    results: AST