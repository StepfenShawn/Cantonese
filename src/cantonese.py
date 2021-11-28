"""
    Created at 2021/1/16 16:23
    Last update at 2021/6/6 9:11
    The interpreter for Cantonese    
"""
import cmd
import re
import sys
import os
import argparse
from src.濑嘢 import 濑啲咩嘢
from src.stack_vm import *

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
    
"""
    AST node for the Token List
"""
def node_print_new(Node : list, arg) -> None:
    """
        Node_print
            |
           arg
    """
    Node.append(["node_print", arg])

def node_sleep_new(Node : list, arg) -> None:
    """
        Node_sleep
            |
           arg
    """
    Node.append(["node_sleep", arg])

def node_break_new(Node : list) -> None:
    Node.append(["node_break"])

def node_exit_new(Node : list) -> None:
    """
        Node_exit
            |
           arg
    """
    Node.append(["node_exit"])

def node_let_new(Node : list, key ,value) -> None:
    """
        Node_let
          /  \
        key   value
    """
    Node.append(["node_let", key, value])

def node_if_new(Node : list, cond, stmt) -> None:
    """
        Node_if
          /  \
        cond  stmt
    """
    Node.append(["node_if", cond, stmt])

def node_elif_new(Node : list, cond, stmt) -> None:
    """
        Node_elif
          /  \
        cond  stmt
    """
    Node.append(["node_elif", cond, stmt])

def node_else_new(Node : list, stmt) -> None:
    """
        Node_else
            |
           stmt
    """
    Node.append(["node_else", stmt])

def node_loop_new(Node : list, cond, stmt) -> None:
    """
        Node_loop
          /  \
        cond  stmt
    """
    Node.append(["node_loop", cond, stmt])

def node_func_new(Node : list, func_name, args, body) -> None:
    """
        Node_fundef
         /  |  \
       name args body
    """
    Node.append(["node_fundef", func_name, args, body])

def node_call_new(Node : list, func_name) -> None:
    """
        Node_call
            |
           name
    """
    Node.append(["node_call", func_name])

def node_build_in_func_call_new(Node : list, var, func_name, args) -> None:
    """
        Node_bcall
          /  \
        name  args
    """
    Node.append(["node_bcall", var, func_name, args])

def node_import_new(Node : list, name) -> None:
    """
        Node_import
            |
           name
    """
    Node.append(["node_import", name])

def node_return_new(Node : list, v) -> None:
    """
        Node_return
            |
          value
    """
    Node.append(["node_return", v])

def node_try_new(Node : list, try_part) -> None:
    """
        Node_try
           |
          stmt
    """
    Node.append(["node_try", try_part])

def node_except_new(Node : list, _except, except_part) -> None:
    """
        Node_except
          /  \
     exception  stmt
    """
    Node.append(["node_except", _except, except_part])

def node_finally_new(Node : list, finally_part) -> None:
    """
        Node_finally
            |
           stmt
    """
    Node.append(["node_finally", finally_part])

def node_raise_new(Node : list, execption) -> None:
    """
        Node_raise
            |
          exception
    """
    Node.append(["node_raise", execption])

def node_for_new(Node : list, iterating_var, sequence, stmt_part) -> None:
    """
        Node_for
         /  |  \
        iter seq stmt
    """
    Node.append(["node_for", iterating_var, sequence, stmt_part])

def node_turtle_new(Node : list, instruction) -> None:
    Node.append(["node_turtle", instruction])

def node_assert_new(Node : list, args) -> None:
    Node.append(["node_assert", args])

def node_model_new(Node : list, model, datatest) -> None:
    """
        Node_model
          /  \
         model dataset
    """
    Node.append(["node_model", model, datatest])

def node_gettype_new(Node : list, value) -> None:
    Node.append(["node_gettype", value])

def node_class_new(Node : list, name, extend, method) -> None:
    """
        Node_class
          / | \
        name extend method
    """
    Node.append(["node_class", name, extend, method])

def node_attribute_new(Node : list, attr_list) -> None:
    Node.append(["node_attr", attr_list])

def node_method_new(Node : list, name, args, stmt) -> None:
    """
        Node_method
         / | \
        name args stmt
    """
    Node.append(["node_method", name, args, stmt])

def node_cmd_new(Node : list, cmd) -> None:
    """
        Node_cmd
            |
        conmmand
    """
    Node.append(["node_cmd", cmd])

def node_list_new(Node : list, name, list) -> None:
    """
        Node_list
          /  \
        name list
    """
    Node.append(["node_list", name, list])

def node_stack_new(Node : list, name) -> None:
    """
        Node_stack
            |
           name
    """
    Node.append(["node_stack", name])

def node_global_new(Node : list, global_table) -> None:
    Node.append(["node_global", global_table])

"""
    Parser for cantonese Token List
"""
class Parser(object):
    def __init__(self, tokens, Node):
        self.tokens = tokens
        self.pos = 0
        self.Node = Node
    
    def syntax_check(self, token, tag):
        if tag == "value" and self.get(0)[1] == token:
            return
        elif tag == "type" and self.get(0)[0] == token:
            return
        else:
            raise "Syntax error!"

    def get(self, offset, get_line = False):
        if self.pos + offset >= len(self.tokens):
            return ["", ""]
        if get_line:
            return self.tokens[self.pos + offset][0]
        return self.tokens[self.pos + offset][1]
    
    def get_value(self, token):
        if token[0] == 'expr':
            # If is expr, Remove the "|"
            token[1] = token[1][1 : -1]
        if token[0] == 'callfunc':
            # If is call func, Remove the '&'
            token[1] = token[1][1 :]
        return token

    def last(self, offset):
        return self.tokens[self.pos - offset][1]
    
    def skip(self, offset):
        self.pos += offset
    
    def match(self, name):
        if self.get(0)[1] == name:
            self.pos += 1
            return True
        else:
            return False
    
    def match_type(self, type):
        if self.get(0)[0] == type:
            self.pos += 1
            return True
        else:
            return False

    def token_type_except(self, tk, err, skip = False, i = 0):
        if isinstance(tk, list):
            if self.get(i)[0] in tk:
                if skip:
                    self.pos += 1
            
        if self.get(0)[0] == tk:
            self.pos += 1
            return
        
        line = self.get(i, get_line = True)
        raise Exception("Line " + str(line) + err + "\n 你嘅类型係: " + self.get(i)[0])

    def token_except(self, tk, err, skip = False, i = 0):
        if isinstance(tk, list):
            if self.get(i)[1] in tk:
                if skip:
                    self.pos += 1
                return

        elif self.get(i)[1] == tk:
            if skip:
                self.pos += 1
            return

        line = self.get(i, get_line = True)
        raise Exception("Line " + str(line) + err + "\n 净系揾到: " + self.get(i)[1])

    # TODO: Add error check
    def parse(self):
        while True:
            if self.match(kw_print):
                node_print_new(self.Node, self.get_value(self.get(0)))
                self.skip(1) # Skip the args
                self.token_except(kw_endprint, " : 濑嘢! 揾唔到 '点样先' ", skip = True)
               
            elif self.match("sleep"):
                node_sleep_new(self.Node, self.get(0))
                self.skip(1)

            elif self.match(kw_exit) or self.match(kw_exit_1) or self.match(kw_exit_2):
                node_exit_new(self.Node)
                self.skip(1)

            elif self.match(kw_global_set):
                table = self.get_value(self.get(0))
                self.skip(1)
                node_global_new(self.Node, table)

            elif self.match(kw_class_assign):
                kw = self.get(0)[1]
                if kw != kw_do:
                    self.token_except(tk = [kw_is, kw_is_2, kw_is_3], i = 1,  err = " : 濑嘢! 揾唔到 '係' " )
                    node_let_new(self.Node, self.get_value(self.get(0)), self.get_value(self.get(2)))
                    self.skip(3)

                if kw == kw_do:  
                    self.token_except(tk = [kw_do], err = " : 濑嘢! 揾唔到 '->' ", skip = True)
                    self.token_except(tk = [kw_begin], err = " : 濑嘢! 揾唔到 '{' ", skip = True)
                    assign_list = []
                    while self.tokens[self.pos][1][1] != kw_end:
                        assign_list.append(self.tokens[self.pos][1])
                        self.pos += 1
                    if len(assign_list) % 3 != 0:
                        raise Exception(" 濑嘢! 唔知你想点? 请检查你嘅赋值语句!!!")
                    for i in range(0, len(assign_list)):
                        k = assign_list[i][1]
                        if k == kw_is or k == kw_is_2 or k == kw_is_3:
                            node_let_new(self.Node, self.get_value(assign_list[i - 1]),
                                    self.get_value(assign_list[i + 1]))
                    self.skip(1)

            elif self.match(kw_assign):
                kw = self.get(0)[1]
                if kw != kw_do:
                    self.token_except(tk = [kw_is, kw_is_2, kw_is_3], i = 1,  err = " : 濑嘢! 揾唔到 '係' " )
                    node_let_new(self.Node, self.get_value(self.get(0)), self.get_value(self.get(2)))
                    self.skip(3)

                if kw == kw_do:  
                    self.token_except(tk = [kw_do], err = " : 濑嘢! 揾唔到 '->' ", skip = True)
                    self.token_except(tk = [kw_begin], err = " : 濑嘢! 揾唔到 '{' ", skip = True)
                    assign_list = []
                    while self.tokens[self.pos][1][1] != kw_end:
                        assign_list.append(self.tokens[self.pos][1])
                        self.pos += 1
                    if len(assign_list) % 3 != 0:
                        raise Exception(" 濑嘢! 唔知你想点? 请检查你嘅赋值语句!!!")
                    for i in range(0, len(assign_list)):
                        k = assign_list[i][1]
                        if k == kw_is or k == kw_is_2 or k == kw_is_3:
                            node_let_new(self.Node, self.get_value(assign_list[i - 1]),
                                    self.get_value(assign_list[i + 1]))
                    self.skip(1)

            
            elif self.match(kw_if):
                cond = self.get_value(self.get(0))
                self.token_except(tk = kw_then, i = 1, err = " : 濑嘢! 揾唔到 '嘅话' ")
                self.token_except(tk = kw_do, i = 2, err = " : 濑嘢! 揾唔到 '->' ")
                self.token_except(tk = kw_begin, i = 3, err = " : 濑嘢! 揾唔到 '{' ")
                self.skip(4) # Skip the "cond", "then", "do", "begin"
                if_case_end = 0 # The times of case "end"
                if_should_end = 1
                node_if = []
                stmt_if = []
                while if_case_end != if_should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == kw_if:
                        if_should_end += 1
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == kw_end:
                        if_case_end += 1
                        if if_case_end != if_should_end:
                            stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == kw_elif:
                        if_should_end += 1
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == kw_assign:
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                        if self.tokens[self.pos][1][1] == kw_do:
                            if_should_end += 1
                    else:
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_if, node_if).parse()
                node_if_new(self.Node, cond, node_if)
            
            elif self.match(kw_elif): # case "定系" elif
                cond = self.get_value(self.get(0))
                self.token_except(tk = kw_then, i = 1, err = " : 濑嘢! 揾唔到 '嘅话' ")
                self.token_except(tk = kw_do, i = 2, err = " : 濑嘢! 揾唔到 '->' ")
                self.token_except(tk = kw_begin, i = 3, err = " : 濑嘢! 揾唔到 '{' ")
                self.skip(4) # Skip the "cond", "then", "do", "begin"
                elif_case_end = 0 # The times of case "end"
                elif_should_end = 1
                node_elif = []
                stmt_elif = []
                while elif_case_end != elif_should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == kw_if:
                        elif_should_end += 1
                        stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == kw_end:
                        elif_case_end += 1
                        if elif_case_end != elif_should_end:
                            stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == kw_elif:
                        elif_should_end += 1
                        stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                     elif self.get(0)[1] == kw_assign:
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                        if self.tokens[self.pos][1][1] == kw_do:
                            elif_should_end += 1
                    else:
                        stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_elif, node_elif).parse()
                node_elif_new(self.Node, cond, node_elif)

            elif self.match(kw_else_or_not): # case "唔系" else
                self.token_except(tk = kw_then, i = 0, err = " : 濑嘢! 揾唔到 '嘅话' ")
                self.token_except(tk = kw_do, i = 1, err = " : 濑嘢! 揾唔到 '->' ")
                self.token_except(tk = kw_begin, i = 2, err = " : 濑嘢! 揾唔到 '{' ")
                self.skip(3) # Skip the "then", "do", "begin"
                else_case_end = 0 # The times of case "end"
                else_should_end = 1
                node_else = []
                stmt_else = []
                while else_case_end != else_should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == kw_if:
                        else_should_end += 1
                        stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == kw_end:
                        else_case_end += 1
                        if else_case_end != else_should_end:
                            stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == kw_elif:
                        else_should_end += 1
                        stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                     elif self.get(0)[1] == kw_assign:
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                        if self.tokens[self.pos][1][1] == kw_do:
                            else_should_end += 1
                    else:
                        stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_else, node_else).parse()
                node_else_new(self.Node, node_else)

            elif self.match(kw_while_do):
                stmt = []
                while self.tokens[self.pos][1][1] != kw_while:
                    stmt.append(self.tokens[self.pos])
                    self.pos += 1
                node_while = []
                self.skip(1)
                cond = self.get_value(self.get(0))
                Parser(stmt, node_while).parse()
                node_loop_new(self.Node, cond, node_while)
                self.skip(2) # Skip the "end"
            
            elif self.match(kw_function): # Case "function"
                if self.get(1)[0] == 'expr':
                   func_name = self.get_value(self.get(0))
                   args = self.get_value(self.get(1))
                   self.token_except(tk = kw_func_begin, i = 2, err = " : 濑嘢! 揾唔到 '要做咩' ")
                   self.skip(3)
                   func_stmt = []
                   while self.tokens[self.pos][1][1] != kw_func_end:
                       func_stmt.append(self.tokens[self.pos])
                       self.pos += 1
                   node_func = []
                   Parser(func_stmt, node_func).parse()
                   node_func_new(self.Node, func_name, args, node_func)
                   self.skip(1) # Skip the funcend
                
                else:
                    func_name = self.get_value(self.get(0))
                    self.token_except(tk = kw_func_begin, i = 1, err = " : 濑嘢! 揾唔到 '要做咩' ")
                    self.skip(2) # Skip the funcbegin
                    func_stmt = []
                    while self.tokens[self.pos][1][1] != kw_func_end:
                        func_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    node_func = []
                    Parser(func_stmt, node_func).parse()
                    node_func_new(self.Node, func_name, "None", node_func)
                    self.skip(1) # Skip the funcend
            
            elif self.match(kw_turtle_beg):
                self.skip(2) # Skip the "do", "begin"
                turtle_inst = []
                while self.tokens[self.pos][1][1] != kw_end:
                    if self.tokens[self.pos][1][0] == 'identifier':
                        pass
                    else:
                        turtle_inst.append(self.get_value(self.tokens[self.pos][1])[1])
                    self.pos += 1
                node_turtle_new(self.Node, turtle_inst)
                self.skip(1)
            
            elif self.match(kw_call):
                node_call_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match(kw_import):
                node_import_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match_type("expr") or self.match_type("identifier"):
                if self.match(kw_from):
                    iterating_var = self.get_value(self.get(-2))
                    seq = "(" + str(self.get_value(self.get(0))[1]) + "," \
                          + str(self.get_value(self.get(2))[1]) + ")"
                    self.skip(3)
                    node_for = []
                    for_stmt = []
                    for_case_end = 0
                    for_should_end = 1
                    while for_should_end != for_case_end and self.pos < len(self.tokens):
                        if (self.get(0)[0] == "expr" or self.get(0)[0] == "identifier") \
                             and self.get(1)[1] == kw_from:
                            for_should_end += 1
                            for_stmt.append(self.tokens[self.pos])
                            self.pos += 1
                        elif self.get(0)[1] == kw_endfor:
                            for_case_end += 1
                            if for_case_end != for_should_end:
                                for_stmt.append(self.tokens[self.pos])
                            self.pos += 1
                        else:
                            for_stmt.append(self.tokens[self.pos])
                            self.pos += 1
                    Parser(for_stmt, node_for).parse()
                    node_for_new(self.Node, iterating_var, seq, node_for)
                
                if self.get(0)[1] == kw_lst_assign:
                    self.skip(1)
                    list = self.get_value(self.get(-2))
                    name = self.get_value(self.get(1))
                    node_list_new(self.Node, name, list)
                    self.skip(2)

                if self.get(0)[1] == kw_set_assign:
                    self.skip(1)
                    list = self.get_value(self.get(-2))
                    name = self.get_value(self.get(1))
                    list[1] = "{" + list[1] + "}"
                    node_let_new(self.Node, name, list)
                    self.skip(2)

                if self.get(0)[1] == kw_do:
                    self.skip(1)
                    id = self.get_value(self.get(-2))
                    args = self.get_value(self.get(1))
                    func = self.get_value(self.get(0))
                    node_build_in_func_call_new(self.Node, id, func, args)
                    self.skip(2)

                if self.get(0)[1] == kw_call_begin:
                    func_name = self.get_value(self.get(-1))
                    self.skip(2)
                    args = self.get_value(self.get(0))
                    cons = ['expr', func_name[1] + '(' + args[1] + ')']
                    self.skip(1)
                    if self.get(0)[1] == kw_get_value:
                        self.skip(1)
                        v = self.get_value(self.get(0))
                        node_let_new(self.Node, v, cons)
                    else:
                        node_call_new(self.Node, cons)

            elif self.match(kw_return):
                node_return_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match(kw_try):
                self.token_except(tk = kw_do, i = 0, err = " : 濑嘢! 揾唔到 '->' ")
                self.token_except(tk = kw_begin, i = 1, err = " : 濑嘢! 揾唔到 '{'")
                self.skip(2) # SKip the "begin, do"
                should_end = 1
                case_end = 0
                node_try = []
                stmt_try = []
                while case_end != should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == kw_end:
                        case_end += 1
                        self.pos += 1
                    else:
                        stmt_try.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_try, node_try).parse()
                node_try_new(self.Node, node_try)
            
            elif self.match(kw_except):
                _except = self.get_value(self.get(0))
                self.token_except(tk = kw_then, i = 1, err = " : 濑嘢! 揾唔到 '嘅话'")
                self.token_except(tk = kw_do, i = 2, err = " : 濑嘢! 揾唔到 '->'")
                self.token_except(tk = kw_begin, i = 3, err = " : 濑嘢! 揾唔到 '{'")
                self.skip(4) # SKip the "except", "then", "begin", "do"
                should_end = 1
                case_end = 0
                node_except = []
                stmt_except = []
                while case_end != should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == kw_end:
                        case_end += 1
                        self.pos += 1
                    else:
                        stmt_except.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_except, node_except).parse()
                node_except_new(self.Node, _except , node_except)

            elif self.match(kw_finally):
                self.token_except(tk = kw_do, i = 0, err =  " : 濑嘢! 揾唔到 '->'")
                self.token_except(tk = kw_begin, i = 1, err = " : 濑嘢! 揾唔到 '{'")
                self.skip(2) # Skip the "begin", "do"
                should_end = 1
                case_end = 0
                node_finally = []
                stmt_finally = []
                while case_end != should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == kw_end:
                        case_end += 1
                        self.pos += 1
                    else:
                        stmt_finally.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_finally, node_finally).parse()
                node_finally_new(self.Node, node_finally)

            elif self.match(kw_assert):
                node_assert_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match(kw_raise):
                node_raise_new(self.Node, self.get_value(self.get(0)))
                self.skip(2)
            
            elif self.match(kw_type):
                node_gettype_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match(kw_pass):
                self.Node.append(["node_pass"])
            
            elif self.match(kw_break):
                node_break_new(self.Node)
            
            elif self.match(kw_class_def):
                class_name = self.get_value(self.get(0))
                self.skip(1)
                if self.match(kw_extend):
                    extend = self.get_value(self.get(0))
                    self.skip(1)
                class_stmt = []
                node_class = []
                while self.tokens[self.pos][1][1] != kw_endclass:
                    class_stmt.append(self.tokens[self.pos])
                    self.pos += 1
                Parser(class_stmt, node_class).parse()
                self.skip(1) # Skip the "end"
                node_class_new(self.Node, class_name, extend, node_class)

            elif self.match(kw_class_init):
                self.skip(1)
                attr_lst = self.get_value(self.get(0))
                self.skip(1)
                node_attribute_new(self.Node, attr_lst)
            
            elif self.match(kw_method):
                method_name = self.get_value(self.get(0))
                self.skip(1)
                # Check if has args
                if self.get(0)[0] == "expr":
                    args = self.get_value(self.get(0))
                    self.skip(1)
                else:
                    args = "None"
                self.skip(2) # Skip the "do", "begin"
                method_stmt = []
                node_method = []
                method_should_end = 1
                method_case_end = 0
                while method_case_end != method_should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == kw_end:
                        method_case_end += 1
                        if method_case_end != method_should_end:
                            method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    elif self.get(0)[1] == kw_if:
                        method_should_end += 1
                        method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    elif self.get(0)[1] == kw_elif:
                        method_should_end += 1
                        method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    elif self.get(0)[1] == kw_else_or_not:
                        method_should_end += 1
                        method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    else:
                        method_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(method_stmt, node_method).parse()
                node_method_new(self.Node, method_name, args, node_method)
            
            elif self.match(kw_cmd):
                node_cmd_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)

            elif self.match(kw_model):
                model = self.get_value(self.get(0))
                self.skip(1)
                self.syntax_check(kw_mod_new, "value")
                self.skip(2)
                datatest = self.get_value(self.get(0))
                self.skip(1)
                node_model_new(self.Node, model, datatest)
            
            elif self.match(kw_stackinit):
                node_stack_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)

            elif self.match(kw_push):
                self.syntax_check(kw_do, "value")
                self.skip(1)
                self.Node.append(["stack_push", self.get_value(self.get(0)), self.get_value(self.\
                    get(1))])
                self.skip(2)
            
            elif self.match(kw_pop):
                self.syntax_check(kw_do, "value")
                self.skip(1)
                self.Node.append(["stack_pop", self.get_value(self.get(0)), self.get_value(self.\
                    get(1))])
                self.skip(1)

            else:
                break

variable = {}
TO_PY_CODE = ""
use_tradition = False # 是否使用繁体
 
def run(Nodes : list, TAB = '', label = '', path = '') -> None:
    def check(tab):
        if label != 'whi_run' and label != 'if_run' and label != 'else_run' and  \
            label != 'elif_run' and label != "func_run" and label != "try_run" and \
            label != "except_run" and label != "finally_run" and label != "for_run" and \
            label != "class_run" and label != "method_run":
            tab = ''
    global TO_PY_CODE
    global use_traditon
    if Nodes == None:
        return None
    for node in Nodes:
        if node[0] == "node_print":
            check(TAB)
            TO_PY_CODE += TAB + "print(" + node[1][1] + ")\n"
            
        if node[0] == "node_sleep":
            check(TAB)
            TO_PY_CODE += TAB + "import time\n"
            TO_PY_CODE += TAB + "time.sleep(" + node[1][1] + ")\n"
        
        if node[0] == "node_import":
            check(TAB)
            if cantonese_lib_import(node[1][1]) == "Not found":
                cantonese_lib_run(node[1][1], path, use_tradition)
            else:
                TO_PY_CODE += TAB + "import " + cantonese_lib_import(node[1][1]) + "\n"

        if node[0] == "node_exit":
            check(TAB)
            TO_PY_CODE += TAB + "exit()\n"

        if node[0] == "node_global":
            check(TAB)
            TO_PY_CODE += TAB + "global " + node[1][1] + "\n"
        
        if node[0] == "node_let":
            check(TAB)
            TO_PY_CODE += TAB + node[1][1] + " = " + node[2][1] + "\n"
        
        if node[0] == "node_if":
            check(TAB)
            TO_PY_CODE += TAB + "if " + node[1][1] + ":\n"
            run(node[2], TAB + '\t', 'if_run')
            label = ''
        
        if node[0] == "node_elif":
            check(TAB)
            TO_PY_CODE += TAB + "elif " + node[1][1] + ":\n"
            run(node[2], TAB + '\t', 'elif_run')
            label = ''
        
        if node[0] == "node_else":
            check(TAB)
            TO_PY_CODE += TAB + "else:\n"
            run(node[1], TAB + '\t', 'else_run')
            label = ''
        
        if node[0] == "node_loop":
            check(TAB)
            TO_PY_CODE += TAB + "while " + "not (" + node[1][1] + "):\n"
            run(node[2], TAB + '\t', 'whi_run')
            label = ''
        
        if node[0] == "node_for":
            check(TAB)
            TO_PY_CODE += TAB + "for " + node[1][1] + " in " + "range" + \
                          node[2] + ":\n"
            run(node[3], TAB + '\t', "for_run")
            label = ''
        
        if node[0] == "node_fundef":
            # check if has args
            if node[2] == 'None':
                check(TAB)
                TO_PY_CODE += TAB + "def " + node[1][1] + "():\n"
                run(node[3], TAB + '\t', 'func_run')
                label = ''
            else:
                check(TAB)
                TO_PY_CODE += TAB + "def " + node[1][1] + "(" + node[2][1] + "):\n"
                run(node[3], TAB + '\t', 'func_run')
                label = ''
        
        if node[0] == "node_call":
            check(TAB)
            TO_PY_CODE += TAB + node[1][1] + "\n"

        if node[0] == "node_break":
            check(TAB)
            TO_PY_CODE += TAB + "break\n"
        
        if node[0] == "node_pass":
            check(TAB)
            TO_PY_CODE += TAB + "pass\n"
        
        if node[0] == "node_bcall":
            check(TAB)
            # check if has args
            if node[3] != "None":
                TO_PY_CODE += TAB + node[1][1] + "." + node[2][1] + "(" + node[3][1] + ")\n"
            else:
                TO_PY_CODE += TAB + node[1][1] + "." + node[2][1] + "()\n"
        
        if node[0] == "node_return":
            check(TAB)
            TO_PY_CODE += TAB + "return " + node[1][1] + "\n"
        
        if node[0] == "node_list":
            check(TAB)
            TO_PY_CODE += TAB + node[1][1] + " = [" + node[2][1] + "]\n"
        
        if node[0] == "node_raise":
            check(TAB)
            TO_PY_CODE += TAB + "raise " + node[1][1] + "\n"
        
        if node[0] == "node_cmd":
            check(TAB)
            TO_PY_CODE += TAB + "os.system(" + node[1][1] + ")\n"
        
        if node[0] == "node_turtle":
            check(TAB)
            cantonese_turtle_init()
            for ins in node[1]:
                TO_PY_CODE += TAB + ins + "\n"
        
        if node[0] == "node_assert":
            check(TAB)
            TO_PY_CODE += TAB + "assert " + node[1][1] + "\n"
        
        if node[0] == "node_gettype":
            check(TAB)
            TO_PY_CODE += TAB + "print(type(" + node[1][1] + "))\n"
        
        if node[0] == "node_try":
            check(TAB)
            TO_PY_CODE += TAB + "try:\n"
            run(node[1], TAB + '\t', 'try_run')
            label = ''
        
        if node[0] == "node_except":
            check(TAB)
            TO_PY_CODE += TAB + "except " + node[1][1] + ":\n" 
            run(node[2], TAB + '\t', 'except_run')
            label = ''
        
        if node[0] == "node_finally":
            check(TAB)
            TO_PY_CODE += TAB + "finally:\n"
            run(node[1], TAB + '\t', 'finally_run')
            label = ''

        if node[0] == "node_class":
            check(TAB)
            TO_PY_CODE += TAB + "class " + node[1][1] + "(" \
                          + node[2][1] + "):\n"
            run(node[3], TAB + '\t', 'class_run')
            label = ''

        if node[0] == "node_attr":
            check(TAB)
            TO_PY_CODE += TAB + "def __init__(self, " + node[1][1] + "):\n"
            attr_lst = node[1][1].replace(" ", "").split(',')
            for i in attr_lst:
                TO_PY_CODE += TAB + '\t' + "self." + i + " = " + i + "\n"

        if node[0] == "node_method":
            check(TAB)
            if node[2] == 'None':
                TO_PY_CODE += TAB + "def " + node[1][1] + "(self):\n"
            else:
                TO_PY_CODE += TAB + "def " + node[1][1] + "(self, " + node[2][1] + "):\n"
            run(node[3], TAB + '\t', "method_run")
            label = ''

        if node[0] == "node_stack":
            check(TAB)
            cantonese_stack_init()
            TO_PY_CODE += TAB + node[1][1] + " = stack()\n"

        if node[0] == "stack_push":
            check(TAB)
            TO_PY_CODE += TAB + node[1][1] + ".push(" + node[2][1] +")\n"
        
        if node[0] == "stack_pop":
            check(TAB)
            TO_PY_CODE += TAB + node[1][1] + ".pop()\n"

        if node[0] == "node_model":
            check(TAB)
            TO_PY_CODE += TAB + cantonese_model_new(node[1][1], node[2][1], \
                                TAB, TO_PY_CODE)

"""
    Built-in library for Cantonese
"""
def cantonese_lib_import(name : str) -> None:
    if name == "random" or name == "随机数":
        cantonese_random_init()
        return "random"
    elif name == "datetime" or name == "日期":
        cantonese_datetime_init()
        return "datetime"
    elif name == "math" or name == "数学":
        cantonese_math_init()
        return "math"
    elif name == "smtplib" or name == "邮箱":
        cantonese_smtplib_init()
        return "smtplib"
    elif name == "xml" or name == "xml解析":
        cantonese_xml_init()
        return "xml"
    elif name == "csv" or name == "csv解析":
        cantonese_csv_init()
        return "csv"
    elif name == "os" or name == "系统":
        return "os"
    elif name == "re" or name == "正则匹配":
        cantonese_re_init()
        return "re"
    elif name == "urllib" or name == "网页获取":
        cantonese_urllib_init()
        return "urllib"
    elif name == "requests" or name == "网络请求":
        cantonese_requests_init()
        return "requests"
    elif name == "socket" or name == "网络连接":
        cantonese_socket_init()
        return "socket"
    elif name == "kivy" or name == "手机程式":
        cantonese_kivy_init()
        return "kivy"
    elif name == "pygame" or name == "游戏":
        cantonese_pygame_init()
        return "pygame"
    elif name == "json" or name == "json解析":
        cantonese_json_init()
        return "json"
    elif name[ : 7] == "python-":
        return name[7 : ]
    else:
        return "Not found"

def cantonese_lib_init() -> None:
    def cantonese_open(file, 模式 = 'r', 解码 = None):
        return open(file, mode = 模式, encoding = 解码)

    def cantonese_close(file) -> None:
        file.close()

    def out_name(file) -> None:
        print(file.name)

    def out_ctx(file, size = None) -> None:
        if size == None:
            print(file.read())
            return
        print(file.read(size))

    def get_name(file) -> str:
        return file.name

    def cantonese_read(file, size = None) -> str:
        if size == None:
            return file.read()
        return file.read(size)
    
    cantonese_func_def("开份文件", cantonese_open)
    cantonese_func_def("关咗佢", cantonese_close)
    cantonese_func_def("睇睇文件名", out_name)
    cantonese_func_def("睇睇有咩", out_ctx)
    cantonese_func_def("文件名", get_name)
    cantonese_func_def("读取", cantonese_read)

    def get_list_end(lst : list):
        return lst[-1]

    def get_list_beg(lst : list):
        return lst[0]

    def where(lst : list, index : int, index2 = None, index3 = None, index4 = None):
        if index2 != None and index3 == None and index4 == None:
            return lst[index][index2]
        if index3 != None and index2 != None and index4 == None:
            return lst[index][index2][index3]
        if index4 != None and index2 != None and index3 != None:
            return lst[index][index2][index3][index4]
        return lst[index]
    
    def lst_insert(lst : list, index : int, obj) -> None:
        lst.insert(index, obj)

    def list_get(lst : list, index : int):
        return lst[index]

    cantonese_func_def("最尾", get_list_end)
    cantonese_func_def("身位", where)
    cantonese_func_def("挜位", lst_insert)
    cantonese_func_def("排头位", get_list_beg)
    cantonese_func_def("摞位", list_get)

    cantonese_func_def("唔啱", False)
    cantonese_func_def("啱", True)

def cantonese_json_init() -> None:
    import json

    def json_load(text):
        return json.loads(text)

    def show_json_load(text):
        print(json.loads(text))
    
    cantonese_func_def("睇下json", show_json_load)
    cantonese_func_def("读取json", json_load)

def cantonese_csv_init() -> None:
    import csv

    def out_csv_read(file):
        for i in csv.reader(file):
            print(i)
    
    def get_csv(file):
        ret = []
        for i in csv.reader(file):
            ret.append(i)
        return i

    cantonese_func_def("睇睇csv有咩", out_csv_read)
    cantonese_func_def("读取csv", get_csv)

def cantonese_random_init() -> None:
    import random
    cantonese_func_def("求其啦", random.random)
    cantonese_func_def("求其int下啦", random.randint)
    cantonese_func_def("求其嚟个", random.randrange)

def cantonese_datetime_init() -> None:
    import datetime
    cantonese_func_def("宜家几点", datetime.datetime.now)

def cantonese_xml_init() -> None:
    from xml.dom.minidom import parse
    import xml.dom.minidom
    
    def make_dom(file) -> None:
        return xml.dom.minidom.parse(file).documentElement

    def has_attr(docelm, attr) -> bool:
        return docelm.hasAttribute(attr)

    def get_attr(docelm, attr):
        print(docelm.getAttribute(attr))
    
    def getElementsByTag(docelm, tag : str, out = None, ctx = None):
        if out == 1:
            print(docelm.getElementsByTagName(tag))
        if ctx != None:
            print(ctx + docelm.getElementsByTagName(tag)[0].childNodes[0].data)
        return docelm.getElementsByTagName(tag)

    cantonese_func_def("整樖Dom树", make_dom)
    cantonese_func_def("Dom有嘢", has_attr)
    cantonese_func_def("睇Dom有咩", get_attr)
    cantonese_func_def("用Tag揾", getElementsByTag)
    cantonese_func_def("用Tag揾嘅", getElementsByTag)

def cantonese_turtle_init() -> None:
    import turtle
    cantonese_func_def("画个圈", turtle.circle)
    cantonese_func_def("写隻字", turtle.write)
    cantonese_func_def("听我支笛", turtle.exitonclick)

def cantonese_smtplib_init() -> None:
    import smtplib
    def send(sender : str, receivers : str,  message : str, 
             smtpObj = smtplib.SMTP('localhost')) -> None:
        try:
            smtpObj.sendmail(sender, receivers, message)         
            print("Successfully sent email!")
        except Exception:
            print("Error: unable to send email")
    cantonese_func_def("send份邮件", send)

def cantonese_stack_init() -> None:
    class _stack(object):
        def __init__(self):
            self.stack = []
        def __str__(self):
            return 'Stack: ' + str(self.stack)
        def push(self, value):
            self.stack.append(value)
        def pop(self):
            if self.stack:
                return self.stack.pop()
            else:
                raise LookupError('stack 畀你丢空咗!')
    cantonese_func_def("stack", _stack)
    cantonese_func_def("我丢", _stack.pop)
    cantonese_func_def("我顶", _stack.push)

def cantonese_func_def(func_name : str, func) -> None:
    variable[func_name] = func

def cantonese_math_init():
    import math
    class Matrix(object):
        def __init__(self, list_a):
            assert isinstance(list_a, list)
            self.matrix = list_a
            self.shape = (len(list_a), len(list_a[0]))
            self.row = self.shape[0]
            self.column = self.shape[1]
        
        def __str__(self):
            return 'Matrix: ' + str(self.matrix)

        def build_zero_value_matrix(self, shape):
            zero_value_mat = []
            for i in range(shape[0]):
                zero_value_mat.append([])
                for j in range(shape[1]):
                    zero_value_mat[i].append(0)
            zero_value_matrix = Matrix(zero_value_mat)
            return zero_value_matrix

        def matrix_addition(self, the_second_mat):
            assert isinstance(the_second_mat, Matrix)
            assert the_second_mat.shape == self.shape
            result_mat = self.build_zero_value_matrix(self.shape)
            for i in range(self.row):
                for j in range(self.column):
                    result_mat.matrix[i][j] = self.matrix[i][j] + the_second_mat.matrix[i][j]
            return result_mat

        def matrix_multiplication(self, the_second_mat):
            assert isinstance(the_second_mat, Matrix)
            assert self.shape[1] == the_second_mat.shape[0]
            shape = (self.shape[0], the_second_mat.shape[1])
            result_mat = self.build_zero_value_matrix(shape)
            for i in range(self.shape[0]):
                for j in range(the_second_mat.shape[1]):
                    number = 0
                    for k in range(self.shape[1]):
                        number += self.matrix[i][k] * the_second_mat.matrix[k][j]
                    result_mat.matrix[i][j] = number
            return result_mat
    
    def corr(a, b):
        if len(a) == 0 or len(b) == 0:
            return None
        a_avg = sum(a) / len(a)
        b_avg = sum(b) / len(b)
        cov_ab = sum([(x - a_avg) * (y - b_avg) for x, y in zip(a, b)])
        sq = math.sqrt(sum([(x - a_avg) ** 2 for x in a]) * sum([(x - b_avg) ** 2 for x in b]))
        corr_factor = cov_ab / sq
        return corr_factor

    def KNN(inX, dataSet, labels, k):
        m, n = len(dataSet), len(dataSet[0])
        distances = []
        for i in range(m):
            sum = 0
            for j in range(n):
                sum += (inX[j] - dataSet[i][j]) ** 2
            distances.append(sum ** 0.5)
        sortDist = sorted(distances)
        classCount = {}
        for i in range(k):
            voteLabel = labels[distances.index(sortDist[i])]
            classCount[voteLabel] = classCount.get(voteLabel, 0) + 1
        sortedClass = sorted(classCount.items(), key = lambda d : d[1], reverse = True)
        return sortedClass[0][0]
    
    def l_reg(testX, X, Y):
        a = b = mxy = sum_x = sum_y = lxy = xiSubSqr = 0.0
        for i in range(len(X)):
            sum_x += X[i]
            sum_y += Y[i]
        x_ave = sum_x / len(X)
        y_ave = sum_y / len(X)
        for i in range(len(X)):
            lxy += (X[i] - x_ave) * (Y[i] - y_ave)
            xiSubSqr += (X[i] - x_ave) * (X[i] - x_ave)
        b = lxy / xiSubSqr
        a = y_ave - b * x_ave
        print("Linear function is:")
        print("y=" + str(b) + "x+"+ str(a))
        return b * testX + a

    cantonese_func_def("KNN", KNN)
    cantonese_func_def("l_reg", l_reg)
    cantonese_func_def("corr", corr)
    cantonese_func_def("矩阵", Matrix)
    cantonese_func_def("点积", Matrix.matrix_multiplication)

def cantonese_model_new(model, datatest, tab, code) -> str:
    if model == "KNN":
        code += tab + "print(KNN(" + datatest + ", 数据, 标签, K))"
    elif model == "L_REG":
        code += tab + "print(l_reg(" + datatest + ", X, Y))"
    else:
        print("揾唔到你嘅模型: " + model + "!")
        code = ""
    return code

def cantonese_re_init() -> None:
    def can_re_match(pattern : str, string : str, flags = 0):
        return re.match(pattern, string, flags)
    
    def can_re_match_out(pattern : str, string : str, flags = 0) -> None:
        print(re.match(pattern, string, flags).span())

    cantonese_func_def("衬", can_re_match_out)
    cantonese_func_def("衬唔衬", can_re_match)

def cantonese_urllib_init() -> None:
    import urllib.request
    def can_urlopen_out(url : str) -> None:
        print(urllib.request.urlopen(url).read())

    def can_urlopen(url : str):
        return urllib.request.urlopen(url)

    cantonese_func_def("睇网页", can_urlopen_out)
    cantonese_func_def("揾网页", can_urlopen)

def cantonese_requests_init() -> None:
    import requests

    def req_get(url : str):
        headers = {
            'user-agent':
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36' \
        }
        res = requests.get(url, headers)
        res.encoding = 'utf-8'
        return res.text

    cantonese_func_def("𠯠求", req_get)

def cantonese_socket_init() -> None:
    import socket

    def s_new():
        return socket.socket() 

    def s_connect(s, port, host = socket.gethostname()):
        s.connect((host, port))
        return s
    
    def s_recv(s, i : int):
        return s.recv(i)
    
    def s_close(s) -> None:
        s.close()

    cantonese_func_def("倾偈", s_connect)
    cantonese_func_def("收风", s_recv)
    cantonese_func_def("通电话", s_new)
    cantonese_func_def("收线", s_close)

def cantonese_kivy_init() -> None:
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.boxlayout import BoxLayout

    def app_show(ctx, 宽 = (.5, .5), 
        高 = {"center_x": .5, "center_y": .5}) -> None:
        return Label(text = ctx, size_hint = 宽, pos_hint = 高)

    def app_run(app_main, build_func) -> None:
        print("The app is running ...")
        def build(self):
            return build_func()
        app_main.build = build
        app_main().run()

    def app_button(ctx, 宽 = (.5, .5), 
        高 = {"center_x": .5, "center_y": .5}) -> None:
        return Button(text = ctx, size_hint = 宽, pos_hint = 高)

    def app_layout(types, 布局 = "", 方向 = 'vertical', 间距 = 15, 内边距 = 10):
        if 布局 ==  "":
            if types == "Box":
                return BoxLayout(orientation = 方向, 
                spacing = 间距, padding = 内边距)
        else:
            for i in types.stack:
                布局.add_widget(i)
    
    def button_bind(btn, func) -> None:
        btn.bind(on_press = func)

    cantonese_func_def("App", App)
    cantonese_func_def("Label", Label)
    cantonese_func_def("Button", Button)
    cantonese_func_def("App运行", app_run)
    cantonese_func_def("同我show", app_show)
    cantonese_func_def("开掣", app_button)
    cantonese_func_def("老作", app_layout)
    cantonese_func_def("睇实佢", button_bind)

def cantonese_pygame_init() -> None:
    import pygame
    from pygame.constants import KEYDOWN

    pygame.init()

    def pygame_setmode(size, caption = ""):
        if caption != "":
            pygame.display.set_caption(caption)
            return pygame.display.set_mode(size)
        return pygame.display.set_mode(size)

    def pygame_imgload(path):
        return pygame.image.load(path)

    def pygame_move(object, speed):
        return object.move(speed)

    def object_rect(object):
        return object.get_rect()

    def pygame_color(color):
        return pygame.Color(color)

    def pygame_key(e):
        return e.key

    def draw(屏幕, obj = "", obj_where = "", event = "", 颜色 = "") -> None:
        if event == "":
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
        else:
            event_map = {
                "KEYDOWN" : KEYDOWN
            }
            for events in pygame.event.get():
                for my_ev in event.stack:
                    if events.type == event_map[my_ev[0]]:
                        my_ev[1](events)
                    if events.type == pygame.QUIT: 
                        sys.exit()
        if 颜色 != "":
            屏幕.fill(颜色)
        if obj != "" and obj_where != "":
            屏幕.blit(obj, obj_where)

        pygame.time.delay(2)

    def direction(obj, dir):
        if dir == "左边" or dir == "left":
            return obj.left
        if dir == "右边" or dir == "right":
            return obj.right
        if dir == "上边" or dir == "top":
            return obj.top
        if dir == "下边" or dir == "bottom":
            return obj.bottom

    def time_tick(clock_obj, t):
        clock_obj.tick(t)

    def pygame_rectload(屏幕, 颜色, X, Y, H = 20, W = 20):
        pygame.draw.rect(屏幕, 颜色, pygame.Rect(X, Y, H, W))

    def screen_fill(screen, color):
        screen.fill(color)

    def sprite_add(group, sprite):
        group.add(sprite)

    cantonese_func_def("屏幕老作", pygame_setmode)
    cantonese_func_def("图片老作", pygame_imgload)
    cantonese_func_def("矩形老作", pygame_rectload)
    cantonese_func_def("玩跑步", pygame_move)
    cantonese_func_def("in边", object_rect)
    cantonese_func_def("上画", draw)
    cantonese_func_def("揾位", direction)
    cantonese_func_def("画公仔", pygame.sprite.Sprite.__init__)
    cantonese_func_def("公仔", pygame.sprite.Sprite)
    cantonese_func_def("公仔集", pygame.sprite.Group)
    cantonese_func_def("嚟个公仔", sprite_add)
    cantonese_func_def("计时器", pygame.time.Clock)
    cantonese_func_def("睇表", time_tick)
    cantonese_func_def("校色", pygame_color)
    cantonese_func_def("屏幕校色", screen_fill)
    cantonese_func_def("摞掣", pygame_key)
    cantonese_func_def("刷新", pygame.display.flip)

def cantonese_lib_run(lib_name : str, path : str, use_tradition : bool) -> None:
    pa = os.path.dirname(path) # Return the last file Path
    tokens = []
    code = ""
    found = False
    for dirpath,dirnames,files in os.walk(pa):
        if lib_name + '.cantonese' in files:
            code = open(pa + '/' + lib_name + '.cantonese', encoding = 'utf-8').read()
            code = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', code)
            found = True
    if found == False:
        raise ImportError(lib_name + '.cantonese not found.')
    if use_tradition:
        for token in cantonese_token(code, traditional_keywords):
            tokens.append(token)
    else:
        for token in cantonese_token(code, keywords):
            tokens.append(token)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    run(cantonese_parser.Node, path = path)


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
kw_set_assign = "埋堆"
kw_global_set = "Share下"
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
    kw_set_assign,
    kw_global_set,
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

tr_kw_print = "畀我睇下"
tr_kw_endprint = "點樣先"
tr_kw_exit = "收工"
tr_kw_in = "喺"
tr_kw_elif = "定系"
tr_kw_turtle_beg = "老作一下"
tr_kw_type = "起底"
tr_kw_assign = "講嘢"
tr_kw_class_def = "咩系"
tr_kw_else_or_not = "唔系"
tr_kw_is = "系"
tr_kw_if = "如果"
tr_kw_then = "嘅話"
tr_kw_do = "->"
tr_kw_begin = "{"
tr_kw_end = "}"
tr_kw_pass = "咩都唔做"
tr_kw_while_do = "落操場玩跑步"
tr_kw_function = "$"
tr_kw_call = "用下"
tr_kw_import = "使下"
tr_kw_func_begin = "要做咩"
tr_kw_func_end = "搞掂"
tr_kw_is_2 = "就"
tr_kw_assert = "諗下"
tr_kw_class_assign = "佢嘅"
tr_kw_while = "玩到"
tr_kw_whi_end = "為止"
tr_kw_return = "還數"
tr_kw_try = "執嘢"
tr_kw_except = "揾到"
tr_kw_finally = "執手尾"
tr_kw_raise = "掟個"
tr_kw_raise_end = "來睇下"
tr_kw_from = "從"
tr_kw_to = "行到"
tr_kw_endfor = "行曬"
tr_kw_extend = "佢個老豆叫"
tr_kw_method = "佢識得"
tr_kw_endclass = "明白未啊"
tr_kw_cmd = "落Order"
tr_kw_break = "飲茶先啦"
tr_kw_lst_assign = "拍住上"
tr_kw_set_assign = "埋堆"
tr_kw_global_set = "Share下"
tr_kw_is_3 = "係"
tr_kw_exit_1 = "辛苦曬啦"
tr_kw_exit_2 = "同我躝"
tr_kw_false = "唔啱"
tr_kw_true = "啱"
tr_kw_none = "冇"
tr_kw_stackinit = "有條仆街叫"
tr_kw_push = "頂你"
tr_kw_pop = "丟你"
tr_kw_model = "嗌"
tr_kw_mod_new = "過嚟估下"
tr_kw_class_init = "佢有啲咩"
tr_kw_self = "自己嘅"
tr_kw_call_begin = "下"
tr_kw_get_value = "@" 

traditional_keywords = (
    tr_kw_print,
    tr_kw_endprint,
    tr_kw_exit,
    tr_kw_in,
    tr_kw_elif,
    tr_kw_turtle_beg,
    tr_kw_type,
    tr_kw_assign,
    tr_kw_class_def,
    tr_kw_else_or_not,
    tr_kw_is,
    tr_kw_if,
    tr_kw_then,
    tr_kw_do,
    tr_kw_begin,
    tr_kw_end,
    tr_kw_pass,
    tr_kw_while_do,
    tr_kw_function,
    tr_kw_call,
    tr_kw_import,
    tr_kw_func_begin,
    tr_kw_func_end,
    tr_kw_is_2,
    tr_kw_assert,
    tr_kw_class_assign,
    tr_kw_while,
    tr_kw_whi_end,
    tr_kw_return,
    tr_kw_try,
    tr_kw_except,
    tr_kw_finally,
    tr_kw_raise,
    tr_kw_raise_end,
    tr_kw_from,
    tr_kw_to,
    tr_kw_endfor,
    tr_kw_extend,
    tr_kw_method,
    tr_kw_endclass,
    tr_kw_cmd,
    tr_kw_break,
    tr_kw_lst_assign,
    tr_kw_set_assign,
    tr_kw_global_set,
    tr_kw_is_3,
    tr_kw_exit_1,
    tr_kw_exit_2,
    tr_kw_false,
    tr_kw_true,
    tr_kw_none,
    tr_kw_stackinit,
    tr_kw_push,
    tr_kw_pop,
    tr_kw_model,
    tr_kw_mod_new,
    tr_kw_class_init,
    tr_kw_self,
    tr_kw_call_begin,
    tr_kw_get_value
)

dump_ast = False
dump_lex = False
to_js = False

def cantonese_run(code : str, is_to_py : bool, file : str, use_tradition : bool) -> None:
    
    global dump_ast
    global dump_lex
    
    if use_tradition:
        tokens = cantonese_token(code, traditional_keywords)
    else:
        tokens = cantonese_token(code, keywords)
    if dump_lex:
        for token in tokens:
            print("line " + str(token[0]) + ": " + str(token[1]))
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    if dump_ast:
        print(cantonese_parser.Node)
    if to_js:
        import src.Compile
        js, fh = src.Compile.Compile(cantonese_parser.Node, "js", file).ret()
        f = open(fh, 'w', encoding = 'utf-8')
        f.write(js)
        exit(1)

    run(cantonese_parser.Node, path = file)
    cantonese_lib_init()
    if is_to_py:
        print(TO_PY_CODE)
    if debug:
        import dis
        print(dis.dis(TO_PY_CODE))
    else:
        import traceback
        try:
            exec(TO_PY_CODE, variable)
        except Exception as e:
            print("濑嘢！" + "\n".join(濑啲咩嘢(e)))

class AST(object):
    def __init__(self, Nodes) -> None:
        self.Nodes = Nodes

    def next(self, n) -> None:
        self.Nodes = self.Nodes[n : ]

    def current(self):
        if len(self.Nodes) == 0:
            return [""]
        return self.Nodes[0]

    def check(self, node, v) -> bool:
        return node[0] == v

    def run_if(self):
        elif_part = [[], [], []]
        else_part = [[], []]
        if self.current()[0] == 'node_elif':
            elif_part = self.current()
            self.next(1)
        elif self.current()[0] == 'node_else':
            else_part = self.current()
            self.next(1)
        return elif_part, else_part

    def run_except(self):
        # ["node_except", _except, except_part]
        except_part = [[], [], []]
        finally_part = [[], []]
        if self.current()[0] == 'node_except':
            except_part = self.current()
            self.next(1)
        elif self.current()[0] == 'node_finally':
            except_part = self.current()
            self.next(1)
        return except_part.finally_part


    def get_node(self) -> list:
        
        if len(self.Nodes) == 0:
            return "NODE_END"

        node = self.Nodes[0]
        
        if node[0] == 'node_print':
            self.next(1)
            return PrintStmt(node[1])

        if node[0] == 'node_let':
            self.next(1)
            return AssignStmt(node[1][1], node[2])

        if node[0] == 'node_exit':
            self.next(1)
            return ExitStmt()

        if node[0] == 'node_pass':
            self.next(1)
            return PassStmt()

        if node[0] == 'node_if':
            self.next(1)
            elif_part, else_part = self.run_if()
            return IfStmt([node[1], node[2]], [elif_part[1], elif_part[2]], \
                         [else_part[1]])

        if node[0] == 'node_try':
            self.next(1)
            except_part, finally_part = self.run_except()
            return ExceptStmt([node[1]], [except_part[1], except_part[2]], \
                            [finally_part[1]])

        if node[0] == 'node_call':
            self.next(1)
            return

        if node[0] == 'node_for':
            self.next(1)
            return ForStmt(node[1], node[2], node[3])

        if node[0] == 'node_gettype':
            self.next(1)
            return TypeStmt(node[1])

        if node[0] == 'node_loop':
            self.next(1)
            return WhileStmt(node[1], node[2])

        if node[0] == 'node_break':
            self.next(1)
            return BreakStmt()

        if node[0] == 'node_raise':
            self.next(1)
            return RaiseStmt(node[1])
        

        raise Exception("睇唔明嘅Node: " + str(node))

def make_stmt(Nodes : list, stmts : list) -> list:
    ast = AST(Nodes)
    # Get stmt from AST
    while True:
        stmt = ast.get_node()
        if stmt == "NODE_END":
            break
        stmts.append(stmt)
    return stmts

class PrintStmt(object):
    def __init__(self, expr) -> None:
        self.expr = expr
        self.type = "PrintStmt"

    def __str__(self):
        ret = "print_stmt: " + self.expr

class AssignStmt(object):
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.type = "AssignStmt"
    
class PassStmt(object):
    def __init__(self):
        self.type = "PassStmt"

class ExitStmt(object):
    def __init__(self):
        self.type = "ExitStmt"

    def __str__(self):
        return "exit_stmt"

class TypeStmt(object):
    def __init__(self, var):
        self.type = "TypeStmt"
        self.var = var

class IfStmt(object):
    def __init__(self, if_stmt, elif_stmt, else_stmt) -> None:
        self.if_stmt = if_stmt
        self.elif_stmt = elif_stmt
        self.else_stmt = else_stmt
        self.type = "IfStmt"

    def __str__(self):
        ret = "if_stmt:" + str(self.if_stmt) + \
              "elif_stmt:" + str(self.elif_stmt) + \
              "else_stmt: " + str(self.else_stmt)
        return ret

class ForStmt(object):
    def __init__(self, _iter, seq, stmt) -> None:
        self._iter = _iter
        self.seq = seq
        self.stmt = stmt
        self.type = "ForStmt"

class WhileStmt(object):
    def __init__(self, cond, stmt) -> None:
        self.cond = cond
        self.stmt = stmt
        self.type = "WhileStmt"

class BreakStmt(object):
    def __init__(self):
        self.type = "BreakStmt"

class CallStmt(object):
    def __init__(self, func, args) -> None:
        self.type = "CallStmt"

class ExceptStmt(object):
    def __init__(self, try_part, except_part, finally_part) -> None:
        self.type = "ExceptStmt"
        self.try_part = try_part
        self.except_part = except_part
        self.finally_part = finally_part

class RaiseStmt(object):
    def __init__(self, exception) -> None:
        self.type = "RaiseStmt"
        self.exception = exception

ins_idx = 0 # 指令索引
cansts_idx = 0
name_idx = 0
debug = False

def cantonese_run_with_vm(code : str, file : bool, use_tradition : bool) -> None:
    tokens = []
    if use_tradition:
        for token in cantonese_token(code, traditional_keywords):
            tokens.append(token)
    else:
        for token in cantonese_token(code, keywords):
            tokens.append(token)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    if dump_ast:
        print(cantonese_parser.Node)
    if dump_lex:
        print(tokens)
    gen_op_code = []
    stmt = make_stmt(cantonese_parser.Node, [])
    run_with_vm(stmt, gen_op_code, True, path = file)
    code = Code()
    code.ins_lst = gen_op_code
    if debug:
        for j in gen_op_code:
            print(j)
    cs = CanState(code)
    cs._run()
    
def run_with_vm(stmts : list, gen_op_code, end, path = '', state = []) -> None:
    
    global ins_idx

    for stmt in stmts:
        if stmt.type == "PrintStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.expr))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_PRINT_ITEM", None))
        
        if stmt.type == "AssignStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.value))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NEW_NAME", stmt.key))

        if stmt.type == "PassStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NOP", None))

        if stmt.type == "IfStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.if_stmt[0]))
            s = make_stmt(stmt.if_stmt[1], [])
            # 先将要跳转的地址设置为None
            ins_idx += 1
            start_idx = ins_idx
            gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_FALSE", None))
            run_with_vm(s, gen_op_code, False, path)
            
            # TODO: need test elif stmt
            if stmt.elif_stmt != [[], []]:
                gen_op_code[start_idx - 1].set_args(ins_idx + 1)
                ins_idx += 1
                jmp_start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", None))
                ins_idx += 1
                gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST",  stmt.elif_stmt[0]))
                s = make_stmt(stmt.elif_stmt[1], [])
                ins_idx += 1
                start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_FALSE", None))
                run_with_vm(s, gen_op_code, False, path)
                gen_op_code[jmp_start_idx - 1].set_args(ins_idx - jmp_start_idx)

            elif stmt.else_stmt != [[]]:
                gen_op_code[start_idx - 1].set_args(ins_idx + 1)
                ins_idx += 1
                s = make_stmt(stmt.else_stmt[0], [])
                jmp_start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", None))
                run_with_vm(s, gen_op_code, False, path)
                gen_op_code[jmp_start_idx - 1].set_args(ins_idx - jmp_start_idx)

            else:
                gen_op_code[start_idx - 1].set_args(ins_idx)
        
        if stmt.type == "ForStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", 
                    stmt.seq[stmt.seq.index("(") + 1 : stmt.seq.index(",")]))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", 
                    stmt.seq[stmt.seq.index(",") + 1 : stmt.seq.index(")")]))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_CALL_FUNC", "range"))

        if stmt.type == "TypeStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.var))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_CALL_FUNC", "type"))
            

        if stmt.type == "WhileStmt":
            current_idx = ins_idx
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.cond))
            s = make_stmt(stmt.stmt, [])
            ins_idx += 1
            start_idx = ins_idx
            gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_TRUE", None))
            run_with_vm(s, gen_op_code, False, path)
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_JMP_ABSOLUTE", current_idx))
            gen_op_code[start_idx - 1].set_args(ins_idx)

        if stmt.type == "BreakStmt":
            ins_idx += 1
            # TODO: implement the break stmt
            gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", 1))

        if stmt.type == "RaiseStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_RAISE", eval(stmt.exception[1])))

    if end:
        ins_idx += 1
        gen_op_code.append(Instruction(ins_idx, "OP_RETURN", None)) # 结尾指令


class WebParser(object):
    def __init__(self, tokens : list, Node : list) -> None:
        self.tokens = tokens
        self.pos = 0
        self.Node = Node

    def get(self, offset : int) -> list:
        if self.pos + offset >= len(self.tokens):
            return ["", ""]
        return self.tokens[self.pos + offset]
        
    def match(self, name : str) -> bool:
        if self.get(0)[1] == name:
            return True
        return False
    
    def match_type(self, name : str) -> bool:
        if self.get(0)[0] == name:
            return True
        return False
    
    def check(self, a, b) -> None:
        if a == b:
            return
        raise LookupError("Error Token:" + str(b))

    def skip(self, offset) -> None:
            self.pos += offset
    
    def run(self, Nodes : list) -> None:
        for node in Nodes:
            if node[0] == "node_call":
                web_call_new(node[1][0], node[1][1], node[2])
            if node[0] == "node_css":
                style_def(node[1][0], node[1][1], node[1][2])
        
    def parse(self) -> None:
        while True:
            if self.match("老作一下"):
                self.skip(1)
                self.check(self.get(0)[1], "{")
                self.skip(1)
                stmt = []
                node_main = []
                while self.tokens[self.pos][1] != "}":
                    stmt.append(self.tokens[self.pos])
                    self.pos += 1
                self.skip(1)
                WebParser(stmt, node_main).parse()
                self.Node = node_main
                self.run(self.Node)
            elif self.match_type("id"):
                if self.get(1)[0] == "keywords" and self.get(1)[1] == "要点画":
                    id = self.get(0)[1]
                    self.skip(2)
                    style_stmt = []
                    node_style = []
                    while self.tokens[self.pos][1] != "搞掂":
                        style_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    self.cantonese_css_parser(style_stmt, id)
                else:
                    name = self.get(0)[1]
                    self.skip(1)
                    self.check(self.get(0)[1], "=>")
                    self.skip(1)
                    self.check(self.get(0)[1], "[")
                    self.skip(1)
                    args = []
                    while self.tokens[self.pos][1] != "]":
                        args.append(self.tokens[self.pos][1])
                        self.pos += 1
                    self.skip(1)
                    with_style = False
                    if self.match('$'): # case 'style_with'
                        style_id = self.get(1)[1]
                        self.skip(2)
                        args.append(style_id)
                        with_style = True
                    web_ast_new(self.Node, "node_call", [name, args], with_style)
            else:
                break

    def cantonese_css_parser(self, stmt : list, id : str) -> None:
        cssParser(stmt, []).parse(id)

class cssParser(WebParser):
    def parse(self, id : str) -> None:
        while True:
            if self.match_type("id"):
                key = self.get(0)[1]
                self.skip(1)
                self.check(self.get(0)[1], "=>")
                self.skip(1)
                self.check(self.get(0)[1], "[")
                self.skip(1)
                value = []
                while self.tokens[self.pos][1] != "]":
                    value.append(self.tokens[self.pos][1])
                    self.pos += 1
                self.skip(1)
                web_ast_new(self.Node, "node_css", [id, key, value])
            else:
                break
        self.run(self.Node)

def web_ast_new(Node : list, type : str, ctx : list, with_style = True) -> None:
    Node.append([type, ctx, with_style])

def get_str(s : str) -> str:
    return eval("str(" + s + ")")

sym = {}
style_attr = {}
style_value_attr = {}

TO_HTML = "<html>\n"

def title(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        t_beg, t_end = "<title>", "</title>\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        t_beg, t_end = "<title id = \"" + style + "\">", "</title>\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end


def h(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        h_beg, h_end = "<h1>", "</h1>\n"
        TO_HTML += h_beg + get_str(args[0]) + h_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        size = "" if len(args) == 1 else args[1]
        t_beg, t_end = "<h" + size + " id = \"" + style + "\">", "</h" + size + ">\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end

def img(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        i_beg, i_end = "<img src = ", ">\n"
        TO_HTML += i_beg + get_str(args[0]) + i_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        i_beg, i_end = "<img id = \"" + style + "\" src = ", ">\n"
        TO_HTML += i_beg + get_str(args[0]) + i_end

def audio(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        a_beg, a_end = "<audio src = ", "</audio>\n"
        TO_HTML += a_beg + get_str(args[0]) + a_end

def sym_init() -> None:
    global sym
    global style_attr

    sym['打标题'] = title
    sym['拎笔'] = h
    sym['睇下'] = img
    sym['Music'] = audio
    #sym['画格仔'] = table

    style_attr['要咩色'] = "color"
    style_attr['要咩背景颜色'] = "background-color"
    style_attr['要点对齐'] = "text-align"
    style_attr['要几高'] = 'height'
    style_attr['要几阔'] = 'width'

    style_value_attr['红色'] = "red"
    style_value_attr['黄色'] = "yellow"
    style_value_attr['白色'] = "white"
    style_value_attr['黑色'] = "black"
    style_value_attr['绿色'] = "green"
    style_value_attr['蓝色'] = "blue"
    style_value_attr['居中'] = "centre"

def head_init() -> None:
    global TO_HTML
    TO_HTML += "<head>\n"
    TO_HTML += "<meta charset=\"utf-8\" />\n"
    TO_HTML += "</head>\n"

def web_init() -> None:
    global TO_HTML
    sym_init()
    head_init()

def web_end() -> None:
    global TO_HTML
    TO_HTML += "</html>"

style_sym = {}

def style_def(id : str, key : str, value : list) -> None:
    global style_sym
    if id not in style_sym:
        style_sym[id] = [[key, value]]
        return
    style_sym[id].append([key, value])
    
def style_build(value : list) -> None:
    s = ""
    for item in value:
        if get_str(item[1][0]) not in style_value_attr.keys() and item[0] in style_attr.keys():
            s += style_attr[item[0]] + " : " + get_str(item[1][0]) + ";\n"
        elif get_str(item[1][0]) not in style_value_attr.keys() and item[0] not in style_attr.keys():
            s += item[0] + " : " + get_str(item[1][0]) + ";\n"
        elif get_str(item[1][0]) in style_value_attr.keys() and item[0] not in style_attr.keys():
            s += item[0] + " : " + style_value_attr[get_str(item[1][0])] + ";\n"
        else:
            s += style_attr[item[0]] + " : " + style_value_attr[get_str(item[1][0])] + ";\n"
    return s

def style_exec(sym : dict) -> None:
    global TO_HTML
    gen = ""
    s_beg, s_end = "\n<style type=\"text/css\">\n", "</style>\n"
    for key, value in sym.items():
        gen += "#" +  key + "{\n" + style_build(value) + "}\n"
    TO_HTML += s_beg + gen + s_end

def web_call_new(func : str, args_list : list, with_style = False) -> None:
    if func in sym:
        sym[func](args_list, with_style)
    else:
        func(args_list, with_style)

def get_html_file(name : str) -> str:
    return name[ : len(name) - len('cantonese')] + 'html'

class WebLexer(lexer):
    def __init__(self, code, keywords):
        super().__init__(code, keywords)
        self.re_callfunc, self.re_expr, self.op,\
        self.op_get_code, self.op_gen_code, \
        self.build_in_funcs, self.bif_get_code, \
        self.bif_gen_code = "", "", "", "", "", "", "", ""
    
    def get_token(self):
        self.skip_space()

        if len(self.code) == 0:
            return ['EOF', 'EOF']

        c = self.code[0]
        if self.isChinese(c) or c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return ['keywords', token]
            return ['id', token]

        if c == '=':
            if self.check("=>"):
                self.next(2)
                return ['keywords', "=>"]

        if c in ('\'', '"'):
            return ['string', self.scan_short_string()]
        
        if c == '.' or c.isdigit():
            token = self.scan_number()
            return ['num', token]

        if c == '{':
            self.next(1)
            return ["keywords", c]

        if c == '}':
            self.next(1)
            return ["keywords", c]

        if c == '[':
            self.next(1)
            return ["keywords", c]

        if c == ']':
            self.next(1)
            return ["keywords", c]

        if c == '$':
            self.next(1)
            return ["keywords", c]

        if c == '(':
            self.next(1)
            return ["keywords", c]
        
        if c == ')':
            self.next(1)
            return ["keywords", c]

        self.error("睇唔明嘅Token: " + c)

def cantonese_web_run(code : str, file_name : str, open_serv = True) -> None:
    global TO_HTML
    keywords = ("老作一下", "要点画", "搞掂", "执嘢")
    lex = WebLexer(code, keywords)
    tokens = []
    while True:
        token = lex.get_token()
        tokens.append(token)
        if token == ['EOF', 'EOF']:
            break
    
    web_init()
    WebParser(tokens, []).parse()
    web_end()
        
    if style_sym != {}:
        style_exec(style_sym)
    print(TO_HTML)

    if open_serv:
        import socket
        ip_port = ('127.0.0.1', 80)
        back_log = 10
        buffer_size = 1024
        webserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        webserver.bind(ip_port)
        webserver.listen(back_log)
        print("Cantonese Web Starting at 127.0.0.1:80 ...")
        while True:
            conn, addr = webserver.accept()
            recvdata = conn.recv(buffer_size)
            conn.sendall(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
            conn.sendall(bytes(TO_HTML, "utf-8"))
            conn.close()
            if input("input Y to exit:"):
                print("Cantonese Web exiting...")
                break
    
    else:
        f = open(get_html_file(file_name), 'w', encoding = 'utf-8')
        f.write(TO_HTML)
    exit(0)

class AsmLerxer(lexer):
    def __init__(self, code, keywords, ins):
        super().__init__(code, keywords)
        self.ins = ins
        self.op, self.op_get_code, self.op_gen_code, \
        self.build_in_funcs, self.re_callfunc, self.bif_get_code, \
        self.bif_gen_code = "", "", "", "", "", "", ""
        self.re_register = r"[(](.*?)[)]"

    def scan_register(self):
        return self.scan(self.re_register)

    def get_token(self):
        # TODO
        self.skip_space()
        if len(self.code) == 0:
            return [self.line, ['EOF', 'EOF']]
        
        c = self.code[0]

        if c == '|':
           token = self.scan_expr()
           return [self.line, ['expr', token]]

        if c == '(':
            token = self.scan_register()
            return [self.line, ['register', token]]
        
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
            if token in self.ins:
                return [self.line, ['ins', token]]
            return [self.line, ['identifier', token]]
        
        if c in ('\'', '"'):
            return [self.line, ['string', self.scan_short_string()]]
        
        if c == '.' or c.isdigit():
            token = self.scan_number()
            return [self.line, ['num', token]]

        if c == '-':
            if self.check('->'):
                self.next(2)
                return [self.line, ['keyword', '->']]
        
        self.error("睇唔明嘅Token: " + c)

TO_ASM = ""

class AsmParser(object):
    def __init__(self, tokens : list, Node : list) -> None:
        self.tokens = tokens
        self.pos = 0
        self.Node = Node

    def get(self, offset : int) -> list:
        if self.pos + offset >= len(self.tokens):
            return [None, ["", ""]]
        return self.tokens[self.pos + offset]
        
    def match(self, name : str) -> bool:
        if self.get(0)[1][1] == name:
            return True
        return False
    
    def match_type(self, name : str) -> bool:
        if self.get(0)[1][0] == name:
            return True
        return False
    
    def check(self, a, b) -> None:
        if a == b:
            return
        raise LookupError("Error Token:" + str(b))

    def skip(self, offset) -> None:
            self.pos += offset

    def get_value(self, token):
        if token[1][0] == 'expr':
            # If is expr, Remove the "|"
            token[1][1] = token[1][1][1 : -1]
        if token[1][0] == 'register':
            token[1][1] = token[1][1][1 : -1]
        return token[1][1]

    def run(self, Nodes) -> None:
        global TO_ASM
        for node in Nodes:
            if node[0] == 'node_data':
                TO_ASM += "section .data\n"
                for d in node[1]:
                    TO_ASM += d[0] + " equ " + d[1] + "\n"

            if node[0] == 'node_mov':
                TO_ASM += "mov " + node[1][0] + ", " + node[1][1] + "\n"

            if node[0] == 'node_int':
                TO_ASM += "int " + node[1][0] + "\n"

            if node[0] == 'node_global':
                TO_ASM += "global " + node[1][0] + "\n"

            if node[0] == 'node_code':
                TO_ASM += node[1][0] + ":\n"
                self.run(node[1][1])

    def parse(self) -> None:
        while True:
            if self.match_type('expr'):
                if self.get(1)[1][1] == "有咩":
                    data_name = self.get(0)[1]
                    self.skip(4)
                    data_stmt = []
                    while self.tokens[self.pos][1][1] != "}":
                        data_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    ret = self.data_parse(data_stmt, data_name)
                    asm_ast_new(self.Node, "node_data", ret)
            
                if self.get(1)[1][1] == "要做咩":
                    code_name = self.get_value(self.get(0))
                    self.skip(4)
                    code_stmt = []
                    while self.tokens[self.pos][1][1] != "}":
                        code_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    stmt_node = []
                    AsmParser(code_stmt, stmt_node).parse()
                    asm_ast_new(self.Node, "node_code", [code_name, stmt_node])

                if self.get(1)[1][1] == "排头位":
                    start_name = self.get_value(self.get(0))
                    self.skip(4)
                    asm_ast_new(self.Node, "node_global", [start_name])

            elif self.match_type('register'):
                reg = self.get_value(self.get(0))
                self.skip(1)
                if self.get(0)[1][1] == "收数":
                    self.skip(2)
                    data = self.get_value(self.get(0))
                    asm_ast_new(self.Node, 'node_mov', [reg, data])
                    self.skip(1)
            
            elif self.match("仲要等埋"):
                self.skip(2)
                addr = self.get_value(self.get(0))
                asm_ast_new(self.Node, 'node_int', [addr])
                self.skip(1)

            else:
                break

    def data_parse(self, stmt, name) -> None:
        return dataParser(stmt, []).parse(name)
        
class dataParser(AsmParser):
    def parse(self, name) -> None:
        ret = []
        while True:
            if self.match_type("identifier"):
                key = self.get_value(self.get(0))
                self.skip(1)
                self.check(self.get(0)[1][1], "係")
                self.skip(1)
                val = self.get_value(self.get(0))
                self.skip(1)
                ret.append([key, val])
            else:
                break
        return ret

def asm_ast_new(Node : list, type : str, ctx : list) -> None:
    Node.append([type, ctx])


def Cantonese_asm_run(code : str, file_name : str) -> None:
    global TO_ASM

    ins_mov_from = "收数"
    ins_int = "仲要等埋"
    kw_datadef = "有咩"
    kw_secdef = "要做咩"
    kw_is = "係"
    kw_main = "排头位"
    kw_begin = "开工"

    keywords = (kw_datadef, kw_secdef,
            kw_is, kw_main, kw_begin)
    ins = (ins_mov_from, ins_int)
    lex = AsmLerxer(code, keywords, ins)
    tokens = []

    while True:
        token = lex.get_token()
        tokens.append(token)
        if token[1] == ['EOF', 'EOF']:
            break

    AST = []
    AsmParser(tokens, AST).parse()
    AsmParser(tokens, AST).run(AST)
    print(TO_ASM)
    exit(1)

class 交互(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = '> '

    def default(self, code):
        if code is not None:
            cantonese_run(code, False, '【标准输入】', False)


def 开始交互():
    交互().cmdloop("早晨！")

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", nargs = '?', default = "")
    arg_parser.add_argument("-to_py", action = "store_true")
    arg_parser.add_argument("-to_js", action = "store_true")
    arg_parser.add_argument("-to_asm", action = "store_true")
    arg_parser.add_argument("-讲翻py", action = "store_true")
    arg_parser.add_argument("-to_web", action = "store_true")
    arg_parser.add_argument("-倾偈", action = "store_true")
    arg_parser.add_argument("-compile", action = "store_true")
    arg_parser.add_argument("-讲白啲", action = "store_true")
    arg_parser.add_argument("-use_tr", action = "store_true")
    arg_parser.add_argument("-install", action = "store_true")
    arg_parser.add_argument("-stack_vm", action = "store_true")
    arg_parser.add_argument("-ast", action = "store_true")
    arg_parser.add_argument("-lex", action = "store_true")
    arg_parser.add_argument("-debug", action = "store_true")
    arg_parser.add_argument("-v", action = "store_true")
    args = arg_parser.parse_args()

    global use_tradition
    global dump_ast
    global dump_lex
    global to_js
    global debug

    if args.v:
        print("0.0.7")
        exit(1)

    if not args.file:
        sys.exit(开始交互())

    try:
        with open(args.file, encoding = "utf-8") as f:
            code = f.read()
            # Skip the comment
            code = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', code)
            is_to_py = False
            if args.to_py or args.讲翻py:
                is_to_py = True
            if args.use_tr:
                use_tradition = True
            if args.install:
                import urllib.request
                print("Installing ... ")
                # TODO: Insatll the cantonese library
                #urllib.request.urlretrieve()
                print("Successful installed!")
                exit()
            if args.to_web or args.倾偈:
                if args.compile or args.讲白啲:
                    cantonese_web_run(code, args.file, False)
                else:
                    cantonese_web_run(code, args.file, True)
            if args.ast:
                dump_ast = True
            if args.lex:
                dump_lex = True
            if args.debug:
                debug = True
            if args.stack_vm:
                cantonese_run_with_vm(code, args.file, use_tradition)
                exit(1)
            if args.to_js:
                to_js = True
            if args.to_asm:
                Cantonese_asm_run(code, args.file)
            cantonese_run(code, is_to_py, args.file, use_tradition)
    except FileNotFoundError:
        print("濑嘢!: 揾唔到你嘅文件 :(")

if __name__ == '__main__':
    main()
