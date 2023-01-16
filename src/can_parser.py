from keywords import *
import can_ast

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

    # TODO:
    # exp1 where exp2
    def parse_exp13(self):
        exp = self.parse_exp12()
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
            else:
                break
        return exp
    
    # exp1 <|> exp2
    def parse_exp9(self):
        exp = self.parse_exp8()
        while self.get_type(self.current()) == TokenType.OP_BOR:
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '|', exp, self.parse_exp8())
        return exp

    # exp1 ! exp2
    def parse_exp8(self):
        exp = self.parse_exp7()
        while self.get_type(self.current()) == TokenType.OP_WAVE:
            line = self.current()[0]
            self.skip(1)
            exp = can_ast.BinopExp(line, '!', exp, self.parse_exp8())
        return exp

    # exp1 & exp2
    def parse_exp7(self):
        exp = self.parse_exp6()
        while self.get_type(self.current()) == TokenType.OP_BAND:
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
            else:
                break
        return exp

     # *, %, /, //
    def parse_exp3(self):
        exp = self.parse_exp2()
        while True:
            if self.get_type(self.current()) in (TokenType.OP_MUL, TokenType.OP_MOD, TokenType.OP_DIV):
                line, op = self.current()[0], self.get_token_value(self.current())
                self.skip(1) # Skip the op
                exp = can_ast.BinopExp(line, op, exp, self.parse_exp2())
            else:
                break
        return exp

    # unop exp
    def parse_exp2(self):
        if self.get_type(self.current()) == TokenType.OP_NOT:
            line, op = self.current()[0], self.get_token_value(self.current())
            self.skip(1) # Skip the op
            exp = can_ast.UnopExp(line, op, self.parse_exp2())
            return exp
        return self.parse_exp1()

    # x ^ y
    def parse_exp1(self):
        exp = self.parse_exp0()
        if self.get_type(self.current()) == TokenType.OP_POW:
            line, op = self.current()[0], self.get_token_value(self.current())
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

        # lambda function
        elif self.get_token_value(tk) == '$$':
            return self.parse_functiondef()
        
        return self.parse_prefixexp()
    """
    prefixexp ::= var
          | '(' exp ')'
          | '|' exp '|'
          | functioncall

    var ::= id
          | prefixexp '[' exp ']'
          | prefixexp '->' id
    """
    def parse_prefixexp(self):
        if self.get_type(self.current()) == TokenType.IDENTIFIER:
            line, name = self.current()[0], self.get_token_value(self.current())
            self.skip(1)
            exp = can_ast.IdExp(line, name)
        elif self.get_type(self.current()) == TokenType.SEP_LPAREN:
            exp = self.parse_parens_exp()
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

    def finish_prefixexp(self, exp : can_ast.AST):
        while True:
            kind, value = self.get_type(self.current()), self.get_token_value(self.current())
            if kind == TokenType.SEP_LBRACK:
                self.skip(1)
                key_exp : can_ast.AST = self.parse_exp()
                self.get_next_token_of_kind(TokenType.SEP_RBRACK, 0)
                exp = can_ast.ObjectAccessExp(self.get_line(), exp, key_exp)
            elif kind == TokenType.SEP_DOT or \
                (kind == TokenType.KEYWORD and value == kw_do):
                self.skip(1)
                tk = self.get_next_token_of_kind(TokenType.IDENTIFIER, 0)
                line, name = tk[0], self.get_token_value(tk)
                key_exp = can_ast.IdExp(line, name)
                exp = can_ast.ObjectAccessExp(line, exp, key_exp)
            elif (kind == TokenType.SEP_LPAREN) or \
                (kind == TokenType.KEYWORD and value == kw_call_begin):
                exp = self.finish_functioncall_exp(exp)
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
            return can_ast.FuncCallExp(line, last_line, prefix_exp, "", args)
        else:
            line = self.get_line()
            args = self.parse_args()
            last_line = self.get_line()
            return can_ast.FuncCallExp(line, last_line, prefix_exp, "", args)

    """
    parlist ::= idlist [',', '<*>']
             | '<*>'
    """
    def parse_parlist(self):
        kind = self.get_type(self.current())

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
    functoindef ::= '$$' idlist '->' block '搞掂'
    """
    def parse_functiondef(self):
        pass
    
    """
    args ::= '|' explist '|'
           | '(' {explist} ')'
           | LiteralString
           | Numeral
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
        elif self.get_type(tk) == TokenType.STRING:
            self.skip(1)
            args = [can_ast.StringExp(tk[0], self.get_token_value(tk))]
        elif self.get_type(tk) == TokenType.NUM:
            self.skip(1)
            args = [can_ast.NumeralExp(tk[0], self.get_token_value(tk))]
        return args

class StatParser(ParserBase):
    def __init__(self, token_list : list) -> None:
        super(StatParser, self).__init__(token_list)
        self.pos = 0
        self.tokens = token_list

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
                exp_parser = ExpParser(self.tokens[self.pos : ])
                prefix_exps = exp_parser.parse_exp()
                skip_step = exp_parser.pos = exp_parser.pos # we will skip it in parse_for_stat
                del exp_parser
                if self.get_token_value(self.look_ahead(skip_step)) in [kw_from, tr_kw_from]:
                    return self.parse_for_stat(prefix_exps, skip_step)
            elif tk_value == kw_function:
                return self.parse_func_def_stat()

        elif kind == TokenType.IDENTIFIER:
            if self.get_token_value(self.look_ahead(1)) in [kw_from, tr_kw_from]:
                return self.parse_for_stat()

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
        exp_parser = ExpParser(self.tokens[self.pos : ])
        args = exp_parser.parse_args()
        self.skip(exp_parser.pos)
        self.get_next_token_of(kw_endprint, step = 0)
        del exp_parser # free the memory
        return can_ast.PrintStat(args)

    # Parser for muti-assign
    def parse_assign_block(self):
        # Nothing in assignment block
        if self.get_type(self.current()) == TokenType.SEP_RCURLY:
            self.skip(1)
            return can_ast.AssignStat(0, can_ast.AST, can_ast.AST)
        var_list = []
        exp_list = []
        while self.get_type(self.current()) != TokenType.SEP_RCURLY:
            var_list.append(self.parse_var_list())
            self.get_next_token_of([kw_is, kw_is_3], 0)
            exp_parser = ExpParser(self.tokens[self.pos : ])
            exp_list.append(exp_parser.parse_exp_list())
            self.skip(exp_parser.pos)
            del exp_parser # free the memory
        
        # Skip the SEP_RCURLY
        self.skip(1)
        return can_ast.AssignStat(self.get_line(), var_list, exp_list)

    def parse_assign_stat(self):
        self.skip(1)
        if self.get_token_value(self.current()) != kw_do:
            var_list = self.parse_var_list()
            self.get_next_token_of([kw_is, kw_is_3], 0)
            exp_parser = ExpParser(self.tokens[self.pos : ])
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
        exp_parser = ExpParser(self.tokens[self.pos : ])
        exp = exp_parser.parse_prefixexp()
        self.skip(exp_parser.pos)
        del exp_parser
        var_list : list = [self.check_var(exp)]
    
        while self.get_type(self.current()) == TokenType.SEP_COMMA:
            self.skip(1)
            exp_parser = ExpParser(self.tokens[self.pos : ])
            exp = exp_parser.parse_prefixexp()
            self.skip(exp_parser.pos)
            del exp_parser
            var_list.append(self.check_var(exp))

        return var_list

    def check_var(self, exp : can_ast.AST):
        if isinstance(exp, can_ast.IdExp) or \
           isinstance(exp, can_ast.ObjectAccessExp):
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

        if_exps : list = []
        if_blocks : list = []
        elif_exps : list = []
        elif_blocks : list = []
        else_blocks : list = []

        exp_parser = ExpParser(self.tokens[self.pos : ])
        if_exps.append(exp_parser.parse_exp())
        self.skip(exp_parser.pos)
        self.get_next_token_of([kw_then, tr_kw_then], 0)
        self.get_next_token_of(kw_do, 0)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
        del exp_parser # free the memory
        while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
            block_parser = StatParser(self.tokens[self.pos : ])
            if_blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser # free the memory
        self.skip(1) # Skip the SEP_RCURLY '}'

        while self.get_token_value(self.current()) in [kw_elif, tr_kw_elif]:
            self.skip(1) # skip and try to get the next token
            exp_parser = ExpParser(self.tokens[self.pos : ])
            elif_exps.append(exp_parser.parse_exp())
            self.skip(exp_parser.pos)
            self.get_next_token_of([kw_then, tr_kw_then], 0)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            del exp_parser # free the memory
            while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
                block_parser = StatParser(self.tokens[self.pos : ])
                elif_blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser # free the memory
            self.skip(1) # Skip the SEP_RCURLY '}'

        if self.get_token_value(self.current()) == kw_else_or_not:
            self.skip(1) # Skip and try yo get the next token
            self.get_next_token_of([kw_then, tr_kw_then], 0)
            self.get_next_token_of(kw_do, 0)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY, 0)
            while (self.get_type(self.current()) != TokenType.SEP_RCURLY):
                block_parser = StatParser(self.tokens[self.pos : ])
                else_blocks.append(block_parser.parse())
                self.skip(block_parser.pos)
                del block_parser # free the memory
            self.skip(1) # Skip the SEP_RCURLY '}'

        return can_ast.IfStat(if_exps, if_blocks, elif_exps, elif_blocks, else_blocks)


    def parse_import_stat(self):
        self.skip(1) # Skip the kw_import
        exp_parser = ExpParser(self.tokens[self.pos : ])
        idlist = exp_parser.parse_idlist()
        self.skip(exp_parser.pos)
        del exp_parser # free thr memory
        return can_ast.ImportStat(idlist)

    def parse_global_stat(self):
        self.skip(1) # Skip the kw_global
        exp_parser = ExpParser(self.tokens[self.pos : ])
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
            block_parser =  StatParser(self.tokens[self.pos : ])
            blocks.append(block_parser.parse())
            self.skip(block_parser.pos)
            del block_parser # free the memory

        self.skip(1) # Skip the kw_while
        
        exp_parser = ExpParser(self.tokens[self.pos : ])
        cond_exps.append(exp_parser.parse_exp())
        self.skip(exp_parser.pos)
        del exp_parser # free the memory
        self.get_next_token_of([kw_whi_end, tr_kw_whi_end], 0)

        return can_ast.WhileStat(cond_exps, blocks)

    def parse_for_stat(self, prefix_exp : ExpParser = None, skip_prefix_exp : int = 0):
        blocks : list = []

        if prefix_exp == None:
            exp_parser = ExpParser(self.tokens[self.pos : ])
            id = exp_parser.parse_exp()
            self.skip(exp_parser.pos)
            del exp_parser # free the memory

        else:
            id = prefix_exp
            self.skip(skip_prefix_exp)
        
        self.get_next_token_of([kw_from, tr_kw_from], 0)

        exp_parser = ExpParser(self.tokens[self.pos : ])
        from_exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory
        self.get_next_token_of([kw_to, tr_kw_to], 0)

        exp_parser = ExpParser(self.tokens[self.pos : ])
        to_exp = exp_parser.parse_exp()
        self.skip(exp_parser.pos)
        del exp_parser # free the memory

        while (self.get_token_value(self.current()) not in [kw_endfor, tr_kw_endfor]):
            block_parse = StatParser(self.tokens[self.pos : ])
            blocks.append(block_parse.parse())
            self.skip(block_parse.pos)
            del block_parse # free the memory

        self.skip(1)

        return can_ast.ForStat(id, from_exp, to_exp, blocks)

    def parse_func_def(self):
        self.skip(1) # Skip the kw_function
        
        
        exp_parser = ExpParser(self.tokens[self.pos : ])
        args = exp_parser.parse_idlist()
        del exp_parser # free the memory
