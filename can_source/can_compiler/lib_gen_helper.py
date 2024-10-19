from copy import deepcopy
from typing import List
import sys, os

from can_source.can_ast import IdExp
from can_source.can_libs import fix_lib_name
from can_source.can_parser.exp.names_parser import DependTree


def get_trace(tree: DependTree):
    trace = []

    def visitor(_tree: DependTree, path: list):
        if _tree:
            path.append(_tree.v)
        if _tree.child:
            for child in _tree.child:
                visitor(child, deepcopy(path))
        else:
            trace.append(path)

    visitor(tree, [])
    return trace


def gen_import(lib_trace: List[IdExp], cls: "Codegen") -> str:  # type: ignore
    res = []
    for _ in lib_trace:
        name, need_load = fix_lib_name(cls.codegen_expr(_))
        if name == "python" or name == "py":
            continue
        if name == "std":
            name = "can_source.can_libs"
        if need_load:
            for pa in sys.path:
                if os.path.exists(f"{pa}/{name}.cantonese"):
                    with open(f"{pa}/{name}.cantonese", encoding="utf-8") as f:
                        os.environ[f"{pa}/{name}.cantonese_SOURCE"] = f.read()
        res.append(name)

    if len(res) == 1:
        return "import " + ".".join(res)
    else:
        return "from " + ".".join(res[:-1]) + " import " + res[-1] + "\n"
