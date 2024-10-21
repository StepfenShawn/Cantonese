from can_source.can_lexer.can_lexer import *
import can_source.can_ast as can_ast


class MacroPatParser:

    @classmethod
    def from_ParserFn(cls, F):
        cls.Fn = F
        return cls

    @classmethod
    def parse_meta_var(cls):
        """
        解析宏规则里面嘅元变量 eg: `@v: str`
        """
        cls.Fn.skip_once()
        _id = cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER)
        cls.Fn.eat_tk_by_value(":")
        frag_spec = cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER)
        meta_exp = can_ast.MacroMetaId(_id, frag_spec)
        return meta_exp

    @classmethod
    def parse_meta_rep_exp(cls):
        """
        解析宏规则里面嘅表达式 eg: `$(...)+`
        """
        cls.Fn.skip_once()
        cls.Fn.eat_tk_by_kind(TokenType.SEP_LPAREN)
        tokentree = []
        while not cls.Fn.match(TokenType.SEP_RPAREN):
            tokentree.append(cls.parse_macro_rule())
        cls.Fn.eat_tk_by_kind(TokenType.SEP_RPAREN)
        return cls.finish_meta_exp(tokentree)

    @classmethod
    def parse_meta_rep_stmt(cls):
        """
        解析宏定义(`block`)里面嘅表达式 eg: `$(...)+`
        """
        cls.Fn.skip_once()
        tokentree = cls.parse_tokentrees()
        return cls.finish_meta_exp(tokentree)

    @classmethod
    def parse_macro_rule(cls) -> list:
        if cls.Fn.match("$"):
            return cls.parse_meta_rep_exp()
        elif cls.Fn.match("@"):
            return cls.parse_meta_var()
        else:
            return cls.Fn.look_ahead()

    @classmethod
    def finish_meta_exp(cls, meta_exp):
        meta_exp = can_ast.MacroMetaRepExpInPat(meta_exp, None, None)
        meta_exp.rep_sep = cls.Fn.look_ahead().value
        op_tk = cls.Fn.eat_tk_by_value(["*", "+", "?"])
        meta_exp.rep_op = op_tk.value
        return meta_exp

    @classmethod
    def parse_tokentrees(cls) -> list:
        tokentrees = []
        open_ch = cls.Fn.eat_tk_by_kind(TokenType.SEP_LPAREN)
        while not cls.Fn.match(TokenType.SEP_RPAREN):
            next_tk = cls.Fn.try_look_ahead()
            if next_tk.typ == TokenType.SEP_LPAREN:
                tokentrees.append(cls.parse_tokentrees())
            elif next_tk.value == "@":
                cls.Fn.skip_once()
                meta_var = cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER)
                tokentrees.append(can_ast.MetaIdExp(meta_var.value))
            else:
                cls.Fn.skip_once()
                tokentrees.append(next_tk)
        close_ch = cls.Fn.eat_tk_by_kind(TokenType.SEP_RPAREN)
        return can_ast.TokenTree(tokentrees, open_ch, close_ch)
