"""
   Cantonese语言虚拟机
   Created at 2021/7/18/7:58 
"""

# 施工中... 请戴好安全帽
from enum import Enum, unique
from typing import Dict

@unique
class CanType(Enum):
    NONE = -1
    NULL = 0
    BOOLEAN = 1
    L_USER_DATA = 2
    NUMBER = 3
    STRING = 4
    FUNCTION = 5
    USER_DATA = 6
    THREAD = 7
    LIST = 8
    DICT = 9

class CanValue(object):
    @staticmethod
    def type_of(val):
        if val is None:
            return CanType.NULL
        elif isinstance(val, bool):
            return CanType.BOOLEAN
        elif isinstance(val, int) or isinstance(val, float):
            return CanType.NUMBER
        elif isinstance(val, str):
            return CanType.STRING
        elif isinstance(val, list):
            return CanType.LIST
        elif isinstance(val, dict):
            return CanType.DICT
        raise Exception('Type not support')

    @staticmethod
    def to_boolean(val):
        if val is None:
            return False
        elif isinstance(val, bool):
            return val
        else:
            return True

    @staticmethod
    def is_integer(val):
        return val == int(val)

    @staticmethod
    def parse_integer(s):
        try:
            return int(s)
        except ValueError:
            return None

    @staticmethod
    def parse_float(s):
        try:
            return float(s)
        except ValueError:
            return None

    @staticmethod
    def to_integer(val):
        if isinstance(val, int):
            return val
        elif isinstance(val, float):
            return int(val) if CanValue.is_integer(val) else None
        elif isinstance(val, str):
            return CanValue.parse_integer(val)

    @staticmethod
    def to_float(val):
        if isinstance(val, float):
            return val
        elif isinstance(val, int):
            return float(val)
        elif isinstance(val, str):
            return CanValue.parse_float(val)

    @staticmethod
    def float2integer(val):
        if isinstance(val, float):
            if CanValue.is_integer(val):
                return int(val)
        return val

    @staticmethod
    def fb2int(val):
        if val < 8:
            return val
        return ((val & 7) + 8) << ((val >> 3) - 1)

@unique
class ArithOp(Enum):
    ADD = 0 # +
    SUB = 1 # -
    MUL = 2 # *
    DIV = 3 # /
    MOD = 4 # %
    IDIV = 5 # //
    POW = 6 # ^
    BAND = 7 # &
    BOR = 8 # |
    BXOR = 9 # ~
    SHL = 10 # <<
    SHR = 11 # >>

class LocalVar(object):
    def __init__(self, v) -> None:
        self.var_name = v.get_can_str()
        self.start_pc = v.read_uint32()
        self.end_pc = v.read_uint32()

# 编码模式
IABC = 0    # A, B, C三个操作数
IABx = 1    # A, Bx两个操作数
IAsBx = 2   # A, sBx(有符号整数)
IAx = 3     # Ax操作数

# 操作数类型
OpArgN = 0
OpArgU = 1
OpArgR = 2
OpArgK = 3

class CantoneseStack(object):
    MAX_STACK_SIZE = 1000

    def __init__(self):
        self.stack = []
       
    def top(self) -> int:
        return len(self.stack)
    
    def push(self, val) -> None:
        if len(self.stack) > CantoneseStack.MAX_STACK_SIZE:
            raise Exception("Stack Over Flow")
        self.stack.append(val)

    def pop(self):
        ret = self.stack[-1]
        self.stack.pop()
        return ret

    def check(self, n) -> bool:
        return len(self.stack) + n <= CantoneseStack.MAX_STACK_SIZE

    def abs_index(self, idx) -> int:
        if idx >= 0:
            return idx
        return idx + len(self.stack) + 1
    
    # 判断该索引是否有效
    def is_valid(self, idx) -> bool:
        idx = self.abs_index(idx)
        return (idx > 0) and (idx <= len(self.stack))

    def get(self, idx):
        if not self.is_valid(idx):
            return None
        return self.stack[self.abs_index(idx) - 1]

    def set(self, idx, val):
        if not self.is_valid(idx):
            raise Exception('Invalid Index')
        self.stack[self.abs_index(idx) - 1] = val

    # 倒置
    def reverse(self, _from, to) -> None:
        while _from < to:
            self.stack[_from], self.stack[to] = self.stack[to], \
                                self.stack[_from]
            _from += 1
            to -= 1

class CanState(object):
    def __init__(self, proto):
        self.stack = CantoneseStack()
        self.proto = proto
        self.pc = 0

    # 返回栈的顶部索引
    def get_top(self):
        return self.stack.top()
    
    def abs_index(self, idx) -> int:
        return self.stack.abs_index(idx)

    def check_stack(self, n) -> bool:
        return self.stack.check(n)

    # 从栈顶中弹出n个值
    def pop(self, n) -> None:
        for i in range(n):
            self.stack.pop()
    
    # 把值从一个位置复制到另一个位置
    def copy(self, src, dst) -> None:
        val = self.stack.get(src)
        self.stack.set(dst, val)

    # 旋转操作
    def rotate(self, idx, n):
        t = self.stack.top() - 1
        p = self.stack.abs_index(idx) - 1
        m = t - n if n >= 0 else p - n - 1
        self.stack.reverse(p, m)
        self.stack.reverse(m + 1, t)
        self.stack.reverse(p, t)

    # 把指定索引处的值推入栈顶
    def push_value(self, idx) -> None:
        val = self.stack.get(idx)
        self.stack.push(val)

    # 将栈顶值弹出并写入指定位置
    def replace(self, idx):
        val = self.stack.pop()
        self.stack.set(idx, val)

    # 将栈顶值弹出并插入指定位置
    def insert(self, idx):
        self.rotate(idx, 1)

    def remove(self, idx):
        self.rotate(idx, -1)
        self.pop(1)

    def set_top(self, idx):
        new_top = self.stack.abs_index(idx)
        assert(new_top >= 0)

        n = self.stack.top() - new_top
        if n > 0:
            for i in range(n):
                self.stack.pop()
        elif n < 0:
            for i in range(-n):
                self.stack.push(None)

    def type_name(tp) -> str:
        if tp == CanType.NONE:
            return "no value"
        elif tp == CanType.NULL:
            return "null"
        elif tp == CanType.BOOLEAN:
            return "boolean"
        elif tp == CanType.NUMBER:
            return "number"
        elif tp == CanType.STRING:
            return "string"
        elif tp == CanType.FUNCTION:
            return "function"
        elif tp == CanType.USER_DATA:
            return "userdata"
        elif tp == CanType.DICT:
            return "dict"
        elif tp == CanType.LIST:
            return "list"

    def type(self, idx):
        if self.stack.is_valid(idx):
            val = self.stack.get(idx)
            return CanValue.type_of(val)
        return CanType.NONE

    def is_none(self, idx) -> bool:
        return self.type(idx) == CanType.NONE

    def is_null(self, idx) -> bool:
        return self.type(idx) == CanType.NULL

    def is_none_or_null(self, idx) -> bool:
        return self.is_none(idx) or self.is_null(idx)

    def is_boolean(self, idx) -> bool:
        return self.type(idx) == CanType.BOOLEAN

    def is_integer(self, idx) -> bool:
        return isinstance(self.stack.get(idx), int)

    def is_number(self, idx) -> bool:
        return self.to_number(idx) is not None

    def is_string(self, idx) -> bool:
        tp = self.type(idx)
        return tp == CanType.STRING or tp == CanType.NUMBER

    def is_thread(self, idx) -> bool:
        return self.type(idx) == CanType.THREAD

    def is_function(self, idx) -> bool:
        return self.type(idx) == CanType.FUNCTION

    def is_list(self, idx) -> bool:
        return self.type(idx) == CanType.LIST

    def is_dict(self, idx) -> bool:
        return self.type(idx) == CanType.DICT

    def to_boolean(self, idx):
        val = self.stack.get(idx)
        return CanValue.to_boolean(val)

    def to_integer(self, idx):
        i = self.to_integerx(idx)
        return 0 if i is None else i

    def to_integerx(self, idx):
        val = self.stack.get(idx)
        return val if isinstance(val, int) else None

    def to_number(self, idx):
        val = self.stack.get(idx)
        if isinstance(val, float):
            return val
        elif isinstance(val, int):
            return float(val)
        return 0

    def to_string(self, idx):
        val = self.stack.get(idx)
        if isinstance(val, str):
            return val
        elif isinstance(val, int) or isinstance(val, float):
            s = str(val)
            self.stack.set(idx, s)
            return s
        return ''

    def to_list(self, idx):
        val = self.stack.get(idx)
        return str(val)

    def to_dict(self, idx):
        val = self.stack.get(idx)
        return str(val)
    
    def print_stack(self):
        top = self.stack.top()
        for i in range(1, top + 1):
            t = self.type(i)
            if t == CanType.BOOLEAN:
                print('[%s]' % ('true' if self.to_boolean(i) else 'false'), end='')
            elif t == CanType.NUMBER:
                if self.is_integer(i):
                    print('[%d]' % self.to_integer(i), end='')
                else:
                    print('[%g]' % self.to_number(i), end='')
            elif t == CanType.STRING:
                print('["%s"]' % self.to_string(i), end='')
            elif t == CanType.LIST:
                print("[" + self.to_list(i) + "]", end='')
            elif t == CanType.DICT:
                print("[" + self.to_dict(i) + "]", end='')
            else:
                print('[%s]' % CanState.type_name(t), end='')

        print()

    def push_null(self):
        self.stack.push(None)

    def push_boolean(self, b):
        self.stack.push(b)

    def push_integer(self, n):
        self.stack.push(n)

    def push_number(self, n):
        self.stack.push(n)

    def push_string(self, s):
        self.stack.push(s)

    def push_list(self, l):
        self.stack.push(l)

    def push_dict(self, d):
        self.stack.push(d)