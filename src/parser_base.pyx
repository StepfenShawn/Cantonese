from can_lexer cimport TokenType, can_token

# The root(father) of all Parser classes.
cdef class ParserBase:

    def __init__(self, token_list : list) -> None:
        self.pos = 0
        self.tokens = token_list

    cpdef can_token look_ahead(self, int step):
        return self.tokens[self.pos + step]

    cpdef can_token current(self):
        return self.look_ahead(0)

    cpdef can_token get_next_token_of_kind(self, TokenType k, int step):
        cdef can_token tk = self.look_ahead(step)
        cdef object err = ""
        if k != tk.typ:
            err = f"Line {tk.line}: {tk.value}附近睇唔明啊大佬!!! Excepted: {str(k)}"
            self.error(err)
        self.pos += 1
        return tk
    
    cpdef can_token get_next_token_of(self, object expectation, int step):
        cdef can_token tk = self.look_ahead(step)
        cdef object err = ""
        if isinstance(expectation, list):
            if tk.value not in expectation:
                err = f"Line {tk.lineno}: 睇唔明嘅语法: {tk.value}系唔系'{expectation}'啊?"
                self.error(err)
            self.pos += 1
            return tk
        else:
            if expectation != tk.value:
                err = f"Line {tk.lineno}: 睇唔明嘅语法: {tk.value}系唔系'{expectation}'啊?"
                self.error(err)
            self.pos += 1
            return tk

    cpdef skip(self, int step):
        self.pos += step

    cpdef int get_line(self):
        return self.tokens[self.pos].lineno

    cpdef error(self, object args):
        raise Exception(args)