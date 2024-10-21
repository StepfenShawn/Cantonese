from can_source.can_lexer.can_lexer import *
import can_source.can_ast as can_ast


class MacroBodyParser:

    @classmethod
    def from_ParserFn(cls, F):
        cls.Fn = F
        return cls

    @classmethod
    def parse_meta_rep_stmt(cls):  # type: ignore
        """
        解析宏定义(`body`)里面嘅表达式 eg: `${...}+`
        """
        cls.Fn.skip_once()
        token_tree = cls.parse_tokentrees()
        return cls.finish_meta_exp(token_tree)

    @classmethod
    def finish_meta_exp(cls, exp):
        meta_exp = can_ast.MacroMetaRepExpInBlock(exp, None, None)
        meta_exp.rep_sep = cls.Fn.look_ahead()
        op_tk = cls.Fn.eat_tk_by_value(["*", "+", "?"])
        meta_exp.rep_op = op_tk.value
        return meta_exp

    @classmethod
    def parse_tokentrees(cls) -> list:  # type: ignore
        tokentrees = []
        open_ch = cls.Fn.eat_tk_by_kind(TokenType.SEP_LCURLY)
        while not cls.Fn.match(TokenType.SEP_RCURLY):
            next_tk = cls.Fn.try_look_ahead()
            if next_tk.typ == TokenType.SEP_LCURLY:
                tokentrees.append(cls.parse_tokentrees())
            elif next_tk.value == "@":
                cls.Fn.skip_once()
                meta_var = cls.Fn.eat_tk_by_kind(TokenType.IDENTIFIER)
                tokentrees.append(can_ast.MetaIdExp(meta_var.value))
            elif next_tk.value == "$":
                tokentrees.append(cls.parse_meta_rep_stmt())
            else:
                cls.Fn.skip_once()
                tokentrees.append(next_tk)
        close_ch = cls.Fn.eat_tk_by_kind(TokenType.SEP_RCURLY)
        return can_ast.TokenTree(tokentrees, open_ch, close_ch)
