from can_source.can_lexer import *
from can_source.Ast import can_ast
from can_source.parser_base import *
from can_source.util.can_utils import ParserUtil
from can_source.exp_parser import ExpParser, ClassBlockExpParser

class StatParser(ParserBase):
    def __init__(self, token_ctx: tuple, expParser = ExpParser) -> None:
        super(StatParser, self).__init__(token_ctx)
        self.tokens, self.buffer_tokens = token_ctx
        # Function address type:
        # We can choose the class `ExpParser` Or `ClassBlockExpParser`
        self.ExpParser = expParser

    def getExpParser(self):
        return self.ExpParser(self.get_token_ctx())

    def parse_var_list(self):
        exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_prefixexp)
        var_list : list = [self.check_var(exp)]
        while self.try_look_ahead().typ == TokenType.SEP_COMMA:
            self.skip_once()
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
    
    @pos_tracker
    def parse(self):
        tk = self.try_look_ahead()
        kind, tk_value = tk.typ, tk.value

        if kind == TokenType.KEYWORD:
            if tk_value == kw_print:
                self.skip_once(); return self.parse_print_stat()
            
            elif tk_value in [kw_exit, kw_exit_1, kw_exit_2]:
                self.skip_once(); return self.parse_exit_stat()
            
            elif tk_value == kw_assign:
                self.skip_once(); return self.parse_assign_stat()
            
            elif tk_value == kw_if:
                self.skip_once(); return self.parse_if_stat()
            
            elif tk_value == kw_import:
                self.skip_once(); return self.parse_import_stat()
            
            elif tk_value == kw_global_set:
                self.skip_once(); return self.parse_global_stat()
            
            elif tk_value == kw_break:
                self.skip_once(); return self.parse_break_stat()

            elif tk_value == kw_continue:
                self.skip_once(); return self.parse_continue_stat()
            
            elif tk_value == kw_while_do:
                self.skip_once(); return self.parse_while_stat()

            elif tk_value == kw_pass:
                self.skip_once(); return self.parse_pass_stat()
            
            elif tk_value == kw_return:
                self.skip_once(); return self.parse_return_stat()
            
            elif tk_value == kw_del:
                self.skip_once(); return self.parse_del_stat()

            elif tk_value == kw_type:
                self.skip_once(); return self.exp_type_stat()

            elif tk_value == kw_assert:
                self.skip_once(); return self.parse_assert_stat()

            elif tk_value == kw_try:
                self.skip_once(); return self.parse_try_stat()

            elif tk_value == kw_raise:
                self.skip_once(); return self.parse_raise_stat()

            elif tk_value == kw_cmd:
                self.skip_once(); return self.parse_cmd_stat()

            elif tk_value == kw_stackinit:
                self.skip_once(); return self.parse_stack_init_stat()

            elif tk_value == kw_push:
                self.skip_once(); return self.parse_stack_push_stat()

            elif tk_value == kw_pop:
                self.skip_once(); return self.parse_stack_pop_stat()

            elif tk_value == kw_match:
                self.skip_once(); return self.parse_match_stat()

            elif tk_value == kw_call_native:
                self.skip_once(); return self.parse_call_native_stat()

            elif tk_value == '&&':
                self.skip_once(); return self.parse_for_each_stat()

            elif tk_value == kw_model:
                self.skip_once(); return self.parse_model_new_stat()

            elif tk_value == kw_turtle_beg:
                self.skip_once(); return self.parse_turtle_stat()

            elif tk_value == kw_pls:
                self.skip_once(); return self.parse_pls_stat()

            else:
                self.error(tk, info=f"\033[0;31m濑嘢!!!\033[0m: 個`{tk.value}`好似有D唔三唔四", 
                    tips=f" 幫緊你只不過有心無力 :(")

                
        elif kind == TokenType.EOF:
            return "EOF"

        else:
            exp_parser = self.ExpParser(self.get_token_ctx())
            prefix_exp = exp_parser.parse_exp()
            next_tk = self.try_look_ahead()
            if next_tk.value == kw_from:
                return self.parse_for_stat(prefix_exp)
            
            elif next_tk.value == kw_get_value:
                return self.parse_suffix_assign_stat(prefix_exp)
            
            elif next_tk.value in [kw_lst_assign]:
                return self.parse_list_assign_stat(prefix_exp)

            elif next_tk.value in [kw_set_assign]:
                return self.parse_set_assign_stat(prefix_exp)
            # kw_laa1
            else:
                return self.parse_class_method_call_stat(prefix_exp)
    
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
        args = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_args)
        self.get_next_token_of([kw_endprint])
        return can_ast.PrintStat(args, self.cur_lexer_pos)

    # Parser for muti-assign
    def parse_assign_block(self):
        # Nothing in assignment block
        if self.try_look_ahead().value == kw_end_assign:
            self.skip_once()
            return can_ast.PassStat(self.cur_lexer_pos)
        var_list : list = []
        exp_list : list= []
        while self.try_look_ahead().value != kw_end_assign:
            var_list.append(self.parse_var_list()[0])
            self.get_next_token_of(kw_is)
            exp_list.append(ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)[0])
        
        # Skip the SEP_RCURLY
        self.skip_once()
        return can_ast.AssignBlockStat(var_list, exp_list, self.cur_lexer_pos)

    def parse_assign_stat(self):
        if self.try_look_ahead().value == kw_do:
            # Skip the kw_do
            self.skip_once()
            return self.parse_assign_block()
        elif self.try_look_ahead().value == kw_function:
            self.skip_once()
            return self.parse_func_def_stat()
        else:
            var_list = self.parse_var_list()
            self.get_next_token_of(kw_is)
            if self.try_look_ahead().value == kw_class_def:
                self.skip_once(); return self.parse_class_def(class_name=var_list[0])
            else:            
                exp_list = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
                return can_ast.AssignStat(var_list, exp_list, self.cur_lexer_pos)

    def parse_exit_stat(self):
        return can_ast.ExitStat(self.cur_lexer_pos)

    def parse_if_stat(self):
        if_blocks : list = []
        elif_exps : list = []
        elif_blocks : list = []
        else_blocks : list = []

        if_exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        self.get_next_token_of([kw_then])
        self.get_next_token_of(kw_do)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)

        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            if_blocks.append(block_parser.parse())
        self.skip_once() # Skip the SEP_RCURLY '}'

        while self.try_look_ahead().value in [kw_elif]:
            self.skip_once() # skip and try to get the next token
            elif_exps.append(ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp))
            self.get_next_token_of([kw_then])
            self.get_next_token_of(kw_do)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY)
            
            elif_block : list = []
            
            while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                elif_block.append(block_parser.parse())
                
            elif_blocks.append(elif_block)

            self.skip_once() # Skip the SEP_RCURLY '}'

        if self.try_look_ahead().value == kw_else_or_not:
            self.skip_once() # Skip and try yo get the next token
            self.get_next_token_of([kw_then])
            self.get_next_token_of(kw_do)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY)
            while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                else_blocks.append(block_parser.parse())
            self.skip_once() # Skip the SEP_RCURLY '}'

        return can_ast.IfStat(if_exps, if_blocks, elif_exps, elif_blocks, else_blocks, self.cur_lexer_pos)

    def parse_import_stat(self):
        idlist = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_idlist)
        return can_ast.ImportStat(idlist, self.cur_lexer_pos)

    def parse_global_stat(self):
        idlist = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_idlist)
        return can_ast.GlobalStat(idlist, self.cur_lexer_pos)

    def parse_break_stat(self):
        return can_ast.BreakStat(self.cur_lexer_pos)

    def parse_continue_stat(self):
        return can_ast.ContinueStat(self.cur_lexer_pos)

    def parse_while_stat(self):
        blocks : list = []
        while self.try_look_ahead().value != kw_while:
            block_parser =  StatParser(self.get_token_ctx(), self.ExpParser)
            blocks.append(block_parser.parse())
            
        self.skip_once() # Skip the kw_while
       
        cond_exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        self.get_next_token_of([kw_whi_end])

        return can_ast.WhileStat(can_ast.UnopExp('not', cond_exps), blocks, self.cur_lexer_pos)

    def parse_for_stat(self, prefix_exp : ExpParser):
        blocks : list = []

        id = prefix_exp
        
        self.get_next_token_of(kw_from)

        from_exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        self.get_next_token_of(kw_to)

        to_exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)

        while self.try_look_ahead().value != kw_endfor:
            block_parse = StatParser(self.get_token_ctx(), self.ExpParser)
            blocks.append(block_parse.parse())
            
        self.skip_once()

        return can_ast.ForStat(id, from_exp, to_exp, blocks, self.cur_lexer_pos)

    def parse_func_def_stat(self):
        name = self.get_next_token_of_kind(TokenType.IDENTIFIER).value        
        exp_parser = self.ExpParser(self.get_token_ctx())
        args : list = exp_parser.parse_parlist()
        args = [] if args == None else args

        self.get_next_token_of([kw_func_begin, kw_do])

        blocks : list = []
        while (self.try_look_ahead().value not in [kw_func_end]):
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            blocks.append(block_parser.parse())

        self.skip_once()

        return can_ast.FunctionDefStat(can_ast.IdExp(name), args, blocks, 
                                    self.cur_lexer_pos)

    def parse_suffix_assign_stat(self, prefix_exp: can_ast.AST):
        self.skip_once()
        var_list = self.parse_var_list()
        return can_ast.AssignStat(var_list,
                [prefix_exp],
                self.cur_lexer_pos)
    
    def parse_class_method_call_stat(self, prefix_exp: can_ast.AST):
        self.get_next_token_of(kw_laa1)
        return can_ast.CallStat(prefix_exp, self.cur_lexer_pos)

    def parse_list_assign_stat(self, prefix_exp: can_ast.AST):
        self.get_next_token_of(kw_lst_assign)
        self.get_next_token_of(kw_do)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(varlist, 
                [prefix_exp],
                self.cur_lexer_pos)

    def parse_set_assign_stat(self, prefix_exp : can_ast.AST):
        self.get_next_token_of(kw_set_assign)
        self.get_next_token_of(kw_do)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(varlist, 
                [prefix_exp],
                self.cur_lexer_pos)

    def parse_pass_stat(self):
        return can_ast.PassStat(self.cur_lexer_pos)

    def parse_assert_stat(self):
        exp = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp)
        return can_ast.AssertStat(exp, self.cur_lexer_pos)

    def parse_return_stat(self):
        exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
        return can_ast.ReturnStat(exps, self.cur_lexer_pos)

    def parse_del_stat(self):
        exps = ParserUtil.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
        return can_ast.DelStat(exps, self.cur_lexer_pos)

    def parse_try_stat(self):
        self.get_next_token_of(kw_do)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)

        try_blocks : list = []
        except_exps : list = []
        except_blocks : list = []
        finally_blocks : list = []

        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            try_blocks.append(block_parser.parse())

        self.skip_once()
        self.get_next_token_of([kw_except])
        
        exp_parser = self.getExpParser()
        except_exps.append(exp_parser.parse_exp())

        self.get_next_token_of([kw_then])
        self.get_next_token_of([kw_do])
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)

        # a temp list to save the block
        except_block = []
        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            except_block.append(block_parser.parse())
        
        self.skip_once()
        except_blocks.append(except_block)

        while self.try_look_ahead().value == kw_except:
            self.skip_once()
            self.get_next_token_of([kw_then])

            exp_parser = self.getExpParser()
            except_exps.append(exp_parser.parse_exp())

            self.get_next_token_of(kw_do)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY)

            # clear the list
            except_block = []
            while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                except_block.append(block_parser.parse())
            
            except_blocks.append(except_block)

        if self.try_look_ahead().value == kw_finally:
            self.skip_once()
            self.get_next_token_of(kw_do)
            self.get_next_token_of_kind(TokenType.SEP_LCURLY)

            while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                finally_blocks.append(block_parser.parse())

            self.skip_once()

        return can_ast.TryStat(try_blocks, except_exps, except_blocks, finally_blocks, self.cur_lexer_pos)

    def parse_raise_stat(self):
        exp_parser = self.getExpParser()
        name_exp = exp_parser.parse_exp()
        self.get_next_token_of([kw_raise_end])
        return can_ast.RaiseStat(name_exp, self.cur_lexer_pos)

    def exp_type_stat(self):
        name_exp = ParserUtil.parse_exp(self, self.getExpParser(), self.ExpParser.parse_exp)
        return can_ast.TypeStat(name_exp, self.cur_lexer_pos)

    def parse_cmd_stat(self):
        exp_parser = self.getExpParser()
        args = exp_parser.parse_args()

        return can_ast.CmdStat(args, self.cur_lexer_pos)

    def parse_class_def(self, class_name: can_ast.AST):      
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)
        self.get_next_token_of([kw_extend])
        
        exp_parser = self.getExpParser()
        extend_name : list = exp_parser.parse_exp_list()

        class_blocks = []
        
        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            class_block_parser = ClassBlockStatParser(self.get_token_ctx())
            class_blocks.append(class_block_parser.parse())

        self.skip_once()

        return can_ast.ClassDefStat(class_name, extend_name, class_blocks, self.cur_lexer_pos)

    def parse_stack_init_stat(self):
        exp_parser = self.getExpParser()
        exps = exp_parser.parse_exp()

        return can_ast.AssignStat([exps], [
            can_ast.FuncCallExp(can_ast.IdExp('stack'), [])
        ], self.cur_lexer_pos)

    def parse_stack_push_stat(self):
        self.get_next_token_of(kw_do)

        exp_parser = self.getExpParser()
        exps = exp_parser.parse_exp()

        exp_parser = self.getExpParser()
        args = exp_parser.parse_args()

        return can_ast.MethodCallStat(exps, can_ast.IdExp('push'), 
                    args, self.cur_lexer_pos)

    def parse_stack_pop_stat(self):
        self.get_next_token_of(kw_do)

        exp_parser = self.getExpParser()
        exps = exp_parser.parse_exp()

        return can_ast.MethodCallStat(exps, can_ast.IdExp('pop'), 
                    [], self.cur_lexer_pos)

    def parse_lambda_def_stat(self):
        exp_parse = self.getExpParser()
        lambda_exp = [exp_parse.parse_functiondef_expr()]

        self.get_next_token_of(kw_get_value)
        exp_parse = self.getExpParser()
        id_exp = exp_parse.parse_idlist()

        return can_ast.AssignStat(id_exp, lambda_exp, self.cur_lexer_pos)

    def parse_match_stat(self):
        match_val : list = []
        match_block : list = []
        default_match_block : list = []
        exp_parser = self.getExpParser()
        match_id = exp_parser.parse_exp()

        self.get_next_token_of(kw_do)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)

        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            while self.try_look_ahead().value in [kw_case]:
                self.skip_once()
                exp_parser = self.getExpParser()
                match_val.append(exp_parser.parse_exp())

                self.get_next_token_of(kw_do)
                self.get_next_token_of_kind(TokenType.SEP_LCURLY)

                block : list = []

                while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
                    stat_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                    block.append(stat_parser.parse())

                self.skip_once()
                match_block.append(block)
            
            if self.try_look_ahead().value == kw_else_or_not:
                self.skip_once()
                self.get_next_token_of([kw_then])
                self.get_next_token_of(kw_do)
                self.get_next_token_of_kind(TokenType.SEP_LCURLY)

                while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
                    stat_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                    default_match_block.append(stat_parser.parse())

                self.skip_once()
        
        self.skip_once()

        return can_ast.MatchStat(match_id, match_val, match_block, default_match_block, self.cur_lexer_pos)

    def parse_for_each_stat(self):
        id_list : list = []
        exp_list : list = []
        blocks : list = []

        exp_parser = self.getExpParser()
        id_list = exp_parser.parse_idlist()

        self.get_next_token_of(kw_in)

        exp_parser = self.getExpParser()
        exp_list = exp_parser.parse_exp_list()

        self.get_next_token_of(kw_do)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)

        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            stat_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            blocks.append(stat_parser.parse())
        
        self.skip_once()

        return can_ast.ForEachStat(id_list, exp_list, blocks, self.cur_lexer_pos)

    def parse_call_native_stat(self):
        tk = self.get_next_token_of_kind(TokenType.CALL_NATIVE_EXPR)
        return can_ast.ExtendStat(tk.value[3 : -5], self.cur_lexer_pos)

    def parse_model_new_stat(self):

        exp_parser = self.getExpParser()
        model_name = exp_parser.parse_exp()

        self.get_next_token_of([kw_mod_new])
        self.get_next_token_of(kw_do)

        exp_parser = self.getExpParser()
        dataset = exp_parser.parse_exp()

        return can_ast.ModelNewStat(model_name, dataset, self.cur_lexer_pos)

    def parse_turtle_stat(self):
        instruction_ident : list = ["首先", "跟住", "最尾"]
        self.get_next_token_of(kw_do)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)

        exp_blocks : list = []

        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            if self.try_look_ahead().value in instruction_ident and \
                self.try_look_ahead().typ == TokenType.IDENTIFIER:
                self.skip_once()
            else:
                exp_parser = self.getExpParser()
                exp_blocks.append(exp_parser.parse_exp())

        self.skip_once()

        return can_ast.TurtleStat(exp_blocks, self.cur_lexer_pos)

    def parse_pls_stat(self):
        func_name = self.getExpParser().parse_exp()
        self.get_next_token_of(kw_laa1)
        return can_ast.FuncCallStat(func_name, [], self.cur_lexer_pos)

class ClassBlockStatParser(StatParser):
    def __init__(self, token_ctx: tuple, ExpParser = ClassBlockExpParser) -> None:
        super().__init__(token_ctx, ExpParser)

    def parse_method_block(self):
        exp_parser = self.getExpParser()
        name_exp = exp_parser.parse_exp()

        exp_parser = self.getExpParser()
        args : list = exp_parser.parse_parlist()
        args = [] if args == None else args

        self.get_next_token_of([kw_func_begin, kw_do])
        
        blocks : list = []
        # '{' ... '}'
        if self.try_look_ahead().typ == TokenType.SEP_LCURLY:
            self.skip_once()
            while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = ClassBlockStatParser(self.get_token_ctx(), self.ExpParser)
                blocks.append(block_parser.parse())
        
        # '=> ... '%%'
        else:
            while self.try_look_ahead().value not in [kw_func_end]:
                block_parser = ClassBlockStatParser(self.get_token_ctx(), self.ExpParser)
                blocks.append(block_parser.parse())
        self.skip_once()
        
        return can_ast.MethodDefStat(name_exp, args, blocks, self.cur_lexer_pos)

    def parse_class_init_stat(self):
        exp_parser = self.getExpParser()
        args = exp_parser.parse_parlist()

        self.get_next_token_of(kw_do)
        self.get_next_token_of_kind(TokenType.SEP_LCURLY)

        blocks : list = []
        while self.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            blocks.append(block_parser.parse())

        self.skip_once()

        return can_ast.MethodDefStat(can_ast.IdExp('__init__'), args, blocks, self.cur_lexer_pos)
        
    def parse_class_assign_stat(self):
        return self.parse_assign_stat()

    def parse(self):
        tk = self.try_look_ahead()
        kind, tk_value = tk.typ, tk.value
        if tk_value == kw_method:
            self.skip_once(); return self.parse_method_block()
        elif tk_value == kw_class_assign:
            self.skip_once(); return self.parse_class_assign_stat()
        elif tk_value == kw_class_init:
            self.skip_once(); return self.parse_class_init_stat()
        else:
            return super().parse()