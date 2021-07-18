"""
   Cantonese语言虚拟机
   Created at 2021/7/18/7:58 
"""

# 施工中... 请戴好安全帽

class CantoneseStack(object):
    MAX_STACK_SIZE = 1000

    def __init__(self, can_state):
        self.stack = []
        self.closure = None
        self.varargs = None
        self.pc = 0
        self.caller = None
        self.can_state = can_state
        self.open_upvalues = {}

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