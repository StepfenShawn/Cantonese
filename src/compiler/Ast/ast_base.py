from abc import ABC

# The base class for all AST nodes.
class AST(ABC):
    def __str__(self) -> str:
        return "BaseAST\n"