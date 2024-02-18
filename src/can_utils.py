from can_lexer import can_token, TokenType
from parser_base import ParserBase
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
    def get_type(token : can_token) -> TokenType:
        return token.typ

    @staticmethod
    def get_token_value(token : can_token) -> str:
        return token.value

    @staticmethod
    def parse_exp(cur_parser: ParserBase, parser: ParserBase, by, dontskip=False):
        if (hasattr(parser, "parse_%s" % by.__type__)):
            res_exp = getattr(parser, "parse_%s" % by.__type__)()
            if not dontskip:
                cur_parser.skip(parser.pos)
            return res_exp
        else:
            raise Exception(\
        "Unkonown exp type, If you case this error please issue to Cantonese repo on github")