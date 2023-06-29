from abc import ABC, abstractmethod

class ParserABC(ABC):
    def __init__(self, token_list : list) -> None:
        self.pos = 0
        self.tokens = token_list

    def look_ahead(self, step = 1) -> list:
        return self.tokens[self.pos + step]

    def current(self) -> list:
        return self.look_ahead(0)

    def get_next_token_of_kind(self, k, step = 1) -> list:
        tk = self.look_ahead(step)
        if k != tk[1][0]:
            err = 'Line %s: %s附近睇唔明啊大佬!!! Excepted: %s' % (str(tk[0]), str(tk[1][1]), str(k))
            self.error(err)
        self.pos += 1
        return tk
    
    def get_next_token_of(self, expectation : str, step = 1) -> list:
        tk = self.look_ahead(step)
        if isinstance(expectation, list):
            if tk[1][1] not in expectation:
                err = 'Line {0}: 睇唔明嘅语法: {1}系唔系"{2}"啊?'.format(tk[0], tk[1][1], expectation)
                self.error(err)
            self.pos += 1
            return tk
        else:
            if expectation != tk[1][1]:
                err = 'Line {0}: 睇唔明嘅语法: {1}系唔系"{2}"啊?'.format(tk[0], tk[1][1], expectation)
                self.error(err)
            self.pos += 1
            return tk

    def skip(self, step) -> None:
        self.pos += step

    def get_line(self) -> int:
        return self.tokens[self.pos][0]

    @abstractmethod
    def error(self, f, *args):
       pass