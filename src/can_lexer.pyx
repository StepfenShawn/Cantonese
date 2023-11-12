import re
from can_keywords cimport *

cdef class can_token:
    def __init__(self, int lineno, TokenType typ, str value):
        self.lineno = lineno
        self.typ = typ
        self.value = value

"""
    Get the Cantonese Token List
"""
cdef class lexer:
    def __init__(self, code: str, keywords: tuple):
        self.code = code
        self.keywords = keywords
        self.line = 1
        self.re_number = r"^0[xX][0-9a-fA-F]*(\.[0-9a-fA-F]*)?([pP][+\-]?[0-9]+)?|^[0-9]*(\.[0-9]*)?([eE][+\-]?[0-9]+)?"
        self.re_id = r"^[_\d\w]+|^[\u4e00-\u9fa5]+"
        self.re_str = r"(?s)(^'(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(^\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")"
        self.re_expr = r"[|][\S\s]*?[|]"
        self.re_python_expr = r"[~][\S\s]*?[#]"
        self.re_callfunc = r"[&](.*?)[)]"

    cdef next(self, int n):
        self.code = self.code[n:]

    cdef check(self, str s):
        return self.code.startswith(s)

    @staticmethod
    cdef bint is_white_space(str c):
        return c in ('\t', '\n', '\v', '\f', '\r', ' ')

    @staticmethod
    cdef bint is_new_line(str c):
        return c in ('\r', '\n')

    @staticmethod
    cdef bint isChinese(str word):
        for ch in word:
            if '\u4e00' <= ch <= '\u9fff':
                return True
        return False

    cdef skip_space(self):
        while len(self.code) > 0:
            if self.check('\r\n') or self.check('\n\r'):
                self.next(2)
                self.line += 1
            elif lexer.is_new_line(self.code[0]):
                self.next(1)
                self.line += 1
            elif self.check('?') or self.check(':') or self.check('：') or self.check('？'):
                self.next(1)
            elif self.check('「') or self.check('」'):
                self.next(1)
            elif lexer.is_white_space(self.code[0]):
                self.next(1)
            else:
                break

    cdef str scan(self, str pattern):
        cdef object m = re.match(pattern, self.code)
        if m:
            token = m.group()
            self.next(len(token))
            return token
    
    cdef str scan_identifier(self):
        return self.scan(self.re_id)

    cdef str scan_expr(self):
        return self.scan(self.re_expr)

    cdef str scan_python_expr(self):
        return self.scan(self.re_python_expr)

    cdef str scan_number(self):
        return self.scan(self.re_number)

    cdef str scan_callfunc(self):
        return self.scan(self.re_callfunc)

    cdef str scan_short_string(self):
        m = re.match(self.re_str, self.code)
        if m:
            s = m.group()
            self.next(len(s))
            return s
        self.error('unfinished string')

    cdef error(self, str args):
        cdef str err = '{0}: {1}'.format(self.line, args)
        raise Exception(err)

    cdef can_token get_token(self):
        self.skip_space()
        if len(self.code) == 0:
            return can_token(self.line, TokenType.EOF, 'EOF')

        c = self.code[0]
        
        if c == '&':
            if self.check('&&'):
                self.next(2)
                return can_token(self.line, TokenType.KEYWORD, '&&')
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_BAND, '&')

        if c == '|':
            if self.check('|>'):
                self.next(2)
                return can_token(self.line, TokenType.SEPICFIC_ID_END, '|>')
            else:
                self.next(1)
                return can_token(self.line, TokenType.KEYWORD, '|')

        if c == '%':
            if self.check('%%'):
                self.next(2)
                return can_token(self.line, TokenType.KEYWORD, kw_func_end)
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_MOD, '%')

        if c == '~':
            token = self.scan_python_expr()
            return can_token(self.line, TokenType.EXTEND_EXPR, token)

        if c == '-':
            if self.check('->'):
                self.next(2)
                return can_token(self.line, TokenType.KEYWORD, kw_do)
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_MINUS, '-')

        if c == '=':
            if self.check('=>'):
                self.next(2)
                return can_token(self.line, TokenType.KEYWORD, kw_do)
            elif self.check('==>'):
                self.next(3)
                return can_token(self.line, TokenType.KEYWORD, '==>')
            elif self.check('=='):
                self.next(2)
                return can_token(self.line, TokenType.OP_EQ, '==')
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_ASSIGN, '=')
            
        if c == '$':
            if self.check('$$'):
                self.next(2)
                return can_token(self.line, TokenType.KEYWORD, '$$')
            self.next(1)
            return can_token(self.line, TokenType.KEYWORD, '$')

        if c == '<':
            if self.check('<*>'):
                self.next(3)
                return can_token(self.line, TokenType.KEYWORD, '<*>')

            elif self.check('<|>'):
                self.next(3)
                return can_token(self.line, TokenType.OP_BOR, '<|>')

            elif self.check('<->'):
                self.next(3)
                return can_token(self.line, TokenType.OP_CONCAT, '<->')

            elif self.check('<<<'):
                self.next(3)
                return can_token(self.line, TokenType.KEYWORD, '<<<')

            elif self.check('<$>'):
                self.next(3)
                return can_token(self.line, TokenType.KEYWORD, '<$>')

            elif self.check('<='):
                self.next(2)
                return can_token(self.line, TokenType.OP_LE, '<=')
            
            elif self.check('<<'):
                self.next(2)
                return can_token(self.line, TokenType.OP_SHL, '<<')

            elif self.check('<|'):
                self.next(2)
                return can_token(self.line, TokenType.SEPCIFIC_ID_BEG, '<|')

            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_LT, '<')
        
        if c == '>':
            if self.check('>>>'):
                self.next(3)
                return can_token(self.line, TokenType.KEYWORD, '>>>')
            elif self.check('>='):
                self.next(2)
                return can_token(self.line, TokenType.OP_GE, '>=')
            elif self.check('>>'):
                self.next(2)
                return can_token(self.line, TokenType.OP_SHR, '>>')
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_GT, '>')

        if c == '!':
            if self.check('!='):
                self.next(2)
                return can_token(self.line, TokenType.OP_NE, '!=')
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_NOT, '!')

        if c == '@':
            if self.check('@@@'):
                self.next(3)
                return can_token(self.line, TokenType.KEYWORD, '@@@')
            elif self.check('@@'):
                self.next(2)
                return can_token(self.line, TokenType.KEYWORD, '@@')
            else:
                self.next(1)
                return can_token(self.line, TokenType.KEYWORD, '@')
        
        if c == '{':
            self.next(1)
            return can_token(self.line, TokenType.SEP_LCURLY, '{')
        
        if c == '}':
            self.next(1)
            return can_token(self.line, TokenType.SEP_RCURLY, '}')

        if c == '(':
            self.next(1)
            return can_token(self.line, TokenType.SEP_LPAREN, '(')

        if c == ')':
            self.next(1)
            return can_token(self.line, TokenType.SEP_RPAREN, ')')

        if c == '[':
            self.next(1)
            return can_token(self.line, TokenType.SEP_LBRACK, '[')

        if c == ']':
            self.next(1)
            return can_token(self.line, TokenType.SEP_RBRACK, ']')

        if c == '.':
            self.next(1)
            return can_token(self.line, TokenType.SEP_DOT, c)

        if lexer.isChinese(c) or c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return can_token(self.line, TokenType.KEYWORD, token)
            return can_token(self.line, TokenType.IDENTIFIER, token)
        
        if c in ('\'', '"'):
            return can_token(self.line, TokenType.STRING, self.scan_short_string())
        
        if c.isdigit():
            token = self.scan_number()
            return can_token(self.line, TokenType.NUM, token)

        if c == '+':
            self.next(1)
            return can_token(self.line, TokenType.OP_ADD, c)

        if c == '-':
            self.next(1)
            return can_token(self.line, TokenType.OP_MINUS, c)

        if c == '*':
            if self.check('**'):
                self.next(2)
                return can_token(self.line, TokenType.OP_POW, c)
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_MUL, c)

        if c == '/':
            if self.check('//'):
                self.next(2)
                return can_token(self.line, TokenType.OP_IDIV, '//')
            else:
                self.next(1)
                return can_token(self.line, TokenType.OP_DIV, c)

        if c == '&':
            self.next(1)
            return can_token(self.line, TokenType.OP_BAND, c)

        if c == '^':
            self.next(1)
            return can_token(self.line, TokenType.OP_WAVE, c)

        if c == ',':
            self.next(1)
            return can_token(self.line, TokenType.SEP_COMMA, ',')

        if c == '#':
            if self.check('##'):
                self.next(2)
                return can_token(self.line, TokenType.KEYWORD, '##')

        self.error("睇唔明嘅Token: " + c)

cpdef list cantonese_token(code : str):
    cdef lexer lex = lexer(code, keywords)
    cdef list tokens = []
    
    while True:
        token = lex.get_token()
        tokens.append(token)
        if token.typ == TokenType.EOF:
            break
    return tokens

cpdef print_token(tk : can_token):
    print(f"[{tk.lineno}, [{tk.typ}, {tk.value}]")