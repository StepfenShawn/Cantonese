from can_source.can_lexer.can_lexer import *
import can_source.can_ast as can_ast


class NamesParser:
    @classmethod
    def from_ParserFn(cls, F):
        cls.Fn = F
        return cls

    @classmethod
    def parse(cls):
        id_exp = can_ast.IdExp(name=cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER).value)
        return cls.finish(id_exp)

    @classmethod
    def finish(cls, root_exp):
        chains = [root_exp]
        while cls.Fn.match(TokenType.DCOLON):
            cls.Fn.skip_once()
            if cls.Fn.match(TokenType.IDENTIFIER):
                chains.append(
                    can_ast.IdExp(name=cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER).value)
                )
            elif cls.Fn.match("*"):
                chains.append(can_ast.IdExp(name="*"))
            elif cls.Fn.match(TokenType.SEP_LCURLY):
                cls.Fn.skip_once()
                l = cls.parse_names_set()
                if l:
                    chains.append(l)
                cls.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
                break
        return chains
    
    @classmethod
    def parse_names_set(cls):
        if cls.Fn.match(TokenType.IDENTIFIER):
            tk = cls.Fn.look_ahead()
            ids = [can_ast.IdExp(tk.value)]
            while cls.Fn.match(TokenType.SEP_COMMA):
                cls.Fn.skip_once()
                if not cls.Fn.match(TokenType.IDENTIFIER):
                    cls.error("Excepted identifier type in library names set!")
                ids.append(can_ast.IdExp(cls.Fn.look_ahead().value))
            return ids

        else:
            return None
