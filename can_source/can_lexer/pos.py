class Pos:
    """
        Token 喺 source file 嘅位置
    """
    __slot__ = ("line", "offset", "end_line", "end_offset")

    def __init__(self, line: int, offset: int, end_line: int, end_offset: int):
        self.line = line
        self.offset = offset
        self.end_line = end_line
        self.end_offset = end_offset
