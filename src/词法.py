import re

"""
    Get the Cantonese Token List
"""

kw_print = "畀我睇下"
kw_endprint = "点样先"
kw_exit = "收工"
kw_in = "喺"
kw_elif = "定系"
kw_turtle_beg = "老作一下"
kw_type = "起底"
kw_assign = "讲嘢"
kw_class_def = "咩系"
kw_else_or_not = "唔系"
kw_is = "系"
kw_if = "如果"
kw_then = "嘅话"
kw_do = "->"
kw_begin = "{"
kw_end = "}"
kw_pass = "咩都唔做"
kw_while_do = "落操场玩跑步"
kw_function = "$"
kw_call = "用下"
kw_import = "使下"
kw_func_begin = "要做咩"
kw_func_end = "搞掂"
kw_is_2 = "就"
kw_assert = "谂下"
kw_class_assign = "佢嘅"
kw_while = "玩到"
kw_whi_end = "为止"
kw_return = "还数"
kw_try = "执嘢"
kw_except = "揾到"
kw_finally = "执手尾"
kw_raise = "掟个"
kw_raise_end = "来睇下"
kw_from = "从"
kw_to = "行到"
kw_endfor = "行晒"
kw_extend = "佢个老豆叫"
kw_method = "佢识得"
kw_endclass = "明白未啊"
kw_cmd = "落Order"
kw_break = "饮茶先啦"
kw_lst_assign = "拍住上"
kw_is_3 = "係"
kw_exit_1 = "辛苦晒啦"
kw_exit_2 = "同我躝"
kw_false = "唔啱"
kw_true = "啱"
kw_none = "冇"
kw_stackinit = "有条仆街叫"
kw_push = "顶你"
kw_pop = "丢你"
kw_model = "嗌"
kw_mod_new = "过嚟估下"
kw_class_init = "佢有啲咩"
kw_self = "自己嘅"
kw_call_begin = "下"
kw_get_value = "@" 

keywords = (
    kw_print,
    kw_endprint,
    kw_exit,
    kw_in,
    kw_elif,
    kw_turtle_beg,
    kw_type,
    kw_assign,
    kw_class_def,
    kw_else_or_not,
    kw_is,
    kw_if,
    kw_then,
    kw_do,
    kw_begin,
    kw_end,
    kw_pass,
    kw_while_do,
    kw_function,
    kw_call,
    kw_import,
    kw_func_begin,
    kw_func_end,
    kw_is_2,
    kw_assert,
    kw_class_assign,
    kw_while,
    kw_whi_end,
    kw_return,
    kw_try,
    kw_except,
    kw_finally,
    kw_raise,
    kw_raise_end,
    kw_from,
    kw_to,
    kw_endfor,
    kw_extend,
    kw_method,
    kw_endclass,
    kw_cmd,
    kw_break,
    kw_lst_assign,
    kw_is_3,
    kw_exit_1,
    kw_exit_2,
    kw_false,
    kw_true,
    kw_none,
    kw_stackinit,
    kw_push,
    kw_pop,
    kw_model,
    kw_mod_new,
    kw_class_init,
    kw_self,
    kw_call_begin,
    kw_get_value
)

class lexer(object):
    def __init__(self, code, keywords):
        self.code = code
        self.keywords = keywords
        self.line = 1
        self.re_new_line = re.compile(r"\r\n|\n\r|\n|\r")
        self.re_number = r"^0[xX][0-9a-fA-F]*(\.[0-9a-fA-F]*)?([pP][+\-]?[0-9]+)?|^[0-9]*(\.[0-9]*)?([eE][+\-]?[0-9]+)?"
        self.re_id = r"^[_\d\w]+|^[\u4e00-\u9fa5]+"
        self.re_str = r"(?s)(^'(\\\\|\\'|\\\n|\\z\s*|[^'\n])*')|(^\"(\\\\|\\\"|\\\n|\\z\s*|[^\"\n])*\")"
        self.re_expr = r"[|](.*?)[|]"
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
            return [self.line, ['EOF', 'EOF']]

        c = self.code[0]
        
        if c == '&':
            token = self.scan_callfunc() + ')'
            token = self.trans(token, self.make_rep(self.bif_get_code, self.bif_gen_code))
            return [self.line, ['expr', token]]

        if c == '|':
           token = self.scan_expr()
           token = self.trans(token, self.make_rep(self.bif_get_code, self.bif_gen_code))
           token = self.trans(token, self.make_rep(self.op_get_code, self.op_gen_code))
           return [self.line, ['expr', token]]

        if c == '-':
            if self.check('->'):
                self.next(2)
                return [self.line, ['keyword', '->']]
        
        if c == '$':
            self.next(1)
            return [self.line, ['keyword', '$']]

        if c == '@':
            self.next(1)
            return [self.line, ['keyword', '@']]
        
        if c == '{':
            self.next(1)
            return [self.line, ['keyword', '{']]
        
        if c == '}':
            self.next(1)
            return [self.line, ['keyword', '}']]            

        if self.isChinese(c) or c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return [self.line, ['keywords', token]]
            return [self.line, ['identifier', token]]
        
        if c in ('\'', '"'):
            return [self.line, ['string', self.scan_short_string()]]
        
        if c == '.' or c.isdigit():
            token = self.scan_number()
            return [self.line, ['num', token]]

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
        if token[1] == ['EOF', 'EOF']:
            break
    return tokens
