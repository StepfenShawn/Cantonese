import re
import sys

def cantonese_token(code):
    keywords = r'(?P<keywords>(畀我睇下){1}|(点样先){1}|(收工){1}|(喺){1}|(定){1}|(老作一下){1}|(起底){1}|' \
               r'(讲嘢){1}|(唔系){1}|(系){1})|(如果){1}|(嘅话){1}|(->){1}|({){1}|(}){1}|(同埋){1}|(咩都唔做){1}|' \
               r'(落操场玩跑步){1}|(\$){1}|(用下){1}|(使下){1}|(要做咩){1}|(搞掂){1}|(就){1}|(谂下){1}|(佢嘅){1}|' \
               r'(玩到){1}|(为止){1}|(返转头){1}|(执嘢){1}|(揾到){1}|(执手尾){1}|(掟个){1}|(来睇下){1}|' \
               r'(从){1}|(行到){1}|(行晒){1}|(咩系){1}|(佢个老豆叫){1}|(佢识得){1}|(明白未啊){1}|(落Order){1}|' \
               r'(拍住上){1}|(係){1}|(比唔上){1}|(或者){1}|(辛苦晒啦){1}|(同我躝)|(唔啱){1}|(啱){1}|(冇){1}|' \
               r'(有条扑街叫){1}|(顶你){1}|(丢你){1}|(嗌){1}|(过嚟估下){1}'
    kw_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), keywords[13 : ])
    keywords_gen_code = ["print", "endprint", "exit", "in", "or", "turtle_begin", "gettype", 
                         "assign", "is not", "is", "if", "then", "do", "begin", "end", "and", "pass",     
                         "while_do", "$", "call", "import", "funcbegin", "funcend", "is", "assert", "assign", 
                         "while", "whi_end", "return", "try", "except", "finally", "raise", "endraise",
                         "from", "to", "endfor", "class", "extend", "method", "endclass", "cmd", "ass_list", "is",
                         "<", "or", "exit", "exit", "False", "True", "None", "stackinit", "push", "pop", "model", "mod_new"
            ]
    num = r'(?P<num>\d+)'
    ID =  r'(?P<ID>[a-zA-Z_][a-zA-Z_0-9]*)'
    op = r'(?P<op>(加){1}|(减){1}|(乘){1}|(整除){1}|(除){1}|(余){1})'
    op_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), op[5 : ])
    op_gen_code = ["+", "-", "*", "//", "/", "%"]
    string = r'(?P<string>\"([^\\\"]|\\.)*\")'
    expr = r'(?P<expr>[|](.*?)[|])'
    callfunc = r'(?P<callfunc>[&](.*?)[)])'
    build_in_funcs = r'(?P<build_in_funcs>(瞓){1}|(加啲){1}|(摞走){1}|(嘅长度){1}|(阵先){1}|' \
                     r'(畀你){1}|(散水){1})'
    bif_get_code = re.findall(re.compile(r'[(](.*?)[)]', re.S), build_in_funcs[19 :])
    bif_gen_code = ["sleep", "append", "remove", ".__len__()", "2", "input", "clear"]
    patterns = re.compile('|'.join([keywords, ID, num, string, expr, callfunc, build_in_funcs, op]))

    def make_rep(list1, list2):
        assert len(list1) == len(list2)
        ret = []
        for i in range(len(list1)):
            ret.append([list1[i], list2[i]])
        return ret

    def trans(lastgroup, code, rep):
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
    
def node_print_new(Node, arg):
    Node.append(["node_print", arg])

def node_sleep_new(Node, arg):
    Node.append(["node_sleep", arg])

def node_exit_new(Node):
    Node.append(["node_exit"])

def node_let_new(Node, key ,value):
    Node.append(["node_let", key, value])

def node_if_new(Node, cond, stmt):
    Node.append(["node_if", cond, stmt])

def node_elif_new(Node, cond, stmt):
    Node.append(["node_elif", cond, stmt])

def node_else_new(Node, stmt):
    Node.append(["node_else", stmt])

def node_loop_new(Node, cond, stmt):
    Node.append(["node_loop", cond, stmt])

def node_func_new(Node, func_name, args, body):
    Node.append(["node_fundef", func_name, args, body])

# TODO: Add args
def node_call_new(Node, func_name):
    Node.append(["node_call", func_name])

def node_build_in_func_call_new(Node, var, func_name, args):
    Node.append(["node_bcall", var, func_name, args])

def node_import_new(Node, name):
    Node.append(["node_import", name])

def node_return_new(Node, v):
    Node.append(["node_return", v])

def node_try_new(Node, try_part):
    Node.append(["node_try", try_part])

def node_except_new(Node, _except, except_part):
    Node.append(["node_except", _except, except_part])

def node_finally_new(Node, finally_part):
    Node.append(["node_finally", finally_part])

def node_raise_new(Node, execption):
    Node.append(["node_raise", execption])

def node_for_new(Node, iterating_var, sequence, stmt_part):
    Node.append(["node_for", iterating_var, sequence, stmt_part])

def node_turtle_new(Node, instruction):
    Node.append(["node_turtle", instruction])

def node_assert_new(Node, args):
    Node.append(["node_assert", args])

def node_model_new(Node, model, datatest):
    Node.append(["node_model", model, datatest])

def node_gettype_new(Node, value):
    Node.append(["node_gettype", value])

def node_class_new(Node, name, extend, method):
    Node.append(["node_class", name, extend, method])

def node_method_new(Node, name, args, stmt):
    Node.append(["node_method", name, args, stmt])

def node_cmd_new(Node, cmd):
    Node.append(["node_cmd", cmd])

def node_list_new(Node, name, list):
    Node.append(["node_list", name, list])

def node_stack_new(Node, name):
    Node.append(["node_stack", name])

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
                    elif self.get(0)[1] == "elif":
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
                    elif self.get(0)[1] == "elif":
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
                    elif self.get(0)[1] == "elif":
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
                   func_name = self.get(0)
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
                    func_name = self.get(0)
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
                turtle_inst = "from turtle import * \n"
                while self.tokens[self.pos][1] != "end":
                    turtle_inst += str(self.get_value(self.tokens[self.pos])[1]) + '\n'
                    self.pos += 1
                turtle_inst = turtle_inst.replace("画个圈", "circle").replace("写隻字", "write").\
                    replace("听我支笛", "exitonclick")
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

                elif self.get(1)[1] == 'do':
                    list = self.get_value(self.get(-1))
                    name = self.get_value(self.get(2))
                    node_list_new(self.Node, name, list)
                    self.skip(3)

                elif self.get(1)[0] != 'keywords' and self.get(1)[0] != 'call_func':
                    args = self.get_value(self.get(1))
                    node_build_in_func_call_new(self.Node, self.get_value(self.get(-1)), self.get_value(self.get(0)), args)
                    self.skip(2)
                
                else:
                    args = "None"
                    node_build_in_func_call_new(self.Node, self.get_value(self.get(-1)), self.get_value(self.get(0)), args)
                    self.skip(1)

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
                while self.tokens[self.pos][1] != "end" and self.pos < len(self.tokens):
                    method_stmt.append(self.tokens[self.pos])
                    self.pos += 1
                Parser(method_stmt, node_method).parse()
                self.skip(1) # Skip the "end"
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
TO_HTML = ""
# TODO: Build a simple vm for Cantonese  
def run(Nodes, TAB = '', label = '', to_html = False):
    def check(tab):
        if label != 'whi_run' and label != 'if_run' and label != 'else_run' and  \
            label != 'elif_run' and label != "func_run" and label != "try_run" and \
            label != "except_run" and label != "finally_run" and label != "for_run" and \
            label != "class_run" and label != "method_run":
            tab = ''
    global TO_PY_CODE
    global TO_HTML
    if Nodes == None:
        return None
    for node in Nodes:
        if node[0] == "node_print":
            check(TAB)
            TO_PY_CODE += TAB + "print(" + node[1][1] + ")\n"
            if to_html:
                TO_HTML += "<h1>" + node[1][1] + "</h1>"
        
        if node[0] == "node_sleep":
            check(TAB)
            TO_PY_CODE += TAB + "import time\n"
            TO_PY_CODE += TAB + "time.sleep(" + node[1][1] + ")\n"
        
        if node[0] == "node_import":
            check(TAB)
            TO_PY_CODE += TAB + "import " + node[1][1] + "\n" + \
            cantonese_lib_import(node[1][1], TAB, TO_PY_CODE) + '\n'

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
            TO_PY_CODE += TAB + "while " + node[1][1] + ":\n"
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
            exec(node[1], variable)
        
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
            TO_PY_CODE += TAB + "class stack(object):\n" + \
                  "\tdef __init__(self):\n" + \
                  "\t\tself.stack = []\n" + \
                  "\tdef __str__(self):\n" + \
                  "\t\treturn 'Stack: ' + str(self.stack)\n" + \
                  "\tdef push(self, value):\n" + \
                  "\t\tself.stack.append(value)\n" + \
                  "\tdef pop(self):\n" + \
                  "\t\tif self.stack:\n" + \
                  "\t\t\tself.stack.pop()\n" + \
                  "\t\telse:\n" + \
                  "\t\t\traise LookupError('stack 畀你丢空咗!')\n"
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

def cantonese_lib_import(name, tab, code):
    if name == "random":
        return cantonese_random_init(tab, code)
    elif name == "datetime":
        return cantonese_datetime_init(tab, code)
    elif name == "math":
        return cantonese_math_init(tab, code)
    else:
        return ""

def cantonese_random_init(tab, code):
    code += tab + "求其啦 = random.random()\n"
    return code

def cantonese_datetime_init(tab, code):
    code += tab + "宜家几点 = datetime.datetime.now()\n"
    return code

def cantonese_math_init(tab, code):
    code += tab + "def corr(a, b):\n" + \
                  "\tif len(a) == 0 or len(b) == 0:\n" + \
                  "\t\treturn None\n" + \
                  "\ta_avg = sum(a)/len(a)\n" + \
                  "\tb_avg = sum(b)/len(b)\n" + \
                  "\tcov_ab = sum([(x - a_avg) * (y - b_avg) " + \
                   "for x, y in zip(a, b)])\n" + \
                  "\tsq = math.sqrt(sum([(x - a_avg)**2 for x in a])" + \
                  "* sum([(x - b_avg) ** 2 for x in b]))\n" + \
                  "\tcorr_factor = cov_ab / sq\n" + \
                  "\treturn corr_factor\n"
    code += tab + "def KNN(inX, dataSet, labels, k):\n" + \
                  "\tm, n = len(dataSet), len(dataSet[0])\n" + \
                  "\tdistances = []\n" + \
                  "\tfor i in range(m):\n" + \
                  "\t\tsum = 0\n" + \
                  "\t\tfor j in range(n):\n" + \
                  "\t\t\tsum += (inX[j] - dataSet[i][j]) ** 2\n" + \
                  "\t\tdistances.append(sum ** 0.5)\n" + \
                  "\tsortDist = sorted(distances)\n" + \
                  "\tclassCount = {}\n" + \
                  "\tfor i in range(k):\n" + \
                  "\t\tvoteLabel = labels[ distances.index(sortDist[i])]\n" + \
                  "\t\tclassCount[voteLabel] = classCount.get(voteLabel, 0)+1\n" + \
                  "\tsortedClass = sorted(classCount.items(), key=lambda d:d[1], reverse=True)\n" + \
                  "\treturn sortedClass[0][0]\n"
    return code

def cantonese_model_new(model, datatest, tab, code):
    if model == "KNN":
        code += tab + "print(KNN(" + datatest +", 数据, 标签, K))"
    else:
        raise "揾唔到你嘅模型: " + model + "!"
        code = ""
    return code

def cantonese_run(code, is_to_py, is_to_web):
    tokens = []
    for token in cantonese_token(code):
        tokens.append(token)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    run(cantonese_parser.Node, to_html = is_to_web)
    if is_to_py:
        print(TO_PY_CODE)
    elif is_to_web:
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
        exec(TO_PY_CODE, variable)

def main():
    try:
        if len(sys.argv) > 1:
            with open(sys.argv[1], encoding = "utf-8") as f:
                code = f.read()
                # Skip the comment
                code = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', code)
                is_to_py = False
                is_to_web = False
                if len(sys.argv) == 3:
                    if sys.argv[2] == "-to_py":
                        is_to_py = True
                    elif sys.argv[2] == "-to_web":
                        is_to_web = True
                    else:
                        pass
                cantonese_run(code, is_to_py, is_to_web)
        else:
            print("你想点啊? (请输入你嘅文件)")
    except FileNotFoundError:
        print("揾唔到你嘅文件 :(")

if __name__ == '__main__':
    main()