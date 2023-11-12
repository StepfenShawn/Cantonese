from can_lexer cimport TokenType, can_token

# The root(father) of all Parser classes
cdef class ParserBase:
    cdef:
        public int pos
        public list tokens
        
    cpdef public can_token look_ahead(self, int step)
    cpdef public can_token current(self)
    cpdef public can_token get_next_token_of_kind(self, TokenType k, int step)
    cpdef public can_token get_next_token_of(self, object expectation, int step)
    cpdef public skip(self, int step)
    cpdef public int get_line(self)
        
    cpdef readonly error(self, object args)