from can_source.can_lexer import *
import can_source.can_ast as can_ast
from can_source.parser_base import F
from can_source.macros_parser import MacroParser
from can_source.can_sys import can_macros_context

class ExpParser:

    @classmethod
    def parse_exp_list(cls):
        exps = [cls.parse_exp()]

        while F.try_look_ahead().typ == TokenType.SEP_COMMA:
            F.skip_once()
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
        # parse the expr by such precedence:  exp13 > exp12 > exp11 > ... > exp0
        # TODO: build a precedence map
        return cls.parse_exp13()

    # exp1 ==> exp2
    @classmethod
    def parse_exp13(cls):
        exp = cls.parse_exp12()
        if F.try_look_ahead().value == "==>":
            F.skip_once()
            exp = can_ast.MappingExp(exp, cls.parse_exp12())
        return exp

    # exp1 or exp2
    @classmethod
    def parse_exp12(cls):
        exp = cls.parse_exp11()
        while F.try_look_ahead().value in ["or", "或者"]:
            F.skip_once()
            exp = can_ast.BinopExp("or", exp, cls.parse_exp11())
        return exp

    # exp1 and exp2
    @classmethod
    def parse_exp11(cls):
        exp = cls.parse_exp10()
        while F.try_look_ahead().value in ["and", "同埋"]:
            F.skip_once()
            exp = can_ast.BinopExp("and", exp, cls.parse_exp10())
        return exp

    # Compare
    @classmethod
    def parse_exp10(cls):
        exp = cls.parse_exp9()
        while True:
            now = F.try_look_ahead()
            if now.value in (">", ">=", "<", "<=", "==", "!=", kw_is):
                op = now.value
                F.skip_once()
                exp = can_ast.BinopExp(
                    op if op != kw_is else "==", exp, cls.parse_exp9()
                )

            elif now.value in ("in", kw_in):
                F.skip_once()
                exp = can_ast.BinopExp(" in ", exp, cls.parse_exp9())

            elif now.value == "比唔上":
                F.skip_once()
                exp = can_ast.BinopExp("<", exp, cls.parse_exp9())

            else:
                break
        return exp

    # exp1 <|> exp2
    @classmethod
    def parse_exp9(cls):
        exp = cls.parse_exp8()
        while (
            F.try_look_ahead().typ == TokenType.OP_BOR
            or F.try_look_ahead().value == "或"
        ):
            F.skip_once()
            exp = can_ast.BinopExp("|", exp, cls.parse_exp8())
        return exp

    # exp1 ^ exp2
    @classmethod
    def parse_exp8(cls):
        exp = cls.parse_exp7()
        while (
            F.try_look_ahead().typ == TokenType.OP_WAVE
            or F.try_look_ahead().value == "異或"
        ):
            F.skip_once()
            exp = can_ast.BinopExp("^", exp, cls.parse_exp8())
        return exp

    # exp1 & exp2
    @classmethod
    def parse_exp7(cls):
        exp = cls.parse_exp6()
        while (
            F.try_look_ahead().typ == TokenType.OP_BAND
            or F.try_look_ahead().value == "與"
        ):
            F.skip_once()
            exp = can_ast.BinopExp("&", exp, cls.parse_exp8())
        return exp

    # shift
    @classmethod
    def parse_exp6(cls):
        exp = cls.parse_exp5()
        if F.try_look_ahead().typ in (TokenType.OP_SHL, TokenType.OP_SHR):
            op = F.try_look_ahead().value
            F.skip_once()  # Skip the op
            exp = can_ast.BinopExp(op, exp, cls.parse_exp5())

        elif F.try_look_ahead().value == "左移":
            F.skip_once()  # Skip the op
            exp = can_ast.BinopExp("<<", exp, cls.parse_exp5())

        elif F.try_look_ahead().value == "右移":
            F.skip_once()  # Skip the op
            exp = can_ast.BinopExp(">>", exp, cls.parse_exp5())

        else:
            return exp
        return exp

    # exp1 <-> exp2
    @classmethod
    def parse_exp5(cls):
        exp = cls.parse_exp4()
        if F.try_look_ahead().typ != TokenType.OP_CONCAT:
            return exp

        exps = [exp]
        while F.try_look_ahead().typ == TokenType.OP_CONCAT:
            F.skip_once()
            exps.append(cls.parse_exp4())
        return can_ast.ConcatExp(exps)

    # exp1 + / - exp2
    @classmethod
    def parse_exp4(cls):
        exp = cls.parse_exp3()
        while True:
            if F.try_look_ahead().typ in (TokenType.OP_ADD, TokenType.OP_MINUS):
                op = F.try_look_ahead().value
                F.skip_once()  # skip the op
                exp = can_ast.BinopExp(op, exp, cls.parse_exp3())

            elif F.try_look_ahead().value == "加":
                F.skip_once()  # skip the op
                exp = can_ast.BinopExp("+", exp, cls.parse_exp3())

            elif F.try_look_ahead().value == "減":
                F.skip_once()  # skip the op
                exp = can_ast.BinopExp("-", exp, cls.parse_exp3())

            else:
                break

        return exp

    # *, %, /, //
    @classmethod
    def parse_exp3(cls):
        exp = cls.parse_exp2()
        while True:
            if F.try_look_ahead().typ in (
                TokenType.OP_MUL,
                TokenType.OP_MOD,
                TokenType.OP_DIV,
                TokenType.OP_IDIV,
            ):
                op = F.try_look_ahead().value
                F.skip_once()  # Skip the op
                exp = can_ast.BinopExp(op, exp, cls.parse_exp2())

            elif F.try_look_ahead().value == "乘":
                F.skip_once()  # Skip the op
                exp = can_ast.BinopExp("*", exp, cls.parse_exp2())

            elif F.try_look_ahead().value == "餘":
                F.skip_once()  # Skip the op
                exp = can_ast.BinopExp("%", exp, cls.parse_exp2())

            elif F.try_look_ahead().value == "整除":
                F.skip_once()  # Skip the op
                exp = can_ast.BinopExp("//", exp, cls.parse_exp2())

            elif F.try_look_ahead().value == "除":
                F.skip_once()  # Skip the op
                exp = can_ast.BinopExp("//", exp, cls.parse_exp2())

            else:
                break

        return exp

    # unop exp
    @classmethod
    def parse_exp2(cls):
        if (
            F.try_look_ahead().value == "not"
            or F.try_look_ahead().value == "-"
            or F.try_look_ahead().value == "~"
        ):

            op = F.try_look_ahead().value
            F.skip_once()  # Skip the op
            exp = can_ast.UnopExp(op, cls.parse_exp2())
            return exp

        elif F.try_look_ahead().value == "取反":
            op = "~"
            F.skip_once()  # Skip the op
            exp = can_ast.UnopExp(op, cls.parse_exp2())
            return exp

        return cls.parse_exp1()

    # x ** y
    @classmethod
    def parse_exp1(cls):
        exp = cls.parse_exp0()
        if F.try_look_ahead().typ == TokenType.OP_POW:
            op = F.try_look_ahead().value
            F.skip_once()  # Skip the op
            exp = can_ast.BinopExp(op, exp, cls.parse_exp2())
        return exp

    @classmethod
    def parse_exp0(cls):
        tk = F.try_look_ahead()
        if tk.value == "<*>":
            F.skip_once()
            return can_ast.VarArgExp()

        elif tk.typ == TokenType.NUM:
            F.skip_once()
            return can_ast.NumeralExp(tk.value)

        elif tk.typ == TokenType.STRING:
            F.skip_once()
            return can_ast.StringExp(tk.value)

        elif tk.typ == TokenType.SEP_LBRACK:
            return cls.parse_listcons()

        elif tk.typ == TokenType.SEP_LCURLY:
            return cls.parse_mapcons()

        # If-Else expr
        elif tk.value in [kw_expr_if]:
            F.skip_once()
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
        next_tk = F.try_look_ahead()
        if next_tk.typ == TokenType.IDENTIFIER:
            name = next_tk.value
            F.skip_once()
            exp = can_ast.IdExp(name)
        elif next_tk.value == "@":
            F.skip_once()
            id_tk = F.eat_tk_by_kind(TokenType.IDENTIFIER)
            exp = can_ast.MetaIdExp(id_tk.value)
        # '(' exp ')'
        elif next_tk.typ == TokenType.SEP_LPAREN:
            exp = cls.parse_parens_exp()
        # lambda function
        elif next_tk.value == "$$":
            F.skip_once()
            exp = cls.parse_functiondef_expr()
        # '|' exp '|'
        else:
            exp = cls.parse_brack_exp()

        return cls.finish_prefixexp(exp)

    @classmethod
    def parse_parens_exp(cls):
        F.eat_tk_by_kind(TokenType.SEP_LPAREN)
        exp = cls.parse_exp()
        F.eat_tk_by_kind(TokenType.SEP_RPAREN)
        return exp

    @classmethod
    def parse_brack_exp(cls):
        F.eat_tk_by_value("|")
        exp = cls.parse_exp()
        F.eat_tk_by_value("|")
        return exp

    """
    listcons := '[' exp_list ']'
    """

    @classmethod
    def parse_listcons(cls):
        F.eat_tk_by_kind(TokenType.SEP_LBRACK)
        next_tk = F.try_look_ahead()
        if next_tk.typ == TokenType.SEP_RBRACK:  # []
            F.skip_once()
            return can_ast.ListExp("")
        else:
            exps = cls.parse_exp_list()
            F.eat_tk_by_kind(TokenType.SEP_RBRACK)
            return can_ast.ListExp(exps)

    """
    set_or_mapcons := '{' exp_list '}'
    """

    @classmethod
    def parse_mapcons(cls):
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)
        next_tk = F.try_look_ahead()
        if next_tk.typ == TokenType.SEP_RCURLY:  # {}
            F.skip_once()
            return can_ast.MapExp("")
        else:
            exps = cls.parse_exp_list()
            F.eat_tk_by_kind(TokenType.SEP_RCURLY)
            return can_ast.MapExp(exps)

    @classmethod
    def finish_prefixexp(cls, exp: can_ast.AST):
        while True:
            next_tk = F.try_look_ahead()
            kind, value = next_tk.typ, next_tk.value
            if kind == TokenType.SEP_LBRACK:
                F.skip_once()
                key_exp: can_ast.AST = cls.parse_exp()
                F.eat_tk_by_kind(TokenType.SEP_RBRACK)
                exp = can_ast.ListAccessExp(exp, key_exp)
            elif (
                kind == TokenType.SEP_DOT
                or (kind == TokenType.KEYWORD and value == kw_dot)
                or (kind == TokenType.IDENTIFIER and value == "嘅")
            ):
                F.skip_once()
                tk = F.eat_tk_by_kind(TokenType.IDENTIFIER)
                name = tk.value
                key_exp = can_ast.IdExp(name)
                exp = can_ast.ObjectAccessExp(exp, key_exp)
            elif (kind == TokenType.SEP_LPAREN) or (
                kind == TokenType.KEYWORD and value == kw_call_begin
            ):
                exp = cls.finish_functioncall_exp(exp)
            elif kind == TokenType.OP_ASSIGN:
                F.skip_once()
                exp = can_ast.AssignExp(exp, cls.parse_exp())
            elif kind == TokenType.COLON:
                F.skip_once()
                exp = can_ast.AnnotationExp(exp, cls.parse_exp())
                break
            elif kind == TokenType.EXCL:
                F.skip_once()
                macro_name = exp.name
                tokentrees = MacroParser.parse_tokentrees()[1:-1]
                if macro_name not in can_macros_context.macros:
                    raise Exception(f"macro {macro_name} not found!")
                exp = can_macros_context.get(macro_name).eval(tokentrees)
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
        if F.try_look_ahead().value == kw_call_begin:
            F.skip_once()
            F.eat_tk_by_value(kw_dot)
            args = cls.parse_args()
            return can_ast.FuncCallExp(prefix_exp, args)
        else:
            args = cls.parse_args()
            return can_ast.FuncCallExp(prefix_exp, args)

    @classmethod
    def parse_parlist(cls):
        next_tk = F.try_look_ahead()
        if next_tk.typ == TokenType.IDENTIFIER or next_tk.value == "<*>":
            par_parser = ParExpParser(cls.get_token_ctx())
            exps = par_parser.parse_exp_list()
            return exps

        elif next_tk.value == "|":
            F.skip_once()
            par_parser = ParExpParser(cls.get_token_ctx())
            exps = par_parser.parse_exp_list()
            F.eat_tk_by_value("|")
            return exps

        else:
            return []

    """
    idlist ::= id [',', id]
            | '|' id [',', id] '|'
    """

    @classmethod
    def parse_idlist(cls):
        tk = F.try_look_ahead()
        if tk.typ == TokenType.IDENTIFIER:
            ids = [can_ast.IdExp(tk.value)]
            F.skip_once()
            while F.try_look_ahead().typ == TokenType.SEP_COMMA:
                F.skip_once()
                if F.try_look_ahead().typ != TokenType.IDENTIFIER:
                    cls.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(F.look_ahead().value))
            return ids

        elif F.try_look_ahead().value == "|":
            F.skip_once()
            ids = [can_ast.IdExp((F.eat_tk_by_kind(TokenType.IDENTIFIER)).value)]
            while F.try_look_ahead().typ == TokenType.SEP_COMMA:
                F.skip_once()
                if F.try_look_ahead().typ != TokenType.IDENTIFIER:
                    F.error("Excepted identifier type in idlist!")
                ids.append(can_ast.IdExp(F.look_ahead().value))
            F.eat_tk_by_value("|")
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
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)
        blocks = cls.parse_exp_list()
        F.eat_tk_by_kind(TokenType.SEP_RCURLY)
        return can_ast.LambdaExp(idlist, blocks)

    @classmethod
    def parse_if_else_expr(cls):
        CondExp: can_ast.AST = cls.parse_exp()
        F.eat_tk_by_value(kw_dot)
        IfExp: can_ast.AST = cls.parse_exp()
        F.eat_tk_by_value(kw_expr_else)
        F.eat_tk_by_value(kw_dot)
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
        tk = F.try_look_ahead()
        if tk.value == "(":
            F.skip_once()
            next_tk = F.try_look_ahead()
            if next_tk.value != ")":
                args = cls.parse_exp_list()
            F.eat_tk_by_kind(TokenType.SEP_RPAREN)
        elif tk.value == "|":
            F.skip_once()
            next_tk = F.try_look_ahead()
            if next_tk.value != "|":
                args = cls.parse_exp_list()
            F.eat_tk_by_value("|")
        else:
            args = cls.parse_exp_list()
        return args

    @classmethod
    def parse_attrs_def(cls):
        tk = F.try_look_ahead()
        if tk.typ == TokenType.IDENTIFIER:
            F.skip_once()
            F.eat_tk_by_value(":")
            attrs = [
                can_ast.AnnotationExp(
                    can_ast.IdExp(tk.value),
                    can_ast.IdExp(F.eat_tk_by_kind(TokenType.IDENTIFIER).value),
                )
            ]
            while F.try_look_ahead().typ == TokenType.SEP_COMMA:
                F.skip_once()
                tk = F.try_look_ahead()
                if tk.typ != TokenType.IDENTIFIER:
                    break
                else:
                    F.skip_once()
                    F.eat_tk_by_value(":")
                    attrs.append(
                        can_ast.AnnotationExp(
                            can_ast.IdExp(tk.value),
                            can_ast.IdExp(F.eat_tk_by_kind(TokenType.IDENTIFIER).value),
                        )
                    )
            return attrs


"""
    parlist ::= id [',', id | '<*>']
             | id '=' exp [',' id]
             | '<*>'
"""


class ParExpParser(ExpParser):

    # override
    def parse_exp(cls):
        return cls.parse_exp0()

    # override
    def parse_exp0(cls):
        tk = F.try_look_ahead()

        if tk.value == "<*>":
            F.skip_once()
            return can_ast.VarArgExp()

        return cls.parse_prefixexp()

    # override
    def parse_prefixexp(cls):
        tk = F.try_look_ahead()
        if tk.typ == TokenType.IDENTIFIER:
            name = tk.value
            F.skip_once()
            exp = can_ast.IdExp(name)
            return cls.finish_prefixexp(exp)
        else:
            raise Exception("Parlist must be a identifier type!")

    # override
    def finish_prefixexp(cls, exp: can_ast.AST):
        value = F.try_look_ahead().value
        if value == "=" or value == "==>":
            F.skip_once()
            exp_parser = ExpParser(cls.get_token_ctx())
            exp2 = exp_parser.parse_exp()
            return can_ast.AssignExp(exp, exp2)
        return exp
