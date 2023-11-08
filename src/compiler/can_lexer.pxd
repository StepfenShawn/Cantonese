# distutils: language=c++

from keywords cimport *

cdef class can_token:
    cdef:
        public int lineno
        public TokenType typ
        public str value

cdef class lexer:

    cdef:
        public str code
        public tuple keywords
        public int line

    cdef:
        readonly str re_number
        readonly str re_id
        readonly str re_str
        readonly str re_expr
        readonly str re_python_expr
        readonly str re_callfunc
        readonly str op
        readonly list op_get_code
        readonly list op_gen_code
        readonly object build_in_funcs
        readonly list bif_get_code
        readonly list bif_gen_code

    cdef:
        public list make_rep(self, list list1, list list2)
        public str trans(self, str code, list rep)
        public next(self, int n)
        public check(self, str s)
        
        skip_space(self)
        
        public str scan(self, str pattern)
        public str scan_identifier(self)
        public str scan_expr(self)
        public str scan_python_expr(self)
        public str scan_number(self)
        public str scan_callfunc(self)
        public str scan_short_string(self)
        error(self, str args)
        can_token get_token(self)

        @staticmethod
        cdef bint is_white_space(str c)
        @staticmethod
        cdef bint is_new_line(str c)
        @staticmethod
        cdef bint isChinese(str word)

cpdef list cantonese_token(str code)