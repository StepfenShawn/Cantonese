from enum import Enum

class TokenType(Enum):
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
    OP_CONCAT = 20     # <->
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
    CALL_NATIVE_EXPR = 37 # Call the other language,
    SEPCIFIC_ID_BEG = 38 # <|
    SEPICFIC_ID_END = 39 # |>

kw_print = "畀我睇下"
kw_endprint = "點樣先"
kw_exit = "收工"
kw_in = "喺"
kw_elif = "定系"
kw_turtle_beg = "老作一下"
kw_type = "起底"
kw_assign = "講嘢"
kw_class_def = "咩系"
kw_else_or_not = "唔系"
kw_is = "系"
kw_if = "如果"
kw_expr_if = "若然"
kw_expr_else = "唔系咁就"
kw_then = "嘅話"
kw_do = "->"
kw_begin = "{"
kw_end = "}"
kw_pass = "咩都唔做"
kw_while_do = "落操場玩跑步"
kw_function = "$"
kw_call = "用下"
kw_import = "使下"
kw_func_begin = "要做咩"
kw_func_end = "搞掂"
kw_is_2 = "就"
kw_assert = "諗下"
kw_class_assign = "佢嘅"
kw_while = "玩到"
kw_whi_end = "為止"
kw_return = "還數"
kw_try = "執嘢"
kw_except = "揾到"
kw_finally = "執手尾"
kw_raise = "掟個"
kw_raise_end = "嚟睇下"
kw_from = "從"
kw_to = "行到"
kw_endfor = "行曬"
kw_extend = "佢個老豆叫"
kw_method = "佢識得"
kw_endclass = "明白未啊"
kw_cmd = "落Order"
kw_break = "飲茶先啦"
kw_continue = "Hea陣先"
kw_lst_assign = "拍住上"
kw_set_assign = "埋堆"
kw_global_set = "Share下"
kw_is_3 = "係"
kw_exit_1 = "辛苦曬啦"
kw_exit_2 = "同我躝"
kw_false = "唔啱"
kw_true = "啱"
kw_none = "冇"
kw_stackinit = "有條仆街叫"
kw_push = "頂你"
kw_pop = "丟你"
kw_model = "嗌"
kw_mod_new = "過嚟估下"
kw_class_init = "佢有啲咩"
kw_self = "自己嘅"
kw_call_begin = "下"
kw_get_value = "@"
kw_del = "冇鳩用"
kw_del2 = "冇撚用"
kw_match = "match下"
kw_case = "撞見"
kw_func_ty_define = "有條計仔"
kw_func_ty_end = "話你知"
kw_call_native = "我係二五仔"

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
    kw_continue,
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
    kw_del,
    kw_del2,
    kw_func_ty_define,
    kw_func_ty_end,
    kw_call_native
)

syms = {'&', '&&', '|', '|>', '%', 
    '%%', '~', '-', '->', '=', '=>',
    '==>', '==', '$', '$$', '<', 
    '<*>', '<|>', '<->', '<$>', '<=',
    '<<', '<|', '>', '>=', '>>', '!',
    '!=', '@', '@@@', '@@', '{', '}',
    '(', ')', '[', ']', '.', '+', '-',
    '*', '**', '/', '//', '&', '^', ',',
    '##'}