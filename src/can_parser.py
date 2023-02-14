from src.keywords import *
import src.can_ast as can_ast

class ParserBase(object):
    def __init__(self, token_list : list) -> None:
        self.pos = 0
        self.tokens = token_list

    def look_ahead(self, step = 1) -> list:
        return self.tokens[self.pos + step]

    def current(self) -> list:
        return self.look_ahead(0)

    def error(self, f, *args):
        err = f
        err = '{0}:  {1}'.format(self.tokens[self.pos],
                    err)
        raise Exception(err)

    def get_next_token_of_kind(self, k, step = 1) -> list:
        tk = self.look_ahead(step)
        if k != tk[1][0]:
            err = 'Line %s: %s附近睇唔明啊大佬!!! Excepted: %s' % (str(tk[0]), str(tk[1][1]), str(k))
            self.error(err)
        self.pos += 1
        return tk
    
    def get_next_token_of(self, expectation : str, step = 1) -> list:
        tk = self.look_ahead(step)
        if isinstance(expectation, list):
            if tk[1][1] not in expectation:
                err = 'Line {0}: 睇唔明嘅语法: {1}系唔系"{2}"啊?'.format(tk[0], tk[1][1], expectation)
                self.error(err)
            self.pos += 1
            return tk
        else:
            if expectation != tk[1][1]:
                err = 'Line {0}: 睇唔明嘅语法: {1}系唔系"{2}"啊?'.format(tk[0], tk[1][1], expectation)
                self.error(err)
            self.pos += 1
            return tk

    def skip(self, step) -> None:
        self.pos += step

    def get_line(self) -> int:
        return self.tokens[self.pos][0]

    def get_type(self, token : list) -> TokenType:
        return token[1][0]

    def get_token_value(self, token : list) -> str:
        return token[1][1]

class ExpParser(ParserBase):
    def __init__(self, token_list : list) -> None:
        super(ExpParser, self).__init__(token_list)
        self.pos = 0
        self.tokens = token_list

    def parse_exp_list(self):
        exps = [self.parse_exp()]
        while self.get_type(self.current()) == TokenType.SEP_COMMA:
            self.skip(1)
            exps.append(self.parse_exp())
        return exps

    """
    exp ::= null
         | false
         | true
         | Numeral
         | LiteralString
         | functoindef
         | prefixexp
         | exp binop exp
         | unop exp
         | '<*>'
    """
    def parse_exp(self):
        # parse the expr by such precedence:  exp13 > exp12 > exp11 > ... > exp0
        # TODO: build a precedence map
        return self.parse_exp13()

    # exp1 ==> exp2
    def parse_exp13(self):
        exp = self.parse_exp12()
        if self.get_token_value(self.current()) == '==>':
            self.skip(1)
            exp = can_ast.MappingExp(exp, self.parse_exp12())
        return exp

    # exp1 or exp2
    def parse_exp12(self):
        exp = self.parse_exp11()
        while self.get_token_value(self.current()) in ['or', '或者']:
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, 'or', exp, self.parse_exp11())
        return exp

    # exp1 and exp2
    def parse_exp11(self):
        exp = self.parse_exp10()
        while self.get_token_value(self.current()) in ['and', '同埋']:
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, 'and', exp, self.parse_exp10())
        return exp

    # Compare
    def parse_exp10(self):
        exp = self.parse_exp9()
        while True:
            now = self.current()
            if self.get_token_value(now) in ('>', '>=', '<', '<=', '==', '!=', kw_is):
                line, op = now[0], self.get_token_value(now)
                self.skip(1)
                exp = can_ast.BinopExp(line, op if op != kw_is else '==', exp, self.parse_exp9())
            
            elif self.get_token_value(now) in ('in', kw_in, tr_kw_in):
                line = now[0]
                self.skip(1)
                exp = can_ast.BinopExp(line, ' in ', exp, self.parse_exp9())
            
            elif self.get_token_value(now) == '比唔上':
                line = now[0]
                self.skip(1)
                exp = can_ast.BinopExp(line, '<', exp, self.parse_exp9())

            else:
                break
        return exp
    
    # exp1 <|> exp2
    def parse_exp9(self):
        exp = self.parse_exp8()
        while self.get_type(self.current()) == TokenType.OP_BOR or \
            self.get_token_value(self.current()) == "或":
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '|', exp, self.parse_exp8())
        return exp

    # exp1 ^ exp2
    def parse_exp8(self):
        exp = self.parse_exp7()
        while self.get_type(self.current()) == TokenType.OP_WAVE or \
            self.get_token_value(self.current()) == "异或":
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '^', exp, self.parse_exp8())
        return exp

    # exp1 & exp2
    def parse_exp7(self):
        exp = self.parse_exp6()
        while self.get_type(self.current()) == TokenType.OP_BAND or \
            self.get_token_value(self.current()) == '与':
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '&', exp, self.parse_exp8())
        return exp

    # shift
    def parse_exp6(self):
        exp = self.parse_exp5()
        if self.get_type(self.current()) in (TokenType.OP_SHL, TokenType.OP_SHR):
            line = self.current()[0]
            op = self.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp5())
        
        elif self.get_token_value(self.current()) == '左移':
            line, op = self.current()[0], "<<"
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp5())
        
        elif self.get_token_value(self.current()) == '右移':
            line, op = self.current()[0], ">>"
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp5())
        
        else:
            return exp
        return exp

    # exp1 <-> exp2
    def parse_exp5(self):
        exp = self.parse_exp4()
        if (self.get_type(self.current()) != TokenType.OP_CONCAT):
            return exp
        
        line = 0
        exps = [exp]
        while self.get_type(self.current()) == TokenType.OP_CONCAT:
            line = self.current()[0]
            self.skip(1)
            exps.append(self.parse_exp4())
        return can_ast.ConcatExp(line, exps)

    # exp1 + / - exp2
    def parse_exp4(self):
        exp = self.parse_exp3()
        while True:
            if self.get_type(self.current()) in (TokenType.OP_ADD, TokenType.OP_MINUS):
                line, op = self.current()[0], self.get_token_value(self.current())
                self.skip(1) # skip the op
                exp = can_ast.BinopExp(line, op, exp, self.parse_exp3())
            
            elif self.get_token_value(self.current()) == '加':
                line = self.current()[0]
                self.skip(1) # skip the op
                exp = can_ast.BinopExp(line, '+', exp, self.parse_exp3())
            
            elif self.get_token_value(self.current()) == '减':
                line = self.current()[0]
                self.skip(1) # skip the op
                exp = can_ast.BinopExp(line, '-', exp, self.parse_exp3())
            
            else:
                break
        
        return exp

     # *, %, /, //
    def parse_exp3(self):
        exp = self.parse_exp2()
        while True:
            if self.get_type(self.current()) in (TokenType.OP_MUL, TokenType.OP_MOD, 
                    TokenType.OP_DIV, TokenType.OP_IDIV):
                line, op = self.current()[0], self.get_token_value(self.current())
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, op, exp, self.parse_exp2())
            
            elif self.get_token_value(self.current()) == '乘':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '*', exp, self.parse_exp2())

            elif self.get_token_value(self.current()) == '余':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '%', exp, self.parse_exp2())

            elif self.get_token_value(self.current()) == '整除':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '//', exp, self.parse_exp2())

            elif self.get_token_value(self.current()) == '除':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '//', exp, self.parse_exp2())

            else:
                break
        
        return exp

    # unop exp
    def parse_exp2(self):
        if self.get_type(self.current()) == TokenType.OP_NOT or \
            self.get_token_value(self.current()) == 'not' or \
            self.get_token_value(self.current()) == '-' or \
            self.get_token_value(self.current()) == '~':
            line, op = self.current()[0], self.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.UnopExp(line, op, self.parse_exp2())
            return exp

        elif self.get_type(self.current()) == '取反':
            line, op = self.current()[0], '~'
            self.skip(1) # Skip the op
            exp = can_ast.UnopExp(line, op, self.parse_exp2())
            return exp

        return self.parse_exp1()

    # x ** y
    def parse_exp1(self):
        exp = self.parse_exp0()
        if self.get_type(self.current()) == TokenType.OP_POW:
            line, op = self.current()[0], self.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp2())
        return exp

    def parse_exp0(self):
        tk = self.current()
        if self.get_token_value(tk) == '<*>':
            self.skip(1)
            return can_ast.VarArgExp(tk[0])
        
        elif self.get_token_value(tk) in [kw_false, tr_kw_false, "False"]:
            self.skip(1)
            return can_ast.FalseExp(tk[0])
        
        elif self.get_token_value(tk) in [kw_true, tr_kw_true, "True"]:
            self.skip(1)
            return can_ast.TrueExp(tk[0])
        
        elif self.get_token_value(tk) in [kw_none, tr_kw_none, "None"]:
            self.skip(1)
            return can_ast.NullExp(tk[0])
        
        elif self.get_type(tk) == TokenType.NUM:
            self.skip(1)
            return can_ast.NumeralExp(tk[0], self.get_token_value(tk))
        
        elif self.get_type(tk) == TokenType.STRING:
            self.skip(1)
            return can_ast.StringExp(tk[0], self.get_token_value(tk))

        elif self.get_type(tk) == TokenType.SEP_LBRACK:
            return self.parse_listcons()

        elif self.get_type(tk) == TokenType.SEP_LCURLY:
            return self.parse_mapcons()

        # lambda function
        elif self.get_token_value(tk) == '$$':
            return self.parse_functiondef_expr()

        # If-Else expr
        elif self.get_token_value(tk) in [kw_expr_if, tr_kw_expr_if]:
            return self.parse_if_else_expr()
        
        return self.parse_prefixexp()
    """
    prefixexp ::= var
          | '(' exp ')'
          | '|' exp '|'
          | '<|' id '|>'
          | functioncall
          | id '=' exp

    var ::= id
          | prefixexp '[' exp ']'
          | prefixexp '->' id
    """
    def parse_prefixexp(self):
        if self.get_type(self.current()) == TokenType.IDENTIFIER:
            line, name = self.current()[0], self.get_token_value(self.current())
            self.skip(1)
            exp = can_ast.IdExp(line, name)
        elif self.get_type(self.current()) == TokenType.SEPCIFIC_ID_BEG:
            self.skip(1)
            name = self.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0))
            exp = can_ast.SpecificIdExp(name)
            self.get_next_token_of_kind(TokenType.SEPICFIC_ID_END, 0)
        # '(' exp ')'
        elif self.get_type(self.current()) == TokenType.SEP_LPAREN:
            exp = self.parse_parens_exp()
        # '|' exp '|'
        else:
            exp = self.parse_brack_exp()
        return self.finish_prefixexp(exp)
        

    def parse_parens_exp(self):
        self.get_next_token_of_kind(TokenType.SEP_LPAREN, 0)
        exp = self.parse_exp()
        self.get_next_token_of_kind(TokenType.SEP_RPAREN, 0)
        return exp

    def parse_brack_exp(self):
        self.get_next_token_of('|', 0)
        exp = self.parse_exp()
        self.get_next_token_of('|', 0)
        return exp

    """
    listcons := '[' exp_list ']'
    """
    def parse_listcons(self):
        self.get_next_token_of_kind(TokenType.SEP_LBRACK, 0)
        if self.get_type(self.current()) == TokenType.SEP_RBRACK: # []
            self.skip(1)
            return can_ast.ListExp("")
        else:
            exps = self.parse_exp_list()
            self.get_next_token_of_kind(TokenType.SEP_RBRACK, 0)
            return can_ast.ListExp(exps)

    """
    set_or_mapcons := '{' exp_list '}'
    """
    def parse_mapcons(self):
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
        if self.get_type(self.current()) == TokenType.SEP_RCURLY: # {}
            self.skip(1)
            return can_ast.MapExp("")
        else:
            exps = self.parse_exp_list()
            self.get_next_token_of_kind(TokenType.SEP_RCURLY, 0)
            return can_ast.MapExp(exps)
        

    def finish_prefixexp(self, exp : can_ast.AST):
        while True:
            kind, value = self.get_type(self.current()), self.get_token_value(self.current())
            if kind == TokenType.SEP_LBRACK:
                self.skip(1)
                key_exp : can_ast.AST = self.parse_exp()
                self.get_next_token_of_kind(TokenType.SEP_RBRACK, 0)
                exp = can_ast.ListAccessExp(self.get_line(), exp, key_exp)
            elif kind == TokenType.SEP_DOT or \
                (kind == TokenType.KEYWORD and value == kw_do):
                if self.get_type(self.look_ahead(1)) == TokenType.SEP_LCURLY:
                    # || -> { ... } means we in a method define statement. So break it.
                    break
                # Otherwise it's a ObjectAccessExp
                else:
                    self.skip(1)
                    tk = self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)
                    line, name = tk[0], self.get_token_value(tk)
                    key_exp = can_ast.IdExp(line, name)
                    exp = can_ast.ObjectAccessExp(line, exp, key_exp)
            elif (kind == TokenType.SEP_LPAREN) or \
                (kind == TokenType.KEYWORD and value == kw_call_begin):
                exp = self.finish_functioncall_exp(exp)
            elif value == '嘅长度':
                self.skip(1)
                key_exp = can_ast.IdExp(self.get_line(), '__len__()')
                exp = can_ast.ObjectAccessExp(self.get_line(), exp, key_exp)
            elif kind == TokenType.OP_ASSIGN:
                self.skip(1)
                exp = can_ast.AssignExp(exp, self.parse_exp())
            # TODO: Fix bugs here
            elif value in [kw_get_value, tr_kw_get_value]:
                self.skip(1)
                exp = can_ast.AssignExp(self.parse_exp(), exp)
            else:
                break
        return exp

    """
    functioncall ::= prefixexp '下' '->' args
                  | prefixexp args
    """
    def finish_functioncall_exp(self, prefix_exp : can_ast.AST):
        if (self.get_token_value(self.current()) == kw_call_begin):
            self.skip(1)
            self.get_next_token_of(kw_do, 0)
            line = self.get_line()
            args = self.parse_args()
            last_line = self.get_line()
            return can_ast.FuncCallExp(prefix_exp, args)
        else:
            line = self.get_line()
            args = self.parse_args()
            last_line = self.get_line()
            return can_ast.FuncCallExp(prefix_exp, args)

   
    def parse_parlist(self):
        if self.get_type(self.current()) == TokenType.IDENTIFIER or \
            self.get_token_value(self.current()) == '<*>':
            par_parser = ParExpParser(self.tokens[self.pos : ])
            exps = par_parser.parse_exp_list()
            self.skip(par_parser.pos)
            del par_parser # free the memory
            return exps
        
        elif self.get_token_value(self.current()) == '|':
            self.skip(1)
            par_parser = ParExpParser(self.tokens[self.pos : ])
            exps = par_parser.parse_exp_list()
            self.skip(par_parser.pos)
            del par_parser # free the memory
            self.get_next_token_of('|', 0)
            return exps
        
        else:
            return []

    """
    idlist ::= id [',', id]
            | '|' id [',', id] '|'
    """
    def parse_idlist(self):
        tk = self.current()
        if (self.get_type(tk) == TokenType.IDENTIFIER):
            ids = [can_ast.IdExp(self.get_line(), 
                self.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)))]
            while self.get_type(self.current()) == TokenType.SEP_COMMA:
                self.skip(1)
                if (self.get_type(self.current()) != TokenType.IDENTIFIER):
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(self.get_line(), 
                        self.get_token_value(self.current())))
                self.skip(1)
            return ids

        elif (self.get_token_value(tk) == '|'):
            self.skip(1)
            ids = [can_ast.IdExp(self.get_line(), 
                self.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)))]
            while self.get_type(self.current()) == TokenType.SEP_COMMA:
                self.skip(1)
                if (self.get_type(self.current()) != TokenType.IDENTIFIER):
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(self.get_line(), 
                        self.get_token_value(self.current())))
                self.skip(1)
            self.get_next_token_of('|', 0)
            return ids

    """
    lambda_functoindef ::= '$$' idlist '->' block '搞掂'
    """
    def parse_functiondef_expr(self):
        self.skip(1)
        idlist : list = self.parse_idlist()
        blocks : list = []
        self.get_next_token_of(kw_do, 0)
        blocks.append(self.parse_exp())

        return can_ast.LambdaExp(idlist, blocks)

    def parse_if_else_expr(self):
        self.skip(1)
        CondExp : can_ast.AST = self.parse_exp()
        self.get_next_token_of([kw_do, tr_kw_do], 0)
        IfExp : can_ast.AST = self.parse_exp()
        self.get_next_token_of([kw_expr_else, tr_kw_expr_else], 0)
        self.get_next_token_of([kw_do, tr_kw_do], 0)
        ElseExp : can_ast.AST = self.parse_exp()

        return can_ast.IfElseExp(CondExp, IfExp, ElseExp)

    """
    args ::= '|' explist '|'
           | '(' {explist} ')'
           | explist
           | LiteralString
           | Numeral
           | id
    """
    def parse_args(self):
        args = []
        tk = self.current()
        if self.get_token_value(tk) == '(':
            self.skip(1)
            if self.get_token_value(self.current()) != ')':
                args = self.parse_exp_list()
            self.get_next_token_of_kind(TokenType.SEP_RPAREN, step = 0)
        elif self.get_token_value(tk) == '|':
            self.skip(1)
            if self.get_token_value(self.current()) != '|':
                args = self.parse_exp_list()
            self.get_next_token_of('|', step = 0)
        else:
            args = [self.parse_exp()]
        return args

"""
    parlist ::= id [',', id | '<*>']
             | id '=' exp [',' id]
             | '<*>'
"""

class ParExpParser(ExpParser):
    def __init__(self, token_list: list) -> None:
        super().__init__(token_list)

    # override
    def parse_exp(self):
        return self.parse_exp0()

    # override
    def parse_exp0(self):
        tk = self.current()

        if self.get_token_value(tk) == '<*>':
            self.skip(1)
            return can_ast.VarArgExp(tk[0])
        
        return self.parse_prefixexp()

    # override
    def parse_prefixexp(self):
        if self.get_type(self.current()) == TokenType.IDENTIFIER:
            line, name = self.current()[0], self.get_token_value(self.current())
            self.skip(1)
            exp = can_ast.IdExp(line, name)
            return self.finish_prefixexp(exp)
        else:
            raise Exception("Parlist must be a identifier type!")

    # override
    def finish_prefixexp(self, exp: can_ast.AST):
        kind = self.get_type(self.current())
        value = self.get_token_value(self.current())
        if value == '=' or value == '==>':
            self.skip(1)
            exp_parser = ExpParser(self.tokens[self.pos : ])
            exp2 = exp_parser.parse_exp()
            self.skip(exp_parser.pos)
            del exp_parser # free the memory
            return can_ast.AssignExp(exp, exp2)
        return exp

class StatParser(ParserBase):
    def __init__(self, token_list : list, ExpParser = ExpParser) -> None:
        super(StatParser, self).__init__(token_list)
        self.pos = 0
        self.tokens = token_list

        # Function address type:
        # We can choose the class `ExpParser` Or `ClassBlockExpParser`
        self.ExpParser = ExpParser

    def parse(self):
        tk = self.current()
        kind = self.get_type(tk)
        tk_value = self.get_token_value(tk)
        if kind == TokenType.KEYWORD:
            if tk_value in [kw_print, tr_kw_print]:
                return self.parse_print_stat()
            
            elif tk_value in [kw_exit, kw_exit_1, kw_exit_2, tr_kw_exit_1, tr_kw_exit_2]:
                return self.parse_exit_stat()
            
            elif tk_value in [kw_assign, tr_kw_assign]:
                return self.parse_assign_stat()
            
            elif tk_value in [kw_if, tr_kw_if]:
                return self.parse_if_stat()
            
            elif tk_value in [kw_import, tr_kw_import]:
                return self.parse_import_stat()
            
            elif tk_value == kw_global_set:
                return self.parse_global_stat()
            
            elif tk_value in [kw_break, tr_kw_break]:
                return self.parse_break_stat()
            
            elif tk_value in [kw_while_do, tr_kw_while_do]:
                return self.parse_while_stat()
            
            elif tk_value == '|':
                self.skip(1)
                if self.get_token_value(self.current()) == '|':
                    prefix_exps = []
                    skip_step = 0
                else:
                    exp_parser = self.ExpParser(self.tokens[self.pos : ])
                    prefix_exps = exp_parser.parse_exp_list()
                    skip_step = exp_parser.pos = exp_parser.pos # we will skip it in parse_for_stat
                    del exp_parser
                
                self.get_next_token_of('|', skip_step)

                if self.get_token_value(self.look_ahead(skip_step)) in [kw_from, tr_kw_from]:
                    return self.parse_for_stat(prefix_exps, skip_step)
                
                elif self.get_token_value(self.look_ahead(skip_step)) in [kw_call_begin, tr_kw_call_begin]:
                    return self.parse_func_call_stat(prefix_exps, skip_step)
                
                elif self.get_token_value(self.look_ahead(skip_step)) in [kw_lst_assign, tr_kw_lst_assign]:
                    return self.parse_list_assign_stat(prefix_exps, skip_step)

                elif self.get_token_value(self.look_ahead(skip_step)) in [kw_set_assign, tr_kw_set_assign]:
                    return self.parse_set_assign_stat(prefix_exps, skip_step)
                
                elif self.get_token_value(self.look_ahead(skip_step)) in [kw_do, tr_kw_do]:
                    return self.parse_class_method_call_stat(prefix_exps, skip_step) 


            elif tk_value == kw_function:
                return self.parse_func_def_stat()

            elif tk_value == '$$':
                return self.parse_lambda_def_stat()

            elif tk_value in [kw_pass, tr_kw_pass]:
                return self.parse_pass_stat()
            
            elif tk_value in [kw_return, tr_kw_return]:
                return self.parse_return_stat()
            
            elif tk_value in [kw_del, tr_kw_del]:
                return self.parse_del_stat()

            elif tk_value in [kw_type, tr_kw_type]:
                return self.parse_type_stat()

            elif tk_value in [kw_assert, tr_kw_assert]:
                return self.parse_assert_stat()

            elif tk_value in [kw_try, tr_kw_try]:
                return self.parse_try_stat()

            elif tk_value in [kw_raise, tr_kw_raise]:
                return self.parse_raise_stat()

            elif tk_value in [kw_cmd, tr_kw_cmd]:
                return self.parse_cmd_stat()

            elif tk_value in [kw_class_def, tr_kw_class_def]:
                return self.parse_class_def()

            elif tk_value in [kw_call, tr_kw_call]:
                return self.parse_call_stat()

            elif tk_value in [kw_stackinit, tr_kw_stackinit]:
                return self.parse_stack_init_stat()

            elif tk_value in [kw_push, tr_kw_push]:
                return self.parse_stack_push_stat()

            elif tk_value in [kw_pop, tr_kw_pop]:
                return self.parse_stack_pop_stat()

            elif tk_value in [kw_match, tr_kw_match]:
                return self.parse_match_stat()

            elif tk_value == '@@@':
                return self.parse_extend_stat()

            elif tk_value == '&&':
                return self.parse_for_each_stat()

            elif tk_value in [kw_model, tr_kw_model]:
                return self.parse_model_new_stat()

            elif tk_value in [kw_turtle_beg, tr_kw_turtle_beg]:
                return self.parse_turtle_stat()

        elif kind == TokenType.IDENTIFIER:
            if self.get_token_value(self.look_ahead(1)) in [kw_from, tr_kw_from]:
                return self.parse_for_stat()
            
            elif self.get_token_value(self.look_ahead(1)) in [kw_call_begin, tr_kw_call_begin]:
                return self.parse_func_call_stat()

            elif self.get_token_value(self.look_ahead(1)) in [kw_do, tr_kw_do]:
                return self.parse_class_method_call_stat()

        elif kind == TokenType.EOF:
            return
            
    def parse_stats(self):
        stats = []
        while True:
            stat = self.parse()
            if stat is not None:
                stats.append(stat)
            else:
                break
        return stats

    def parse_print_stat(self):
        self.skip(1) # skip the kw_print
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args = exp_parser.parse_args()
        self.skip(exp_parser.pos)
        self.get_next_token_of([kw_endprint, tr_kw_endprint], step = 0)
        del exp_parser # free the memory
        return can_ast.PrintStat(args)

    # Parser for muti-assign
    def parse_assign_block(self):
        # Nothing in assignment block
        if self.get_type(self.current()) == TokenType.SEP_RCURLY:
            self.skip(1)
            return can_ast.AssignStat(0, can_ast.AST, can_ast.AST)
        var_list : list = []
        exp_list : list= []
        while self.get_type(self.current()) != TokenType.SEP_RCURLY:
            var_list.append(self.parse_var_list()[0])
            self.get_next_token_of([kw_is, kw_is_2, kw_is_3], 0)
            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            exp_list.append(exp_parser.parse_exp_list()[0])
            self.skip(exp_parser.pos)
            del exp_parser # free the memory
        
        # Skip the SEP_RCURLY
        self.skip(1)
        return can_ast.AssignBlockStat(self.get_line(), var_list, exp_list)

    def parse_assign_stat(self):
        self.skip(1)
        if self.get_token_value(self.current()) != kw_do:
            var_list = self.parse_var_list()
            self.get_next_token_of([kw_is, kw_is_2, kw_is_3], 0)
            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            exp_list = exp_parser.parse_exp_list()
            self.skip(exp_parser.pos)
            del exp_parser # free the memory
            last_line = self.get_line()
            return can_ast.AssignStat(last_line, var_list, exp_list)
        else:
            # Skip the kw_do
            self.skip(1)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            return self.parse_assign_block()
            # The SEP_RCURLY will be checked in self.parse_assign_block()

    def parse_var_list(self):
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exp = exp_parser.parse_prefixexp()
        self.skip(exp_parser.pos)
        del exp_parser
        var_list : list = [self.check_var(exp)]
    
        while self.get_type(self.current()) == TokenType.SEP_COMMA:
            self.skip(1)
            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            exp = exp_parser.parse_prefixexp()
            self.skip(exp_parser.pos)
            del exp_parser
            var_list.append(self.check_var(exp))

        return var_list

    def check_var(self, exp : can_ast.AST):
        if isinstance(exp, can_ast.IdExp) or \
           isinstance(exp, can_ast.ObjectAccessExp) or \
           isinstance(exp, can_ast.ListAccessExp) or \
           isinstance(exp, can_ast.ClassSelfExp):
           return exp
        else:
            raise Exception('unreachable!')

    def parse_exit_stat(self):
        tk = self.look_ahead()
        self.skip(1)
        return can_ast.ExitStat()

    def parse_if_stat(self):
        # Skip the keyword if
        self.skip(1)
        if_blocks : list = []
        elif_exps : list = []
        elif_blocks : list = []
        else_blocks : list = []

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        if_exps = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        self.get_next_token_of([kw_then, tr_kw_then], 0)
        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
        del exp_parser # free the memory

        while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
            block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            if_blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser # free the memory
        self.skip(1) # Skip the SEP_RCURLY '}'

        while self.get_token_value(self.current()) in [kw_elif, tr_kw_elif]:
            self.skip(1) # skip and try to get the next token
            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            elif_exps.append(exp_parser.parse_exp())
            self.skip(exp_parser.pos)
            self.get_next_token_of([kw_then, tr_kw_then], 0)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            del exp_parser # free the memory
            elif_block : list = []
            while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                elif_block.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser # free the memory
            elif_blocks.append(elif_block)

            self.skip(1) # Skip the SEP_RCURLY '}'

        if self.get_token_value(self.current()) == kw_else_or_not:
            self.skip(1) # Skip and try yo get the next token
            self.get_next_token_of([kw_then, tr_kw_then], 0)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                else_blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser # free the memory
            self.skip(1) # Skip the SEP_RCURLY '}'

        return can_ast.IfStat(if_exps, if_blocks, elif_exps, elif_blocks, else_blocks)


    def parse_import_stat(self):
        self.skip(1) # Skip the kw_import
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        idlist = exp_parser.parse_idlist()
        self.skip(exp_parser.pos)
        del exp_parser # free thr memory
        return can_ast.ImportStat(idlist)

    def parse_global_stat(self):
        self.skip(1) # Skip the kw_global
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        idlist = exp_parser.parse_idlist()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory
        return can_ast.GlobalStat(idlist)

    def parse_break_stat(self):
        self.skip(1) # Skip the kw_break
        return can_ast.BreakStat()

    def parse_while_stat(self):
        self.skip(1) # Skip the kw_while_do
        blocks : list = []
        cond_exps : list = []
        while (self.get_token_value(self.current()) != kw_while):
            block_parser =  StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser # free the memory

        self.skip(1) # Skip the kw_while
        
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        cond_exps = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory
        self.get_next_token_of([kw_whi_end, tr_kw_whi_end], 0)

        return can_ast.WhileStat(cond_exps, blocks)

    def parse_for_stat(self, prefix_exp : ExpParser = None, skip_prefix_exp : int = 0):
        blocks : list = []

        if prefix_exp == None:
            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            id = exp_parser.parse_exp()
            self.skip(exp_parser.pos)
            del exp_parser # free the memory

        else:
            id = prefix_exp[0]
            self.skip(skip_prefix_exp)
        
        self.get_next_token_of([kw_from, tr_kw_from], 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        from_exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory
        self.get_next_token_of([kw_to, tr_kw_to], 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        to_exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        while (self.get_token_value(self.current()) not in [kw_endfor, tr_kw_endfor]):
            block_parse = StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(block_parse.parse())
            self.skip(block_parse.pos)
            del block_parse # free the memory

        self.skip(1)

        return can_ast.ForStat(id, from_exp, to_exp, blocks)

    def parse_func_def_stat(self):
        self.skip(1) # Skip the kw_function
        
        if self.get_token_value(self.current()) == '即係':
            self.skip(1)
            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            args : list = exp_parser.parse_parlist()
            args = [] if args == None else args
            self.get_next_token_of([kw_do], 0)

        else:
            name = self.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0))
            
            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            args : list = exp_parser.parse_parlist()
            args = [] if args == None else args
            self.skip(exp_parser.pos)
            del exp_parser # free the memory

            self.get_next_token_of([kw_func_begin, tr_kw_func_begin, kw_do], 0)

            blocks : list = []
            while (self.get_token_value(self.current()) not in [kw_func_end, tr_kw_func_end]):
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser

            self.skip(1)

        return can_ast.FunctoinDefStat(can_ast.IdExp(self.get_line(), name), args, blocks)

    def parse_func_call_stat(self, prefix_exps : can_ast.AST = None, skip_step : int = 0):
        if prefix_exps == None:
            func_name = can_ast.IdExp(self.get_line(), self.get_token_value(self.current()))
            self.skip(1)
        else:
            func_name = prefix_exps[0]
            self.skip(skip_step)

        self.get_next_token_of([kw_call_begin, tr_kw_call_begin], 0)
        self.get_next_token_of(kw_do, 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args = exp_parser.parse_args()
        self.skip(exp_parser.pos)
        del exp_parser

        if self.get_token_value(self.current()) == kw_get_value:
            self.skip(1)
            var_list = self.parse_var_list()
            return can_ast.AssignStat(self.get_line(), var_list,
                    [can_ast.FuncCallExp(func_name, args)])
        else:
            return can_ast.FuncCallStat(func_name, args)

    def parse_class_method_call_stat(self, prefix_exps : can_ast.AST = None, skip_step : int = 0):
        if prefix_exps == None:
            name_exp = can_ast.IdExp(self.get_line(), self.get_token_value(self.current()))
            self.skip(1)
        else:
            self.skip(skip_step)
            name_exp = prefix_exps[0]

        self.get_next_token_of(kw_do, 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        method : can_ast.AST = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args : list = exp_parser.parse_args()
        self.skip(exp_parser.pos)
        del exp_parser # free thr memory
    
        return can_ast.MethodCallStat(name_exp, method, args)
    
    def parse_list_assign_stat(self, prefix_exp : can_ast.AST, skip_step : int):
        self.skip(skip_step)
        self.get_next_token_of([kw_lst_assign, tr_kw_lst_assign], 0)
        self.get_next_token_of(kw_do, 0)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(self.get_line(), varlist, 
                [can_ast.ListExp(prefix_exp)])

    def parse_set_assign_stat(self, prefix_exp : can_ast.AST, skip_step : int):
        self.skip(skip_step)
        self.get_next_token_of([kw_set_assign, tr_kw_set_assign], 0)
        self.get_next_token_of(kw_do, 0)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(self.get_line(), varlist, 
                [can_ast.MapExp(prefix_exp)])


    def parse_pass_stat(self):
        self.skip(1)
        return can_ast.PassStat()

    def parse_assert_stat(self):
        self.skip(1)
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser

        return can_ast.AssertStat(exp)

    def parse_return_stat(self):
        self.skip(1)
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exps = exp_parser.parse_exp_list()
        self.skip(exp_parser.pos)
        del exp_parser

        return can_ast.ReturnStat(exps)

    def parse_del_stat(self):
        self.skip(1)
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exps = exp_parser.parse_exp_list()
        self.skip(exp_parser.pos)
        del exp_parser

        return can_ast.DelStat(exps)

    def parse_try_stat(self):
        self.skip(1)
        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

        try_blocks : list = []
        except_exps : list = []
        except_blocks : list = []
        finally_blocks : list = []

        while self.get_type(self.current()) != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            try_blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser

        self.skip(1)
        self.get_next_token_of([kw_except, tr_kw_except], 0)
        
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        except_exps.append(exp_parser.parse_exp())
        self.skip(exp_parser.pos)
        del exp_parser

        self.get_next_token_of([kw_then, tr_kw_then], 0)
        self.get_next_token_of([kw_do], 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

        # a temp list to save the block
        except_block = []
        while self.get_type(self.current()) != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            except_block.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser
        
        self.skip(1)
        except_blocks.append(except_block)

        while self.get_token_value(self.current()) in [kw_except, tr_kw_except]:
            self.get_next_token_of([kw_then, tr_kw_then], 0)

            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            except_exps.append(exp_parser.parse_exp())
            self.skip(exp_parser.pos)
            del exp_parser

            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

            # clear the list
            except_block = []
            while self.get_type(self.current()) != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                except_block.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser
            
            except_blocks.append(except_block)

        if self.get_token_value(self.current()) in [kw_finally, tr_kw_finally]:
            self.skip(1)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

            while self.get_type(self.current()) != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                finally_blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser

            self.skip(1)

        return can_ast.TryStat(try_blocks, except_exps, except_blocks, finally_blocks)

    def parse_raise_stat(self):
        self.skip(1)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        name_exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos) # free the memory
        del exp_parser

        self.get_next_token_of([kw_raise_end, tr_kw_raise_end], 0)
        return can_ast.RaiseStat(name_exp)

    def parse_type_stat(self):
        self.skip(1)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        name_exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos) # free the memory
        del exp_parser

        return can_ast.TypeStat(name_exp)

    def parse_cmd_stat(self):
        self.skip(1)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args = exp_parser.parse_args()
        self.skip(exp_parser.pos) # free the memory
        del exp_parser

        return can_ast.CmdStat(args)

    def parse_class_def(self):
        self.skip(1)
        
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        class_name : can_ast.AST = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of([kw_extend, tr_kw_extend], 0)
        
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        extend_name : list = exp_parser.parse_exp_list()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        class_blocks = []
        
        while self.get_token_value(self.current()) not in [kw_endclass, tr_kw_endclass]:
            class_block_parser = ClassBlockStatParser(self.tokens[self.pos : ])
            class_blocks.append(class_block_parser.parse())
            self.skip(class_block_parser.pos)

        self.skip(1)

        return can_ast.ClassDefStat(class_name, extend_name, class_blocks)

    def parse_call_stat(self):
        self.skip(1)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exps = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        return can_ast.CallStat(exps)

    def parse_stack_init_stat(self):
        self.skip(1)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exps = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        return can_ast.AssignStat(self.get_line, [exps], [
            can_ast.FuncCallExp(can_ast.IdExp(self.get_line(), 'stack'), [])
        ])

    def parse_stack_push_stat(self):
        self.skip(1) # skip the kw_push

        self.get_next_token_of(kw_do, 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exps = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args = exp_parser.parse_args()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        return can_ast.MethodCallStat(exps, can_ast.IdExp(self.get_line(), 'push'), 
                    args)

    def parse_stack_pop_stat(self):
        self.skip(1) # skip the kw_pop

        self.get_next_token_of(kw_do, 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exps = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        return can_ast.MethodCallStat(exps, can_ast.IdExp(self.get_line(), 'pop'), 
                    [])

    def parse_lambda_def_stat(self):
        exp_parse = self.ExpParser(self.tokens[self.pos : ])
        lambda_exp = [exp_parse.parse_functiondef_expr()]
        self.skip(exp_parse.pos)
        del exp_parse # free the memory

        self.get_next_token_of(kw_get_value, 0)
        exp_parse = self.ExpParser(self.tokens[self.pos : ])
        id_exp = exp_parse.parse_idlist()
        self.skip(exp_parse.pos)
        del exp_parse # free the memory

        return can_ast.AssignStat(self.get_line(), id_exp, lambda_exp)

    def parse_match_stat(self):
        self.skip(1)
        match_val : list = []
        match_block : list = []
        default_match_block : list = []
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        match_id = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

        while self.get_type(self.current()) != TokenType.SEP_RCURLY:
            while self.get_token_value(self.current()) in [kw_case, tr_kw_case]:
                self.skip(1)
                exp_parser = self.ExpParser(self.tokens[self.pos : ])
                match_val.append(exp_parser.parse_exp())
                self.skip(exp_parser.pos)
                del exp_parser # free the memory

                self.get_next_token_of(kw_do, 0)
                self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

                block : list = []

                while self.get_type(self.current()) != TokenType.SEP_RCURLY:
                    stat_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                    block.append(stat_parser.parse())
                    self.skip(stat_parser.pos)
                    del stat_parser # free the memory

                self.skip(1)
                match_block.append(block)
            
            if self.get_token_value(self.current()) == kw_else_or_not:
                self.skip(1)
                self.get_next_token_of([kw_then, tr_kw_then], 0)
                self.get_next_token_of(kw_do, 0)
                self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

                while self.get_type(self.current()) != TokenType.SEP_RCURLY:
                    stat_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                    default_match_block.append(stat_parser.parse())
                    self.skip(stat_parser.pos)
                    del stat_parser # free the memory

                self.skip(1)
        
        self.skip(1)

        return can_ast.MatchStat(match_id, match_val, match_block, default_match_block)

    def parse_for_each_stat(self):
        self.skip(1)

        id_list : list = []
        exp_list : list = []
        blocks : list = []

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        id_list = exp_parser.parse_idlist()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of([kw_in, tr_kw_in], 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        exp_list = exp_parser.parse_exp_list()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

        while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
            stat_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(stat_parser.parse())
            self.skip(stat_parser.pos)
            del stat_parser # free the memory
        
        self.skip(1)

        return can_ast.ForEachStat(id_list, exp_list, blocks)

    def parse_extend_stat(self):
        self.skip(1)
        tk = self.get_next_token_of_kind(TokenType.EXTEND_EXPR, 0)
        return can_ast.ExtendStat(self.get_token_value(tk)[1 : -1])

    def parse_model_new_stat(self):
        self.skip(1)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        model_name = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of([kw_mod_new, tr_kw_mod_new], 0)
        self.get_next_token_of(kw_do, 0)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        dataset = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        return can_ast.ModelNewStat(model_name, dataset)

    def parse_turtle_stat(self):
        self.skip(1)

        instruction_ident : list = ["首先", "跟住", "最尾"]
        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

        exp_blocks : list = []

        while self.get_type(self.current()) != TokenType.SEP_RCURLY:
            if self.get_token_value(self.current()) in instruction_ident and \
                self.get_type(self.current()) == TokenType.IDENTIFIER:
                self.skip(1)
            else:
                exp_parser = self.ExpParser(self.tokens[self.pos : ])
                exp_blocks.append(exp_parser.parse_exp())
                self.skip(exp_parser.pos)
                del exp_parser # free the memory

        self.skip(1)

        return can_ast.TurtleStat(exp_blocks)

class LambdaBlockExpParser(ExpParser):
    def __init__(self, token_list: list) -> None:
        super().__init__(token_list)

    def parse_exp0(self):
        tk = self.get_token_value(self.current())

class ClassBlockExpParser(ExpParser):
    def __init__(self, token_list: list) -> None:
        super().__init__(token_list)

    def parse_exp0(self):
        tk = self.get_token_value(self.current())
        if tk in [kw_self, tr_kw_self, '@@']:
            self.skip(1)
            return can_ast.ClassSelfExp(super().parse_exp0())
        else:
            return super().parse_exp0()

class ClassBlockStatParser(StatParser):
    def __init__(self, token_list: list, ExpParser = ClassBlockExpParser) -> None:
        super().__init__(token_list, ExpParser)

    def parse_method_block(self):
        
        self.skip(1) # Skip the kw_method

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        name_exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args : list = exp_parser.parse_parlist()
        args = [] if args == None else args
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of([kw_func_begin, tr_kw_func_begin, kw_do], 0)
        
        blocks : list = []
        # '{' ... '}'
        if self.get_type(self.current()) == TokenType.SEP_LCURLY:
            self.skip(1)
            while self.get_type(self.current()) != TokenType.SEP_RCURLY:
                block_parser = ClassBlockStatParser(self.tokens[self.pos : ], self.ExpParser)
                blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser
        
        # '=> ... '%%'
        else:
            while (self.get_token_value(self.current()) not in [kw_func_end, tr_kw_func_end]):
                block_parser = ClassBlockStatParser(self.tokens[self.pos : ], self.ExpParser)
                blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser        

        self.skip(1)
        
        return can_ast.MethodDefStat(name_exp, args, blocks)

    def parse_class_init_stat(self):
        self.skip(1)

        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args = exp_parser.parse_parlist()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

        blocks : list = []
        while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
            block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser # free the memory

        self.skip(1)

        return can_ast.MethodDefStat(can_ast.IdExp(self.get_line(), '__init__'), args, blocks)
        
    def parse_class_assign_stat(self):
        return self.parse_assign_stat()

    def parse(self):
        tk = self.current()
        kind = self.get_type(tk)
        tk_value = self.get_token_value(tk)
        if tk_value in [kw_method, tr_kw_method]:
            return self.parse_method_block()
        elif tk_value in [kw_class_assign, tr_kw_class_assign]:
            return self.parse_class_assign_stat()
        elif tk_value in [kw_class_init, tr_kw_class_init]:
            return self.parse_class_init_stat()
        else:
            return super().parse()