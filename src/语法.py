from 词法 import *
from 语法树 import *

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
