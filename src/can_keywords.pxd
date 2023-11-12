cdef enum TokenType:
    EOF = 0
    VARARG = 1         # <*>
    SEP_COMMA = 2      # ,
    SEP_DOT = 3        # .
    SEP_LPAREN = 4     # (
    SEP_RPAREN = 5     # )
    SEP_LBRACK = 6     # [
    SEP_RBRACK = 7     # ]
    SEP_LCURLY = 8     # {
    SEP_RCURLY = 9     # }
    OP_MINUS = 10      # -
    OP_WAVE = 11       # !
    OP_ADD = 12        # +
    OP_MUL = 13        # *
    OP_DIV = 14        # /
    OP_POW = 15        # ^
    OP_MOD = 16        # %
    OP_BAND = 17       # &
    OP_SHR = 18        # >>
    OP_SHL = 19        # <<
    OP_CONCAT = 20     # ---> or <---
    OP_LT = 21         # <
    OP_LE = 22         # <=
    OP_GT = 23         # >
    OP_GE = 24         # >=
    OP_EQ = 25         # ==
    OP_ASSIGN = 26     # =
    OP_NE = 27         # !=
    OP_AND = 28        # and
    OP_OR = 29         # or
    OP_NOT = 30        # not
    OP_BOR = 31        # |
    OP_IDIV = 32       # //
    KEYWORD = 33
    IDENTIFIER = 34
    STRING = 35
    NUM = 36
    EXTEND_EXPR = 37 # Call the other language,
    SEPCIFIC_ID_BEG = 38 # <|
    SEPICFIC_ID_END = 39 # |>

cdef tuple keywords

cdef:
    str kw_print
    str kw_endprint
    str kw_exit
    str kw_in
    str kw_elif
    str kw_turtle_beg
    str kw_type
    str kw_assign
    str kw_class_def
    str kw_else_or_not
    str kw_is
    str kw_if
    str kw_expr_if
    str kw_expr_else
    str kw_then
    str kw_do
    str kw_begin
    str kw_end
    str kw_pass
    str kw_while_do
    str kw_function
    str kw_call
    str kw_import
    str kw_func_begin
    str kw_func_end
    str kw_is_2
    str kw_assert
    str kw_class_assign
    str kw_while
    str kw_whi_end
    str kw_return
    str kw_try
    str kw_except
    str kw_finally
    str kw_raise
    str kw_raise_end
    str kw_from
    str kw_to
    str kw_endfor
    str kw_extend
    str kw_method
    str kw_endclass
    str kw_cmd
    str kw_break
    str kw_continue
    str kw_lst_assign
    str kw_set_assign
    str kw_global_set
    str kw_is_3
    str kw_exit_1
    str kw_exit_2
    str kw_false
    str kw_true
    str kw_none
    str kw_stackinit
    str kw_push
    str kw_pop
    str kw_model
    str kw_mod_new
    str kw_class_init
    str kw_self
    str kw_call_begin
    str kw_get_value
    str kw_del
    str kw_del2
    str kw_match
    str kw_case