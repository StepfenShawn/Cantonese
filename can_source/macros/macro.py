from abc import ABC, abstractmethod


class Macros(ABC):
    @abstractmethod
    def expand(self, tokentrees: "TokenTree"):  # type: ignore
        pass

    @abstractmethod
    def modify_body(self, body: "Any", meta_vars: "Any"): # type: ignore
        """
            Replace meta vars to ast in body.
        """
        pass