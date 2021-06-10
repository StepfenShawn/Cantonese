"""
    Created at 2021/1/16 16:23
    Last update at 2021/6/6 9:11
    The interpret for Cantonese    
"""
import re
import sys
import io
import os

from pygame.constants import KEYDOWN

"""
    Get the Cantonese Token List
"""
def cantonese_token(code : str) -> list:
    keywords = r'(?P<keywords>(畀我睇下){1}|(点样先){1}|(收工){1}|(喺){1}|(定){1}|(老作一下){1}|(起底){1}|' \
               r'(讲嘢){1}|(咩系){1}|(唔系){1}|(系){1})|(如果){1}|(嘅话){1}|(->){1}|({){1}|(}){1}|(同埋){1}|(咩都唔做){1}|' \
               r'(落操场玩跑步){1}|(\$){1}|(用下){1}|(使下){1}|(要做咩){1}|(搞掂){1}|(就){1}|(谂下){1}|(佢嘅){1}|' \
               r'(玩到){1}|(为止){1}|(返转头){1}|(执嘢){1}|(揾到){1}|(执手尾){1}|(掟个){1}|(来睇下){1}|' \
               r'(从){1}|(行到){1}|(行晒){1}|(佢个老豆叫){1}|(佢识得){1}|(明白未啊){1}|(落Order){1}|(饮茶先啦){1}|' \
               r'(拍住上){1}|(係){1}|(比唔上){1}|(或者){1}|(辛苦晒啦){1}|(同我躝)|(唔啱){1}|(啱){1}|(冇){1}|' \
               r'(有条仆街叫){1}|(顶你){1}|(丢你){1}|(嗌){1}|(过嚟估下){1}|(佢有啲咩){1}|(自己嘅){1}|(下){1}|(\@){1}'
    kw_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), keywords[13 : ])
    keywords_gen_code = ["print", "endprint", "exit", "in", "or", "turtle_begin", "gettype", 
                         "assign", "class", "is not", "is", "if", "then", "do", "begin", "end", "and", "pass",     
                         "while_do", "$", "call", "import", "funcbegin", "funcend", "is", "assert", "assign", 
                         "while", "whi_end", "return", "try", "except", "finally", "raise", "endraise",
                         "from", "to", "endfor", "extend", "method", "endclass", "cmd", "break", "ass_list", "is",
                         "<", "or", "exit", "exit", "False", "True", "None", "stackinit", "push", "pop", "model", 
                         "mod_new", "class_init", "self.", "call_begin", "get_value"
            ]
    num = r'(?P<num>\d+)'
    ID =  r'(?P<ID>[a-zA-Z_][a-zA-Z_0-9]*)'
    op = r'(?P<op>(相加){1}|(加){1}|(减){1}|(乘){1}|(整除){1}|(除){1}|(余){1}|(异或){1}|(取反){1}|(左移){1}|(右移){1}'\
         r'(与){1}|(或){1})'
    op_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), op[5 : ])
    op_gen_code = ["矩阵.matrix_addition", "+", "-", "*", "//", "/", "%", "^", "~", "<<", ">>",
            "&", "|"]
    string = r'(?P<string>\"([^\\\"]|\\.)*\")'
    expr = r'(?P<expr>[|](.*?)[|])'
    callfunc = r'(?P<callfunc>[&](.*?)[)])'
    build_in_funcs = r'(?P<build_in_funcs>(瞓){1}|(加啲){1}|(摞走){1}|(嘅长度){1}|(阵先){1}|' \
                     r'(畀你){1}|(散水){1})'
    bif_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), build_in_funcs[19 :])
    bif_gen_code = ["sleep", "append", "remove", ".__len__()", "2", "input", "clear"]
    patterns = re.compile('|'.join([keywords, ID, num, string, expr, callfunc, build_in_funcs, op]))

    def make_rep(list1 : list, list2 : list) -> list:
        assert len(list1) == len(list2)
        ret = []
        for i in range(len(list1)):
            ret.append([list1[i], list2[i]])
        return ret

    def trans(lastgroup : str, code : str, rep : str) -> str:
        if lastgroup != 'string' and lastgroup != 'ID':
            if lastgroup == 'expr':
                p = re.match(r'\|(.*)同(.*)有几衬\|', code, re.M|re.I)
                if p:
                    code = " corr(" + p.group(1) +", " + p.group(2) + ") "
            for r in rep:
                code = code.replace(r[0], r[1])
        return code
    for match in re.finditer(patterns, code):
        group = match.group()
        group = trans(match.lastgroup, group, make_rep(kw_get_code, keywords_gen_code))
        group = trans(match.lastgroup, group, make_rep(bif_get_code, bif_gen_code))
        group = trans(match.lastgroup, group, make_rep(op_get_code, op_gen_code))
        yield [match.lastgroup, group]

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

    def get(self, offset):
        if self.pos + offset >= len(self.tokens):
            return ["", ""]
        return self.tokens[self.pos + offset]
    
    def get_value(self, token):
        if token[0] == 'expr':
            # If is expr, Remove the "|"
            token[1] = token[1][1 : -1]
        if token[0] == 'callfunc':
            # If is call func, Remove the '&'
            token[1] = token[1][1 :]
        return token

    def last(self, offset):
        return self.tokens[self.pos - offset]
    
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

    # TODO: Add error check
    def parse(self):
        while True:
            if self.match("print"):
                node_print_new(self.Node, self.get_value(self.get(0)))
                self.skip(2) # Skip the args and end_print

            elif self.match("sleep"):
                node_sleep_new(self.Node, self.get(0))
                self.skip(1)

            elif self.match("exit"):
                node_exit_new(self.Node)
                self.skip(1)

            elif self.match("assign") and self.get(1)[1] == 'is':
                node_let_new(self.Node, self.get_value(self.get(0)), self.get_value(self.get(2)))
                self.skip(3)
            
            elif self.match("if"):
                cond = self.get_value(self.get(0))
                self.skip(4) # Skip the "then", "do", "begin"
                if_case_end = 0 # The times of case "end"
                if_should_end = 1
                node_if = []
                stmt_if = []
                while if_case_end != if_should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == "if":
                        if_should_end += 1
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == "end":
                        if_case_end += 1
                        if if_case_end != if_should_end:
                            stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == "or" and self.get(1)[1] == "is":
                        if_should_end += 1
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                    else:
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_if, node_if).parse()
                node_if_new(self.Node, cond, node_if)
            
            elif self.match("or") and self.match("is"): # case "定系" elif
                cond = self.get_value(self.get(0))
                self.skip(4) # Skip the "then", "do", "begin"
                elif_case_end = 0 # The times of case "end"
                elif_should_end = 1
                node_elif = []
                stmt_elif = []
                while elif_case_end != elif_should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == "if":
                        elif_should_end += 1
                        stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == "end":
                        elif_case_end += 1
                        if elif_case_end != elif_should_end:
                            stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == "or" and self.get(1)[1] == "is":
                        elif_should_end += 1
                        stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                    else:
                        stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_elif, node_elif).parse()
                node_elif_new(self.Node, cond, node_elif)

            elif self.match("is not"): # case "唔系" else
                self.skip(3) # Skip the "then", "do", "begin"
                else_case_end = 0 # The times of case "end"
                else_should_end = 1
                node_else = []
                stmt_else = []
                while else_case_end != else_should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == "if":
                        else_should_end += 1
                        stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == "end":
                        else_case_end += 1
                        if else_case_end != else_should_end:
                            stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                    elif self.get(0)[1] == "or" and self.get(1)[1] == "is":
                        else_should_end += 1
                        stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                    else:
                        stmt_else.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_else, node_else).parse()
                node_else_new(self.Node, node_else)

            elif self.match("while_do"):
                stmt = []
                while self.tokens[self.pos][1] != "while":
                    stmt.append(self.tokens[self.pos])
                    self.pos += 1
                node_while = []
                self.skip(1)
                cond = self.get_value(self.get(0))
                Parser(stmt, node_while).parse()
                node_loop_new(self.Node, cond, node_while)
                self.skip(2) # Skip the "end"
            
            elif self.match("$"): # Case "function"
                if self.get(1)[0] == 'expr':
                   func_name = self.get_value(self.get(0))
                   args = self.get_value(self.get(1))
                   self.skip(3)
                   func_stmt = []
                   while self.tokens[self.pos][1] != "funcend":
                       func_stmt.append(self.tokens[self.pos])
                       self.pos += 1
                   node_func = []
                   Parser(func_stmt, node_func).parse()
                   node_func_new(self.Node, func_name, args, node_func)
                   self.skip(1) # Skip the funcend
                else:
                    func_name = self.get_value(self.get(0))
                    self.skip(2) # Skip the funcbegin
                    func_stmt = []
                    while self.tokens[self.pos][1] != "funcend":
                        func_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    node_func = []
                    Parser(func_stmt, node_func).parse()
                    node_func_new(self.Node, func_name, "None", node_func)
                    self.skip(1) # Skip the funcend
            
            elif self.match("turtle_begin"):
                self.skip(2) # Skip the "do", "begin"
                turtle_inst = []
                while self.tokens[self.pos][1] != "end":
                    turtle_inst.append(self.get_value(self.tokens[self.pos])[1])
                    self.pos += 1
                node_turtle_new(self.Node, turtle_inst)
                self.skip(1)
            
            elif self.match("call"):
                node_call_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match("import"):
                node_import_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match_type("expr") or self.match_type("ID"):
                if self.match("from"):
                    iterating_var = self.get_value(self.get(-2))
                    seq = "(" + str(self.get_value(self.get(0))[1]) + "," \
                          + str(self.get_value(self.get(2))[1]) + ")"
                    self.skip(3)
                    node_for = []
                    for_stmt = []
                    for_case_end = 0
                    for_should_end = 1
                    while for_should_end != for_case_end and self.pos < len(self.tokens):
                        if (self.get(0)[0] == "expr" or self.get(0)[0] == "ID") \
                             and self.get(1)[1] == "from":
                            for_should_end += 1
                            for_stmt.append(self.tokens[self.pos])
                            self.pos += 1
                        elif self.get(0)[1] == "endfor":
                            for_case_end += 1
                            if for_case_end != for_should_end:
                                for_stmt.append(self.tokens[self.pos])
                            self.pos += 1
                        else:
                            for_stmt.append(self.tokens[self.pos])
                            self.pos += 1
                    Parser(for_stmt, node_for).parse()
                    node_for_new(self.Node, iterating_var, seq, node_for)
                if self.get(0)[1] == "ass_list":
                    self.skip(1)
                    list = self.get_value(self.get(-2))
                    name = self.get_value(self.get(1))
                    node_list_new(self.Node, name, list)
                    self.skip(2)
                    
                if self.get(0)[1] == 'do':
                    self.skip(1)
                    id = self.get_value(self.get(-2))
                    args = self.get_value(self.get(1))
                    func = self.get_value(self.get(0))
                    node_build_in_func_call_new(self.Node, id, func, args)
                    self.skip(2)
                if self.get(0)[1] == 'call_begin':
                    func_name = self.get_value(self.get(-1))
                    self.skip(2)
                    args = self.get_value(self.get(0))
                    cons = ['expr', func_name[1] + '(' + args[1] + ')']
                    self.skip(1)
                    if self.get(0)[1] == "@":
                        self.skip(1)
                        v = self.get_value(self.get(0))
                        node_let_new(self.Node, v, cons)
                    else:
                        node_call_new(self.Node, cons)

            elif self.match("return"):
                node_return_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match("try"):
                self.skip(2) # SKip the "begin, do"
                should_end = 1
                case_end = 0
                node_try = []
                stmt_try = []
                while case_end != should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == "end":
                        case_end += 1
                        self.pos += 1
                    else:
                        stmt_try.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_try, node_try).parse()
                node_try_new(self.Node, node_try)
            
            elif self.match("except"):
                _except = self.get_value(self.get(0))
                self.skip(4) # SKip the "except", "then", "begin", "do"
                should_end = 1
                case_end = 0
                node_except = []
                stmt_except = []
                while case_end != should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == "end":
                        case_end += 1
                        self.pos += 1
                    else:
                        stmt_except.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_except, node_except).parse()
                node_except_new(self.Node, _except , node_except)

            elif self.match("finally"):
                self.skip(2) # Skip the "begin", "do"
                should_end = 1
                case_end = 0
                node_finally = []
                stmt_finally = []
                while case_end != should_end and self.pos < len(self.tokens):
                    if self.get(0)[1] == "end":
                        case_end += 1
                        self.pos += 1
                    else:
                        stmt_finally.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_finally, node_finally).parse()
                node_finally_new(self.Node, node_finally)

            elif self.match("assert"):
                node_assert_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match("raise"):
                node_raise_new(self.Node, self.get_value(self.get(0)))
                self.skip(2)
            
            elif self.match("gettype"):
                node_gettype_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)
            
            elif self.match("pass"):
                self.Node.append(["node_pass"])
            
            elif self.match("break"):
                node_break_new(self.Node)
            
            elif self.match("class"):
                class_name = self.get_value(self.get(0))
                self.skip(1)
                if self.match("extend"):
                    extend = self.get_value(self.get(0))
                    self.skip(1)
                class_stmt = []
                node_class = []
                while self.tokens[self.pos][1] != "endclass":
                    class_stmt.append(self.tokens[self.pos])
                    self.pos += 1
                Parser(class_stmt, node_class).parse()
                self.skip(1) # Skip the "end"
                node_class_new(self.Node, class_name, extend, node_class)

            elif self.match("class_init"):
                self.skip(1)
                attr_lst = self.get_value(self.get(0))
                self.skip(1)
                node_attribute_new(self.Node, attr_lst)
            
            elif self.match("method"):
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
                    if self.get(0)[1] == "end":
                        method_case_end += 1
                        if method_case_end != method_should_end:
                            method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    elif self.get(0)[1] == "if":
                        method_should_end += 1
                        method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    elif self.get(0)[1] == "or" and self.get(1)[1] == "is":
                        method_should_end += 1
                        method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    elif self.get(0)[1] == "is not":
                        method_should_end += 1
                        method_stmt.append(self.tokens[self.pos])    
                        self.pos += 1
                    else:
                        method_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(method_stmt, node_method).parse()
                node_method_new(self.Node, method_name, args, node_method)
            
            elif self.match("cmd"):
                node_cmd_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)

            elif self.match("model"):
                model = self.get_value(self.get(0))
                self.skip(1)
                self.syntax_check("mod_new", "value")
                self.skip(2)
                datatest = self.get_value(self.get(0))
                self.skip(1)
                node_model_new(self.Node, model, datatest)
            
            elif self.match("stackinit"):
                node_stack_new(self.Node, self.get_value(self.get(0)))
                self.skip(1)

            elif self.match("push"):
                self.syntax_check("do", "value")
                self.skip(1)
                self.Node.append(["stack_push", self.get_value(self.get(0)), self.get_value(self.\
                    get(1))])
                self.skip(2)
            
            elif self.match("pop"):
                self.syntax_check("do", "value")
                self.skip(1)
                self.Node.append(["stack_pop", self.get_value(self.get(0)), self.get_value(self.\
                    get(1))])
                self.skip(1)

            else:
                break

variable = {}
TO_PY_CODE = ""
 
def run(Nodes : list, TAB = '', label = '', path = '') -> None:
    def check(tab):
        if label != 'whi_run' and label != 'if_run' and label != 'else_run' and  \
            label != 'elif_run' and label != "func_run" and label != "try_run" and \
            label != "except_run" and label != "finally_run" and label != "for_run" and \
            label != "class_run" and label != "method_run":
            tab = ''
    global TO_PY_CODE
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
                cantonese_lib_run(node[1][1], path)
            else:
                TO_PY_CODE += TAB + "import " + node[1][1] + "\n"

        if node[0] == "node_exit":
            check(TAB)
            TO_PY_CODE += TAB + "exit()\n"
        
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
    if name == "random":
        cantonese_random_init()
    elif name == "datetime":
        cantonese_datetime_init()
    elif name == "math":
        cantonese_math_init()
    elif name == "smtplib":
        cantonese_smtplib_init()
    elif name == "xml":
        cantonese_xml_init()
    elif name == "csv":
        cantonese_csv_init()
    elif name == "os":
        pass
    elif name == "re":
        cantonese_re_init()
    elif name == "urllib":
        cantonese_urllib_init()
    elif name == "requests":
        cantonese_requests_init()
    elif name == "socket":
        cantonese_socket_init()
    elif name == "kivy":
        cantonese_kivy_init()
    elif name == "pygame":
        cantonese_pygame_init()
    elif name == "json":
        cantonese_json_init()
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
        except SMTPException:
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
    if model == "L_REG":
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
        pygame.display.flip()

    def direction(obj, dir):
        if dir == "左边" or dir == "left":
            return obj.left
        if dir == "右边" or dir == "right":
            return obj.right
        if dir == "上边" or dir == "top":
            return obj.top
        if dir == "call_begin边" or dir == "bottom":
            return obj.bottom

    cantonese_func_def("屏幕老作", pygame_setmode)
    cantonese_func_def("图片老作", pygame_imgload)
    cantonese_func_def("玩跑步", pygame_move)
    cantonese_func_def("in边", object_rect)
    cantonese_func_def("上画", draw)
    cantonese_func_def("揾位", direction)
    cantonese_func_def("画公仔", pygame.sprite.Sprite.__init__)
    cantonese_func_def("公仔", pygame.sprite.Sprite)
    cantonese_func_def("校色", pygame_color)
    cantonese_func_def("摞掣", pygame_key)

def cantonese_lib_run(lib_name : str, path : str) -> None:
    pa = os.path.dirname(path) # Return the last file Path
    tokens = []
    code = ""
    found = False
    for dirpath,dirnames,files in os.walk(pa):
        if lib_name + '.cantonese' in files:
            code = open(pa + '/' + lib_name + '.cantonese', encoding = 'utf-8').read()
            found = True
    if found == False:
        raise ImportError(lib_name + '.cantonese not found.') 
    for token in cantonese_token(code):
        tokens.append(token)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    run(cantonese_parser.Node, path = path)

def cantonese_run(code : str, is_to_py : bool, file : str) -> None:
    tokens = []
    for token in cantonese_token(code):
        tokens.append(token)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    run(cantonese_parser.Node, path = file)
    cantonese_lib_init()
    if is_to_py:
        print(TO_PY_CODE)
    else:
        import traceback
        try:
            exec(TO_PY_CODE, variable)
        except Exception as e:
            print("濑嘢: " + repr(e) + "!")

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
                self.check(self.get(0)[1], "系")
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

def img(args : list) -> None:
    global TO_HTML
    i_beg, i_end = "<img src = ", ">\n"
    TO_HTML += i_beg + eval("str(" + args[0] + ")") + i_end

def sym_init() -> None:
    global sym
    global style_attr

    sym['写标题'] = title
    sym['写隻字'] = h
    sym['睇下'] = img
    #sym['画表格'] = table

    style_attr['颜色'] = "color"
    style_attr['背景颜色'] = "background-color"
    style_attr['对齐方式'] = "text-align"

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
            s += style_attr[item[0]] + " : " + get_str(item[1][0]) + "\n"
        elif get_str(item[1][0]) not in style_value_attr.keys() and item[0] not in style_attr.keys():
            s += item[0] + " : " + get_str(item[1][0]) + "\n"
        elif get_str(item[1][0]) in style_value_attr.keys() and item[0] not in style_attr.keys():
            s += item[0] + " : " + style_value_attr[get_str(item[1][0])] + "\n"
        else:
            s += style_attr[item[0]] + " : " + style_value_attr[get_str(item[1][0])] + "\n"
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

def cantonese_web_run(code : str, file_name : str, open_serv = True) -> None:
    global TO_HTML
    keywords = r'(?P<keywords>(老作一下){1}|({){1}|(}){1}|(=>){1}|(\[){1}|(\]){1}|(要点画){1}|(搞掂){1}|' \
               r'(系){1}|(用下){1}|(->){1}|(\$){1})'
    num = r'(?P<num>\d+)'
    string = r'(?P<string>\"([^\\\"]|\\.)*\")'
    id = r'(?P<id>([\u4e00-\u9fa5]+){1}|([a-zA-Z_][a-zA-Z_0-9]*){1})'
    patterns = re.compile('|'.join([keywords, string, num, id]))
    tokens = []
    for match in re.finditer(patterns, code):
        tokens.append([match.lastgroup, match.group()])
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

def main():
    try:
        if len(sys.argv) > 1:
            """
                install the cantonese library
            """
            if sys.argv[1] == '-install':
                import urllib.request
                print("Installing ... ")
                urllib.request.urlretrieve(sys.argv[2], sys.argv[3])
                print("Successful installed!")
                exit()
            with open(sys.argv[1], encoding = "utf-8") as f:
                code = f.read()
                # Skip the comment
                code = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', code)
                is_to_py = False
                # TODO: Use argparse library
                if len(sys.argv) >= 3:
                    if sys.argv[2] == "-to_py" or sys.argv[2] == "-讲翻py":
                        is_to_py = True
                    if sys.argv[2] == "-to_web" or sys.argv[2] == "-倾偈":
                        if len(sys.argv) > 3 and (sys.argv[3] == "-compile" or sys.argv[3] == "-讲白啲"):
                            cantonese_web_run(code, sys.argv[1], False)
                        else:
                            cantonese_web_run(code, sys.argv[1])
                cantonese_run(code, is_to_py, sys.argv[1])
        else:
            print("你想点啊? (请输入你嘅文件)")
    except FileNotFoundError:
        print("揾唔到你嘅文件 :(")

if __name__ == '__main__':
    main()