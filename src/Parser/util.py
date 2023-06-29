from lexer.keywords import *
from .parse_abc import ParserABC
from .parser_base import *

"""
    Static Factory methods for Parser
"""

class ParserUtil:

    @staticmethod
    def get_type(token : list) -> TokenType:
        return token[1][0]

    @staticmethod
    def get_token_value(token : list) -> str:
        return token[1][1]

    @staticmethod
    def parse_exp(cur_parser : ParserABC, parser : ParserABC, by : exp_type, dontskip=False):
        if (hasattr(parser, "parse_%s" % by.__type__)):
            res_exp = getattr(parser, "parse_%s" % by.__type__)()
            if not dontskip:
                cur_parser.skip(parser.pos)
            return res_exp
        else:
            raise Exception(\
        "Unkonown exp type, If you case this error please issue to Cantonese repo on github")