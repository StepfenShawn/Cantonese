from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer
from pygments.lexer import RegexLexer
from pygments.token import *
from pprint import pprint

class CantoneseLexer(RegexLexer):
    tokens = {
        'root': [
            (r'\d+', Number),
            (r'[_\d\w]+|[\u4e00-\u9fa5]+', Name),
            (r'/\*.*?\*/', Comment),
            (r"(?s)('(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")", String),
            (r'\s+', Whitespace),
            (r".", Generic)
        ]
    }

def format_color(code, type="Python"):
    if type == "Python":
        return highlight(code=code, lexer=PythonLexer(), formatter=TerminalFormatter()).strip('\n')
    else:
        return highlight(code=code, lexer=CantoneseLexer(), formatter=TerminalFormatter()).strip('\n')

_ARROW = '-->'
_BAR = ' | '

class ErrorPrinter:

    def __init__(self, info, pos, ctx, tips, _file, _len = 1):
        self.info = info
        self.pos = pos
        self.ctx = ctx
        self.tips = tips
        self.len = _len
        self.file = _file

        self.print_offset = pos.offset
        for i in range(0, pos.offset):
            # because some chars may occurpy 2-bits when printing
            self.print_offset += (len(self.ctx[i].encode('gbk')) - 1)
        self.hightlight = "cantonese"

    def whitespace(self, num) -> str:
        return ' ' * num

    def show(self, arrow_char='^') -> None:
        strformat = (
f"""{self.info}
 {_ARROW} {self.file} \033[1;34m{self.pos.line}:{self.pos.offset}\033[0m
 {_BAR}
 {_BAR}{self.pos.line}: {format_color(self.ctx, self.hightlight)}
    {self.whitespace(self.print_offset + len(str(self.pos.line)) + 2)}{arrow_char*self.len} Tips:{self.tips}
"""
)
        print(strformat)
        print(f":D 不如跟住我嘅tips繼續符碌下?")

def show_more(data: object):
    MAX_LENGTH = 3
    if len(data) <= MAX_LENGTH:
        pprint(data)
    else:
        cursor = 0
        pprint(data[cursor : cursor + MAX_LENGTH])
        cursor += MAX_LENGTH
        while cursor + MAX_LENGTH < len(data):
            ready_show = data[cursor : cursor + MAX_LENGTH]
            cursor += MAX_LENGTH
            choice = input("--- More --- ? (y/n) ")
            if choice.lower() == 'y':
                pprint(ready_show)
            else:
                return