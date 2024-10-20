import os
import can_source.can_ast as can_ast

from can_source.can_lexer.can_lexer import *
from can_source.can_parser.macro.pattern_parser import MacroPatParser
from can_source.can_parser.macro.body_parser import MacroBodyParser
from can_source.can_context import can_macros_context
from can_source.can_error.compile_time import MacroNotFound
from can_source.can_utils.show.infoprinter import ErrorPrinter


class ExpParser:
    @classmethod
    def from_ParserFn(cls, F):
        cls.Fn = F
        return cls

    @classmethod
    def parse_exp_list(cls):
        exps = [cls.parse_exp()]

        while cls.Fn.match(TokenType.SEP_COMMA):
            cls.Fn.skip_once()
            exps.append(cls.parse_exp())
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

    @classmethod
    def parse_exp(cls):
        # parse the expr by such precedence:  exp13 > exp12 > exp11 > .. > exp0
        # TODO: build a precedence map
        return cls.parse_exp13()

    # exp1 ==> exp2
    @classmethod
    def parse_exp13(cls):
        exp = cls.parse_exp12()
        if cls.Fn.match("==>"):
            cls.Fn.skip_once()
            exp = can_ast.MappingExp(exp, cls.parse_exp12())
        return exp

    # exp1 or exp2
    @classmethod
    def parse_exp12(cls):
        exp = cls.parse_exp11()
        while cls.Fn.match(["or", "或者"]):
            cls.Fn.skip_once()
            exp = can_ast.BinopExp("or", exp, cls.parse_exp11())
        return exp

    # exp1 and exp2
    @classmethod
    def parse_exp11(cls):
        exp = cls.parse_exp10()
        while cls.Fn.match(["and", "同埋"]):
            cls.Fn.skip_once()
            exp = can_ast.BinopExp("and", exp, cls.parse_exp10())
        return exp

    # Compare
    @classmethod
    def parse_exp10(cls):
        exp = cls.parse_exp9()
        while True:
            if cls.Fn.match([">", ">=", "<", "<=", "==", "!=", kw_is]):
                now = cls.Fn.try_look_ahead()
                op = now.value
                cls.Fn.skip_once()
                exp = can_ast.BinopExp(
                    op if op != kw_is else "==", exp, cls.parse_exp9()
                )

            elif cls.Fn.match(["in", kw_in]):
                cls.Fn.skip_once()
                exp = can_ast.BinopExp(" in ", exp, cls.parse_exp9())

            elif cls.Fn.match("比唔上"):
                cls.Fn.skip_once()
                exp = can_ast.BinopExp("<", exp, cls.parse_exp9())

            else:
                break
        return exp

    # exp1 <|> exp2
    @classmethod
    def parse_exp9(cls):
        exp = cls.parse_exp8()
        while cls.Fn.match(TokenType.OP_BOR) or cls.Fn.match("或"):
            cls.Fn.skip_once()
            exp = can_ast.BinopExp("|", exp, cls.parse_exp8())
        return exp

    # exp1 ^ exp2
    @classmethod
    def parse_exp8(cls):
        exp = cls.parse_exp7()
        while cls.Fn.match(TokenType.OP_WAVE) or cls.Fn.match("異或"):
            cls.Fn.skip_once()
            exp = can_ast.BinopExp("^", exp, cls.parse_exp8())
        return exp

    # exp1 & exp2
    @classmethod
    def parse_exp7(cls):
        exp = cls.parse_exp6()
        while cls.Fn.match(TokenType.OP_BAND) or cls.Fn.match("與"):
            cls.Fn.skip_once()
            exp = can_ast.BinopExp("&", exp, cls.parse_exp8())
        return exp

    # shift
    @classmethod
    def parse_exp6(cls):
        exp = cls.parse_exp5()
        if cls.Fn.match([TokenType.OP_SHL, TokenType.OP_SHR]):
            op = cls.Fn.try_look_ahead().value
            cls.Fn.skip_once()  # Skip the op
            exp = can_ast.BinopExp(op, exp, cls.parse_exp5())

        elif cls.Fn.match("左移"):
            cls.Fn.skip_once()  # Skip the op
            exp = can_ast.BinopExp("<<", exp, cls.parse_exp5())

        elif cls.Fn.match("右移"):
            cls.Fn.skip_once()  # Skip the op
            exp = can_ast.BinopExp(">>", exp, cls.parse_exp5())

        else:
            return exp
        return exp

    # exp1 <-> exp2
    @classmethod
    def parse_exp5(cls):
        exp = cls.parse_exp4()
        if not cls.Fn.match(TokenType.OP_CONCAT):
            return exp

        exps = [exp]
        while cls.Fn.match(TokenType.OP_CONCAT):
            cls.Fn.skip_once()
            exps.append(cls.parse_exp4())
        return can_ast.ConcatExp(exps)

    # exp1 + / - exp2
    @classmethod
    def parse_exp4(cls):
        exp = cls.parse_exp3()
        while True:
            if cls.Fn.match([TokenType.OP_ADD, TokenType.OP_MINUS]):
                op = cls.Fn.try_look_ahead().value
                cls.Fn.skip_once()  # skip the op
                exp = can_ast.BinopExp(op, exp, cls.parse_exp3())

            elif cls.Fn.match("加"):
                cls.Fn.skip_once()  # skip the op
                exp = can_ast.BinopExp("+", exp, cls.parse_exp3())

            elif cls.Fn.match("減"):
                cls.Fn.skip_once()  # skip the op
                exp = can_ast.BinopExp("-", exp, cls.parse_exp3())

            else:
                break

        return exp

    # *, %, /, //
    @classmethod
    def parse_exp3(cls):
        exp = cls.parse_exp2()
        while True:
            if cls.Fn.match(
                [
                    TokenType.OP_MUL,
                    TokenType.OP_MOD,
                    TokenType.OP_DIV,
                    TokenType.OP_IDIV,
                ]
            ):
                op = cls.Fn.try_look_ahead().value
                cls.Fn.skip_once()  # Skip the op
                exp = can_ast.BinopExp(op, exp, cls.parse_exp2())

            elif cls.Fn.match("乘"):
                cls.Fn.skip_once()  # Skip the op
                exp = can_ast.BinopExp("*", exp, cls.parse_exp2())

            elif cls.Fn.match("餘"):
                cls.Fn.skip_once()  # Skip the op
                exp = can_ast.BinopExp("%", exp, cls.parse_exp2())

            elif cls.Fn.match("整除"):
                cls.Fn.skip_once()  # Skip the op
                exp = can_ast.BinopExp("//", exp, cls.parse_exp2())

            elif cls.Fn.match("除"):
                cls.Fn.skip_once()  # Skip the op
                exp = can_ast.BinopExp("//", exp, cls.parse_exp2())

            else:
                break

        return exp

    # unop exp
    @classmethod
    def parse_exp2(cls):
        if cls.Fn.match("not") or cls.Fn.match("-") or cls.Fn.match("~"):

            op = cls.Fn.try_look_ahead().value
            cls.Fn.skip_once()  # Skip the op
            exp = can_ast.UnopExp(op, cls.parse_exp2())
            return exp

        elif cls.Fn.match("取反"):
            op = "~"
            cls.Fn.skip_once()  # Skip the op
            exp = can_ast.UnopExp(op, cls.parse_exp2())
            return exp

        return cls.parse_exp1()

    # x ** y
    @classmethod
    def parse_exp1(cls):
        exp = cls.parse_exp0()
        if cls.Fn.match(TokenType.OP_POW):
            op = cls.Fn.try_look_ahead().value
            cls.Fn.skip_once()  # Skip the op
            exp = can_ast.BinopExp(op, exp, cls.parse_exp2())
        return exp

    @classmethod
    def parse_exp0(cls):
        tk = cls.Fn.try_look_ahead()
        if tk.value == "<*>":
            cls.Fn.skip_once()
            return can_ast.VarArgExp()

        elif tk.typ == TokenType.NUM:
            cls.Fn.skip_once()
            return can_ast.NumeralExp(tk.value)

        elif tk.typ == TokenType.SEP_LCURLY:
            return cls.parse_mapcons()

        # If-Else expr
        elif tk.value in [kw_expr_if]:
            cls.Fn.skip_once()
            return cls.parse_if_else_expr()

        return cls.parse_prefixexp()

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

    @classmethod
    def parse_prefixexp(cls):
        if cls.Fn.match(TokenType.IDENTIFIER):
            name = cls.Fn.look_ahead().value
            exp = can_ast.IdExp(name)
        elif cls.Fn.match(TokenType.STRING):
            tk = cls.Fn.look_ahead()
            exp = can_ast.StringExp(tk.value)
        elif cls.Fn.match(TokenType.SEP_LBRACK):
            exp = cls.parse_listcons()
        elif cls.Fn.match("@"):
            cls.Fn.skip_once()
            id_tk = cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER)
            exp = can_ast.MetaIdExp(id_tk.value)
        # '(' exp ')'
        elif cls.Fn.match(TokenType.SEP_LPAREN):
            exp = cls.parse_parens_exp()
        # lambda function
        elif cls.Fn.match("$$"):
            cls.Fn.skip_once()
            exp = cls.parse_functiondef_expr()
        # meta rep
        elif cls.Fn.match("$"):
            exp = MacroBodyParser.from_ParserFn(cls.Fn).parse_meta_rep_stmt(cls)
            return exp
        # '|' exp '|'
        else:
            exp = cls.parse_brack_exp()

        return cls.finish_prefixexp(exp)

    @classmethod
    def parse_parens_exp(cls):
        cls.Fn.eat_tk_by_kind(TokenType.SEP_LPAREN)
        exp = cls.parse_exp()
        cls.Fn.eat_tk_by_kind(TokenType.SEP_RPAREN)
        return exp

    @classmethod
    def parse_brack_exp(cls):
        cls.Fn.eat_tk_by_value("|")
        exp = cls.parse_exp()
        cls.Fn.eat_tk_by_value("|")
        return exp

    """
    listcons := '[' exp_list ']'
    """

    @classmethod
    def parse_listcons(cls):
        cls.Fn.eat_tk_by_kind(TokenType.SEP_LBRACK)
        if cls.Fn.match(TokenType.SEP_RBRACK):  # []
            cls.Fn.skip_once()
            return can_ast.ListExp("")
        else:
            exps = cls.parse_exp_list()
            cls.Fn.eat_tk_by_kind(TokenType.SEP_RBRACK)
            return can_ast.ListExp(exps)

    """
    set_or_mapcons := '{' exp_list '}'
    """

    @classmethod
    def parse_mapcons(cls):
        cls.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)
        if cls.Fn.match(TokenType.SEP_RCURLY):  # {}
            cls.Fn.skip_once()
            return can_ast.MapExp("")
        else:
            exps = cls.parse_exp_list()
            cls.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
            return can_ast.MapExp(exps)

    @classmethod
    def finish_prefixexp(cls, exp: can_ast.AST):
        while True:
            next_tk = cls.Fn.try_look_ahead()
            kind, value = next_tk.typ, next_tk.value
            if kind == TokenType.SEP_LBRACK:
                cls.Fn.skip_once()
                key_exp: can_ast.AST = cls.parse_exp()
                cls.Fn.eat_tk_by_kind(TokenType.SEP_RBRACK)
                exp = can_ast.ListAccessExp(exp, key_exp)
            elif (
                kind == TokenType.SEP_DOT
                or (kind == TokenType.KEYWORD and value == kw_dot)
                or (kind == TokenType.IDENTIFIER and value == "嘅")
            ):
                cls.Fn.skip_once()
                tk = cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER)
                name = tk.value
                key_exp = can_ast.IdExp(name)
                exp = can_ast.ObjectAccessExp(exp, key_exp)
            elif (kind == TokenType.SEP_LPAREN) or (
                kind == TokenType.KEYWORD and value == kw_call_begin
            ):
                exp = cls.finish_functioncall_exp(exp)
            elif kind == TokenType.OP_ASSIGN:
                cls.Fn.skip_once()
                exp = can_ast.AssignExp(exp, cls.parse_exp())
            elif kind == TokenType.COLON:
                cls.Fn.skip_once()
                exp = can_ast.AnnotationExp(exp, cls.parse_exp())
                break
            elif kind == TokenType.EXCL:
                cls.Fn.skip_once()
                macro_name = exp.name
                if (
                    not can_macros_context.lazy_expand
                    and macro_name not in can_macros_context.macros
                ):
                    raise MacroNotFound(
                        f"揾唔到你嘅Macro: `{macro_name}`\n"
                        + "係咪Macro喺其它文件? 咁就試下{% 路徑::"
                        + macro_name
                        + " %} 啦!"
                    )
                tokentrees = MacroPatParser.from_ParserFn(cls.Fn).parse_tokentrees()
                if can_macros_context.lazy_expand:
                    exp = can_ast.CallMacro(macro_name, tokentrees)
                else:
                    exp = can_macros_context.get(macro_name).expand(tokentrees)
                break
            else:
                break
        return exp

    """
    functioncall ::= prefixexp '下' '->' args
                  | prefixexp args
    """

    @classmethod
    def finish_functioncall_exp(cls, prefix_exp: can_ast.AST):
        if cls.Fn.match(kw_call_begin):
            cls.Fn.skip_once()
            cls.Fn.eat_tk_by_value(kw_dot)
            args = cls.parse_args()
            return can_ast.FuncCallExp(prefix_exp, args)
        else:
            args = cls.parse_args()
            return can_ast.FuncCallExp(prefix_exp, args)

    @classmethod
    def parse_parlist(cls):
        next_tk = cls.Fn.try_look_ahead()
        if next_tk.typ == TokenType.IDENTIFIER or next_tk.value == "<*>":
            exps = cls.parse_exp_list()
            return exps

        elif next_tk.value == "|":
            cls.Fn.skip_once()
            exps = cls.parse_exp_list()
            cls.Fn.eat_tk_by_value("|")
            return exps

        else:
            return []

    """
    idlist ::= id [',', id]
            | '|' id [',', id] '|'
    """

    @classmethod
    def parse_idlist(cls):
        tk = cls.Fn.try_look_ahead()
        if tk.typ == TokenType.IDENTIFIER:
            ids = [can_ast.IdExp(tk.value)]
            cls.Fn.skip_once()
            while cls.Fn.match(TokenType.SEP_COMMA):
                cls.Fn.skip_once()
                if cls.Fn.try_look_ahead().typ != TokenType.IDENTIFIER:
                    cls.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(cls.Fn.look_ahead().value))
            return ids

        elif cls.Fn.match("|"):
            cls.Fn.skip_once()
            ids = [can_ast.IdExp((cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER)).value)]
            while cls.Fn.match(TokenType.SEP_COMMA):
                cls.Fn.skip_once()
                if not cls.Fn.match(TokenType.IDENTIFIER):
                    cls.Fn.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(cls.Fn.look_ahead().value))
            cls.Fn.eat_tk_by_value("|")
            return ids

        else:
            return None

    """
    lambda_functoindef ::= '$$' idlist '{' exp_list '}'
    """

    @classmethod
    def parse_functiondef_expr(cls):
        idlist: list = cls.parse_idlist()
        blocks: list = []
        cls.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)
        blocks = cls.parse_exp_list()
        cls.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
        return can_ast.LambdaExp(idlist, blocks)

    @classmethod
    def parse_if_else_expr(cls):
        CondExp: can_ast.AST = cls.parse_exp()
        cls.Fn.eat_tk_by_value(kw_dot)
        IfExp: can_ast.AST = cls.parse_exp()
        cls.Fn.eat_tk_by_value(kw_expr_else)
        cls.Fn.eat_tk_by_value(kw_dot)
        ElseExp: can_ast.AST = cls.parse_exp()

        return can_ast.IfElseExp(CondExp, IfExp, ElseExp)

    """
    args ::= '|' explist '|'
           | '(' {explist} ')'
           | explist
           | LiteralString
           | Numeral
           | id
    """

    @classmethod
    def parse_args(cls):
        args = []
        tk = cls.Fn.try_look_ahead()
        if tk.value == "(":
            cls.Fn.skip_once()
            next_tk = cls.Fn.try_look_ahead()
            if next_tk.value != ")":
                args = cls.parse_exp_list()
            cls.Fn.eat_tk_by_kind(TokenType.SEP_RPAREN)
        elif tk.value == "|":
            cls.Fn.skip_once()
            next_tk = cls.Fn.try_look_ahead()
            if next_tk.value != "|":
                args = cls.parse_exp_list()
            cls.Fn.eat_tk_by_value("|")
        else:
            args = cls.parse_exp_list()
        return args

    @classmethod
    def parse_attrs_def(cls):
        tk = cls.Fn.try_look_ahead()
        if tk.typ == TokenType.IDENTIFIER:
            cls.Fn.skip_once()
            cls.Fn.eat_tk_by_value(":")
            attrs = [
                can_ast.AnnotationExp(
                    can_ast.IdExp(tk.value),
                    can_ast.IdExp(cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER).value),
                )
            ]
            while cls.Fn.try_look_ahead().typ == TokenType.SEP_COMMA:
                cls.Fn.skip_once()
                tk = cls.Fn.try_look_ahead()
                if tk.typ != TokenType.IDENTIFIER:
                    break
                else:
                    cls.Fn.skip_once()
                    cls.Fn.eat_tk_by_value(":")
                    attrs.append(
                        can_ast.AnnotationExp(
                            can_ast.IdExp(tk.value),
                            can_ast.IdExp(
                                cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER).value
                            ),
                        )
                    )
            return attrs
