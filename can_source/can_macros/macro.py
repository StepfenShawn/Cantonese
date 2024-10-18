from abc import ABC, abstractmethod
from typing import Any, Dict


class Macros(ABC):
    @abstractmethod
    def expand(self, tokentrees: Any):
        pass

    @abstractmethod
    def ensure_repetition(self, rep: Any, meta_vars: Dict[str, Any]) -> bool:
        """
        確保重覆操作是否能展開
        """
        pass

    @abstractmethod
    def yield_repetition(self, rep: Any, meta_vars: Dict[str, Any]) -> Any:
        """
        展開重覆操作
        """
        pass

    @abstractmethod
    def modify_body(self, body: Any, meta_vars: Any):
        """
        Replace meta vars to ast in body.
        負責展開宏.
        """
        pass
