import re
from keywords import *

"""
    Get the Cantonese Token List
"""

class lexer(object):
    def __init__(self, code, keywords):
        self.code = code
        self.keywords = keywords
        self.line = 1
        self.re_new_line = re.compile(r"\r\n|\n\r|\n|\r")
        self.re_number = r"^0[xX][0-9a-fA-F]*(\.[0-9a-fA-F]*)?([pP][+\-]?[0-9]+)?|^[0-9]*(\.[0-9]*)?([eE][+\-]?[0-9]+)?"
        self.re_id = r"^[_\d\w]+|^[\u4e00-\u9fa5]+"
        self.re_str = r"(?s)(^'(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(^\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")"
        self.re_expr = r"[|][\S\s]*?[|]"
        self.re_python_expr = r"[~][\S\s]*?[#]"
        self.re_callfunc = r"[&](.*?)[)]"
        self.op = r'(?P<op>(相加){1}|(加){1}|(减){1}|(乘){1}|(整除){1}|(除){1}|(余){1}|(异或){1}|(取反){1}|(左移){1}|(右移){1}'\
        r'(与){1}(或者){1}|(或){1}|(系){1})|(同埋){1}|(自己嘅){1}|(比唔上){1}|(喺){1}'
        self.op_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), self.op[5 : ])
        self.op_gen_code = ["矩阵.matrix_addition", "+", "-", "*", "//", "/", "%", "^", "~", "<<", ">>",
            "&", "or", "|", "==", "and", "self.", '<', 'in']
        self.build_in_funcs = r'(?P<build_in_funcs>(瞓){1}|(加啲){1}|(摞走){1}|(嘅长度){1}|(阵先){1}|' \
                     r'(畀你){1}|(散水){1})'
        self.bif_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), self.build_in_funcs[19 :])
        self.bif_gen_code = ["sleep", "append", "remove", ".__len__()", "2", "input", "clear"]
    
    def make_rep(self, list1 : list, list2 : list) -> list:
        assert len(list1) == len(list2)
        ret = []
        for i in range(len(list1)):
            ret.append([list1[i], list2[i]])
        return ret

    def trans(self, code : str, rep : str) -> str:
        p = re.match(r'\|(.*)同(.*)有几衬\|', code, re.M|re.I)
        if p:
            code = " corr(" + p.group(1) +", " + p.group(2) + ") "
        for r in rep:
            code = code.replace(r[0], r[1])
        return code

    def next(self, n):
        self.code = self.code[n:]

    def check(self, s):
        return self.code.startswith(s)

    @staticmethod
    def is_white_space(c):
        return c in ('\t', '\n', '\v', '\f', '\r', ' ')

    @staticmethod
    def is_new_line(c):
        return c in ('\r', '\n')

    @staticmethod
    def isChinese(word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False


    def skip_space(self):
        while len(self.code) > 0:
            if self.check('\r\n') or self.check('\n\r'):
                self.next(2)
                self.line += 1
            elif self.is_new_line(self.code[0]):
                self.next(1)
                self.line += 1
            elif self.check('?') or self.check(':') or self.check('：') or self.check('？'):
                self.next(1)
            elif self.check('「') or self.check('」'):
                self.next(1)
            elif self.is_white_space(self.code[0]):
                self.next(1)
            else:
                break

    def scan(self, pattern):
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

    def scan_callfunc(self):
        return self.scan(self.re_callfunc)

    def scan_short_string(self):
        m = re.match(self.re_str, self.code)
        if m:
            s = m.group()
            self.next(len(s))
            return s
        self.error('unfinished string')
        return ''

    def error(self, f, *args):
        err = f.format(*args)
        err = '{0}: {1}'.format(self.line, err)
        raise Exception(err)

    def get_token(self):
        self.skip_space()
        if len(self.code) == 0:
            return [self.line, [TokenType.EOF, 'EOF']]

        c = self.code[0]
        
        if c == '&':
            if self.check('&&'):
                self.next(2)
                return [self.line, [TokenType.KEYWORD, '&&']]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_BAND, '&']]

        if c == '|':
            if self.check('|>'):
                self.next(2)
                return [self.line, [TokenType.SEPICFIC_ID_END, '|>']]
            else:
                self.next(1)
                return [self.line, [TokenType.KEYWORD, '|']]

        if c == '%':
            if self.check('%%'):
                self.next(2)
                return [self.line, [TokenType.KEYWORD, kw_func_end]]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_MOD, '%']]

        if c == '~':
            token = self.scan_python_expr()
            return [self.line, [TokenType.EXTEND_EXPR, token]]

        if c == '-':
            if self.check('->'):
                self.next(2)
                return [self.line, [TokenType.KEYWORD, kw_do]]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_MINUS, '-']]

        if c == '=':
            if self.check('=>'):
                self.next(2)
                return [self.line, [TokenType.KEYWORD, kw_do]]
            elif self.check('==>'):
                self.next(3)
                return [self.line, [TokenType.KEYWORD, '==>']]
            elif self.check('=='):
                self.next(2)
                return [self.line, [TokenType.OP_EQ, '==']]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_ASSIGN, '=']]
            
        if c == '$':
            if self.check('$$'):
                self.next(2)
                return [self.line, [TokenType.KEYWORD, '$$']]
            self.next(1)
            return [self.line, [TokenType.KEYWORD, '$']]

        if c == '<':
            if self.check('<*>'):
                self.next(3)
                return [self.line, [TokenType.KEYWORD, '<*>']]

            elif self.check('<$>'):
                self.next(3)
                return [self.line, [TokenType.KEYWORD, '<$>']]

            elif self.check('<|>'):
                self.next(3)
                return [self.line, [TokenType.OP_BOR, '<|>']]

            elif self.check('<->'):
                self.next(3)
                return [self.line, [TokenType.OP_CONCAT, '<->']]
            
            elif self.check('<='):
                self.next(2)
                return [self.line, [TokenType.OP_LE, '<=']]
            
            elif self.check('<<'):
                self.next(2)
                return [self.line, [TokenType.OP_SHL, '<<']]

            elif self.check('<|'):
                self.next(2)
                return [self.line, [TokenType.SEPCIFIC_ID_BEG, '<|']]

            else:
                self.next(1)
                return [self.line, [TokenType.OP_LT, '<']]
        
        if c == '>':
            if self.check('>='):
                self.next(2)
                return [self.line, [TokenType.OP_GE, '>=']]
            elif self.check('>>'):
                self.next(2)
                return [self.line, [TokenType.OP_SHR, '>>']]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_GT, '>']]

        if c == '!':
            if self.check('!='):
                self.next(2)
                return [self.line, [TokenType.OP_NE, '!=']]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_NOT, '!']]

        if c == '@':
            if self.check('@@@'):
                self.next(3)
                return [self.line, [TokenType.KEYWORD, '@@@']]
            elif self.check('@@'):
                self.next(2)
                return [self.line, [TokenType.KEYWORD, '@@']]
            else:
                self.next(1)
                return [self.line, [TokenType.KEYWORD, '@']]
        
        if c == '{':
            self.next(1)
            return [self.line, [TokenType.SEP_LCURLY, '{']]
        
        if c == '}':
            self.next(1)
            return [self.line, [TokenType.SEP_RCURLY, '}']]

        if c == '(':
            self.next(1)
            return [self.line, [TokenType.SEP_LPAREN, '(']]

        if c == ')':
            self.next(1)
            return [self.line, [TokenType.SEP_RPAREN, ')']]

        if c == '[':
            self.next(1)
            return [self.line, [TokenType.SEP_LBRACK, '[']]

        if c == ']':
            self.next(1)
            return [self.line, [TokenType.SEP_RBRACK, ']']]

        if c == '.':
            self.next(1)
            return [self.line, [TokenType.SEP_DOT, c]]

        if self.isChinese(c) or c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return [self.line, [TokenType.KEYWORD, token]]
            return [self.line, [TokenType.IDENTIFIER, token]]
        
        if c in ('\'', '"'):
            return [self.line, [TokenType.STRING, self.scan_short_string()]]
        
        if c.isdigit():
            token = self.scan_number()
            return [self.line, [TokenType.NUM, token]]

        if c == '+':
            self.next(1)
            return [self.line, [TokenType.OP_ADD, c]]

        if c == '-':
            self.next(1)
            return [self.line, [TokenType.OP_MINUS, c]]

        if c == '*':
            if self.check('**'):
                self.next(2)
                return [self.line, [TokenType.OP_POW, c]]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_MUL, c]]

        if c == '/':
            if self.check('//'):
                self.next(2)
                return [self.line, [TokenType.OP_IDIV, '//']]
            else:
                self.next(1)
                return [self.line, [TokenType.OP_DIV, c]]

        if c == '&':
            self.next(1)
            return [self.line, [TokenType.OP_BAND, c]]

        if c == '^':
            self.next(1)
            return [self.line, [TokenType.OP_WAVE, c]]

        if c == ',':
            self.next(1)
            return [self.line, [TokenType.SEP_COMMA, ',']]

        if c == '#':
            if self.check('##'):
                self.next(2)
                return [self.line, [TokenType.KEYWORD, '##']]

        self.error("睇唔明嘅Token: " + c)

    def escape(self, s):
        ret = ''
        while len(s) > 0:
            if s[0] != '\\':
                ret += s[0]
                s = s[1:]
                continue

            if len(s) == 1:
                self.error('unfinished string')

            if s[1] == 'a':
                ret += '\a'
                s = s[2:]
                continue
            elif s[1] == 'b':
                ret += '\b'
                s = s[2:]
                continue
            elif s[1] == 'f':
                ret += '\f'
                s = s[2:]
                continue
            elif s[1] == 'n' or s[1] == '\n':
                ret += '\n'
                s = s[2:]
                continue
            elif s[1] == 'r':
                ret += '\r'
                s = s[2:]
                continue
            elif s[1] == 't':
                ret += '\t'
                s = s[2:]
                continue
            elif s[1] == 'v':
                ret += '\v'
                s = s[2:]
                continue
            elif s[1] == '"':
                ret += '"'
                s = s[2:]
                continue
            elif s[1] == '\'':
                ret += '\''
                s = s[2:]
                continue
            elif s[1] == '\\':
                ret += '\\'
                s = s[2:]
                continue

def cantonese_token(code : str, keywords : str) -> list:
    lex = lexer(code, keywords)
    tokens = []
    while True:
        token = lex.get_token()
        tokens.append(token)
        if token[1] == [TokenType.EOF, 'EOF']:
            break
    return tokens