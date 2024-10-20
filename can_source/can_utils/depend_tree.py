from copy import deepcopy
from typing import List, Any
from pathlib import Path


class DependTree:
    """
        A Data Structure represent the library chains!  
        使下 A::{B, C::*} =>   
      A  
    /   \  
    B     C  
            \  
            *  
    """

    def __init__(self, v: Any):
        self.v = v
        self.child = None


def get_trace(tree: DependTree) -> List[List[Any]]:
    trace = []

    def visitor(_tree: DependTree, path: List) -> None:
        if _tree:
            path.append(_tree.v)
        if _tree.child:
            for child in _tree.child:
                visitor(child, deepcopy(path))
        else:
            trace.append(path)

    visitor(tree, [])
    return trace


def depend_to_url(chains: List[Any], std_alias: str) -> str:
    root = chains.pop(0).name
    link = Path("") if root != "std" else Path(std_alias)
    for other in chains:
        link /= other.name
    return str(link)
