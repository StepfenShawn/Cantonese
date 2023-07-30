import sys
sys.path.append("..")

from lexer.keywords import *
from Ast import can_ast
from .parser_base import *
from .util import ParserUtil

class ExpParser(ParserBase):
    def __init__(self, token_list : list) -> None:
        super(ExpParser, self).__init__(token_list)
        self.pos = 0
        self.tokens = token_list

    @exp_type('exp_list')
    def parse_exp_list(self):
        exps = [self.parse_exp()]
        while ParserUtil.get_type(self.current()) == TokenType.SEP_COMMA:
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
    @exp_type('exp')
    def parse_exp(self):
        # parse the expr by such precedence:  exp13 > exp12 > exp11 > ... > exp0
        # TODO: build a precedence map
        return self.parse_exp13()

    # exp1 ==> exp2
    def parse_exp13(self):
        exp = self.parse_exp12()
        if ParserUtil.get_token_value(self.current()) == '==>':
            self.skip(1)
            exp = can_ast.MappingExp(exp, self.parse_exp12())
        return exp

    # exp1 or exp2
    def parse_exp12(self):
        exp = self.parse_exp11()
        while ParserUtil.get_token_value(self.current()) in ['or', '或者']:
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, 'or', exp, self.parse_exp11())
        return exp

    # exp1 and exp2
    def parse_exp11(self):
        exp = self.parse_exp10()
        while ParserUtil.get_token_value(self.current()) in ['and', '同埋']:
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, 'and', exp, self.parse_exp10())
        return exp

    # Compare
    def parse_exp10(self):
        exp = self.parse_exp9()
        while True:
            now = self.current()
            if ParserUtil.get_token_value(now) in ('>', '>=', '<', '<=', '==', '!=', kw_is):
                line, op = now[0], ParserUtil.get_token_value(now)
                self.skip(1)
                exp = can_ast.BinopExp(line, op if op != kw_is else '==', exp, self.parse_exp9())
            
            elif ParserUtil.get_token_value(now) in ('in', kw_in, tr_kw_in):
                line = now[0]
                self.skip(1)
                exp = can_ast.BinopExp(line, ' in ', exp, self.parse_exp9())
            
            elif ParserUtil.get_token_value(now) == '比唔上':
                line = now[0]
                self.skip(1)
                exp = can_ast.BinopExp(line, '<', exp, self.parse_exp9())

            else:
                break
        return exp
    
    # exp1 <|> exp2
    def parse_exp9(self):
        exp = self.parse_exp8()
        while ParserUtil.get_type(self.current()) == TokenType.OP_BOR or \
            ParserUtil.get_token_value(self.current()) == "或":
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '|', exp, self.parse_exp8())
        return exp

    # exp1 ^ exp2
    def parse_exp8(self):
        exp = self.parse_exp7()
        while ParserUtil.get_type(self.current()) == TokenType.OP_WAVE or \
            ParserUtil.get_token_value(self.current()) == "异或":
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '^', exp, self.parse_exp8())
        return exp

    # exp1 & exp2
    def parse_exp7(self):
        exp = self.parse_exp6()
        while ParserUtil.get_type(self.current()) == TokenType.OP_BAND or \
            ParserUtil.get_token_value(self.current()) == '与':
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '&', exp, self.parse_exp8())
        return exp

    # shift
    def parse_exp6(self):
        exp = self.parse_exp5()
        if ParserUtil.get_type(self.current()) in (TokenType.OP_SHL, TokenType.OP_SHR):
            line = self.current()[0]
            op = ParserUtil.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp5())
        
        elif ParserUtil.get_token_value(self.current()) == '左移':
            line, op = self.current()[0], "<<"
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp5())
        
        elif ParserUtil.get_token_value(self.current()) == '右移':
            line, op = self.current()[0], ">>"
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp5())
        
        else:
            return exp
        return exp

    # exp1 <-> exp2
    def parse_exp5(self):
        exp = self.parse_exp4()
        if (ParserUtil.get_type(self.current()) != TokenType.OP_CONCAT):
            return exp
        
        line = 0
        exps = [exp]
        while ParserUtil.get_type(self.current()) == TokenType.OP_CONCAT:
            line = self.current()[0]
            self.skip(1)
            exps.append(self.parse_exp4())
        return can_ast.ConcatExp(line, exps)

    # exp1 + / - exp2
    def parse_exp4(self):
        exp = self.parse_exp3()
        while True:
            if ParserUtil.get_type(self.current()) in (TokenType.OP_ADD, TokenType.OP_MINUS):
                line, op = self.current()[0], ParserUtil.get_token_value(self.current())
                self.skip(1) # skip the op
                exp = can_ast.BinopExp(line, op, exp, self.parse_exp3())
            
            elif ParserUtil.get_token_value(self.current()) == '加':
                line = self.current()[0]
                self.skip(1) # skip the op
                exp = can_ast.BinopExp(line, '+', exp, self.parse_exp3())
            
            elif ParserUtil.get_token_value(self.current()) == '减':
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
            if ParserUtil.get_type(self.current()) in (TokenType.OP_MUL, TokenType.OP_MOD, 
                    TokenType.OP_DIV, TokenType.OP_IDIV):
                line, op = self.current()[0], ParserUtil.get_token_value(self.current())
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, op, exp, self.parse_exp2())
            
            elif ParserUtil.get_token_value(self.current()) == '乘':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '*', exp, self.parse_exp2())

            elif ParserUtil.get_token_value(self.current()) == '余':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '%', exp, self.parse_exp2())

            elif ParserUtil.get_token_value(self.current()) == '整除':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '//', exp, self.parse_exp2())

            elif ParserUtil.get_token_value(self.current()) == '除':
                line = self.current()[0]
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, '//', exp, self.parse_exp2())

            else:
                break
        
        return exp

    # unop exp
    def parse_exp2(self):
        if ParserUtil.get_type(self.current()) == TokenType.OP_NOT or \
            ParserUtil.get_token_value(self.current()) == 'not' or \
            ParserUtil.get_token_value(self.current()) == '-' or \
            ParserUtil.get_token_value(self.current()) == '~':
            line, op = self.current()[0], ParserUtil.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.UnopExp(line, op, self.parse_exp2())
            return exp

        elif ParserUtil.get_type(self.current()) == '取反':
            line, op = self.current()[0], '~'
            self.skip(1) # Skip the op
            exp = can_ast.UnopExp(line, op, self.parse_exp2())
            return exp

        return self.parse_exp1()

    # x ** y
    def parse_exp1(self):
        exp = self.parse_exp0()
        if ParserUtil.get_type(self.current()) == TokenType.OP_POW:
            line, op = self.current()[0], ParserUtil.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(line, op, exp, self.parse_exp2())
        return exp

    def parse_exp0(self):
        tk = self.current()
        if ParserUtil.get_token_value(tk) == '<*>':
            self.skip(1)
            return can_ast.VarArgExp(tk[0])
        
        elif ParserUtil.get_token_value(tk) in [kw_false, tr_kw_false, "False"]:
            self.skip(1)
            return can_ast.FalseExp(tk[0])
        
        elif ParserUtil.get_token_value(tk) in [kw_true, tr_kw_true, "True"]:
            self.skip(1)
            return can_ast.TrueExp(tk[0])
        
        elif ParserUtil.get_token_value(tk) in [kw_none, tr_kw_none, "None"]:
            self.skip(1)
            return can_ast.NullExp(tk[0])
        
        elif ParserUtil.get_type(tk) == TokenType.NUM:
            self.skip(1)
            return can_ast.NumeralExp(tk[0], ParserUtil.get_token_value(tk))
        
        elif ParserUtil.get_type(tk) == TokenType.STRING:
            self.skip(1)
            return can_ast.StringExp(tk[0], ParserUtil.get_token_value(tk))

        elif ParserUtil.get_type(tk) == TokenType.SEP_LBRACK:
            return self.parse_listcons()

        elif ParserUtil.get_type(tk) == TokenType.SEP_LCURLY:
            return self.parse_mapcons()

        # lambda function
        elif ParserUtil.get_token_value(tk) == '$$':
            return self.parse_functiondef_expr()

        # If-Else expr
        elif ParserUtil.get_token_value(tk) in [kw_expr_if, tr_kw_expr_if]:
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
          | prefixexp '==>' id
    """
    @exp_type('prefixexp')
    def parse_prefixexp(self):
        if ParserUtil.get_type(self.current()) == TokenType.IDENTIFIER:
            line, name = self.current()[0], ParserUtil.get_token_value(self.current())
            self.skip(1)
            exp = can_ast.IdExp(line, name)
        elif ParserUtil.get_type(self.current()) == TokenType.SEPCIFIC_ID_BEG:
            self.skip(1)
            name = ParserUtil.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0))
            exp = can_ast.SpecificIdExp(name)
            self.get_next_token_of_kind(TokenType.SEPICFIC_ID_END, 0)
        # '(' exp ')'
        elif ParserUtil.get_type(self.current()) == TokenType.SEP_LPAREN:
            exp = self.parse_parens_exp()
        # '|' exp '|'
        else:
            exp = self.parse_brack_exp()
        return self.finish_prefixexp(exp)
        
    @exp_type('parens_exp')
    def parse_parens_exp(self):
        self.get_next_token_of_kind(TokenType.SEP_LPAREN, 0)
        exp = self.parse_exp()
        self.get_next_token_of_kind(TokenType.SEP_RPAREN, 0)
        return exp

    @exp_type('brack_exp')
    def parse_brack_exp(self):
        self.get_next_token_of('|', 0)
        exp = self.parse_exp()
        self.get_next_token_of('|', 0)
        return exp

    """
    listcons := '[' exp_list ']'
    """
    @exp_type('listcons')
    def parse_listcons(self):
        self.get_next_token_of_kind(TokenType.SEP_LBRACK, 0)
        if ParserUtil.get_type(self.current()) == TokenType.SEP_RBRACK: # []
            self.skip(1)
            return can_ast.ListExp("")
        else:
            exps = self.parse_exp_list()
            self.get_next_token_of_kind(TokenType.SEP_RBRACK, 0)
            return can_ast.ListExp(exps)

    """
    set_or_mapcons := '{' exp_list '}'
    """
    @exp_type('mapcons')
    def parse_mapcons(self):
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
        if ParserUtil.get_type(self.current()) == TokenType.SEP_RCURLY: # {}
            self.skip(1)
            return can_ast.MapExp("")
        else:
            exps = self.parse_exp_list()
            self.get_next_token_of_kind(TokenType.SEP_RCURLY, 0)
            return can_ast.MapExp(exps)
        

    def finish_prefixexp(self, exp : can_ast.AST):
        while True:
            kind, value = ParserUtil.get_type(self.current()), ParserUtil.get_token_value(self.current())
            if kind == TokenType.SEP_LBRACK:
                self.skip(1)
                key_exp : can_ast.AST = self.parse_exp()
                self.get_next_token_of_kind(TokenType.SEP_RBRACK, 0)
                exp = can_ast.ListAccessExp(self.get_line(), exp, key_exp)
            elif kind == TokenType.SEP_DOT or \
                (kind == TokenType.KEYWORD and value == kw_do):
                if ParserUtil.get_type(self.look_ahead(1)) == TokenType.SEP_LCURLY:
                    # || -> { ... } means we in a method define statement. So break it.
                    break
                # Otherwise it's a ObjectAccessExp
                else:
                    self.skip(1)
                    tk = self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)
                    line, name = tk[0], ParserUtil.get_token_value(tk)
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
        if (ParserUtil.get_token_value(self.current()) == kw_call_begin):
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

    @exp_type('parlist')
    def parse_parlist(self):
        if ParserUtil.get_type(self.current()) == TokenType.IDENTIFIER or \
            ParserUtil.get_token_value(self.current()) == '<*>':
            par_parser = ParExpParser(self.tokens[self.pos : ])
            exps = par_parser.parse_exp_list()
            self.skip(par_parser.pos)
            del par_parser # free the memory
            return exps
        
        elif ParserUtil.get_token_value(self.current()) == '|':
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
    @exp_type('idlist')
    def parse_idlist(self):
        tk = self.current()
        if (ParserUtil.get_type(tk) == TokenType.IDENTIFIER):
            ids = [can_ast.IdExp(self.get_line(), 
                ParserUtil.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)))]
            while ParserUtil.get_type(self.current()) == TokenType.SEP_COMMA:
                self.skip(1)
                if (ParserUtil.get_type(self.current()) != TokenType.IDENTIFIER):
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(self.get_line(), 
                        ParserUtil.get_token_value(self.current())))
                self.skip(1)
            return ids

        elif (ParserUtil.get_token_value(tk) == '|'):
            self.skip(1)
            ids = [can_ast.IdExp(self.get_line(), 
                ParserUtil.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)))]
            while ParserUtil.get_type(self.current()) == TokenType.SEP_COMMA:
                self.skip(1)
                if (ParserUtil.get_type(self.current()) != TokenType.IDENTIFIER):
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(self.get_line(), 
                        ParserUtil.get_token_value(self.current())))
                self.skip(1)
            self.get_next_token_of('|', 0)
            return ids

    """
    lambda_functoindef ::= '$$' idlist '->' block '搞掂'
    """
    @exp_type('functiondef_expr')
    def parse_functiondef_expr(self):
        self.skip(1)
        idlist : list = self.parse_idlist()
        blocks : list = []
        self.get_next_token_of(kw_do, 0)
        blocks.append(self.parse_exp())
        self.get_next_token_of([kw_func_end, tr_kw_func_end], 0)
        return can_ast.LambdaExp(idlist, blocks)

    @exp_type('if_else_expr')
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
    @exp_type('args')
    def parse_args(self):
        args = []
        tk = self.current()
        if ParserUtil.get_token_value(tk) == '(':
            self.skip(1)
            if ParserUtil.get_token_value(self.current()) != ')':
                args = self.parse_exp_list()
            self.get_next_token_of_kind(TokenType.SEP_RPAREN, step = 0)
        elif ParserUtil.get_token_value(tk) == '|':
            self.skip(1)
            if ParserUtil.get_token_value(self.current()) != '|':
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
    @exp_type('exp')
    def parse_exp(self):
        return self.parse_exp0()

    # override
    def parse_exp0(self):
        tk = self.current()

        if ParserUtil.get_token_value(tk) == '<*>':
            self.skip(1)
            return can_ast.VarArgExp(tk[0])
        
        return self.parse_prefixexp()

    # override
    @exp_type('prefixexp')
    def parse_prefixexp(self):
        if ParserUtil.get_type(self.current()) == TokenType.IDENTIFIER:
            line, name = self.current()[0], ParserUtil.get_token_value(self.current())
            self.skip(1)
            exp = can_ast.IdExp(line, name)
            return self.finish_prefixexp(exp)
        else:
            raise Exception("Parlist must be a identifier type!")

    # override
    def finish_prefixexp(self, exp: can_ast.AST):
        kind = ParserUtil.get_type(self.current())
        value = ParserUtil.get_token_value(self.current())
        if value == '=' or value == '==>':
            self.skip(1)
            exp_parser = ExpParser(self.tokens[self.pos : ])
            exp2 = exp_parser.parse_exp()
            self.skip(exp_parser.pos)
            del exp_parser # free the memory
            return can_ast.AssignExp(exp, exp2)
        return exp

class StatParser(ParserBase):
    def __init__(self, token_list : list, expParser = ExpParser) -> None:
        super(StatParser, self).__init__(token_list)
        self.pos = 0
        self.tokens = token_list

        # Function address type:
        # We can choose the class `ExpParser` Or `ClassBlockExpParser`
        self.ExpParser = expParser

    def getExpParser(self):
        return self.ExpParser(self.tokens[self.pos : ])

    def parse(self):
        tk = self.current()
        kind = ParserUtil.get_type(tk)
        tk_value = ParserUtil.get_token_value(tk)
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
                if ParserUtil.get_token_value(self.current()) == '|':
                    prefix_exps = []
                    skip_step = 0
                else:
                    exp_parser = self.ExpParser(self.tokens[self.pos : ])
                    prefix_exps = exp_parser.parse_exp_list()
                    skip_step = exp_parser.pos # we will skip it in parse_for_stat
                    del exp_parser
                
                self.get_next_token_of('|', skip_step)

                if ParserUtil.get_token_value(self.look_ahead(skip_step)) in [kw_from, tr_kw_from]:
                    return self.parse_for_stat(prefix_exps, skip_step)
                
                elif ParserUtil.get_token_value(self.look_ahead(skip_step)) in [kw_call_begin, tr_kw_call_begin]:
                    return self.parse_func_call_stat(prefix_exps, skip_step)
                
                elif ParserUtil.get_token_value(self.look_ahead(skip_step)) in [kw_lst_assign, tr_kw_lst_assign]:
                    return self.parse_list_assign_stat(prefix_exps, skip_step)

                elif ParserUtil.get_token_value(self.look_ahead(skip_step)) in [kw_set_assign, tr_kw_set_assign]:
                    return self.parse_set_assign_stat(prefix_exps, skip_step)
                
                elif ParserUtil.get_token_value(self.look_ahead(skip_step)) in [kw_do, tr_kw_do]:
                    return self.parse_class_method_call_stat(prefix_exps, skip_step) 

            elif tk_value == '<<<':
                return self.parse_func_def_with_type_stat()

            elif tk_value == '<$>':
                return self.parse_match_mode_func_def_stat()

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
                return self.exp_type_stat()

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
            if ParserUtil.get_token_value(self.look_ahead(1)) in [kw_from, tr_kw_from]:
                return self.parse_for_stat()
            
            elif ParserUtil.get_token_value(self.look_ahead(1)) in [kw_call_begin, tr_kw_call_begin]:
                return self.parse_func_call_stat()

            elif ParserUtil.get_token_value(self.look_ahead(1)) in [kw_do, tr_kw_do]:
                return self.parse_class_method_call_stat()

        elif kind == TokenType.EOF:
            return
        
        else:
            raise Exception("Unknown grammer in %s" % (str(self.get_line())))
            
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
        args = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_args)
        self.get_next_token_of([kw_endprint, tr_kw_endprint], step = 0)
        return can_ast.PrintStat(args)

    # Parser for muti-assign
    def parse_assign_block(self):
        # Nothing in assignment block
        if ParserUtil.get_type(self.current()) == TokenType.SEP_RCURLY:
            self.skip(1)
            return can_ast.AssignStat(self.get_line(), can_ast.AST, can_ast.AST)
        var_list : list = []
        exp_list : list= []
        while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
            var_list.append(self.parse_var_list()[0])
            self.get_next_token_of([kw_is, kw_is_2, kw_is_3], 0)
            exp_list.append(ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)[0])

        # Skip the SEP_RCURLY
        self.skip(1)
        return can_ast.AssignBlockStat(self.get_line(), var_list, exp_list)

    def parse_assign_stat(self):
        self.skip(1)
        if ParserUtil.get_token_value(self.current()) != kw_do:
            var_list = self.parse_var_list()
            self.get_next_token_of([kw_is, kw_is_2, kw_is_3], 0)
            exp_list = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
            last_line = self.get_line()
            return can_ast.AssignStat(last_line, var_list, exp_list)
        else:
            # Skip the kw_do
            self.skip(1)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            return self.parse_assign_block()
            # The SEP_RCURLY will be checked in self.parse_assign_block()

    def parse_var_list(self):
        exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_prefixexp)
        var_list : list = [self.check_var(exp)]
    
        while ParserUtil.get_type(self.current()) == TokenType.SEP_COMMA:
            self.skip(1)
            exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_prefixexp)
            var_list.append(self.check_var(exp))

        return var_list

    def check_var(self, exp : can_ast.AST):
        if isinstance(exp, (can_ast.IdExp, can_ast.ObjectAccessExp, 
                            can_ast.ListAccessExp, can_ast.MappingExp,
                            can_ast.ClassSelfExp)):
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

        if_exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        self.get_next_token_of([kw_then, tr_kw_then], 0)
        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

        while (ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY):
            block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            if_blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser # free the memory
        self.skip(1) # Skip the SEP_RCURLY '}'

        while ParserUtil.get_token_value(self.current()) in [kw_elif, tr_kw_elif]:
            self.skip(1) # skip and try to get the next token
            elif_exps.append(ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp))
            self.get_next_token_of([kw_then, tr_kw_then], 0)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            
            elif_block : list = []
            
            while (ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY):
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                elif_block.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser # free the memory
            elif_blocks.append(elif_block)

            self.skip(1) # Skip the SEP_RCURLY '}'

        if ParserUtil.get_token_value(self.current()) == kw_else_or_not:
            self.skip(1) # Skip and try yo get the next token
            self.get_next_token_of([kw_then, tr_kw_then], 0)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            while (ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY):
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                else_blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser # free the memory
            self.skip(1) # Skip the SEP_RCURLY '}'

        return can_ast.IfStat(if_exps, if_blocks, elif_exps, elif_blocks, else_blocks)


    def parse_import_stat(self):
        self.skip(1) # Skip the kw_import
        idlist = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_idlist)
        return can_ast.ImportStat(idlist)

    def parse_global_stat(self):
        self.skip(1) # Skip the kw_global
        idlist = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_idlist)
        return can_ast.GlobalStat(idlist)

    def parse_break_stat(self):
        self.skip(1) # Skip the kw_break
        return can_ast.BreakStat()

    def parse_while_stat(self):
        self.skip(1) # Skip the kw_while_do
        blocks : list = []
        cond_exps : list = []
        while (ParserUtil.get_token_value(self.current()) != kw_while):
            block_parser =  StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser # free the memory

        self.skip(1) # Skip the kw_while
        
        cond_exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        self.get_next_token_of([kw_whi_end, tr_kw_whi_end], 0)

        return can_ast.WhileStat(can_ast.UnopExp(self.get_line(), 'not', cond_exps), blocks)

    def parse_for_stat(self, prefix_exp : ExpParser = None, skip_prefix_exp : int = 0):
        blocks : list = []

        if prefix_exp == None:
            id = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)

        else:
            id = prefix_exp[0]
            self.skip(skip_prefix_exp)
        
        self.get_next_token_of([kw_from, tr_kw_from], 0)

        from_exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        self.get_next_token_of([kw_to, tr_kw_to], 0)

        to_exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)

        while (ParserUtil.get_token_value(self.current()) not in [kw_endfor, tr_kw_endfor]):
            block_parse = StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(block_parse.parse())
            self.skip(block_parse.pos)
            del block_parse # free the memory

        self.skip(1)

        return can_ast.ForStat(id, from_exp, to_exp, blocks)

    def parse_func_def_with_type_stat(self):
        self.get_next_token_of("<<<", 0)

        args_type : list = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_parlist)
        args_type = [] if args_type == None else args_type

        self.get_next_token_of("收皮", 0)
        
        if (ParserUtil.get_token_value(self.current())) != '>>>':
            rets_type = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_idlist)

        rets_type = [] if rets_type == None else rets_type

        self.get_next_token_of('>>>', 0)

        return self.parse_func_def_stat(decl_args_type=args_type, decl_ret_type=rets_type)

    def parse_match_mode_func_def_stat(self):
        args_list : list = []
        block_list : list = []
        while (ParserUtil.get_token_value(self.current()) == '<$>'):
            self.skip(1)

            name = ParserUtil.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0))            
            args : list = ParserUtil.parse_exp(self, self.getExpParser(), by=self.Exp_parser.parse_exp_list)
            args = [] if args == None else args

            args_list.append(args)

            self.get_next_token_of("即係", 0)
            self.get_next_token_of([kw_do], 0)
            body = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)

            block_list.append(body)

            self.get_next_token_of([kw_func_end, tr_kw_func_end], 0)
        
        return can_ast.MatchModeFuncDefStat(can_ast.IdExp(self.get_line(), name), args_list, block_list)

    def parse_func_def_stat(self, decl_args_type = [], decl_ret_type = []):
        self.get_next_token_of(kw_function, 0)
        
        name = ParserUtil.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0))            
        exp_parser = self.ExpParser(self.tokens[self.pos : ])
        args : list = exp_parser.parse_parlist()
        args = [] if args == None else args
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        self.get_next_token_of([kw_func_begin, tr_kw_func_begin, kw_do], 0)

        blocks : list = []
        while (ParserUtil.get_token_value(self.current()) not in [kw_func_end, tr_kw_func_end]):
            block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser

        self.skip(1)
        return can_ast.FunctionDefStat(can_ast.IdExp(self.get_line(), name), args, blocks, 
                                    decl_args_type, decl_ret_type)

    def parse_func_call_stat(self, prefix_exps : can_ast.AST = None, skip_step : int = 0):
        if prefix_exps == None:
            func_name = can_ast.IdExp(self.get_line(), ParserUtil.get_token_value(self.current()))
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

        if ParserUtil.get_token_value(self.current()) == kw_get_value:
            self.skip(1)
            var_list = self.parse_var_list()
            return can_ast.AssignStat(self.get_line(), var_list,
                    [can_ast.FuncCallExp(func_name, args)])
        else:
            return can_ast.FuncCallStat(func_name, args)

    def parse_class_method_call_stat(self, prefix_exps : can_ast.AST = None, skip_step : int = 0):
        if prefix_exps == None:
            name_exp = can_ast.IdExp(self.get_line(), ParserUtil.get_token_value(self.current()))
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
        exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        return can_ast.AssertStat(exp)

    def parse_return_stat(self):
        self.skip(1)
        exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
        return can_ast.ReturnStat(exps)

    def parse_del_stat(self):
        self.skip(1)
        exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
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

        while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
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
        while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            except_block.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser
        
        self.skip(1)
        except_blocks.append(except_block)

        while ParserUtil.get_token_value(self.current()) in [kw_except, tr_kw_except]:
            self.get_next_token_of([kw_then, tr_kw_then], 0)

            exp_parser = self.ExpParser(self.tokens[self.pos : ])
            except_exps.append(exp_parser.parse_exp())
            self.skip(exp_parser.pos)
            del exp_parser

            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

            # clear the list
            except_block = []
            while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                except_block.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser
            
            except_blocks.append(except_block)

        if ParserUtil.get_token_value(self.current()) in [kw_finally, tr_kw_finally]:
            self.skip(1)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

            while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
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

    def exp_type_stat(self):
        self.skip(1)
        name_exp = ParserUtil.parse_exp(self, self.getExpParser(), self.ExpParser.parse_exp)

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
        
        while ParserUtil.get_token_value(self.current()) not in [kw_endclass, tr_kw_endclass]:
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

        while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
            while ParserUtil.get_token_value(self.current()) in [kw_case, tr_kw_case]:
                self.skip(1)
                exp_parser = self.ExpParser(self.tokens[self.pos : ])
                match_val.append(exp_parser.parse_exp())
                self.skip(exp_parser.pos)
                del exp_parser # free the memory

                self.get_next_token_of(kw_do, 0)
                self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

                block : list = []

                while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
                    stat_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
                    block.append(stat_parser.parse())
                    self.skip(stat_parser.pos)
                    del stat_parser # free the memory

                self.skip(1)
                match_block.append(block)
            
            if ParserUtil.get_token_value(self.current()) == kw_else_or_not:
                self.skip(1)
                self.get_next_token_of([kw_then, tr_kw_then], 0)
                self.get_next_token_of(kw_do, 0)
                self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)

                while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
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

        while (ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY):
            stat_parser = StatParser(self.tokens[self.pos : ], self.ExpParser)
            blocks.append(stat_parser.parse())
            self.skip(stat_parser.pos)
            del stat_parser # free the memory
        
        self.skip(1)

        return can_ast.ForEachStat(id_list, exp_list, blocks)

    def parse_extend_stat(self):
        self.skip(1)
        tk = self.get_next_token_of_kind(TokenType.EXTEND_EXPR, 0)
        return can_ast.ExtendStat(ParserUtil.get_token_value(tk)[1 : -1])

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

        while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
            if ParserUtil.get_token_value(self.current()) in instruction_ident and \
                ParserUtil.get_type(self.current()) == TokenType.IDENTIFIER:
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
        tk = ParserUtil.get_token_value(self.current())

class ClassBlockExpParser(ExpParser):
    def __init__(self, token_list: list) -> None:
        super().__init__(token_list)

    # Override
    def parse_exp0(self):
        tk = ParserUtil.get_token_value(self.current())
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
        if ParserUtil.get_type(self.current()) == TokenType.SEP_LCURLY:
            self.skip(1)
            while ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY:
                block_parser = ClassBlockStatParser(self.tokens[self.pos : ], self.ExpParser)
                blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser
        
        # '=> ... '%%'
        else:
            while (ParserUtil.get_token_value(self.current()) not in [kw_func_end, tr_kw_func_end]):
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
        while (ParserUtil.get_type(self.current()) != TokenType.SEP_RCURLY):
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
        kind = ParserUtil.get_type(tk)
        tk_value = ParserUtil.get_token_value(tk)
        if tk_value in [kw_method, tr_kw_method]:
            return self.parse_method_block()
        elif tk_value in [kw_class_assign, tr_kw_class_assign]:
            return self.parse_class_assign_stat()
        elif tk_value in [kw_class_init, tr_kw_class_init]:
            return self.parse_class_init_stat()
        else:
            return super().parse()