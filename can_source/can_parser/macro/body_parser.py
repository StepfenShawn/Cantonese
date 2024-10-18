from can_source.can_lexer.can_lexer import *
import can_source.can_ast as can_ast


class MacroBodyParser:

    @classmethod
    def from_ParserFn(cls, F):
        cls.Fn = F
        return cls

    @classmethod
    def parse_meta_rep_stmt(cls, f: "ExpParser"):  # type: ignore
        """
        解析宏定义(`body`)里面嘅表达式 eg: `$(...)+`
        """
        cls.Fn.skip_once()
        cls.Fn.eat_tk_by_kind(TokenType.SEP_LPAREN)
        exp = f.from_ParserFn(cls.Fn).parse_exp()
        cls.Fn.eat_tk_by_kind(TokenType.SEP_RPAREN)
        return cls.finish_meta_exp(exp)

    @classmethod
    def finish_meta_exp(cls, exp):
        meta_exp = can_ast.MacroMetaRepExp(exp, None, None)
        if not cls.Fn.match(["*", "+", "?"]):
            meta_exp.rep_sep = cls.Fn.look_ahead().value

        op_tk = cls.Fn.eat_tk_by_value(["*", "+", "?"])
        meta_exp.rep_op = op_tk.value
        return meta_exp
