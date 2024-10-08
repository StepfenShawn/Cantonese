from can_source.can_lexer import *
import can_source.can_ast as can_ast
from can_source.parser_base import ParserFn, pos_tracker
from can_source.exp_parser import ExpParser
from can_source.macros_parser import MacroParser
from can_source.can_sys import can_macros_context
from can_source.can_macros import CanMacro


class StatParser:

    def __init__(self, from_):
        if isinstance(from_, ParserFn):
            self.Fn = from_
        else:
            self.Fn = ParserFn(ctx=from_)

    def parse_var_list(self):
        exp = ExpParser.from_ParserFn(self.Fn).parse_prefixexp()
        var_list: list = [self.check_var(exp)]
        while self.Fn.try_look_ahead().typ == TokenType.SEP_COMMA:
            self.Fn.skip_once()
            exp = ExpParser.from_ParserFn(self.Fn).parse_prefixexp()
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
        tk = self.Fn.try_look_ahead()
        kind, tk_value = tk.typ, tk.value

        if kind == TokenType.KEYWORD:
            if tk_value == kw_print:
                self.Fn.skip_once()
                return self.parse_print_stat()

            elif tk_value in [kw_exit, kw_exit_1, kw_exit_2]:
                self.Fn.skip_once()
                return self.parse_exit_stat()

            elif tk_value == kw_assign:
                self.Fn.skip_once()
                return self.parse_assign_stat()

            elif tk_value == kw_if:
                self.Fn.skip_once()
                return self.parse_if_stat()

            elif tk_value == kw_import:
                self.Fn.skip_once()
                return self.parse_import_stat()

            elif tk_value == kw_global_set:
                self.Fn.skip_once()
                return self.parse_global_stat()

            elif tk_value == kw_break:
                self.Fn.skip_once()
                return self.parse_break_stat()

            elif tk_value == kw_continue:
                self.Fn.skip_once()
                return self.parse_continue_stat()

            elif tk_value == kw_while_do:
                self.Fn.skip_once()
                return self.parse_while_stat()

            elif tk_value == kw_pass:
                self.Fn.skip_once()
                return self.parse_pass_stat()

            elif tk_value == kw_return:
                self.Fn.skip_once()
                return self.parse_return_stat()

            elif tk_value == kw_del:
                self.Fn.skip_once()
                return self.parse_del_stat()

            elif tk_value == kw_type:
                self.Fn.skip_once()
                return self.exp_type_stat()

            elif tk_value == kw_assert:
                self.Fn.skip_once()
                return self.parse_assert_stat()

            elif tk_value == kw_try:
                self.Fn.skip_once()
                return self.parse_try_stat()

            elif tk_value == kw_raise:
                self.Fn.skip_once()
                return self.parse_raise_stat()

            elif tk_value == kw_cmd:
                self.Fn.skip_once()
                return self.parse_cmd_stat()

            elif tk_value == kw_stackinit:
                self.Fn.skip_once()
                return self.parse_stack_init_stat()

            elif tk_value == kw_push:
                self.Fn.skip_once()
                return self.parse_stack_push_stat()

            elif tk_value == kw_pop:
                self.Fn.skip_once()
                return self.parse_stack_pop_stat()

            elif tk_value == kw_match:
                self.Fn.skip_once()
                return self.parse_match_stat()

            elif tk_value == kw_call_native:
                self.Fn.skip_once()
                return self.parse_call_native_stat()

            elif tk_value == "&&":
                self.Fn.skip_once()
                return self.parse_for_each_stat()

            elif tk_value == kw_pls:
                self.Fn.skip_once()
                return self.parse_pls_stat()

            else:
                self.Fn.error(
                    tk,
                    info=f"\033[0;31m濑嘢!!!\033[0m: 個`{tk.value}`好似有D唔三唔四",
                    tips=f" 幫緊你只不過有心無力 :(",
                )

        elif kind == TokenType.EOF:
            return "EOF"

        else:
            return self.with_prefix_stats()

    def with_prefix_stats(self):
        prefix_exp = ExpParser.from_ParserFn(self.Fn).parse_exp()
        next_tk = self.Fn.try_look_ahead()
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
        args = ExpParser.from_ParserFn(self.Fn).parse_args()
        self.Fn.eat_tk_by_value(kw_endprint)
        return can_ast.PrintStat(args)

    # Parser for muti-assign
    def parse_assign_block(self):
        # Nothing in assignment block
        if self.Fn.try_look_ahead().value == kw_end_assign:
            self.Fn.skip_once()
            return can_ast.PassStat()
        var_list: list = []
        exp_list: list = []
        while self.Fn.try_look_ahead().value != kw_end_assign:
            var_list.append(self.parse_var_list()[0])
            self.Fn.eat_tk_by_value(kw_is)
            exp_list.append(ExpParser.from_ParserFn(self.Fn).parse_exp_list()[0])

        self.Fn.eat_tk_by_value(kw_end_assign)
        return can_ast.AssignBlockStat(var_list, exp_list)

    def parse_assign_stat(self):
        if self.Fn.try_look_ahead().value == kw_do:
            # Skip the kw_do
            self.Fn.skip_once()
            return self.parse_assign_block()
        elif self.Fn.try_look_ahead().value == kw_function:
            self.Fn.skip_once()
            return self.parse_func_def_stat()
        else:
            var_list = self.parse_var_list()
            self.Fn.eat_tk_by_value(kw_is)
            if self.Fn.try_look_ahead().value == kw_class_def:
                self.Fn.skip_once()
                return self.parse_class_def(class_name=var_list[0])
            elif self.Fn.try_look_ahead().value == kw_macro_def:
                self.Fn.skip_once()
                return self.parse_macro_def(macro_name=var_list[0])
            else:
                exp_list = ExpParser.from_ParserFn(self.Fn).parse_exp_list()
                return can_ast.AssignStat(var_list, exp_list)

    def parse_exit_stat(self):
        return can_ast.ExitStat()

    def parse_if_stat(self):

        elif_exps: list = []
        elif_blocks: list = []
        else_blocks: list = []

        if_exps = ExpParser.from_ParserFn(self.Fn).parse_exp()

        self.Fn.eats((kw_then, kw_do, TokenType.SEP_LCURLY))

        if_blocks = self.Fn.many(
            other_parse_fn=self.parse,
            util_cond=lambda: self.Fn.try_look_ahead().typ == TokenType.SEP_RCURLY,
        )

        self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)

        while self.Fn.try_look_ahead().value in [kw_elif]:
            self.Fn.eat_tk_by_value(kw_elif)

            elif_exps.append(ExpParser.from_ParserFn(self.Fn).parse_exp())

            self.Fn.eats((kw_then, kw_do, TokenType.SEP_LCURLY))

            elif_block = self.Fn.many(
                other_parse_fn=self.parse,
                util_cond=lambda: self.Fn.try_look_ahead().typ == TokenType.SEP_RCURLY,
            )

            elif_blocks.append(elif_block)

            self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)  # Skip the SEP_RCURLY '}'

        if self.Fn.try_look_ahead().value == kw_else_or_not:
            self.Fn.eats((kw_else_or_not, kw_then, kw_do, TokenType.SEP_LCURLY))

            else_blocks = self.Fn.many(
                other_parse_fn=self.parse,
                util_cond=lambda: self.Fn.try_look_ahead().typ == TokenType.SEP_RCURLY,
            )

            self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)  # Skip the SEP_RCURLY '}'

        return can_ast.IfStat(if_exps, if_blocks, elif_exps, elif_blocks, else_blocks)

    def parse_import_stat(self):
        idlist = ExpParser.from_ParserFn(self.Fn).parse_idlist()
        return can_ast.ImportStat(idlist)

    def parse_global_stat(self):
        idlist = ExpParser.from_ParserFn(self.Fn).parse_idlist()
        return can_ast.GlobalStat(idlist)

    def parse_break_stat(self):
        return can_ast.BreakStat()

    def parse_continue_stat(self):
        return can_ast.ContinueStat()

    def parse_while_stat(self):
        blocks = self.Fn.many(
            other_parse_fn=self.parse,
            util_cond=lambda: self.Fn.try_look_ahead().value == kw_while,
        )

        self.Fn.eat_tk_by_value(kw_while)  # Skip the kw_while

        cond_exps = ExpParser.from_ParserFn(self.Fn).parse_exp()
        self.Fn.eat_tk_by_value(kw_whi_end)

        return can_ast.WhileStat(can_ast.UnopExp("not", cond_exps), blocks)

    def parse_for_stat(self, prefix_exp: can_ast.AST):
        blocks: list = []

        id = prefix_exp

        self.Fn.eat_tk_by_value(kw_from)

        from_exp = ExpParser.from_ParserFn(self.Fn).parse_exp()
        self.Fn.eat_tk_by_value(kw_to)

        to_exp = ExpParser.from_ParserFn(self.Fn).parse_exp()

        blocks = self.Fn.many(
            other_parse_fn=self.parse,
            util_cond=lambda: self.Fn.try_look_ahead().value == kw_endfor,
        )

        self.Fn.eat_tk_by_value(kw_endfor)

        return can_ast.ForStat(id, from_exp, to_exp, blocks)

    def parse_func_def_stat(self):
        name = self.Fn.eat_tk_by_kind(TokenType.IDENTIFIER).value
        args = ExpParser.from_ParserFn(self.Fn).parse_parlist()
        args = [] if args == None else args

        self.Fn.eat_tk_by_value([kw_func_begin, kw_do])

        blocks = self.Fn.many(
            other_parse_fn=self.parse,
            util_cond=lambda: self.Fn.try_look_ahead().value == kw_func_end,
        )

        self.Fn.eat_tk_by_value(kw_func_end)

        return can_ast.FunctionDefStat(can_ast.IdExp(name), args, blocks)

    def parse_suffix_assign_stat(self, prefix_exp: can_ast.AST):
        self.Fn.skip_once()
        var_list = self.parse_var_list()
        return can_ast.AssignStat(var_list, [prefix_exp])

    def parse_class_method_call_stat(self, prefix_exp: can_ast.AST):
        self.Fn.eat_tk_by_value([kw_laa1, kw_gamlaa1])
        return can_ast.CallStat(prefix_exp)

    def parse_list_assign_stat(self, prefix_exp: can_ast.AST):
        self.Fn.eat_tk_by_value(kw_lst_assign)
        self.Fn.eat_tk_by_value(kw_do)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(varlist, [prefix_exp])

    def parse_set_assign_stat(self, prefix_exp: can_ast.AST):
        self.Fn.eat_tk_by_value(kw_set_assign)
        self.Fn.eat_tk_by_value(kw_do)
        varlist = self.parse_var_list()

        return can_ast.AssignStat(varlist, [prefix_exp])

    def parse_pass_stat(self):
        return can_ast.PassStat()

    def parse_assert_stat(self):
        exp = ExpParser.from_ParserFn(self.Fn).parse_exp()
        return can_ast.AssertStat(exp)

    def parse_return_stat(self):
        exps = ExpParser.from_ParserFn(self.Fn).parse_exp_list()
        return can_ast.ReturnStat(exps)

    def parse_del_stat(self):
        exps = ExpParser.from_ParserFn(self.Fn).parse_exp_list()
        return can_ast.DelStat(exps)

    def parse_try_stat(self):
        self.Fn.eat_tk_by_value(kw_do)
        self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

        try_blocks: list = []
        except_exps: list = []
        except_blocks: list = []
        finally_blocks: list = []

        while self.Fn.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(
                self.get_token_ctx(), self.ExpParser.from_ParserFn(self.Fn)
            )
            try_blocks.append(block_parser.parse())

        self.Fn.skip_once()
        self.Fn.eat_tk_by_value([kw_except])

        except_exps.append(ExpParser.from_ParserFn(self.Fn).parse_exp())

        self.Fn.eat_tk_by_value([kw_then])
        self.Fn.eat_tk_by_value([kw_do])
        self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

        # a temp list to save the block
        except_block = []
        while self.Fn.try_look_ahead().typ != TokenType.SEP_RCURLY:
            block_parser = StatParser(
                self.get_token_ctx(), self.ExpParser.from_ParserFn(self.Fn)
            )
            except_block.append(block_parser.parse())

        self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
        except_blocks.append(except_block)

        while self.Fn.try_look_ahead().value == kw_except:
            self.Fn.skip_once()
            self.Fn.eat_tk_by_value(kw_then)

            exp_parser = self.getExpParser()
            except_exps.append(exp_parser.parse_exp())

            self.Fn.eat_tk_by_value(kw_do)
            self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

            # clear the list
            except_block = []
            while self.Fn.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(
                    self.get_token_ctx(), self.ExpParser.from_ParserFn(self.Fn)
                )
                except_block.append(block_parser.parse())

            except_blocks.append(except_block)

        if self.Fn.try_look_ahead().value == kw_finally:
            self.Fn.skip_once()
            self.Fn.eat_tk_by_value(kw_do)
            self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

            while self.Fn.try_look_ahead().typ != TokenType.SEP_RCURLY:
                block_parser = StatParser(
                    self.get_token_ctx(), self.ExpParser.from_ParserFn(self.Fn)
                )
                finally_blocks.append(block_parser.parse())

            self.Fn.skip_once()

        return can_ast.TryStat(try_blocks, except_exps, except_blocks, finally_blocks)

    def parse_raise_stat(self):
        name_exp = ExpParser.from_ParserFn(self.Fn).parse_exp()
        self.Fn.eat_tk_by_value(kw_raise_end)
        return can_ast.RaiseStat(name_exp)

    def exp_type_stat(self):
        name_exp = ExpParser.from_ParserFn(self.Fn).parse_exp()
        return can_ast.TypeStat(name_exp)

    def parse_cmd_stat(self):
        args = ExpParser.from_ParserFn(self.Fn).parse_args()
        return can_ast.CmdStat(args)

    def parse_macro_block(self):
        tk = self.Fn.try_look_ahead()
        # case a meta expr
        if tk.value == "$":
            return ""
        else:
            return self.parse()

    def parse_macro_def(self, macro_name: can_ast.AST):
        self.Fn.eat_tk_by_value(kw_do)
        match_rules: list = []
        match_blocks: list = []

        while self.Fn.try_look_ahead().value != kw_func_end:
            while self.Fn.try_look_ahead().value == "|":
                self.Fn.skip_once()
                self.Fn.eat_tk_by_kind(TokenType.SEP_LPAREN)
                cur_match_rules = self.Fn.many(
                    other_parse_fn=MacroParser.from_ParserFn(self.Fn).parse_macro_rule,
                    util_cond=lambda: self.Fn.try_look_ahead().typ
                    == TokenType.SEP_RPAREN,
                )
                self.Fn.eat_tk_by_kind(TokenType.SEP_RPAREN)
                match_rules.append(cur_match_rules)
                self.Fn.eats((kw_do, TokenType.SEP_LCURLY))
                block = self.Fn.many(
                    other_parse_fn=self.parse_macro_block,
                    util_cond=lambda: self.Fn.try_look_ahead().typ
                    == TokenType.SEP_RCURLY,
                )

                self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
                match_blocks.append(block)

        self.Fn.eat_tk_by_value(kw_func_end)
        n = macro_name.name
        can_macros_context.update(n, CanMacro(n, match_rules, match_blocks))
        return can_ast.MacroDefStat(match_rules, match_blocks)

    def parse_class_def(self, class_name: can_ast.AST):
        self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

        extend_name = self.Fn.maybe(
            other_parse_fn=ExpParser.from_ParserFn(self.Fn).parse_exp_list,
            case_cond=lambda: self.Fn.try_look_ahead().value == kw_extend,
        )

        class_blocks = self.Fn.many(
            other_parse_fn=self.parse_class_block,
            util_cond=lambda: self.Fn.try_look_ahead().typ == TokenType.SEP_RCURLY,
        )

        self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)

        return can_ast.ClassDefStat(class_name, extend_name, class_blocks)

    def parse_class_block(self):
        tk = self.Fn.try_look_ahead()
        kind, tk_value = tk.typ, tk.value
        if tk_value == kw_method:
            self.Fn.skip_once()
            name_exp = ExpParser.from_ParserFn(self.Fn).parse_exp()

            args = ExpParser.from_ParserFn(self.Fn).parse_idlist()
            args = [] if args == None else args

            self.Fn.eat_tk_by_value(kw_do)
            self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

            blocks = self.Fn.many(
                other_parse_fn=self.parse,
                util_cond=lambda: self.Fn.try_look_ahead().typ == TokenType.SEP_RCURLY,
            )

            self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)

            return can_ast.MethodDefStat(name_exp, args, blocks)

        elif tk_value == kw_class_assign:
            self.Fn.skip_once()
            return self.parse_class_assign_stat()

        elif tk_value == kw_class_init:
            self.Fn.skip_once()
            self.Fn.eat_tk_by_value(kw_do)
            self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)
            attrs = ExpParser.from_ParserFn(self.Fn).parse_attrs_def()
            self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
            return can_ast.AttrDefStat(attrs)

        else:
            return self.parse()

    def parse_stack_init_stat(self):
        exps = ExpParser.from_ParserFn(self.Fn).parse_exp()
        return can_ast.AssignStat(
            [exps], [can_ast.FuncCallExp(can_ast.IdExp("stack"), [])]
        )

    def parse_stack_push_stat(self):
        self.Fn.eat_tk_by_value(kw_do)

        exps = ExpParser.from_ParserFn(self.Fn).parse_exp()
        args = ExpParser.from_ParserFn(self.Fn).parse_args()

        return can_ast.MethodCallStat(exps, can_ast.IdExp("push"), args)

    def parse_stack_pop_stat(self):
        self.Fn.eat_tk_by_value(kw_do)

        exps = ExpParser.from_ParserFn(self.Fn).parse_exp()

        return can_ast.MethodCallStat(exps, can_ast.IdExp("pop"), [])

    def parse_lambda_def_stat(self):
        lambda_exp = [ExpParser.from_ParserFn(self.Fn).parse_functiondef_expr()]

        self.Fn.eat_tk_by_value(kw_get_value)
        id_exp = ExpParser.from_ParserFn(self.Fn).parse_idlist()

        return can_ast.AssignStat(id_exp, lambda_exp)

    def parse_match_stat(self):
        match_val: list = []
        match_block: list = []
        default_match_block: list = []
        match_id = ExpParser.from_ParserFn(self.Fn).parse_exp()

        self.Fn.eat_tk_by_value(kw_do)

        while self.Fn.try_look_ahead().value != kw_func_end:
            while self.Fn.try_look_ahead().value == "|":
                self.Fn.skip_once()
                if self.Fn.try_look_ahead().value == kw_case:
                    self.Fn.skip_once()
                    match_val.append(ExpParser.from_ParserFn(self.Fn).parse_exp())

                    self.Fn.eat_tk_by_value(kw_do)
                    self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

                    block = self.Fn.many(
                        other_parse_fn=self.parse,
                        util_cond=lambda: self.Fn.try_look_ahead().typ
                        == TokenType.SEP_RCURLY,
                    )

                    self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)

                    match_block.append(block)

                elif self.Fn.try_look_ahead().value == "_":
                    self.Fn.skip_once()
                    self.Fn.eat_tk_by_value(kw_do)
                    self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

                    default_match_block = self.Fn.many(
                        other_parse_fn=self.parse,
                        util_cond=lambda: self.Fn.try_look_ahead().typ
                        == TokenType.SEP_RCURLY,
                    )

                    self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)

                else:
                    self.error(
                        self.Fn.try_look_ahead(), info="MatchBlock只允許`撞見`同`_`"
                    )

        self.Fn.eat_tk_by_value(kw_func_end)

        return can_ast.MatchStat(match_id, match_val, match_block, default_match_block)

    def parse_for_each_stat(self):
        id_list = ExpParser.from_ParserFn(self.Fn).parse_idlist()

        self.Fn.eat_tk_by_value(kw_in)

        exp_list = ExpParser.from_ParserFn(self.Fn).parse_exp_list()

        self.Fn.eat_tk_by_value(kw_do)
        self.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)

        blocks = self.Fn.many(
            other_parse_fn=self.parse,
            util_cond=lambda: self.Fn.try_look_ahead().typ == TokenType.SEP_RCURLY,
        )

        self.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)

        return can_ast.ForEachStat(id_list, exp_list, blocks)

    def parse_call_native_stat(self):
        tk = self.Fn.eat_tk_by_kind(TokenType.CALL_NATIVE_EXPR)
        return can_ast.ExtendStat(tk.value[3:-5])

    def parse_pls_stat(self):
        func_name = ExpParser.from_ParserFn(self.Fn).parse_exp()
        self.Fn.eat_tk_by_value(kw_laa1)
        return can_ast.FuncCallStat(func_name, [])
