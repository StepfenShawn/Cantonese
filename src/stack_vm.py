"""
   Cantonese语言栈式虚拟机
   Created at 2021/7/20 23:11 
"""

# 施工中... 请戴好安全帽
from enum import Enum, unique
from collections import namedtuple

@unique
class OpCode(Enum):
    OP_LOAD_CONST = 0
    OP_POP_TOP = 1
    OP_PRINT_ITEM = 2

class Instruction(object):
    def __init__(self, opcode, args) -> None:
        self.opcode = opcode
        self.args = args

    def get_opcode(self):
        return self.opcode

    def get_args(self):
        return self.args

class Arithmetic(object):
    def mul(a, b):
        return a * b

    def div(a, b):
        return a / b

    def fdiv(a, b):
        return a // b

    def mod(a, b):
        return a % b

    def add(a, b):
        return a + b

    def sub(a, b):
        return a - b

    def getitem(a, b):
        return a[b]

    def lshift(a, b):
        return a << b

    def rshift(a, b):
        return a >> b

    def and_(a, b):
        return a & b

    def xor(a, b):
        return a ^ b

    def or_(a, b):
        return a | b

    def pos(a):
        return +a

    def neg(a):
        return -a

    def not_(a):
        return not a
    
    def invert(a):
        return ~a

BINARY_OPERATORS = {
    'POWER':    pow,           # a ** b 
    'MULTIPLY': Arithmetic.mul,  # a * b
    'DIVIDE':   Arithmetic.div,  # a / b
    'FLOOR_DIVIDE': Arithmetic.fdiv,  # a // b
    'MODULO':   Arithmetic.mod,           # a % b
    'ADD':      Arithmetic.add,           # a + b
    'SUBTRACT': Arithmetic.sub,           # a - b
    'SUBSCR':   Arithmetic.getitem,       # a[b]
    'LSHIFT':   Arithmetic.lshift,        # a << b
    'RSHIFT':   Arithmetic.rshift,        # a >> b
    'AND':      Arithmetic.and_,          # a & b
    'XOR':      Arithmetic.xor,           # a ^ b
    'OR':       Arithmetic.or_,           # a | b
}

UNARY_OPERATORS = {
    'POSITIVE': Arithmetic.pos,  # +a
    'NEGATIVE': Arithmetic.neg,  # -a
    'NOT':      Arithmetic.not_,  # not a
    'CONVERT':  repr,           # str(a)
    'INVERT':   Arithmetic.invert,  # ~ a
}

class Code(object):
    def __init__(self) -> None:
        self.co_argcount = None
        self.co_nlocals = None
        self.co_stacksize = None
        self.co_flags = None
        self.co_code = None 
        self.co_consts = None
        self.co_names = None
        self.co_varnames = None 
        self.co_freevars = None 
        self.co_cellvars = None
        self.co_filename = None
        self.co_name = None
        self.co_firstlineno = None
        self.co_lnotab = None
        self.ins_lst = []
        self.version = None
        self.mtime = None

class CanState(object):
    def __init__(self, code_obj) -> None:
        self.code_obj = code_obj

    def op_run(self, opname, arg):
        op_func = getattr(self, opname, None)
        if not op_func:
            print("OpCode {} not defined".format(opname))
            return
        else:
            return op_func(arg) if arg != None else op_func()

    def parse(self, i):
        return self.code_obj.ins_lst[i].get_opcode(), \
               self.code_obj.ins_lst[i].get_args()

    def _run(self) -> None:
        thread_state = ThreadState()
        self.object = CanObject(thread_state = thread_state,
                                 _code = self.code_obj,
                                 _globals = {},
                                 _locals = {})
        self.object.lasti += 1
        pc = 0
        while pc < len(self.code_obj.ins_lst):
            opname, arg = self.parse(pc)
            ret = self.op_run(opname, arg)
            pc += 1
            if ret:
                print("return value:{}\n".format(ret))
                break

    def get_const(self, index : int):
        return self.object._code.co_consts[index]

    def get_name(self, index : int):
        return self.object._code.co_names[index]

    def get_top(self):
        return self.object.stack[-1]

    def set_top(self, value) -> None:
        self.object.stack[-1] = value

    def push(self, value) -> None:
        self.object.stack.append(value)

    def pop(self):
        return self.object.stack.pop()

    def popn(self, n):
        if n:
            ret = self.object.stack[-n : ]
            self.object.stack[-n : ] = []
            return ret
        else:
            return []

    def unaryOperator(self, op):
        val = self.top()
        self.set_top(UNARY_OPERATORS[op](value))

    def binaryOperator(self, op):
        x, y = self.popn(2)
        self.push(BINARY_OPERATORS[op](x, y))

    def inplaceOperator(self, op):
        y = self.pop()
        x = self.top()
        self.set_top(self.BINARY_OPERATORS[op](x, y))

    def OP_POP_TOP(self):
        self.pop()

    def OP_NOP(self):
        pass
    
    def OP_PUSH_TOP(self):
        self.push(self.top())

    def OP_LOAD_CONST(self, index):
        value = self.get_const(index)
        self.push(value)

    def OP_PRINT_ITEM(self):
        value = self.pop()
        print(value)

class CanObject(object):
    def __init__(self, thread_state, _code, _globals, _locals) -> None:
        self.last_stack = thread_state.stack
        self._code = _code
        self._globals = _globals
        self._locals = _locals
        self._builtins = None
        self.stack = []
        self.lasti = -1

        if self.last_stack == None:
            self._builtins = __builtins__
        else:
            self._builtins = self.last_stack._builtins

class ThreadState(object):
    def __init__(self):
        self.stack = None