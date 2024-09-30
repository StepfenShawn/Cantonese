from can_source.can_lexer import *
import can_source.can_ast as can_ast
from can_source.parser_base import F


class MacroParser:
    @classmethod
    def parse_meta_var(cls):
        """
        解析宏规则里面嘅元变量 eg: `@v: str`
        """
        F.skip_once()
        _id = F.eat_tk_by_kind(TokenType.IDENTIFIER)
        F.eat_tk_by_value(":")
        frag_spec = F.eat_tk_by_kind(TokenType.IDENTIFIER)
        meta_exp = can_ast.MacroMetaId(_id, frag_spec)
        return meta_exp

    @classmethod
    def parse_meta_exp(cls):
        """
        解析宏规则里面嘅表达式 eg: `$(...)+`
        """
        F.skip_once()
        F.eat_tk_by_kind(TokenType.SEP_LPAREN)
        exp_atom = []
        while F.try_look_ahead().typ != TokenType.SEP_RPAREN:
            meta_exp = exp_atom.extend(cls.parse_macro_rule())
        F.eat_tk_by_kind(TokenType.SEP_RPAREN)
        return cls.finish_meta_exp(meta_exp)

    @classmethod
    def parse_macro_rule(cls) -> list:
        next_tk = F.try_look_ahead()
        if next_tk.value == "$":
            return cls.parse_meta_exp()
        elif next_tk.value == "@":
            return cls.parse_meta_var()
        else:
            F.skip_once()
            return next_tk

    @classmethod
    def finish_meta_exp(cls, meta_exp):
        next_tk = F.try_look_ahead()
        meta_exp = can_ast.MacroMetaExp(meta_exp, None, None)
        if next_tk.value == ",":
            F.skip_once()
            meta_exp.rep_sep = next_tk.value
            next_tk = F.try_look_ahead()
        if next_tk.value in ["*", "+", "?"]:
            F.skip_once()
            meta_exp.rep_op = next_tk.value

        return meta_exp

    @classmethod
    def parse_tokentrees(cls) -> list:
        tokentrees = []
        F.eat_tk_by_kind(TokenType.SEP_LCURLY)
        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            next_tk = F.try_look_ahead()
            if next_tk.typ == TokenType.SEP_LCURLY:
                tokentrees.extend(cls.parse_tokentrees())
            else:
                F.skip_once()
                tokentrees.append(next_tk)
        F.eat_tk_by_kind(TokenType.SEP_RCURLY)
        return tokentrees
