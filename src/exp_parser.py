from can_lexer import *
from Ast import can_ast
from parser_base import *
from util.can_utils import ParserUtil, exp_type

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
            self.skip(1)
            exp = can_ast.BinopExp('or', exp, self.parse_exp11())
        return exp

    # exp1 and exp2
    def parse_exp11(self):
        exp = self.parse_exp10()
        while ParserUtil.get_token_value(self.current()) in ['and', '同埋']:
            self.skip(1)
            exp = can_ast.BinopExp('and', exp, self.parse_exp10())
        return exp

    # Compare
    def parse_exp10(self):
        exp = self.parse_exp9()
        while True:
            now = self.current()
            if ParserUtil.get_token_value(now) in ('>', '>=', '<', '<=', '==', '!=', kw_is):
                op = ParserUtil.get_token_value(now)
                self.skip(1)
                exp = can_ast.BinopExp(op if op != kw_is else '==', exp, self.parse_exp9())
            
            elif ParserUtil.get_token_value(now) in ('in', kw_in):
                self.skip(1)
                exp = can_ast.BinopExp(' in ', exp, self.parse_exp9())
            
            elif ParserUtil.get_token_value(now) == '比唔上':
                self.skip(1)
                exp = can_ast.BinopExp('<', exp, self.parse_exp9())

            else:
                break
        return exp
    
    # exp1 <|> exp2
    def parse_exp9(self):
        exp = self.parse_exp8()
        while ParserUtil.get_type(self.current()) == TokenType.OP_BOR or \
            ParserUtil.get_token_value(self.current()) == "或":
            self.skip(1)
            exp = can_ast.BinopExp('|', exp, self.parse_exp8())
        return exp

    # exp1 ^ exp2
    def parse_exp8(self):
        exp = self.parse_exp7()
        while ParserUtil.get_type(self.current()) == TokenType.OP_WAVE or \
            ParserUtil.get_token_value(self.current()) == "異或":
            self.skip(1)
            exp = can_ast.BinopExp('^', exp, self.parse_exp8())
        return exp

    # exp1 & exp2
    def parse_exp7(self):
        exp = self.parse_exp6()
        while ParserUtil.get_type(self.current()) == TokenType.OP_BAND or \
            ParserUtil.get_token_value(self.current()) == '與':
            self.skip(1)
            exp = can_ast.BinopExp('&', exp, self.parse_exp8())
        return exp

    # shift
    def parse_exp6(self):
        exp = self.parse_exp5()
        if ParserUtil.get_type(self.current()) in (TokenType.OP_SHL, TokenType.OP_SHR):
            op = ParserUtil.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(op, exp, self.parse_exp5())
        
        elif ParserUtil.get_token_value(self.current()) == '左移':
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp("<<", exp, self.parse_exp5())
        
        elif ParserUtil.get_token_value(self.current()) == '右移':
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(">>", exp, self.parse_exp5())
        
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
            line = self.current().lineno
            self.skip(1)
            exps.append(self.parse_exp4())
        return can_ast.ConcatExp(line, exps)

    # exp1 + / - exp2
    def parse_exp4(self):
        exp = self.parse_exp3()
        while True:
            if ParserUtil.get_type(self.current()) in (TokenType.OP_ADD, TokenType.OP_MINUS):
                op = ParserUtil.get_token_value(self.current())
                self.skip(1) # skip the op
                exp = can_ast.BinopExp(op, exp, self.parse_exp3())
            
            elif ParserUtil.get_token_value(self.current()) == '加':
                self.skip(1) # skip the op
                exp = can_ast.BinopExp('+', exp, self.parse_exp3())
            
            elif ParserUtil.get_token_value(self.current()) == '減':
                self.skip(1) # skip the op
                exp = can_ast.BinopExp('-', exp, self.parse_exp3())
            
            else:
                break
        
        return exp

     # *, %, /, //
    def parse_exp3(self):
        exp = self.parse_exp2()
        while True:
            if ParserUtil.get_type(self.current()) in (TokenType.OP_MUL, TokenType.OP_MOD, 
                    TokenType.OP_DIV, TokenType.OP_IDIV):
                line, op = self.current().lineno, ParserUtil.get_token_value(self.current())
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(op, exp, self.parse_exp2())
            
            elif ParserUtil.get_token_value(self.current()) == '乘':
                line = self.current().lineno
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp('*', exp, self.parse_exp2())

            elif ParserUtil.get_token_value(self.current()) == '餘':
                line = self.current().lineno
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp('%', exp, self.parse_exp2())

            elif ParserUtil.get_token_value(self.current()) == '整除':
                line = self.current().lineno
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp('//', exp, self.parse_exp2())

            elif ParserUtil.get_token_value(self.current()) == '除':
                line = self.current().lineno
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp('//', exp, self.parse_exp2())

            else:
                break
        
        return exp

    # unop exp
    def parse_exp2(self):
        if ParserUtil.get_type(self.current()) == TokenType.OP_NOT or \
            ParserUtil.get_token_value(self.current()) == 'not' or \
            ParserUtil.get_token_value(self.current()) == '-' or \
            ParserUtil.get_token_value(self.current()) == '~':
            op = ParserUtil.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.UnopExp(op, self.parse_exp2())
            return exp

        elif ParserUtil.get_type(self.current()) == '取反':
            op = '~'
            self.skip(1) # Skip the op
            exp = can_ast.UnopExp(op, self.parse_exp2())
            return exp

        return self.parse_exp1()

    # x ** y
    def parse_exp1(self):
        exp = self.parse_exp0()
        if ParserUtil.get_type(self.current()) == TokenType.OP_POW:
            line, op = self.current().lineno, ParserUtil.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.BinopExp(op, exp, self.parse_exp2())
        return exp

    def parse_exp0(self):
        tk = self.current()
        if ParserUtil.get_token_value(tk) == '<*>':
            self.skip(1)
            return can_ast.VarArgExp()
        
        elif ParserUtil.get_token_value(tk) in [kw_false, "False"]:
            self.skip(1)
            return can_ast.FalseExp()
        
        elif ParserUtil.get_token_value(tk) in [kw_true, "True"]:
            self.skip(1)
            return can_ast.TrueExp()
        
        elif ParserUtil.get_token_value(tk) in [kw_none, "None"]:
            self.skip(1)
            return can_ast.NullExp()
        
        elif ParserUtil.get_type(tk) == TokenType.NUM:
            self.skip(1)
            return can_ast.NumeralExp(ParserUtil.get_token_value(tk))
        
        elif ParserUtil.get_type(tk) == TokenType.STRING:
            self.skip(1)
            return can_ast.StringExp(ParserUtil.get_token_value(tk))

        elif ParserUtil.get_type(tk) == TokenType.SEP_LBRACK:
            return self.parse_listcons()

        elif ParserUtil.get_type(tk) == TokenType.SEP_LCURLY:
            return self.parse_mapcons()

        # lambda function
        elif ParserUtil.get_token_value(tk) == '$$':
            return self.parse_functiondef_expr()

        # If-Else expr
        elif ParserUtil.get_token_value(tk) in [kw_expr_if]:
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
            line, name = self.current().lineno, ParserUtil.get_token_value(self.current())
            self.skip(1)
            exp = can_ast.IdExp(name)
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
                exp = can_ast.ListAccessExp(exp, key_exp)
            elif kind == TokenType.SEP_DOT or \
                (kind == TokenType.KEYWORD and value == kw_do):
                if ParserUtil.get_type(self.look_ahead(1)) == TokenType.SEP_LCURLY:
                    # || -> { ... } means we in a method define statement. So break it.
                    break
                # Otherwise it's a ObjectAccessExp
                else:
                    self.skip(1)
                    tk = self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)
                    name = ParserUtil.get_token_value(tk)
                    key_exp = can_ast.IdExp(name)
                    exp = can_ast.ObjectAccessExp(exp, key_exp)
            elif (kind == TokenType.SEP_LPAREN) or \
                (kind == TokenType.KEYWORD and value == kw_call_begin):
                exp = self.finish_functioncall_exp(exp)
            elif value == '嘅長度':
                self.skip(1)
                key_exp = can_ast.IdExp('__len__()')
                exp = can_ast.ObjectAccessExp(exp, key_exp)
            elif kind == TokenType.OP_ASSIGN:
                self.skip(1)
                exp = can_ast.AssignExp(exp, self.parse_exp())
            # TODO: Fix bugs here
            elif value in [kw_get_value]:
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
            ids = [can_ast.IdExp(
                ParserUtil.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)))]
            while ParserUtil.get_type(self.current()) == TokenType.SEP_COMMA:
                self.skip(1)
                if (ParserUtil.get_type(self.current()) != TokenType.IDENTIFIER):
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp( 
                        ParserUtil.get_token_value(self.current())))
                self.skip(1)
            return ids

        elif (ParserUtil.get_token_value(tk) == '|'):
            self.skip(1)
            ids = [can_ast.IdExp( 
                ParserUtil.get_token_value(self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)))]
            while ParserUtil.get_type(self.current()) == TokenType.SEP_COMMA:
                self.skip(1)
                if (ParserUtil.get_type(self.current()) != TokenType.IDENTIFIER):
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp( 
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
        self.get_next_token_of(kw_func_end, 0)
        return can_ast.LambdaExp(idlist, blocks)

    @exp_type('if_else_expr')
    def parse_if_else_expr(self):
        self.skip(1)
        CondExp : can_ast.AST = self.parse_exp()
        self.get_next_token_of(kw_do, 0)
        IfExp : can_ast.AST = self.parse_exp()
        self.get_next_token_of(kw_expr_else, 0)
        self.get_next_token_of(kw_do, 0)
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
    def __init__(self, token_list: list, file="") -> None:
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
            return can_ast.VarArgExp()
        
        return self.parse_prefixexp()

    # override
    @exp_type('prefixexp')
    def parse_prefixexp(self):
        if ParserUtil.get_type(self.current()) == TokenType.IDENTIFIER:
            line, name = self.current().lineno, ParserUtil.get_token_value(self.current())
            self.skip(1)
            exp = can_ast.IdExp(name)
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

class ClassBlockExpParser(ExpParser):
    def __init__(self, token_list: list) -> None:
        super().__init__(token_list)

    # Override
    def parse_exp0(self):
        tk = ParserUtil.get_token_value(self.current())
        if tk in [kw_self, '@@']:
            self.skip(1)
            return can_ast.ClassSelfExp(super().parse_exp0())
        else:
            return super().parse_exp0()