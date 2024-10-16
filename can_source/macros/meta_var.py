from typing import Union, List
from can_source.can_ast import AST


class MetaVar:
    """
    表示一個match咗嘅元變量
    """

    def __init__(self, v: AST):
        # 確保係 `List`
        self.v = [v]

    @property
    def value(self) -> Union[AST | List[AST]]:
        if len(self.v) == 1:
            return self.v[0]
        else:
            return self.v

    def add_matched_value(self, v: AST) -> None:
        """
        將一個已經匹配嘅 AST 添加到 meta_var (`repetition`情況下調用)
        """
        self.v.append(v)

    def get_repetition_times(self) -> int:
        """
        返回喺repetition操作時重覆嘅次數
        """
        return len(self.v)
