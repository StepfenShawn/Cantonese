from can_source.parser_base import Parser_base, can_context
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
    def parse_exp(cur_parser: Parser_base, parser: Parser_base, by):
        if (hasattr(parser, "parse_%s" % by.__type__)):
            res_exp = getattr(parser, "parse_%s" % by.__type__)()
            cur_parser.last_tk = parser.last_tk
            return res_exp
        else:
            raise Exception(\
        "Unkonown exp type, If you case this error please issue to Cantonese repo on github")

    @staticmethod
    def many(cur_parser: Parser_base, parser: Parser_base, 
             by: str, util_cond) -> list:
        result = []
        while not util_cond():
            result.append(getattr(parser, by)())
        return result
    
    @staticmethod
    def oneplus(cur_parser: Parser_base, parser: Parser_base,
                by: str, util_cond) -> list:
        result = [getattr(parser, by)()]
        while not util_cond():
            result.append(getattr(parser, by)())
        return result

    @staticmethod
    def maybe(cur_parser: Parser_base, parser: Parser_base, 
              by: str, case_cond) -> object:
        result = None
        if case_cond():
            cur_parser.skip_once()
            result = getattr(parser, by)()
        return result