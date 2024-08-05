from can_source.can_lexer import *
from can_source.Ast import can_ast
from can_source.parser_base import Parser_base
from can_source.util.can_utils import exp_type
from can_source.macros_parser import MacroParser

class ExpParser(Parser_base):

    @exp_type('exp_list')
    def parse_exp_list(self):
        exps = [self.parse_exp()]
        
        while self.try_look_ahead().typ == TokenType.SEP_COMMA:
            self.skip_once()
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
        if self.try_look_ahead().value == '==>':
            self.skip_once()
            exp = can_ast.MappingExp(exp, self.parse_exp12())
        return exp

    # exp1 or exp2
    def parse_exp12(self):
        exp = self.parse_exp11()
        while self.try_look_ahead().value in ['or', '或者']:
            self.skip_once()
            exp = can_ast.BinopExp('or', exp, self.parse_exp11())
        return exp

    # exp1 and exp2
    def parse_exp11(self):
        exp = self.parse_exp10()
        while self.try_look_ahead().value in ['and', '同埋']:
            self.skip_once()
            exp = can_ast.BinopExp('and', exp, self.parse_exp10())
        return exp

    # Compare
    def parse_exp10(self):
        exp = self.parse_exp9()
        while True:
            now = self.try_look_ahead()
            if now.value in ('>', '>=', '<', '<=', '==', '!=', kw_is):
                op = now.value
                self.skip_once()
                exp = can_ast.BinopExp(op if op != kw_is else '==', exp, self.parse_exp9())
            
            elif now.value in ('in', kw_in):
                self.skip_once()
                exp = can_ast.BinopExp(' in ', exp, self.parse_exp9())
            
            elif now.value == '比唔上':
                self.skip_once()
                exp = can_ast.BinopExp('<', exp, self.parse_exp9())

            else:
                break
        return exp
    
    # exp1 <|> exp2
    def parse_exp9(self):
        exp = self.parse_exp8()
        while self.try_look_ahead().typ == TokenType.OP_BOR or \
            self.try_look_ahead().value == "或":
            self.skip_once()
            exp = can_ast.BinopExp('|', exp, self.parse_exp8())
        return exp

    # exp1 ^ exp2
    def parse_exp8(self):
        exp = self.parse_exp7()
        while self.try_look_ahead().typ == TokenType.OP_WAVE or \
            self.try_look_ahead().value == "異或":
            self.skip_once()
            exp = can_ast.BinopExp('^', exp, self.parse_exp8())
        return exp

    # exp1 & exp2
    def parse_exp7(self):
        exp = self.parse_exp6()
        while self.try_look_ahead().typ == TokenType.OP_BAND or \
            self.try_look_ahead().value == '與':
            self.skip_once()
            exp = can_ast.BinopExp('&', exp, self.parse_exp8())
        return exp

    # shift
    def parse_exp6(self):
        exp = self.parse_exp5()
        if self.try_look_ahead().typ in (TokenType.OP_SHL, TokenType.OP_SHR):
            op = self.try_look_ahead().value
            self.skip_once() # Skip the op
            exp = can_ast.BinopExp(op, exp, self.parse_exp5())
        
        elif self.try_look_ahead().value == '左移':
            self.skip_once() # Skip the op
            exp = can_ast.BinopExp("<<", exp, self.parse_exp5())
        
        elif self.try_look_ahead().value == '右移':
            self.skip_once() # Skip the op
            exp = can_ast.BinopExp(">>", exp, self.parse_exp5())
        
        else:
            return exp
        return exp

    # exp1 <-> exp2
    def parse_exp5(self):
        exp = self.parse_exp4()
        if (self.try_look_ahead().typ != TokenType.OP_CONCAT):
            return exp
        
        exps = [exp]
        while self.try_look_ahead().typ == TokenType.OP_CONCAT:
            self.skip_once()
            exps.append(self.parse_exp4())
        return can_ast.ConcatExp(exps)

    # exp1 + / - exp2
    def parse_exp4(self):
        exp = self.parse_exp3()
        while True:
            if self.try_look_ahead().typ in (TokenType.OP_ADD, TokenType.OP_MINUS):
                op = self.try_look_ahead().value
                self.skip_once() # skip the op
                exp = can_ast.BinopExp(op, exp, self.parse_exp3())
            
            elif self.try_look_ahead().value == '加':
                self.skip_once() # skip the op
                exp = can_ast.BinopExp('+', exp, self.parse_exp3())
            
            elif self.try_look_ahead().value == '減':
                self.skip_once() # skip the op
                exp = can_ast.BinopExp('-', exp, self.parse_exp3())
            
            else:
                break
        
        return exp

    # *, %, /, //
    def parse_exp3(self):
        exp = self.parse_exp2()
        while True:
            if self.try_look_ahead().typ in (TokenType.OP_MUL, TokenType.OP_MOD, 
                    TokenType.OP_DIV, TokenType.OP_IDIV):
                op = self.try_look_ahead().value
                self.skip_once() # Skip the op
                exp = can_ast.BinopExp(op, exp, self.parse_exp2())
            
            elif self.try_look_ahead().value == '乘':
                self.skip_once() # Skip the op
                exp = can_ast.BinopExp('*', exp, self.parse_exp2())

            elif self.try_look_ahead().value == '餘':
                self.skip_once() # Skip the op
                exp = can_ast.BinopExp('%', exp, self.parse_exp2())

            elif self.try_look_ahead().value == '整除':
                self.skip_once() # Skip the op
                exp = can_ast.BinopExp('//', exp, self.parse_exp2())

            elif self.try_look_ahead().value == '除':
                self.skip_once() # Skip the op
                exp = can_ast.BinopExp('//', exp, self.parse_exp2())

            else:
                break
        
        return exp

    # unop exp
    def parse_exp2(self):
        if  self.try_look_ahead().value == 'not' or \
            self.try_look_ahead().value == '-' or \
            self.try_look_ahead().value == '~':
            
            op = self.try_look_ahead().value
            self.skip_once() # Skip the op
            exp = can_ast.UnopExp(op, self.parse_exp2())
            return exp

        elif self.try_look_ahead().value == '取反':
            op = '~'
            self.skip_once() # Skip the op
            exp = can_ast.UnopExp(op, self.parse_exp2())
            return exp

        return self.parse_exp1()

    # x ** y
    def parse_exp1(self):
        exp = self.parse_exp0()
        if self.try_look_ahead().typ == TokenType.OP_POW:
            op = self.try_look_ahead().value
            self.skip_once() # Skip the op
            exp = can_ast.BinopExp(op, exp, self.parse_exp2())
        return exp

    def parse_exp0(self):
        tk = self.try_look_ahead()
        if tk.value == '<*>':
            self.skip_once()
            return can_ast.VarArgExp()
                
        elif tk.typ == TokenType.NUM:
            self.skip_once()
            return can_ast.NumeralExp(tk.value)
        
        elif tk.typ == TokenType.STRING:
            self.skip_once()
            return can_ast.StringExp(tk.value)

        elif tk.typ == TokenType.SEP_LBRACK:
            return self.parse_listcons()

        elif tk.typ == TokenType.SEP_LCURLY:
            return self.parse_mapcons()

        # If-Else expr
        elif tk.value in [kw_expr_if]:
            self.skip_once()
            return self.parse_if_else_expr()
        
        return self.parse_prefixexp()
    """
    prefixexp ::= var
          | '(' exp ')'
          | '|' exp '|'
          | functioncall
          | id '=' exp

    var ::= id
          | prefixexp '[' exp ']'
          | prefixexp '->' id
          | prefixexp '==>' id
    """
    @exp_type('prefixexp')
    def parse_prefixexp(self):
        next_tk = self.try_look_ahead()
        if next_tk.typ == TokenType.IDENTIFIER:
            name = next_tk.value
            self.skip_once()
            exp = can_ast.IdExp(name)
        # '(' exp ')'
        elif next_tk.typ == TokenType.SEP_LPAREN:
            exp = self.parse_parens_exp()
        # lambda function
        elif next_tk.value == "$$":
            self.skip_once()
            exp = self.parse_functiondef_expr()
        # '|' exp '|'
        else:
            exp = self.parse_brack_exp()
        
        return self.finish_prefixexp(exp)
    
    @exp_type('parens_exp')
    def parse_parens_exp(self):
        self.eat_tk_by_kind(TokenType.SEP_LPAREN)
        exp = self.parse_exp()
        self.eat_tk_by_kind(TokenType.SEP_RPAREN)
        return exp

    @exp_type('brack_exp')
    def parse_brack_exp(self):
        self.eat_tk_by_value('|')
        exp = self.parse_exp()
        self.eat_tk_by_value('|')
        return exp

    """
    listcons := '[' exp_list ']'
    """
    @exp_type('listcons')
    def parse_listcons(self):
        self.eat_tk_by_kind(TokenType.SEP_LBRACK)
        next_tk = self.try_look_ahead()
        if next_tk.typ == TokenType.SEP_RBRACK: # []
            self.skip_once()
            return can_ast.ListExp("")
        else:
            exps = self.parse_exp_list()
            self.eat_tk_by_kind(TokenType.SEP_RBRACK)
            return can_ast.ListExp(exps)

    """
    set_or_mapcons := '{' exp_list '}'
    """
    @exp_type('mapcons')
    def parse_mapcons(self):
        self.eat_tk_by_kind(TokenType.SEP_LCURLY)
        next_tk = self.try_look_ahead()
        if next_tk.typ == TokenType.SEP_RCURLY: # {}
            self.skip_once()
            return can_ast.MapExp("")
        else:
            exps = self.parse_exp_list()
            self.eat_tk_by_kind(TokenType.SEP_RCURLY)
            return can_ast.MapExp(exps)
        
    def finish_prefixexp(self, exp : can_ast.AST):
        while True:
            next_tk = self.try_look_ahead()
            kind, value = next_tk.typ, next_tk.value
            if kind == TokenType.SEP_LBRACK:
                self.skip_once()
                key_exp : can_ast.AST = self.parse_exp()
                self.eat_tk_by_kind(TokenType.SEP_RBRACK)
                exp = can_ast.ListAccessExp(exp, key_exp)
            elif kind == TokenType.SEP_DOT or \
                (kind == TokenType.KEYWORD and value == kw_dot):
                    self.skip_once()
                    tk = self.eat_tk_by_kind(TokenType.IDENTIFIER)
                    name = tk.value
                    key_exp = can_ast.IdExp(name)
                    exp = can_ast.ObjectAccessExp(exp, key_exp)
            elif (kind == TokenType.SEP_LPAREN) or \
                (kind == TokenType.KEYWORD and value == kw_call_begin):
                exp = self.finish_functioncall_exp(exp)
            elif value == '嘅長度':
                self.skip_once()
                key_exp = can_ast.IdExp('__len__()')
                exp = can_ast.ObjectAccessExp(exp, key_exp)
            elif kind == TokenType.OP_ASSIGN:
                self.skip_once()
                exp = can_ast.AssignExp(exp, self.parse_exp())
            elif kind == TokenType.COLON:
                self.skip_once()
                exp = can_ast.AnnotationExp(exp, self.parse_exp())
                break
            elif kind == TokenType.EXCL:
                self.skip_once()
                macroParser = MacroParser(self.get_token_ctx())
                exp = can_ast.MacroCallExp(exp, macroParser.parse_tokentrees()[1:-1])
                break
            else:
                break
        return exp

    """
    functioncall ::= prefixexp '下' '->' args
                  | prefixexp args
    """
    def finish_functioncall_exp(self, prefix_exp : can_ast.AST):
        if self.try_look_ahead().value == kw_call_begin:
            self.skip_once()
            self.eat_tk_by_value(kw_dot)
            args = self.parse_args()
            return can_ast.FuncCallExp(prefix_exp, args)
        else:
            args = self.parse_args()
            return can_ast.FuncCallExp(prefix_exp, args)

    @exp_type('parlist')
    def parse_parlist(self):
        next_tk = self.try_look_ahead()
        if next_tk.typ == TokenType.IDENTIFIER or \
            next_tk.value == '<*>':
            par_parser = ParExpParser(self.get_token_ctx())
            exps = par_parser.parse_exp_list()
            return exps
        
        elif next_tk.value == '|':
            self.skip_once()
            par_parser = ParExpParser(self.get_token_ctx())
            exps = par_parser.parse_exp_list()
            self.eat_tk_by_value('|')
            return exps
        
        else:
            return []

    """
    idlist ::= id [',', id]
            | '|' id [',', id] '|'
    """
    @exp_type('idlist')
    def parse_idlist(self):
        tk = self.try_look_ahead()
        if tk.typ == TokenType.IDENTIFIER:
            ids = [can_ast.IdExp(tk.value)]
            self.skip_once()
            while self.try_look_ahead().typ == TokenType.SEP_COMMA:
                self.skip_once()
                if self.try_look_ahead().typ != TokenType.IDENTIFIER:
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp( 
                        self.look_ahead().value))
            return ids

        elif self.try_look_ahead().value == '|':
            self.skip_once()
            ids = [can_ast.IdExp((self.eat_tk_by_kind(TokenType.IDENTIFIER)).value)]
            while self.try_look_ahead().typ == TokenType.SEP_COMMA:
                self.skip_once()
                if self.try_look_ahead().typ != TokenType.IDENTIFIER:
                    self.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp( 
                        self.look_ahead().value))
            self.eat_tk_by_value('|')
            return ids
        
        else:
            return None

    """
    lambda_functoindef ::= '$$' idlist '{' exp_list '}'
    """
    @exp_type('functiondef_expr')
    def parse_functiondef_expr(self):
        idlist : list = self.parse_idlist()
        blocks : list = []
        self.eat_tk_by_kind(TokenType.SEP_LCURLY)
        blocks = self.parse_exp_list()
        self.eat_tk_by_kind(TokenType.SEP_RCURLY)
        return can_ast.LambdaExp(idlist, blocks)

    @exp_type('if_else_expr')
    def parse_if_else_expr(self):
        CondExp : can_ast.AST = self.parse_exp()
        self.eat_tk_by_value(kw_dot)
        IfExp : can_ast.AST = self.parse_exp()
        self.eat_tk_by_value(kw_expr_else)
        self.eat_tk_by_value(kw_dot)
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
        tk = self.try_look_ahead()
        if tk.value == '(':
            self.skip_once()
            next_tk = self.try_look_ahead()
            if next_tk.value != ')':
                args = self.parse_exp_list()
            self.eat_tk_by_kind(TokenType.SEP_RPAREN)
        elif tk.value == '|':
            self.skip_once()
            next_tk = self.try_look_ahead()
            if next_tk.value != '|':
                args = self.parse_exp_list()
            self.eat_tk_by_value('|')
        else:
            args = self.parse_exp_list()
        return args

"""
    parlist ::= id [',', id | '<*>']
             | id '=' exp [',' id]
             | '<*>'
"""

class ParExpParser(ExpParser):
    
    # override
    @exp_type('exp')
    def parse_exp(self):
        return self.parse_exp0()

    # override
    def parse_exp0(self):
        tk = self.try_look_ahead()

        if tk.value == '<*>':
            self.skip_once()
            return can_ast.VarArgExp()
        
        return self.parse_prefixexp()

    # override
    @exp_type('prefixexp')
    def parse_prefixexp(self):
        tk = self.try_look_ahead()
        if tk.typ == TokenType.IDENTIFIER:
            name = tk.value
            self.skip_once()
            exp = can_ast.IdExp(name)
            return self.finish_prefixexp(exp)
        else:
            raise Exception("Parlist must be a identifier type!")

    # override
    def finish_prefixexp(self, exp: can_ast.AST):
        value = self.try_look_ahead().value
        if value == '=' or value == '==>':
            self.skip_once()
            exp_parser = ExpParser(self.get_token_ctx())
            exp2 = exp_parser.parse_exp()
            return can_ast.AssignExp(exp, exp2)
        return exp

class ClassBlockExpParser(ExpParser):
    # Override
    def parse_exp0(self):
        tk = self.try_look_ahead().value
        if tk in [kw_self, '@@']:
            self.skip_once()
            return can_ast.ClassSelfExp(super().parse_exp0())
        else:
            return super().parse_exp0()