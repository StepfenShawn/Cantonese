from abc import ABC, abstractmethod


class Macros(ABC):
    @abstractmethod
    def expand(self, tokentrees: "TokenTree") -> "MacroResult":  # type: ignore
        pass
