from can_source.can_lexer import *
import can_source.can_ast as can_ast
from can_source.parser_base import F


class MacroParser:
    @classmethod
    def parse_meta_exp(cls):
        F.skip_once()
        if F.try_look_ahead().typ == TokenType.SEP_LPAREN:
            meta_exp = cls.parse_macro_rule()
            return cls.finish_meta_exp(meta_exp)

        elif F.try_look_ahead().typ == TokenType.IDENTIFIER:
            _id = F.eat_tk_by_kind(TokenType.IDENTIFIER)
            F.eat_tk_by_value(":")
            frag_spec = F.eat_tk_by_kind(TokenType.IDENTIFIER)
            meta_exp = can_ast.MacroMetaId(_id, frag_spec)
            return meta_exp

    @classmethod
    def parse_macro_rule(cls) -> list:
        tokentrees = []
        tokentrees.append(F.eat_tk_by_kind(TokenType.SEP_LPAREN))
        while F.try_look_ahead().typ != TokenType.SEP_RPAREN:
            next_tk = F.try_look_ahead()
            if next_tk.value == "$":
                tokentrees.append(cls.parse_meta_exp())
            elif next_tk.typ == TokenType.SEP_LPAREN:
                tokentrees.extend(cls.parse_macro_rule())
            else:
                F.skip_once()
                tokentrees.append(next_tk)
        tokentrees.append(F.eat_tk_by_kind(TokenType.SEP_RPAREN))
        return tokentrees

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
        tokentrees.append(F.eat_tk_by_kind(TokenType.SEP_LCURLY))
        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            next_tk = F.try_look_ahead()
            if next_tk.typ == TokenType.SEP_LCURLY:
                tokentrees.extend(cls.parse_tokentrees())
            else:
                F.skip_once()
                tokentrees.append(next_tk)
        tokentrees.append(F.eat_tk_by_kind(TokenType.SEP_RCURLY))
        return tokentrees
