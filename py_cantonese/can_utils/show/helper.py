from py_cantonese.can_utils.show.highlight import (
    highlight,
    PythonLexer,
    CantoneseLexer,
    TerminalFormatter,
)
from pprint import pprint


def format_color(code, type="Python"):
    if type == "Python":
        return highlight(
            code=code, lexer=PythonLexer(), formatter=TerminalFormatter()
        ).strip("\n")
    else:
        return highlight(
            code=code, lexer=CantoneseLexer(), formatter=TerminalFormatter()
        ).strip("\n")


def whitespace(num) -> str:
    return " " * num


def show_more(data: object):
    MAX_LENGTH = 3
    if len(data) <= MAX_LENGTH:
        pprint(data)
    else:
        cursor = 0
        pprint(data[cursor : cursor + MAX_LENGTH])
        cursor += MAX_LENGTH
        while cursor < len(data):
            ready_show = data[cursor : cursor + MAX_LENGTH]
            cursor += MAX_LENGTH
            choice = input("--- More --- ? (y/n) ")
            if choice.lower() == "y":
                pprint(ready_show)
            else:
                return
