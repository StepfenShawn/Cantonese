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

class ParserUtil:

    @staticmethod
    def parse_exp(cur_parser: ParserBase, parser: ParserBase, by):
        if (hasattr(parser, "parse_%s" % by.__type__)):
            res_exp = getattr(parser, "parse_%s" % by.__type__)()
            cur_parser.last_tk = parser.last_tk
            return res_exp
        else:
            raise Exception(\
        "Unkonown exp type, If you case this error please issue to Cantonese repo on github")