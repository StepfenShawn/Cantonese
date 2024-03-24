from can_source.can_lexer import can_token, TokenType
from can_source.parser_base import ParserBase
import functools

def exp_type(type):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__type__ = type
        return wrapper
    return decorator

class ParserF:

    @staticmethod
    def parse_exp(cur_parser: ParserBase, parser: ParserBase, by):
        if (hasattr(parser, "parse_%s" % by.__type__)):
            res_exp = getattr(parser, "parse_%s" % by.__type__)()
            cur_parser.last_tk = parser.last_tk
            return res_exp
        else:
            raise Exception(\
        "Unkonown exp type, If you case this error please issue to Cantonese repo on github")

    @staticmethod
    def many(cur_parser: ParserBase, parser: ParserBase, 
             by: str, util_cond) -> list:
        result = []
        while not util_cond():
            p = parser(cur_parser.get_token_ctx())
            result.append(getattr(p, by)())
        return result

    @staticmethod
    def maybe(cur_parser: ParserBase, parser: ParserBase, 
              by: str, case_cond) -> object:
        result = None
        if case_cond():
            cur_parser.skip_once()
            p = parser(cur_parser.get_token_ctx())
            result = getattr(p, by)()
        return result
