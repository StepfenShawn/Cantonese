class TokenType:
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
    
kw_print = "畀我睇下"
kw_endprint = "点样先"
kw_exit = "收工"
kw_in = "喺"
kw_elif = "定系"
kw_turtle_beg = "老作一下"
kw_type = "起底"
kw_assign = "讲嘢"
kw_class_def = "咩系"
kw_else_or_not = "唔系"
kw_is = "系"
kw_if = "如果"
kw_expr_if = "若然"
kw_expr_else = "唔系咁就"
kw_then = "嘅话"
kw_do = "->"
kw_begin = "{"
kw_end = "}"
kw_pass = "咩都唔做"
kw_while_do = "落操场玩跑步"
kw_function = "$"
kw_call = "用下"
kw_import = "使下"
kw_func_begin = "要做咩"
kw_func_end = "搞掂"
kw_is_2 = "就"
kw_assert = "谂下"
kw_class_assign = "佢嘅"
kw_while = "玩到"
kw_whi_end = "为止"
kw_return = "还数"
kw_try = "执嘢"
kw_except = "揾到"
kw_finally = "执手尾"
kw_raise = "掟个"
kw_raise_end = "来睇下"
kw_from = "从"
kw_to = "行到"
kw_endfor = "行晒"
kw_extend = "佢个老豆叫"
kw_method = "佢识得"
kw_endclass = "明白未啊"
kw_cmd = "落Order"
kw_break = "饮茶先啦"
kw_lst_assign = "拍住上"
kw_set_assign = "埋堆"
kw_global_set = "Share下"
kw_is_3 = "係"
kw_exit_1 = "辛苦晒啦"
kw_exit_2 = "同我躝"
kw_false = "唔啱"
kw_true = "啱"
kw_none = "冇"
kw_stackinit = "有条仆街叫"
kw_push = "顶你"
kw_pop = "丢你"
kw_model = "嗌"
kw_mod_new = "过嚟估下"
kw_class_init = "佢有啲咩"
kw_self = "自己嘅"
kw_call_begin = "下"
kw_get_value = "@" 
kw_del = "delete下"
kw_match = "match下"
kw_case = "撞见"

tr_kw_print = "畀我睇下"
tr_kw_endprint = "點樣先"
tr_kw_exit = "收工"
tr_kw_in = "喺"
tr_kw_elif = "定系"
tr_kw_turtle_beg = "老作一下"
tr_kw_type = "起底"
tr_kw_assign = "講嘢"
tr_kw_class_def = "咩系"
tr_kw_else_or_not = "唔系"
tr_kw_is = "系"
tr_kw_if = "如果"
tr_kw_expr_if = "若然"
tr_kw_expr_else = "唔系咁就"
tr_kw_then = "嘅話"
tr_kw_do = "->"
tr_kw_begin = "{"
tr_kw_end = "}"
tr_kw_pass = "咩都唔做"
tr_kw_while_do = "落操場玩跑步"
tr_kw_function = "$"
tr_kw_call = "用下"
tr_kw_import = "使下"
tr_kw_func_begin = "要做咩"
tr_kw_func_end = "搞掂"
tr_kw_is_2 = "就"
tr_kw_assert = "諗下"
tr_kw_class_assign = "佢嘅"
tr_kw_while = "玩到"
tr_kw_whi_end = "為止"
tr_kw_return = "還數"
tr_kw_try = "執嘢"
tr_kw_except = "揾到"
tr_kw_finally = "執手尾"
tr_kw_raise = "掟個"
tr_kw_raise_end = "來睇下"
tr_kw_from = "從"
tr_kw_to = "行到"
tr_kw_endfor = "行曬"
tr_kw_extend = "佢個老豆叫"
tr_kw_method = "佢識得"
tr_kw_endclass = "明白未啊"
tr_kw_cmd = "落Order"
tr_kw_break = "飲茶先啦"
tr_kw_lst_assign = "拍住上"
tr_kw_set_assign = "埋堆"
tr_kw_global_set = "Share下"
tr_kw_is_3 = "係"
tr_kw_exit_1 = "辛苦曬啦"
tr_kw_exit_2 = "同我躝"
tr_kw_false = "唔啱"
tr_kw_true = "啱"
tr_kw_none = "冇"
tr_kw_stackinit = "有條仆街叫"
tr_kw_push = "頂你"
tr_kw_pop = "丟你"
tr_kw_model = "嗌"
tr_kw_mod_new = "過嚟估下"
tr_kw_class_init = "佢有啲咩"
tr_kw_self = "自己嘅"
tr_kw_call_begin = "下"
tr_kw_get_value = "@"
tr_kw_del = "delete下"
tr_kw_match = "match下"
tr_kw_case = "撞見"

keywords = (
    kw_print,
    kw_endprint,
    kw_exit,
    kw_in,
    kw_elif,
    kw_turtle_beg,
    kw_type,
    kw_assign,
    kw_class_def,
    kw_else_or_not,
    kw_is,
    kw_if,
    kw_expr_if,
    kw_expr_else,
    kw_then,
    kw_do,
    kw_begin,
    kw_end,
    kw_pass,
    kw_while_do,
    kw_function,
    kw_call,
    kw_import,
    kw_func_begin,
    kw_func_end,
    kw_is_2,
    kw_assert,
    kw_class_assign,
    kw_while,
    kw_whi_end,
    kw_return,
    kw_try,
    kw_except,
    kw_finally,
    kw_raise,
    kw_raise_end,
    kw_from,
    kw_to,
    kw_endfor,
    kw_extend,
    kw_method,
    kw_endclass,
    kw_cmd,
    kw_break,
    kw_del,
    kw_lst_assign,
    kw_set_assign,
    kw_global_set,
    kw_is_3,
    kw_exit_1,
    kw_exit_2,
    kw_false,
    kw_true,
    kw_none,
    kw_stackinit,
    kw_push,
    kw_pop,
    kw_model,
    kw_mod_new,
    kw_class_init,
    kw_self,
    kw_call_begin,
    kw_get_value,
    kw_match,
    kw_case,
    tr_kw_print,
    tr_kw_endprint,
    tr_kw_exit,
    tr_kw_in,
    tr_kw_elif,
    tr_kw_turtle_beg,
    tr_kw_type,
    tr_kw_assign,
    tr_kw_class_def,
    tr_kw_else_or_not,
    tr_kw_is,
    tr_kw_if,
    tr_kw_expr_if,
    tr_kw_expr_else,
    tr_kw_then,
    tr_kw_do,
    tr_kw_begin,
    tr_kw_end,
    tr_kw_pass,
    tr_kw_while_do,
    tr_kw_function,
    tr_kw_call,
    tr_kw_import,
    tr_kw_func_begin,
    tr_kw_func_end,
    tr_kw_is_2,
    tr_kw_assert,
    tr_kw_class_assign,
    tr_kw_while,
    tr_kw_whi_end,
    tr_kw_return,
    tr_kw_try,
    tr_kw_except,
    tr_kw_finally,
    tr_kw_raise,
    tr_kw_raise_end,
    tr_kw_from,
    tr_kw_to,
    tr_kw_endfor,
    tr_kw_extend,
    tr_kw_method,
    tr_kw_endclass,
    tr_kw_cmd,
    tr_kw_break,
    tr_kw_lst_assign,
    tr_kw_set_assign,
    tr_kw_global_set,
    tr_kw_is_3,
    tr_kw_exit_1,
    tr_kw_exit_2,
    tr_kw_false,
    tr_kw_true,
    tr_kw_none,
    tr_kw_stackinit,
    tr_kw_push,
    tr_kw_pop,
    tr_kw_model,
    tr_kw_mod_new,
    tr_kw_class_init,
    tr_kw_self,
    tr_kw_call_begin,
    tr_kw_get_value,
    tr_kw_match,
    tr_kw_case
)