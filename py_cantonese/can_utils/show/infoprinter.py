from py_cantonese.can_utils.show.helper import format_color, whitespace


_ARROW = "-->"
_BAR = " | "


class ErrorPrinter:

    def __init__(self, info, pos, ctx, tips, _file, _len=1):
        self.info = info
        self.pos = pos
        self.ctx = ctx
        self.tips = tips
        self.len = _len
        self.file = _file

        self.print_offset = pos.offset
        for i in range(0, pos.offset):
            # because some chars may occurpy 2-bits when printing
            self.print_offset += len(self.ctx[i].encode("gbk")) - 1
        self.hightlight = "cantonese"

    def err_msg(self, arrow_char="^") -> None:
        strformat = f"""{self.info}
 {_ARROW} {self.file} \033[1;34m{self.pos.line}:{self.pos.offset}\033[0m
 {_BAR}
 {_BAR}{self.pos.line}: {format_color(self.ctx, 'cantonese')}
    {whitespace(self.print_offset + len(str(self.pos.line)) + 2)}{arrow_char*self.len} Tips:{self.tips}
:D 不如跟住我嘅tips繼續符碌下?"""
        return strformat

    def show_multline(self) -> None:
        strformat = f"""{self.info}
 {_ARROW} {self.file} \033[1;34m{self.pos.line}:{self.pos.offset}-{self.pos.end_line}:{self.pos.end_offset}\033[0m
 {_BAR}
"""
        for line in range(self.pos.line, self.pos.end_line + 1):
            strformat += (
                f"  -> {line}: {format_color(next(self.ctx), self.hightlight)}\n"
            )
        strformat += f"\nTips:{self.tips}\n"
        print(strformat)
        print(f":D 不如跟住我嘅tips繼續符碌下?")
