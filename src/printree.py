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


class AsciiPrinter(TreePrinter):
    """A printer that uses ASCII characters only."""
    ROOT = '.'
    EDGE = '|   '
    BRANCH_NEXT = '|-- '
    BRANCH_LAST = '`-- '
    ARROW = '->'


def ptree(obj, depth: int = None, annotated: bool = False, sprout_str=': ') -> None:
    TreePrinter(depth=depth, annotated=annotated).ptree(obj, sprout_str)

def _newline_repr(obj_repr, prefix) -> str:
    counter = count()
    newline = lambda x: next(counter) != 0
    return textwrap.indent(obj_repr, prefix, newline)


def _itree(obj, formatter, subscription, prefix="", last=False, level=0, depth=0, sprout_str=': '):
    
    if isinstance(subscription, int) and sprout_str != ': ':
        subscription = ""

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