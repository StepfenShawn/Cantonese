from pprint import pprint
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import PythonLexer
from pygments.lexer import RegexLexer
from pygments.token import *


class CantoneseLexer(RegexLexer):
    tokens = {
        "root": [
            (r"\d+", Number),
            (r"[_\d\w]+|[\u4e00-\u9fa5]+", Name),
            (r"/\*.*?\*/", Comment),
            (r"#[^\n]*", Comment),
            (
                r"(?s)('(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")",
                String,
            ),
            (r"\s+", Whitespace),
            (r".", Generic),
        ]
    }
