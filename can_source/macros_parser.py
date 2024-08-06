from can_source.can_lexer import *
import can_source.can_ast as can_ast
from can_source.parser_base import F
# from can_source.util.can_utils import ParserF as F


class MacroParser:
    def parse_meta_exp(self):
        F.skip_once()
        if F.try_look_ahead().typ == TokenType.SEP_LPAREN:
            meta_exp = self.parse_macro_rule()
            return self.finish_meta_exp(meta_exp)
        
        elif F.try_look_ahead().typ == TokenType.IDENTIFIER:
            _id = F.eat_tk_by_kind(TokenType.IDENTIFIER)
            F.eat_tk_by_value(':')
            frag_spec = F.eat_tk_by_kind(TokenType.IDENTIFIER)
            meta_exp = can_ast.MacroMetaId(_id, frag_spec)
            return meta_exp

    def parse_macro_rule(self) -> list:
        tokentrees = []
        tokentrees.append(
            F.eat_tk_by_kind(TokenType.SEP_LPAREN))
        while F.try_look_ahead().typ != TokenType.SEP_RPAREN:
            next_tk = F.try_look_ahead()
            if next_tk.value == '@':
                tokentrees.append(self.parse_meta_exp())
            elif next_tk.typ == TokenType.SEP_LPAREN:
                tokentrees.extend(self.parse_macro_rule())
            else:
                F.skip_once()
                tokentrees.append(next_tk)
        tokentrees.append(
            F.eat_tk_by_kind(TokenType.SEP_RPAREN)
        )
        return tokentrees
    
    def finish_meta_exp(self, meta_exp):
        next_tk = F.try_look_ahead()
        meta_exp = can_ast.MacroMetaExp(meta_exp, None, None)
        if next_tk.value == ',':
            F.skip_once()
            meta_exp.rep_sep = next_tk.value
            next_tk = F.try_look_ahead()
        if next_tk.value in ["*", "+", "?"]:
            F.skip_once()
            meta_exp.rep_op = next_tk.value
        
        return meta_exp
    
    def parse_tokentrees(self) -> list:
        tokentrees = []
        tokentrees.append(
            F.eat_tk_by_kind(TokenType.SEP_LCURLY))
        while F.try_look_ahead().typ != TokenType.SEP_RCURLY:
            next_tk = F.try_look_ahead()
            if next_tk.typ == TokenType.SEP_LCURLY:
                tokentrees.extend(self.parse_tokentrees())
            else:
                F.skip_once()
                tokentrees.append(next_tk)
        tokentrees.append(
            F.eat_tk_by_kind(TokenType.SEP_RCURLY))
        return tokentrees