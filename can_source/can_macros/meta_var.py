from typing import Union, List
from can_source.can_lexer.can_token import can_token


class MetaVar:
    """
    表示match咗嘅元變量
    """

    def __init__(self, v: can_token):
        # 確保係 `List`
        self.v = [v]
        self._yiled = (x for x in self.v)

    @property
    def value(self) -> Union[can_token, List[can_token]]:
        if len(self.v) == 0:
            raise Exception("No value")
        try:
            return next(self._yiled)
        except StopIteration:
            self.reyield()
            return next(self._yiled)

    def reyield(self) -> None:
        self._yiled = (x for x in self.v)

    def add_matched_value(self, v: can_token) -> None:
        """
        將一個已經匹配嘅 Token 添加到 meta_var (`repetition`情況下調用)
        """
        self.v.append(v)
        self._yiled = (x for x in self.v)

    def get_repetition_times(self) -> int:
        """
        返回喺repetition操作時重覆嘅次數
        """
        return len(self.v)
