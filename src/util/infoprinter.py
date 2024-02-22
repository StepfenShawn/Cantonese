from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer
from pygments.lexer import RegexLexer
from pygments.token import *

class CantoneseLexer(RegexLexer):
    tokens = {
        'root': [
            (r'\d+', Number),
            (r'[_\d\w]+|[\u4e00-\u9fa5]+', Name),
            (r'/\*.*?\*/', Comment),
            (r"(?s)('(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")", String),
            (r'\s+', Whitespace),
            (r".", Generic)
        ]
    }

def format_color(code, type="Python"):
    if type == "Python":
        return highlight(code=code, lexer=PythonLexer(), formatter=TerminalFormatter()).strip('\n')
    else:
        return highlight(code=code, lexer=CantoneseLexer(), formatter=TerminalFormatter()).strip('\n')

_ARROW = '-->'
_BAR = ' | '

class ErrorPrinter:

    def __init__(self, info, pos, ctx, tips, _file, _len = 1):
        self.info = info
        self.pos = pos
        self.ctx = ctx
        self.tips = tips
        self.len = _len
        self.file = _file

        self.print_offset = pos.offset
        for i in range(0, pos.offset):
            # because some chars may occurpy 2-bits when printing
            self.print_offset += (len(self.ctx[i].encode('gbk')) - 1)
        self.hightlight = "cantonese"

    def whitespace(self, num) -> str:
        return ' ' * num

    def show(self, arrow_char='^') -> None:
        strformat = (
f"""{self.info}
 {_ARROW} {self.file} \033[1;34m{self.pos.line}:{self.pos.offset}\033[0m
 {_BAR}{format_color(self.ctx, self.hightlight)}
    {self.whitespace(self.print_offset)}{arrow_char*self.len} Tips:{self.tips}
"""
)
        print(strformat)
        print(f":D 不如跟住我嘅tips繼續符碌下?")

"""
    The printree library
    refer to https://github.com/chrizzFTD/printree (MIT License)
"""

import textwrap
import contextvars
from pprint import isrecursive
from itertools import count
from collections import abc

_recursive_ids = contextvars.ContextVar('recursive')


class TreePrinter:
    """Default printer for printree.

    Uses unicode characters.
    """
    ROOT = '┐'
    EDGE = '│   '
    BRANCH_NEXT = '├── '
    BRANCH_LAST = '└── '
    ARROW = '→'

    def __init__(self, depth: int = None, annotated: bool = False):
        """
        :param depth: If the data structure being printed is too deep, the next contained level is replaced by [...]. By default, there is no constraint on the depth of the objects being formatted.
        :param annotated: Whether or not to include annotations for branches, like the object type and amount of children.
        """
        self.level = 0
        self.depth = depth
        self.annotated = bool(annotated)

    @property
    def depth(self) -> int:
        """Maximum depth to traverse while creating the tree representation."""
        return self._depth

    @depth.setter
    def depth(self, value):
        if not (isinstance(value, int) or value is None):
            raise TypeError(f"Expected depth to be an int or None. Got '{type(value).__name__}' instead.")
        if isinstance(value, int) and value < 0:
            raise ValueError(f"Depth must be a positive integer or zero. Got '{value}' instead.")
        self._depth = value if value else float("inf")

    def ptree(self, obj, sprout_str=': '):
        self.level = 0
        def f():
            _recursive_ids.set(set())
            for i in _itree(obj, self, subscription=self.ROOT, depth=self.depth, sprout_str=sprout_str):
                print(i)
        contextvars.copy_context().run(f)

def ptree(obj, depth: int = None, annotated: bool = False, sprout_str=': ') -> None:
    TreePrinter(depth=depth, annotated=annotated).ptree(obj, sprout_str)

def _newline_repr(obj_repr, prefix) -> str:
    counter = count()
    newline = lambda x: next(counter) != 0
    return textwrap.indent(obj_repr, prefix, newline)

def _itree(obj, formatter, subscription, prefix="", last=False, level=0, depth=0, sprout_str=': '):
    formatter.level = level
    sprout = level > 0
    children = []
    objid = id(obj)
    recursive = isrecursive(obj)
    recursive_ids = _recursive_ids.get()
    sprout_repr = sprout_str if sprout else ''
    newlevel = '    ' if last else formatter.EDGE
    newline_prefix = f"{prefix}{newlevel}"
    newprefix = f"{prefix}{formatter.BRANCH_LAST if last else formatter.BRANCH_NEXT}" if sprout else ""
    subscription_repr = f'{newprefix}{_newline_repr(f"{subscription}", newline_prefix)}'
    if recursive and objid in recursive_ids:
        item_repr = f"{sprout_repr}<Recursion on {type(obj).__name__} with id={objid}>"
    elif isinstance(obj, (str, bytes)):
        # Indent new lines with a prefix so that a string like "new\nline" adjusts to:
        #      ...
        #      |- 42: new
        #      |      line
        #      ...
        # for this, calculate how many characters each new line should have for padding
        prefix_len = len(prefix)  # how much we have to copy before subscription string
        last_line = subscription_repr.expandtabs().splitlines()[-1]
        newline_padding = len(last_line[prefix_len:]) + prefix_len + 2  # last 2 are ": "
        item_repr = _newline_repr(f"{sprout_repr}{obj}", f"{last_line[:prefix_len] + newlevel:<{newline_padding}}")
    elif isinstance(obj, abc.Iterable):
        # for other iterable objects, enumerate to track subscription and child count
        ismap = isinstance(obj, abc.Mapping)
        enumerateable = obj.items() if ismap else obj
        accessor = (lambda i, v: (i, *v)) if ismap else lambda i, v: (i, i, v)
        enumerated = enumerate(enumerateable)
        children.extend(accessor(*enum) for enum in enumerated)
        contents = f'items={len(children)}' if children else "empty"
        item_repr = f' {formatter.ARROW} {type(obj).__name__}[{contents}]' if formatter.annotated else ''
        if children and level == depth:
            item_repr = f"{item_repr} [...]"
            children.clear()  # avoid deeper traversal
    else:
        item_repr = f"{sprout_repr}{obj}"
    if recursive:
        recursive_ids.add(objid)

    yield f"{subscription_repr}{item_repr}"
    child_count = len(children)
    prefix += newlevel if sprout else ""  # only add level prefix starting at level 1
    for index, key, value in children:
        yield from _itree(value, formatter, key, prefix, index == (child_count - 1), level + 1, depth, sprout_str)