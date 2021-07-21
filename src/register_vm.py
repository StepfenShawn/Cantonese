"""
   Cantonese语言寄存器式虚拟机
   Created at 2021/7/18 7:58 
"""

# 施工中... 请戴好安全帽
from enum import Enum, unique
from typing import Dict
from collections import namedtuple

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

class Upvalue(object):
    def __init__(self, instack, idx):
        self.instack = instack
        self.idx = idx

class LocalVar(object):
    def __init__(self, var_name, start_pc, end_pc):
        self.var_name = var_name
        self.start_pc = start_pc
        self.end_pc = end_pc

class Prototype(object):
    def __init__(self, source, line_defined, last_line_defined, num_params,
                is_vararg, max_stack_size, code, constants, upvalues, protos,
                line_infos, local_vars):
        self.source = source
        self.line_defined = line_defined
        self.last_line_defined = last_line_defined
        self.num_params =num_params
        self.is_vararg = is_vararg
        self.max_stack_size = max_stack_size
        self.code = code
        self.constants = constants 
        self.upvalues = upvalues
        self.protos =protos
        self.line_infos = line_infos
        self.local_vars = local_vars
    
    def get_code(self):
        return self.code

    def get_constants(self):
        return self.constants

    def get_max_stack_size(self):
        return self.max_stack_size

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

@unique
class CmpOp(Enum):
    EQ = 0 # ==
    NEQ = 1 # !=
    LT = 2 # <
    LE = 3 # <=
    GT = 4 # >
    GE = 5 # >=


class Compare:
    @staticmethod
    def eq(a, b) -> bool:
        return a == b

    @staticmethod
    def lt(a, b) -> bool:
        return a < b

    @staticmethod
    def le(a, b) -> bool:
        return a <= b

    @staticmethod
    def gt(a, b) -> bool:
        return a > b

    @staticmethod
    def ge(a, b) -> bool:
        return a >= b

    @staticmethod
    def neq(a, b) -> bool:
        return a != b

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

class OpCode:
    MOVE = 0
    LOADK = 1
    LOADKX = 2
    LOADBOOL = 3
    LOADNULL = 4
    GETUPVAL = 5
    GETTABUP = 6
    GETTABLE = 7
    SETTABUP = 8
    SETUPVAL = 9
    SETTABLE = 10
    NEWTABLE = 11
    SELF = 12
    ADD = 13
    SUB = 14
    MUL = 15
    MOD = 16
    POW = 17
    DIV = 18
    IDIV = 19
    BAND = 20
    BOR = 21
    BXOR = 22
    SHL = 23
    SHR = 24
    NOT = 25
    LEN = 26
    CONCAT = 27
    JMP = 28
    EQ = 29
    LT = 30
    LE = 31
    TEST = 32
    TESTSET = 33
    CALL = 34
    TAILCALL = 35
    RETURN = 36
    FORLOOP = 37
    FORPREP = 38
    TFORCALL = 39
    TFORLOOP = 40
    SETLIST = 41
    CLOSURE = 42
    VARARG = 43
    EXTRAARG = 44

    def __init__(self, test_flag, set_a_flag, arg_b_mode, 
                    arg_c_mode, op_mode, name, action):
        self.test_flag = test_flag # 是否为逻辑测试相关指令
        self.set_a_flag = set_a_flag # 是否修改Ax
        self.arg_b_mode = arg_b_mode
        self.arg_c_mode = arg_c_mode
        self.op_mode = op_mode # OpCode的格式
        self.name = name
        self.action = action

class Instruction(object):
    def __init__(self, code):
        self.code = code

    def op_code(self):
        return self.code['opcode']

    def a_b_c(self):
        return self.code['a'], self.code['b'], self.code['c']

    def a_bx(self):
        return self.code['a'], self.code['bx']

    def ax(self):
        return self.code['ax']

    def op_name(self):
        return op_codes[self.op_code()].name

    def op_mode(self):
        return op_code[self.op_code()].op_mode

    def arg_b_mode(self):
        return op_codes[self.op_code()].arg_b_mode

    def arg_c_mode(self):
        return op_codes[self.op_code()].arg_c_mode

    def execute(self, vm):
        op_codes[self.op_code()].action(self, vm)
    
# R(A) := R(B) 将B寄存器的值移动到A处   
def move(inst, vm):
    a, b, _ = inst.a_b_c()
    # 转化成栈索引
    a += 1
    b += 1
    vm.copy(b, a)

# R(A) := Lst(Bx)
def laodk(inst, vm):
    a, bx = inst.a_bx()
    a += 1
    vm.get_const(bx)
    vm.replace(a)

# R(A) := Kst(extra arg)
def loadkx(inst, vm):
    a, _ = inst.a_bx()
    a += 1
    ax = Instruction(vm.fetch()).ax()
    vm.get_const(ax)
    vm.replace(a)


# R(A) := (bool)B; if (C) pc++
def loadbool(inst, vm):
    a, b, c = inst.a_b_c()
    vm.push_boolean(b != 0)
    vm.replace(a + 1)

    if c != 0:
        vm.add_pc(1)

def loadnull(inst, vm):
    a, b, _ = inst.a_b_c()
    a += 1

    vm.push_null()
    for i in range(a, a + b):
        vm.copy(-1, i)
    vm.pop(1)

def arith_binary(inst, vm, op):
    a, b, c = inst.a_b_c()
    a += 1

    vm.get_rk(b)
    vm.get_rk(c)
    vm.arith(op)
    vm.replace(a)

def arith_unary(inst, vm, op):
    a, b, _ = inst.a_b_c()
    a += 1
    b += 1

    vm.push_value(b)
    vm.arith(op)
    vm.replace(a)

def vm_add(inst, vm):
    arith_binary(inst, vm, ArithOp.ADD)


def vm_sub(inst, vm):
    arith_binary(inst, vm, ArithOp.SUB)


def vm_mul(inst, vm):
    arith_binary(inst, vm, ArithOp.MUL)


def vm_mod(inst, vm):
    arith_binary(inst, vm, ArithOp.MOD)


def vm_pow(inst, vm):
    arith_binary(inst, vm, ArithOp.POW)


def vm_div(inst, vm):
    arith_binary(inst, vm, ArithOp.DIV)


def vm_idiv(inst, vm):
    arith_binary(inst, vm, ArithOp.IDIV)


def vm_band(inst, vm):
    arith_binary(inst, vm, ArithOp.BAND)


def vm_bor(inst, vm):
    arith_binary(inst, vm, ArithOp.BOR)


def vm_bxor(inst, vm):
    arith_binary(inst, vm, ArithOp.BXOR)


def vm_shl(inst, vm):
    arith_binary(inst, vm, ArithOp.SHL)


def vm_shr(inst, vm):
    arith_binary(inst, vm, ArithOp.SHR)

def length(inst, vm):
    a, b, _ = inst.a_b_c()
    a += 1
    b += 1

    vm.len(b)
    vm.replace(a)

def concat(inst, vm):
    a, b, c = inst.a_b_c()
    a += 1
    b += 1
    c += 1
    n = c - b + 1

    vm.check_stack()
    for i in range(b, c + 1):
        vm.push_value(i)

    vm.concat(n)
    vm.replace(a)

def jmp(inst, vm):
    a, sbx = inst.a_sbx()
    vm.add_pc(sbx)
    assert(a == 0)

def compare(inst, vm, op):
    a, b, c = inst.a_b_c()
    vm.get_rk(b)
    vm.get_rk(c)
    if vm.compare(-2, op, -1):
        vm.add_pc(1)
    vm.pop(2)

def vm_eq(inst, vm):
    compare(inst, vm, CmpOp.EQ)

def vm_lt(inst, vm):
    compare(inst, vm, CmpOp.LT)

def vm_le(inst, vm):
    compare(inst, vm, CmpOp.LE)

def vm_gt(inst, vm):
    compare(inst, vm, CmpOp.GT)

def vm_ge(inst, vm):
    compare(inst, vm, CmpOp.GE)

def vm_neq(inst, vm):
    compare(inst, vm, CmpOp.NEQ)

def vm_not(inst, vm):
    a, b, _ = inst.a_b_c()
    a += 1
    b += 1

    vm.push_boolean(not vm.to_boolean(b))
    vm.replace(a)

op_codes = {
    OpCode(0, 1, OpArgR, OpArgN, IABC,  "MOVE    ", move),
    OpCode(0, 1, OpArgK, OpArgN, IABx,  "LOADK   ", laodk),
    OpCode(0, 1, OpArgN, OpArgN, IABx,  "LOADKX  ", loadkx),
    OpCode(0, 1, OpArgU, OpArgU, IABC,  "LOADBOOL", None),
    OpCode(0, 1, OpArgU, OpArgN, IABC,  "LOADNULL", loadnull),
    OpCode(0, 1, OpArgU, OpArgN, IABC,  "GETUPVAL", None),
    OpCode(0, 1, OpArgU, OpArgK, IABC,  "GETTABUP", None),
    OpCode(0, 1, OpArgR, OpArgK, IABC,  "GETTABLE", None),
    OpCode(0, 0, OpArgK, OpArgK, IABC,  "SETTABUP", None),
    OpCode(0, 0, OpArgU, OpArgN, IABC,  "SETUPVAL", None),
    OpCode(0, 0, OpArgK, OpArgK, IABC,  "SETTABLE", None),
    OpCode(0, 1, OpArgU, OpArgU, IABC,  "NEWTABLE", None),
    OpCode(0, 1, OpArgR, OpArgK, IABC,  "SELF    ", None),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "ADD     ", vm_add),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "SUB     ", vm_sub),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "MUL     ", vm_mul),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "MOD     ", vm_mod),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "POW     ", vm_pow),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "DIV     ", vm_div),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "IDIV    ", vm_idiv),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "BAND    ", vm_band),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "BOR     ", vm_bor),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "BXOR    ", vm_bxor), 
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "SHL     ", vm_shl),
    OpCode(0, 1, OpArgK, OpArgK, IABC,  "SHR     ", vm_shr),
    OpCode(0, 1, OpArgR, OpArgN, IABC,  "NOT     ", vm_not),
    OpCode(0, 1, OpArgR, OpArgN, IABC,  "LEN     ", length),
    OpCode(0, 1, OpArgR, OpArgR, IABC,  "CONCAT  ", concat),
    OpCode(0, 0, OpArgR, OpArgN, IAsBx, "JMP     ", jmp),
    OpCode(1, 0, OpArgK, OpArgK, IABC,  "EQ      ", vm_eq),
    OpCode(1, 0, OpArgK, OpArgK, IABC,  "LT      ", vm_lt),
    OpCode(1, 0, OpArgK, OpArgK, IABC,  "LE      ", vm_le),
    OpCode(1, 0, OpArgK, OpArgK, IABC,  "GT      ", vm_gt),
    OpCode(1, 0, OpArgK, OpArgK, IABC,  "GE      ", vm_ge),
    OpCode(1, 0, OpArgK, OpArgK, IABC,  "NEQ     ", vm_neq),
    OpCode(1, 0, OpArgN, OpArgU, IABC,  "TEST    ", None),
    OpCode(1, 1, OpArgR, OpArgU, IABC,  "TESTSET ", None),
    OpCode(0, 1, OpArgU, OpArgU, IABC,  "CALL    ", None),
    OpCode(0, 1, OpArgU, OpArgU, IABC,  "TAILCALL", None), 
    OpCode(0, 0, OpArgU, OpArgN, IABC,  "RETURN  ", None),
    OpCode(0, 1, OpArgR, OpArgN, IAsBx, "FORLOOP ", None),
    OpCode(0, 1, OpArgR, OpArgN, IAsBx, "FORPREP ", None),
    OpCode(0, 0, OpArgN, OpArgU, IABC,  "TFORCALL", None),
    OpCode(0, 1, OpArgR, OpArgN, IAsBx, "TFORLOOP", None),
    OpCode(0, 0, OpArgU, OpArgU, IABC,  "SETLIST ", None),
    OpCode(0, 1, OpArgU, OpArgN, IABx,  "CLOSURE ", None),
    OpCode(0, 1, OpArgU, OpArgN, IABC,  "VARARG  ", None),
    OpCode(0, 0, OpArgU, OpArgU, IAx,   "EXTRAARG", None),
}


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
        return tp == CanType.STRING

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
    
    def dump(self):
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

    # 算术运算
    def arich(self, op):
        b = self.stack.pop()
        a = self.stack.pop()
        result = Arithmetic.arich(a, op, b)
        self.stack.push(result)

    def concat(self, n):
        if n == 0:
            self.stack.push('')
        elif n >= 2:
            for i in range(1, n):
                assert(self.is_string(-1) and self.is_string(-2))
                s2 = self.to_string(-1)
                s1 = self.to_string(-2)
                self.stack.pop()
                self.stack.pop()
                self.stack.push(s1 + s2)

    def compare(self, idx1, op, idx2):
        if not self.stack.is_valid(idx1) or not self.stack.is_valid(idx2):
            raise Exception("The stack index is not valid")
            return False

        a = self.stack.get(idx1)
        b = self.stack.get(idx2)
        if op == CmpOp.EQ:
            return Compare.eq(a, b)
        elif op == CmpOp.LT:
            return Compare.lt(a, b)
        elif op == CmpOp.NEQ:
            return Compare.neq(a, b)
        elif op == CmpOp.LE:
            return Compare.le(a, b)
        elif op == CmpOp.GT:
            return Compare.gt(a, b)
        elif op == CmpOp.GE:
            return Compare.ge(a, b)

    # 虚拟机内部循环
    # loop {计算PC, 取指令, 读指令}
    def get_pc(self) -> int:
        return self.pc
        
    # 修改PC, 实现跳转指令
    def add_pc(self, n) -> None:
        self.pc += n

    # 取出当前指令并将PC指向下一条指令
    def fetch(self):
        code = self.proto.get_code()[self.pc]
        self.pc += 1
        return code

        # 将指定常量推入栈顶
    def get_const(self, idx : int) -> None:
        self.stack.push(self.proto.get_constants()[idx])

        # 将指定常量或栈值推入栈顶
    def get_rk(self, rk : int):
        if rk > 0xff: # canstant
            self.get_const(rk & 0xff)
        else:
            self.push_value(rk + 1)

class Arithmetic(object):

    def add(a, b):
        return a + b

    def sub(a, b):
        return a - b

    def mul(a, b):
        return a * b

    def div(a, b):
        return a / b

    def fdiv(a, b):
        return a // b

    def mod(a, b):
        return a % b

    def band(a, b):
        return a & b
    
    def bor(a, b):
        return a | b

    def bxor(a, b):
        return a ^ b

    def shl(a, b):
        if b >= 0:
            return a << b
        return a >> (-b)

    def shr(a, b):
        if b >= 0:
            return a >> b
        return a << (-b)

    operators = {
        ArithOp.ADD: add,
        ArithOp.SUB: sub,
        ArithOp.MUL: mul,
        ArithOp.MOD: mod,
        ArithOp.POW: pow,
        ArithOp.DIV: div,
        ArithOp.IDIV:fdiv,
        ArithOp.BAND:band,
        ArithOp.BOR: bor,
        ArithOp.BXOR:bxor,
        ArithOp.SHL: shl,
        ArithOp.SHR: shr,
    }

    @staticmethod
    def arich(a, op, b):
        func = Arithmetic.operators[op]
        return func(a, b)