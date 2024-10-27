import re
from contextlib import contextmanager
import os
import zhconv
from difflib import get_close_matches

from can_source.can_lexer.can_keywords import *
from can_source.can_lexer.pos import Pos
from can_source.can_lexer.can_token import can_token
from can_source.can_error.compile_time import LexerException
from can_source.can_utils.show.infoprinter import ErrorPrinter


def getCtxByLine(path: str, line: int) -> str:
    """
    get context from file. (Lazy option)
    """
    if path == "【標準輸入】":
        return os.environ.get("REPL_CONTEXT", "Unknow-Context")
    with open(path, encoding="utf-8") as f:
        source = f.read()
    gen = (s for s in source.split("\n"))
    for _ in range(line):
        source = next(gen)
    return source


class lexer:
    """
    Get the Cantonese Token List
    """

    def __init__(self, file: str, code: str, keywords: tuple):
        self.file = file
        self.code = code
        self.keywords = keywords

        self.line = 1
        self.offset = 0

        self.re_number = r"^0[xX][0-9a-fA-F]*(\.[0-9a-fA-F]*)?([pP][+\-]?[0-9]+)?|^[0-9]*(\.[0-9]*)?([eE][+\-]?[0-9]+)?"
        self.re_id = r"^[_\d\w]+|^[\u4e00-\u9fa5]+"
        self.re_str = r"(?s)(^'(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(^\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")"
        self.re_expr = r"[|][\S\s]*?[|]"
        self.re_python_expr = r"#XD[\S\s]*?二五仔係我"
        self.re_comment = re.compile(r"/\*.*?\*/", re.S)
        self.re_single_comment = r"#[^\n]*"

    def getCurPos(self) -> Pos:
        return Pos(line=self.line, offset=self.offset, end_line=None, end_offset=None)

    @property
    def line_and_offset(self):
        return self.line, self.offset

    def next(self, n: int):
        sth = self.code[:n]
        self.line += sth.count("\n")
        if "\n" in sth:
            self.offset = len(sth.split("\n")[-1])
        else:
            self.offset += n
        self.code = self.code[n:]

    def check(self, s: str):
        return self.code.startswith(s)

    @staticmethod
    def is_white_space(c: str):
        return c in ("\t", "\n", "\v", "\f", "\r", " ")

    @staticmethod
    def is_new_line(c: str):
        return c in ("\r", "\n")

    @staticmethod
    def isChinese(word: str):
        for ch in word:
            if "\u4e00" <= ch <= "\u9fff":
                return True
        return False

    def skip_space_or_comment(self):
        while len(self.code) > 0:
            if self.check("/*"):
                _ = self.scan_comment()
            elif self.check("#") and not self.check("#XD"):
                _ = self.scan_single_comment()
            elif lexer.is_new_line(self.code[0]):
                self.next(1)
            elif self.check("：") or self.check("？"):
                self.next(1)
            elif self.check("??"):
                self.next(2)
            elif self.check("「") or self.check("」"):
                self.next(1)
            elif lexer.is_white_space(self.code[0]):
                self.next(1)
            else:
                break

    def scan(self, pattern: str):
        m = re.match(pattern, self.code)
        if m:
            token = m.group()
            self.next(len(token))
            return token

    def scan_identifier(self):
        return self.scan(self.re_id)

    def scan_expr(self):
        return self.scan(self.re_expr)

    def scan_python_expr(self):
        return self.scan(self.re_python_expr)

    def scan_number(self):
        return self.scan(self.re_number)

    def scan_comment(self):
        return self.scan(self.re_comment)

    def scan_single_comment(self):
        return self.scan(self.re_single_comment)

    def scan_short_string(self):
        m = re.match(self.re_str, self.code)
        if m:
            s = m.group()
            self.next(len(s))
            return s
        self.error("unfinished string")

    def error(self, args: str):
        ctx = getCtxByLine(self.file, self.getCurPos().line)
        get_tips = lambda s: ",".join(get_close_matches(s, syms))
        raise LexerException(
            ErrorPrinter(
                info=f"{args}\n 喺 lexer 中察覺到有D痴线",
                pos=self.getCurPos(),
                ctx=ctx,
                tips=f" 係咪`\033[5;33m{get_tips(ctx[self.getCurPos().offset])}\033[0m` ??",
                _file=self.file,
            ).err_msg()
        )

    @contextmanager
    def get_token(self):
        self.skip_space_or_comment()
        start_line, offset = self.line_and_offset
        tk = self.consume_token()
        end_line, end_offset = self.line_and_offset
        tk.pos = Pos(
            line=start_line, offset=offset, end_line=end_line, end_offset=end_offset
        )
        yield tk

    def consume_token(self) -> can_token:
        if len(self.code) == 0:
            return can_token(self.getCurPos(), TokenType.EOF, "EOF")

        c = self.code[0]

        if c == "&":
            if self.check("&&"):
                self.next(2)
                return can_token(None, TokenType.KEYWORD, "&&")
            else:
                self.next(1)
                return can_token(None, TokenType.OP_BAND, "&")

        if c == "|":
            self.next(1)
            return can_token(None, TokenType.BRACK, "|")

        if c == "?":
            self.next(1)
            return can_token(None, TokenType.MARK, "?")

        if c == ":":
            if self.check("::"):
                self.next(2)
                return can_token(None, TokenType.DCOLON, "::")
            else:
                self.next(1)
                return can_token(None, TokenType.COLON, ":")

        if c == "%":
            self.next(1)
            return can_token(None, TokenType.OP_MOD, "%")

        if c == "~":
            token = self.scan_python_expr()
            return can_token(None, TokenType.CALL_NATIVE_EXPR, token)

        if c == "-":
            if self.check("->"):
                self.next(2)
                return can_token(None, TokenType.KEYWORD, kw_dot)
            else:
                self.next(1)
                return can_token(None, TokenType.OP_MINUS, "-")

        if c == "=":
            if self.check("=>"):
                self.next(2)
                return can_token(None, TokenType.KEYWORD, kw_do)
            elif self.check("==>"):
                self.next(3)
                return can_token(None, TokenType.KEYWORD, "==>")
            elif self.check("=="):
                self.next(2)
                return can_token(None, TokenType.OP_EQ, "==")
            else:
                self.next(1)
                return can_token(None, TokenType.OP_ASSIGN, "=")

        if c == "$":
            if self.check("$$"):
                self.next(2)
                return can_token(None, TokenType.KEYWORD, "$$")
            self.next(1)
            return can_token(None, TokenType.KEYWORD, "$")

        if c == "<":
            if self.check("<*>"):
                self.next(3)
                return can_token(None, TokenType.KEYWORD, "<*>")

            elif self.check("<|>"):
                self.next(3)
                return can_token(None, TokenType.OP_BOR, "<|>")

            elif self.check("<->"):
                self.next(3)
                return can_token(None, TokenType.OP_CONCAT, "<->")

            elif self.check("<="):
                self.next(2)
                return can_token(None, TokenType.OP_LE, "<=")

            elif self.check("<<"):
                self.next(2)
                return can_token(None, TokenType.OP_SHL, "<<")

            else:
                self.next(1)
                return can_token(None, TokenType.OP_LT, "<")

        if c == ">":
            if self.check(">="):
                self.next(2)
                return can_token(None, TokenType.OP_GE, ">=")
            elif self.check(">>"):
                self.next(2)
                return can_token(None, TokenType.OP_SHR, ">>")
            else:
                self.next(1)
                return can_token(None, TokenType.OP_GT, ">")

        if c == "!":
            if self.check("!="):
                self.next(2)
                return can_token(None, TokenType.OP_NE, "!=")
            else:
                self.next(1)
                return can_token(None, TokenType.EXCL, "!")

        if c == "@":
            if self.check("@@"):
                self.next(2)
                return can_token(None, TokenType.KEYWORD, "@@")
            else:
                self.next(1)
                return can_token(None, TokenType.KEYWORD, "@")

        if c == "{":
            self.next(1)
            return can_token(None, TokenType.SEP_LCURLY, "{")

        if c == "}":
            self.next(1)
            return can_token(None, TokenType.SEP_RCURLY, "}")

        if c == "(":
            self.next(1)
            return can_token(None, TokenType.SEP_LPAREN, "(")

        if c == ")":
            self.next(1)
            return can_token(None, TokenType.SEP_RPAREN, ")")

        if c == "[":
            self.next(1)
            return can_token(None, TokenType.SEP_LBRACK, "[")

        if c == "]":
            self.next(1)
            return can_token(None, TokenType.SEP_RBRACK, "]")

        if c == ".":
            self.next(1)
            return can_token(None, TokenType.SEP_DOT, c)

        if lexer.isChinese(c) or c == "_" or c.isalpha():
            token = self.scan_identifier()
            token = zhconv.convert(token, "zh-hk").replace("僕", "仆")
            if token in self.keywords:
                return can_token(None, TokenType.KEYWORD, token)
            return can_token(None, TokenType.IDENTIFIER, token)

        if c in ("'", '"'):
            return can_token(None, TokenType.STRING, self.scan_short_string())

        if c.isdigit():
            token = self.scan_number()
            return can_token(None, TokenType.NUM, token)

        if c == "+":
            self.next(1)
            return can_token(None, TokenType.OP_ADD, c)

        if c == "-":
            self.next(1)
            return can_token(None, TokenType.OP_MINUS, c)

        if c == "*":
            if self.check("**"):
                self.next(2)
                return can_token(None, TokenType.OP_POW, c)
            else:
                self.next(1)
                return can_token(None, TokenType.OP_MUL, c)

        if c == "/":
            if self.check("//"):
                self.next(2)
                return can_token(None, TokenType.OP_IDIV, "//")
            else:
                self.next(1)
                return can_token(None, TokenType.OP_DIV, c)

        if c == "&":
            self.next(1)
            return can_token(None, TokenType.OP_BAND, c)

        if c == "^":
            self.next(1)
            return can_token(None, TokenType.OP_WAVE, c)

        if c == ",":
            self.next(1)
            return can_token(None, TokenType.SEP_COMMA, ",")

        if c == "#":
            if self.check("#XD"):
                token = self.scan_python_expr()
                return can_token(None, TokenType.CALL_NATIVE_EXPR, token)

        self.error(f"\033[0;31m濑嘢!!!\033[0m:睇唔明嘅Token: `{c}`")
