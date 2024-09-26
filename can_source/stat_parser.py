from can_source.can_lexer import *
import can_source.can_ast as can_ast
from can_source.parser_base import F, pos_tracker
from can_source.exp_parser import ExpParser
from can_source.macros_parser import MacroParser


class StatParser:
    def parse_var_list(self):
        exp = ExpParser.parse_prefixexp()
        var_list: list = [self.check_var(exp)]
        while F.try_look_ahead().typ == TokenType.SEP_COMMA:
            F.skip_once()
            exp = ExpParser.parse_prefixexp()
            var_list.append(self.check_var(exp))

        return var_list

    def check_var(self, exp: can_ast.AST):
        if isinstance(
            exp,
            (
                can_ast.IdExp,
                can_ast.ObjectAccessExp,
                can_ast.ListAccessExp,
                can_ast.MappingExp,
                can_ast.AnnotationExp,
            ),
        ):
            return exp
        else:
            raise Exception("unreachable!")

    @pos_tracker
    def parse(self):
        tk = F.try_look_ahead()
        kind, tk_value = tk.typ, tk.value

        if kind == TokenType.KEYWORD:
            if tk_value == kw_print:
                F.skip_once()
                return self.parse_print_stat()

            elif tk_value in [kw_exit, kw_exit_1, kw_exit_2]:
                F.skip_once()
                return self.parse_exit_stat()

            elif tk_value == kw_assign:
                F.skip_once()
                return self.parse_assign_stat()

            elif tk_value == kw_if:
                F.skip_once()
                return self.parse_if_stat()

            elif tk_value == kw_import:
                F.skip_once()
                return self.parse_import_stat()

            elif tk_value == kw_global_set:
                F.skip_once()
                return self.parse_global_stat()

            elif tk_value == kw_break:
                F.skip_once()
                return self.parse_break_stat()

            elif tk_value == kw_continue:
                F.skip_once()
                return self.parse_continue_stat()

            elif tk_value == kw_while_do:
                F.skip_once()
                return self.parse_while_stat()

            elif tk_value == kw_pass:
                F.skip_once()
                return self.parse_pass_stat()

            elif tk_value == kw_return:
                F.skip_once()
                return self.parse_return_stat()

            elif tk_value == kw_del:
                F.skip_once()
                return self.parse_del_stat()

            elif tk_value == kw_type:
                F.skip_once()
                return self.exp_type_stat()

            elif tk_value == kw_assert:
                F.skip_once()
                return self.parse_assert_stat()

            elif tk_value == kw_try:
                F.skip_once()
                return self.parse_try_stat()

            elif tk_value == kw_raise:
                F.skip_once()
                return self.parse_raise_stat()

            elif tk_value == kw_cmd:
                F.skip_once()
                return self.parse_cmd_stat()

            elif tk_value == kw_stackinit:
                F.skip_once()
                return self.parse_stack_init_stat()

            elif tk_value == kw_push:
                F.skip_once()
                return self.parse_stack_push_stat()

            elif tk_value == kw_pop:
                F.skip_once()
                return self.parse_stack_pop_stat()

            elif tk_value == kw_match:
                F.skip_once()
                return self.parse_match_stat()

            elif tk_value == kw_call_native:
                F.skip_once()
                return self.parse_call_native_stat()

            elif tk_value == "&&":
                F.skip_once()
                return self.parse_for_each_stat()

            elif tk_value == kw_model:
                F.skip_once()
                return self.parse_model_new_stat()

            elif tk_value == kw_turtle_beg:
                F.skip_once()
                return self.parse_turtle_stat()

            elif tk_value == kw_pls:
                F.skip_once()
                return self.parse_pls_stat()

            else:
                self.error(
                    tk,
                    info=f"\033[0;31m濑嘢!!!\033[0m: 個`{tk.value}`好似有D唔三唔四",
                    tips=f" 幫緊你只不過有心無力 :(",
                )

        elif kind == TokenType.EOF:
            return "EOF"

        else:
            return self.with_prefix_stats()

    def with_prefix_stats(self):
        prefix_exp = ExpParser.parse_exp()
        next_tk = F.try_look_ahead()
        if next_tk.value == kw_from:
            return self.parse_for_stat(prefix_exp)

        elif next_tk.value == kw_get_value:
            return self.parse_suffix_assign_stat(prefix_exp)

        elif next_tk.value == kw_lst_assign:
            return self.parse_list_assign_stat(prefix_exp)

        elif next_tk.value == kw_set_assign:
            return self.parse_set_assign_stat(prefix_exp)
        # kw_laa1
        else:
            return self.parse_class_method_call_stat(prefix_exp)

    def parse_stats(self):
        while True:
            stat = self.parse()
            if stat == None:
                break
            yield stat

    def parse_print_stat(self):
        args = ExpParser.parse_args()
        F.eat_tk_by_value(kw_endprint)
        return can_ast.PrintStat(args)

    # Parser for muti-assign
    def parse_assign_block(self):
        # Nothing in assignment block
        if F.try_look_ahead().value == kw_end_assign:
            F.skip_once()
            return can_ast.PassStat()
        var_list: list = []
        exp_list: list = []
        while F.try_look_ahead().value != kw_end_assign:
            var_list.append(self.parse_var_list()[0])
            F.eat_tk_by_value(kw_is)
            exp_list.append(ExpParser.parse_exp_list()[0])

        F.eat_tk_by_value(kw_end_assign)
        return can_ast.AssignBlockStat(var_list, exp_list)

    def parse_assign_stat(self):
        if F.try_look_ahead().value == kw_do:
            # Skip the kw_do
            F.skip_once()
            return self.parse_assign_block()
        elif F.try_look_ahead().value == kw_function:
            F.skip_once()
            return self.parse_func_def_stat()
        else:
            var_list = self.parse_var_list()
            F.eat_tk_by_value(kw_is)
            if F.try_look_ahead().value == kw_class_def:
                F.skip_once()
                return self.parse_class_def(class_name=var_list[0])
            elif F.try_look_ahead().value == kw_macro_def:
                F.skip_once()
                return self.parse_macro_def(macro_name=var_list[0])
            else:
                exp_list = ExpParser.parse_exp_list()
                return can_ast.AssignStat(var_list, exp_list)

    def parse_exit_stat(self):
        return can_ast.ExitStat()

    def parse_if_stat(self):

        elif_exps: list = []
        elif_blocks: list = []
        else_blocks: list = []

        if_exps = ExpParser.parse_exp()

        F.eats((kw_then, kw_do, TokenType.SEP_LCURLY))

        if_blocks = F.many(
            other_parse_fn=self.parse,
            util_cond=lambda: F.try_look_ahead().typ == TokenType.SEP_RCURLY,
        )

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)

        while F.try_look_ahead().value in [kw_elif]:
            F.eat_tk_by_value(kw_elif)

            elif_exps.append(ExpParser.parse_exp())

            F.eats((kw_then, kw_do, TokenType.SEP_LCURLY))

            elif_block = F.many(
                other_parse_fn=self.parse,
                util_cond=lambda: F.try_look_ahead().typ == TokenType.SEP_RCURLY,
            )

            elif_blocks.append(elif_block)

            F.eat_tk_by_kind(TokenType.SEP_RCURLY)  # Skip the SEP_RCURLY '}'

        if F.try_look_ahead().value == kw_else_or_not:
            F.eats((kw_else_or_not, kw_then, kw_do, TokenType.SEP_LCURLY))

            else_blocks = F.many(
                other_parse_fn=self.parse,
                util_cond=lambda: F.try_look_ahead().typ == TokenType.SEP_RCURLY,
            )

            F.eat_tk_by_kind(TokenType.SEP_RCURLY)  # Skip the SEP_RCURLY '}'

        return can_ast.IfStat(if_exps, if_blocks, elif_exps, elif_blocks, else_blocks)

    def parse_import_stat(self):
        idlist = F.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_idlist)
        return can_ast.ImportStat(idlist)

    def parse_global_stat(self):
        idlist = F.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_idlist)
        return can_ast.GlobalStat(idlist)

    def parse_break_stat(self):
        return can_ast.BreakStat()

    def parse_continue_stat(self):
        return can_ast.ContinueStat()

    def parse_while_stat(self):
        blocks = F.many(
            other_parse_fn=self.parse,
            util_cond=lambda: F.try_look_ahead().value == kw_while,
        )

        F.eat_tk_by_value(kw_while)  # Skip the kw_while

        cond_exps = ExpParser.parse_exp()
        F.eat_tk_by_value(kw_whi_end)

        return can_ast.WhileStat(can_ast.UnopExp("not", cond_exps), blocks)

    def parse_for_stat(self, prefix_exp: ExpParser):
        blocks: list = []

        id = prefix_exp

        F.eat_tk_by_value(kw_from)

        from_exp = ExpParser.parse_exp()
        F.eat_tk_by_value(kw_to)

        to_exp = ExpParser.parse_exp()

        blocks = F.many(
            other_parse_fn=self.parse,
            util_cond=lambda: F.try_look_ahead().value == kw_endfor,
        )

        F.eat_tk_by_value(kw_endfor)

        return can_ast.ForStat(id, from_exp, to_exp, blocks)

    def parse_func_def_stat(self):
        name = F.eat_tk_by_kind(TokenType.IDENTIFIER).value
        exp_parser = self.ExpParser(self.get_token_ctx())
        args: list = exp_parser.parse_parlist()
        args = [] if args == None else args

        F.eat_tk_by_value([kw_func_begin, kw_do])

        blocks = F.many(
            other_parse_fn=self.parse,
            util_cond=lambda: F.try_look_ahead().value == kw_func_end,
        )

        F.eat_tk_by_value(kw_func_end)

        return can_ast.FunctionDefStat(can_ast.IdExp(name), args, blocks)

    def parse_suffix_assign_stat(self, prefix_exp: can_ast.AST):
        F.skip_once()
        var_list = self.parse_var_list()
        return can_ast.AssignStat(var_list, [prefix_exp])

    def parse_class_method_call_stat(self, prefix_exp: can_ast.AST):
        F.eat_tk_by_value([kw_laa1, kw_gamlaa1])
        return can_ast.CallStat(prefix_exp)

    def parse_list_assign_stat(self, prefix_exp: can_ast.AST):
        F.eat_tk_by_value(kw_lst_assign)
        F.eat_tk_by_value(kw_do)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(varlist, [prefix_exp])

    def parse_set_assign_stat(self, prefix_exp: can_ast.AST):
        F.eat_tk_by_value(kw_set_assign)
        F.eat_tk_by_value(kw_do)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(varlist, [prefix_exp])

    def parse_pass_stat(self):
        return can_ast.PassStat()

    def parse_assert_stat(self):
        exp = ExpParser.parse_exp()
        return can_ast.AssertStat(exp)

    def parse_return_stat(self):
        exps = F.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
        return can_ast.ReturnStat(exps)

    def parse_del_stat(self):
        exps = F.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_exp_list)
        return can_ast.DelStat(exps)

    def parse_try_stat(self):
        F.eat_tk_by_value(kw_do)
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)

        try_blocks: list = []
        except_exps: list = []
        except_blocks: list = []
        finally_blocks: list = []

        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            try_blocks.append(block_parser.parse())

        F.skip_once()
        F.eat_tk_by_value([kw_except])

        except_exps.append(ExpParser.parse_exp())

        F.eat_tk_by_value([kw_then])
        F.eat_tk_by_value([kw_do])
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)

        # a temp list to save the block
        except_block = []
        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            except_block.append(block_parser.parse())

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)
        except_blocks.append(except_block)

        while F.try_look_ahead().value == kw_except:
            F.skip_once()
            F.eat_tk_by_value([kw_then])

            exp_parser = self.getExpParser()
            except_exps.append(exp_parser.parse_exp())

            F.eat_tk_by_value(kw_do)
            F.eat_tk_by_kind(TokenType.SEP_LCURLY)

            # clear the list
            except_block = []
            while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                except_block.append(block_parser.parse())

            except_blocks.append(except_block)

        if F.try_look_ahead().value == kw_finally:
            F.skip_once()
            F.eat_tk_by_value(kw_do)
            F.eat_tk_by_kind(TokenType.SEP_LCURLY)

            while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                finally_blocks.append(block_parser.parse())

            F.skip_once()

        return can_ast.TryStat(try_blocks, except_exps, except_blocks, finally_blocks)

    def parse_raise_stat(self):
        name_exp = F.parse_exp(self, self.getExpParser(), self.ExpParser.parse_exp)
        F.eat_tk_by_value(kw_raise_end)
        return can_ast.RaiseStat(name_exp)

    def exp_type_stat(self):
        name_exp = F.parse_exp(self, self.getExpParser(), self.ExpParser.parse_exp)
        return can_ast.TypeStat(name_exp)

    def parse_cmd_stat(self):
        args = F.parse_exp(self, self.getExpParser(), self.ExpParser.parse_args)
        return can_ast.CmdStat(args)

    def parse_macro_def(self, macro_name: can_ast.AST):
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)
        match_rules: list = []
        match_blocks: list = []

        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            while F.try_look_ahead().value in [kw_case]:
                F.skip_once()
                _marcoParser = MacroParser(self.get_token_ctx())
                match_rules.append(_marcoParser.parse_macro_rule()[1:-1])
                F.eats((kw_do, TokenType.SEP_LCURLY))

                block: list = []

                while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
                    stat_parser = StatParser(self.get_token_ctx(), self.ExpParser)
                    block.append(stat_parser.parse())

                F.eat_tk_by_kind(TokenType.SEP_RCURLY)
                match_blocks.append(block)

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)
        return can_ast.MacroDefStat(match_rules, match_blocks)

    def parse_class_def(self, class_name: can_ast.AST):
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)

        extend_name = F.maybe(
            self,
            self.ExpParser,
            by="parse_exp_list",
            case_cond=lambda: F.try_look_ahead().value == kw_extend,
        )

        class_blocks = F.many(
            other_parse_fn=self.parse,
            util_cond=lambda: F.try_look_ahead().typ == TokenType.SEP_RCURLY,
        )

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)

        return can_ast.ClassDefStat(class_name, extend_name, class_blocks)

    def parse_stack_init_stat(self):
        exps = F.parse_exp(self, self.getExpParser(), self.ExpParser.parse_exp)

        return can_ast.AssignStat(
            [exps], [can_ast.FuncCallExp(can_ast.IdExp("stack"), [])]
        )

    def parse_stack_push_stat(self):
        F.eat_tk_by_value(kw_do)

        exps = F.parse_exp(self, self.getExpParser(), self.ExpParser.parse_exp)
        args = F.parse_exp(self, self.getExpParser(), self.ExpParser.parse_args)

        return can_ast.MethodCallStat(exps, can_ast.IdExp("push"), args)

    def parse_stack_pop_stat(self):
        F.eat_tk_by_value(kw_do)

        exps = F.parse_exp(self, self.getExpParser(), self.ExpParser.parse_exp)

        return can_ast.MethodCallStat(exps, can_ast.IdExp("pop"), [])

    def parse_lambda_def_stat(self):
        exp_parse = self.getExpParser()
        lambda_exp = [exp_parse.parse_functiondef_expr()]

        F.eat_tk_by_value(kw_get_value)
        exp_parse = self.getExpParser()
        id_exp = exp_parse.parse_idlist()

        return can_ast.AssignStat(id_exp, lambda_exp)

    def parse_match_stat(self):
        match_val: list = []
        match_block: list = []
        default_match_block: list = []
        match_id = ExpParser.parse_exp()

        F.eat_tk_by_value(kw_do)

        while F.try_look_ahead().value != kw_func_end:
            while F.try_look_ahead().value == "|":
                F.skip_once()
                if F.try_look_ahead().value == kw_case:
                    F.skip_once()
                    match_val.append(ExpParser.parse_exp())

                    F.eat_tk_by_value(kw_do)
                    F.eat_tk_by_kind(TokenType.SEP_LCURLY)

                    block = F.many(
                        other_parse_fn=self.parse,
                        util_cond=lambda: F.try_look_ahead().typ
                        == TokenType.SEP_RCURLY,
                    )

                    F.eat_tk_by_kind(TokenType.SEP_RCURLY)

                    match_block.append(block)

                elif F.try_look_ahead().value == "_":
                    F.skip_once()
                    F.eat_tk_by_value(kw_do)
                    F.eat_tk_by_kind(TokenType.SEP_LCURLY)

                    default_match_block = F.many(
                        other_parse_fn=self.parse,
                        util_cond=lambda: F.try_look_ahead().typ
                        == TokenType.SEP_RCURLY,
                    )

                    F.eat_tk_by_kind(TokenType.SEP_RCURLY)

                else:
                    self.error(F.try_look_ahead(), info="MatchBlock只允許`撞見`同`_`")

        F.eat_tk_by_value(kw_func_end)

        return can_ast.MatchStat(match_id, match_val, match_block, default_match_block)

    def parse_for_each_stat(self):
        id_list = ExpParser.parse_idlist()

        F.eat_tk_by_value(kw_in)

        exp_list = ExpParser.parse_exp_list()

        F.eat_tk_by_value(kw_do)
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)

        blocks = F.many(
            other_parse_fn=self.parse,
            util_cond=lambda: F.try_look_ahead().typ == TokenType.SEP_RCURLY,
        )

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)

        return can_ast.ForEachStat(id_list, exp_list, blocks)

    def parse_call_native_stat(self):
        tk = F.eat_tk_by_kind(TokenType.CALL_NATIVE_EXPR)
        return can_ast.ExtendStat(tk.value[3:-5])

    def parse_model_new_stat(self):

        exp_parser = self.getExpParser()
        model_name = exp_parser.parse_exp()

        F.eats((kw_mod_new, kw_do))

        exp_parser = self.getExpParser()
        dataset = exp_parser.parse_exp()

        return can_ast.ModelNewStat(model_name, dataset)

    def parse_turtle_stat(self):
        instruction_ident: list = ["首先", "跟住", "最尾"]
        F.eats((kw_do, TokenType.SEP_LCURLY))
        exp_blocks: list = []

        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            if (
                F.try_look_ahead().value in instruction_ident
                and F.try_look_ahead().typ == TokenType.IDENTIFIER
            ):
                F.skip_once()
            else:
                exp_blocks.append(ExpParser.parse_exp())

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)

        return can_ast.TurtleStat(exp_blocks)

    def parse_pls_stat(self):
        func_name = ExpParser.parse_exp()
        F.eat_tk_by_value(kw_laa1)
        return can_ast.FuncCallStat(func_name, [])


class ClassBlockStatParser(StatParser):
    def __init__(self, token_ctx: tuple, ExpParser=ExpParser) -> None:
        StatParser.__init__(self, token_ctx, ExpParser)

    def parse_method_block(self):
        name_exp = ExpParser.parse_exp()

        args: list = F.parse_exp(
            self, self.getExpParser(), by=self.ExpParser.parse_parlist
        )
        args = [] if args == None else args

        F.eat_tk_by_value([kw_func_begin, kw_do])

        blocks: list = []
        # '{' ... '}'
        if F.try_look_ahead().typ == TokenType.SEP_LCURLY:
            F.skip_once()
            while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = ClassBlockStatParser(
                    self.get_token_ctx(), self.ExpParser
                )
                blocks.append(block_parser.parse())

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)

        return can_ast.MethodDefStat(name_exp, args, blocks)

    def parse_class_init_stat(self):
        args = F.parse_exp(self, self.getExpParser(), by=self.ExpParser.parse_parlist)
        F.eats((kw_do, TokenType.SEP_LCURLY))

        blocks: list = []
        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(self.get_token_ctx(), self.ExpParser)
            blocks.append(block_parser.parse())

        F.eat_tk_by_kind(TokenType.SEP_RCURLY)

        return can_ast.MethodDefStat(can_ast.IdExp("__init__"), args, blocks)

    def parse_class_assign_stat(self):
        return self.parse_assign_stat()

    @pos_tracker
    def parse(self):
        tk = F.try_look_ahead()
        kind, tk_value = tk.typ, tk.value
        if tk_value == kw_method:
            F.skip_once()
            return self.parse_method_block()
        elif tk_value == kw_class_assign:
            F.skip_once()
            return self.parse_class_assign_stat()
        elif tk_value == kw_class_init:
            F.skip_once()
            return self.parse_class_init_stat()
        else:
            return super().parse()


class MacroBlockStatParser(StatParser):
    def __init__(self, ExpParser=ExpParser) -> None:
        StatParser.__init__(self, ExpParser)

    @pos_tracker
    def parse(self):
        tk = F.try_look_ahead()
        kind, tk_value = tk.typ, tk.value
        if tk_value == "@":
            pass
