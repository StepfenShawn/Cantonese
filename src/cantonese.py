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
from 濑嘢 import 濑啲咩嘢
from 词法 import *
from 语法树 import *
from stack_vm import *

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

    # TODO: Add error check
    def parse(self):
        while True:
            if self.match(kw_print):
                node_print_new(self.Node, self.get_value(self.get(0)))
                self.skip(2) # Skip the args and end_print

            elif self.match("sleep"):
                node_sleep_new(self.Node, self.get(0))
                self.skip(1)

            elif self.match(kw_exit) or self.match(kw_exit_1) or self.match(kw_exit_2):
                node_exit_new(self.Node)
                self.skip(1)

            elif self.match(kw_class_assign) and (self.get(1)[1] == kw_is or self.get(1)[1] == kw_is_2 or \
                                            self.get(1)[1] == kw_is_3):
                node_let_new(self.Node, self.get_value(self.get(0)), self.get_value(self.get(2)))
                self.skip(3)

            elif self.match(kw_assign) and (self.get(1)[1] == kw_is or self.get(1)[1] == kw_is_2 or \
                                            self.get(1)[1] == kw_is_3):
                node_let_new(self.Node, self.get_value(self.get(0)), self.get_value(self.get(2)))
                self.skip(3)
            
            elif self.match(kw_if):
                cond = self.get_value(self.get(0))
                self.skip(4) # Skip the "then", "do", "begin"
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
                    else:
                        stmt_if.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_if, node_if).parse()
                node_if_new(self.Node, cond, node_if)
            
            elif self.match(kw_elif): # case "定系" elif
                cond = self.get_value(self.get(0))
                self.skip(4) # Skip the "then", "do", "begin"
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
                    else:
                        stmt_elif.append(self.tokens[self.pos])
                        self.pos += 1
                Parser(stmt_elif, node_elif).parse()
                node_elif_new(self.Node, cond, node_elif)

            elif self.match(kw_else_or_not): # case "唔系" else
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
        pygame.display.flip()

    def direction(obj, dir):
        if dir == "左边" or dir == "left":
            return obj.left
        if dir == "右边" or dir == "right":
            return obj.right
        if dir == "上边" or dir == "top":
            return obj.top
        if dir == "下边" or dir == "bottom":
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

dump_ast = False
traditional_keywords = "" # TODO

def cantonese_run(code : str, is_to_py : bool, file : str, use_tradition : bool) -> None:
    global dump_ast
    tokens = cantonese_token(code, keywords)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    if dump_ast:
        print(cantonese_parser.Node)
    run(cantonese_parser.Node, path = file)
    cantonese_lib_init()
    if is_to_py:
        print(TO_PY_CODE)
    else:
        import traceback
        try:
            exec(TO_PY_CODE, variable)
        except Exception as e:
            print("濑嘢！" + "\n".join(濑啲咩嘢(e)))

ins_idx = 0 # 指令索引
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
    gen_op_code = []
    co_consts = {}
    co_names = {}
    cansts_idx = 0
    name_idx = 0
    run_with_vm(cantonese_parser.Node, gen_op_code, co_consts, 
                co_names, cansts_idx, name_idx, True, path = file)
    code = Code()
    code.ins_lst = gen_op_code
    if debug:
        for j in gen_op_code:
            print(j)
    code.co_consts = co_consts
    code.co_names = co_names
    cs = CanState(code)
    cs._run()

def run_with_vm(Nodes : list, gen_op_code, co_consts,
            co_names, cansts_idx, name_idx, end, path = '') -> None:
    global ins_idx
    for node in Nodes:
        if node[0] == 'node_print':
            co_consts[cansts_idx] = node[1]
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", cansts_idx))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_PRINT_ITEM", None))
            cansts_idx += 1
        elif node[0] == 'node_let':
            co_names[name_idx] = node[1][1]
            co_consts[cansts_idx] = node[2]
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", cansts_idx))
            ins_idx += 1
            cansts_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NEW_NAME", name_idx))
            name_idx += 1
        elif node[0] == 'node_pass':
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NOP", None))
        elif node[0] == 'node_if':
            co_consts[cansts_idx] = node[1]
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", cansts_idx))
            cansts_idx += 1
            # 先将要跳转的地址设置为None
            ins_idx += 1
            start_idx = ins_idx
            gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_FALSE", None))
            run_with_vm(node[2], gen_op_code, co_consts, co_names, cansts_idx,
                        name_idx, False, path)
            gen_op_code[start_idx - 1].set_args(ins_idx)
        else:
            pass
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


class 交互(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = '> '

    def default(self, 行):
        if 行 is not None:
            cantonese_run(行, False, '【标准输入】', False)


def 开始交互():
    交互().cmdloop("早晨！")

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", nargs='?', default="")
    arg_parser.add_argument("-to_py", action = "store_true")
    arg_parser.add_argument("-讲翻py", action = "store_true")
    arg_parser.add_argument("-to_web", action = "store_true")
    arg_parser.add_argument("-倾偈", action = "store_true")
    arg_parser.add_argument("-compile", action = "store_true")
    arg_parser.add_argument("-讲白啲", action = "store_true")
    arg_parser.add_argument("-use_tr", action = "store_true")
    arg_parser.add_argument("-install", action = "store_true")
    arg_parser.add_argument("-stack_vm", action = "store_true")
    arg_parser.add_argument("-ast", action = "store_true")
    arg_parser.add_argument("-debug", action = "store_true")
    args = arg_parser.parse_args()

    global use_tradition
    global dump_ast
    global debug

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
            if args.debug:
                debug = True
            if args.stack_vm:
                cantonese_run_with_vm(code, args.file, use_tradition)
                exit(1)
            cantonese_run(code, is_to_py, args.file, use_tradition)
    except FileNotFoundError:
        print("揾唔到你嘅文件 :(")
if __name__ == '__main__':
    main()
