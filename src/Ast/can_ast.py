# This file exports all AST nodes to parser
from typing import Union
from .can_exp import *
from .can_stat import *

AST = Union[Stat, Exp] 