from can_source.can_lexer.can_lexer import *
import can_source.can_ast as can_ast


class DependTree:
    def __init__(self, v):
        self.v = v
        self.child = None


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
        depend_tree = DependTree(root_exp)
        cur = depend_tree
        while cls.Fn.match(TokenType.DCOLON):
            cls.Fn.skip_once()
            if cls.Fn.match(TokenType.IDENTIFIER):
                new_node = DependTree(
                    can_ast.IdExp(
                        name=cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER).value
                    )
                )
                cur.child = [new_node]
                cur = new_node
            elif cls.Fn.match("*"):
                cls.Fn.skip_once()
                cur.child = [DependTree(can_ast.IdExp(name="*"))]
                break
            elif cls.Fn.match(TokenType.SEP_LCURLY):
                cls.Fn.skip_once()
                cur.child = cls.parse_names_set()
                cls.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
                break
        return depend_tree

    @classmethod
    def parse_names_set(cls):
        ret = [cls.parse()]
        while cls.Fn.match(TokenType.SEP_COMMA):
            cls.Fn.skip_once()
            ret.append(cls.parse())
        return ret
