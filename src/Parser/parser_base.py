import functools
import sys
sys.path.append("..")

from .parse_abc import ParserABC

'''
Define decorator @parse_type(...)
'''

def exp_type(type):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        wrapper.__type__ = type
        return wrapper
    return decorator

class ParserBase(ParserABC):
    def __init__(self, token_list : list) -> None:
        super().__init__(token_list)

    def error(self, f, *args):
        err = f
        err = '{0}:  {1}'.format(self.tokens[self.pos],
                    err)
        raise Exception(err)