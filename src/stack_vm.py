"""
   Cantonese语言栈式虚拟机
   Created at 2021/7/20 23:11 
"""

# 施工中... 请戴好安全帽
from enum import Enum, unique
from collections import namedtuple

import env

@unique
class OpCode(Enum):
    OP_LOAD_CONST = 0
    OP_POP_TOP = 1
    OP_PRINT_ITEM = 2

class Instruction(object):
    def __init__(self, index, opcode, args) -> None:
        self.index = index
        self.opcode = opcode
        self.args = args

    def get_opcode(self):
        return self.opcode

    def get_args(self):
        return self.args

    def get_idx(self):
        return self.index

    def set_args(self, args):
        self.args = args

    def __str__(self) -> str:
        return str(self.index) + ' ' + self.opcode + ' ' + \
            str(self.args)

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

class RUNTIME_TYPE():
    BREAK = 0

class CanBlock(object):
    def __init__(self, _type, handler, level) -> None:
        self.type = _type
        self.handler = handler
        self.level = level

class Code(object):
    def __init__(self) -> None:
        self.co_argcount = None
        self.co_nlocals = None
        self.co_stacksize = None
        self.co_code = None 
        self.co_consts = None
        self.co_names = None
        self.co_varnames = None 
        self.co_filename = None
        self.co_name = None
        self.co_firstlineno = None
        self.co_lnotab = None
        self.ins_lst = []
        self.version = None

class CanThreadPool(object):
    def __init__(self) -> None:
        self._break = None
        self._raise = None
        self._return = None

class CanState(object):
    def __init__(self, code_obj) -> None:
        self.code_obj = code_obj
        self.ThreadState = ThreadState()
        self.objs = []

    CASE_ERROR = 0x0002
    CASE_RAISE = 0x0004
    CASE_RETURN = 0x0008
    CASE_BREAK = 0x0010

    def op_run(self, opname, arg):
        op_func = getattr(self, opname, None)
        if not op_func:
            print("OpCode {} not defined".format(opname))
            return
        else:
            return op_func(arg) if arg != None else op_func()

    def parse(self):
        co_code = self.code_obj.ins_lst[self.object.lasti]
        self.object.lasti += 1
        return co_code.get_opcode(), co_code.get_args()

    def _run(self) -> None:
        self.object = CanObject(thread_state = self.ThreadState,
                                 _code = self.code_obj,
                                 _globals = {"唔啱" : False, "啱" : True},
                                 _locals = {})
        self.object.lasti += 1
        pool = CanThreadPool()
        while True:
            opname, arg = self.parse()
            ret = self.op_run(opname, arg)
            if ret == "0":
                print("return value:{}\n".format(ret))
                break
            if isinstance(ret, int) and ret == self.CASE_BREAK:
                pool._break = ""
                break
            if isinstance(ret, list) and ret[0] == self.CASE_ERROR:
                raise ret[1]

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

    def push_object(self, obj) -> None:
        self.objects.append(self.object)
        self.object = obj

    def pop(self):
        return self.object.stack.pop()

    def popn(self, n):
        if n:
            ret = self.object.stack[-n : ]
            self.object.stack[-n : ] = []
            return ret
        else:
            return []

    def jumpto(self, value):
        self.object.lasti = value

    def jumpby(self, value):
        self.object.lasti += value

    def stack_level(self):
        return len(self.object.stack)

    def set_block(self, object, b_type, b_handler, b_level):
        block = CanBlock(b_type, b_handler, b_level)
        object.block_stack.append(block)

    def pop_block(self, object):
       return object.block_stack.pop() 

    def unaryOperator(self, op):
        val = self.top()
        self.set_top(UNARY_OPERATORS[op](val))

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
        self.push(self.get_top())

    def OP_LOAD_CONST(self, val):
        self.push(eval(val[1], self.object._globals, self.object._locals))

    def OP_LOAD_NAME(self, name):
        obj = self.object
        if name in obj._locals:
            val = obj._locals[name]
        elif name in obj._globals:
            val = obj._globals[name]
        elif name in obj._builtins:
            val = obj._builtins[name]
        else:
            raise NameError("name %s is not defined.".foramt(name))
        self.push(val)
        
    def OP_LOAD_BUITIN_FUNC(self, _func):
        self.push(_func)

    def OP_NEW_NAME(self, name):
        val = self.pop()
        self.object._locals[name] = val

    def OP_PRINT_ITEM(self):
        val = self.pop()
        print(val)

    def OP_RETURN(self):
        return "0"

    def OP_POP_JMP_IF_FALSE(self, idx):
        val = self.pop()
        if not val:
            self.jumpto(idx)
        
    def OP_POP_JMP_IF_TRUE(self, idx):
        val = self.pop()
        if val:
            self.jumpto(idx)
    
    def OP_END(self):
        pass

    def OP_JMP_FORWARD(self, addr):
        self.jumpby(addr)

    def OP_SETUP_LOOP(self, dest):
        self.set_block(self.object, 'loop', self.object.lasti + dest, self.stack_level())

    def OP_GET_ITER(self):
        val = self.get_top()
        val_iter = iter(val)
        if val_iter:
            self.set_top(val_iter)
        else:
            self.pop()

    def OP_FOR_ITER(self, dest):  
        it = self.top()
        try:
            val = next(it)
            self.push(val)
        except StopIteration:
            self.pop()
            self.jumpby(dest)

    def OP_JMP_ABSOLUTE(self, dest):
        self.jumpto(dest)

    def OP_SETUP_LIST(self, num):
        ret = []
        for i in range(num):
            ret.insert(0, self.pop())
        self.push(ret)

    def OP_SETUP_LOOP(self, dest) -> None:
        self.set_block(self.object, 'loop', self.object.lasti + dest, self.stack_level)

    def OP_SETUP_FINALLY(self, dest) -> None:
        self.set_block(self.object, 'finally', self.object.lasti + dest, self.stack_level)

    def OP_SETUP_EXCEPT(self, dest) -> None:
        self.set_block(self.object, 'except', self.object.lasti + dest, self.stack_level)

    def OP_POP_BLOCK(self):
        block = self.pop_block(self.object)
        while self.stack_level() > block.b_level:
            self.pop()

    def OP_BREAK_LOOP(self):
        return self.CASE_BREAK

    def OP_CALL_FUNC(self, func):
        arg = self.popn(env.Env.Env._env[func][1])
        x = env.Env.Env._env[func][0](arg)
        self.push(x)

    def OP_FOR_LOOP(self, _iter, _from, _to, _code):
        for _iter[1] in range(_from, _to):
            self.eval_object(_code)

    def OP_RAISE(self, Error):
        return [self.CASE_ERROR, Error]

class CanObject(object):
    def __init__(self, thread_state, _code, _globals, _locals) -> None:
        self.last_stack = thread_state.stack
        self._code = _code
        self._globals = _globals
        self._locals = _locals
        self._builtins = None
        self.stack = []
        self.lasti = -1
        self.block_stack = []

        if self.last_stack == None:
            self._builtins = __builtins__
        else:
            self._builtins = self.last_stack._builtins

class Function(object):
    def __init__(self, code, arg_default):
        self.func_code = code
        self.globals = globals
        self.arg_default = arg_default
        # self.closure = closure
        # self.vm = vm

        # TODO: 支持闭包
        # if closure:
        #    pass

class ThreadState(object):
    def __init__(self):
        self.stack = None