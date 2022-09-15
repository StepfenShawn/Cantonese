import dis


"""
    1st return register
"""
class Register_rax(object):
    def __init__(self) -> None:
        self.used = False
"""
    2nd return register
"""
class Register_rdx(object):
    def __init__(self) -> None:
        self.used = False

class Register_rcx(object):
    def __init__(self) -> None:
        self.used = False

class Register_ecx(object):
    def __init__(self) -> None:
        self.used = False

"""
    used to pass 5th argument to functions
"""
class Register_r8(object):
    def __init__(self) -> None:
        self.used = False

"""
    Used to pass 6th argument to functions
"""
class Register_r9(object):
    def __init__(self) -> None:
        self.used = False

"""
    temp register
"""
class Register_r10(object):
    def __init__(self) -> None:
        self.used = False

class AsmRunner(object):
    def __init__(self, Nodes, asm_code, label = '', path = ''):
        self.LC = 0 # For count the string
        self.BC = 0 # For count the block
        self.asm_code = asm_code # The asm code
        self.path = path
        self.Nodes = Nodes
        self.global_head = """
        #----------------------Welcome to Cantonese-------------------------
        # by Stepfen Shawn
        #-------------------------------------------------------------------
        """
        self.file_head = "\t.file " + self.path
        self.stack_size = 16
        self.rpb_offset = 0

        self.lc_data_map = {}
        self.bc_data_map = {}
        self.func_segment_list = []

        self.var_type_map = {}
        self.var_address_map = {}

        """
            Size map:
            1 : BYTE PTR
            2 : WORD PTR
            4 : DWORD PTR
            8 : QWORD PTR
        """

        self.int_size = 4
        self.long_size = 4
        self.float_size = 4
        self.double_size = 8
        self.string_size = 8 # char* type
        self.char_size = 1


        # The base attr : to mark which registers used for function block
        self.rax = Register_rax()
        self.ecx = Register_ecx()
        self.r8 = Register_r8()
        self.r9 = Register_r9()

        self.register = [self.rax, self.ecx, self.r8, self.r9]

        self.reg_map = {"rax": ["rax", "eax", "ax", "al"],
               "rbx": ["rbx", "ebx", "bx", "bl"],
               "rcx": ["rcx", "ecx", "cx", "cl"],
               "rdx": ["rdx", "edx", "dx", "dl"],
               "rsi": ["rsi", "esi", "si", "sil"],
               "rdi": ["rdi", "edi", "di", "dil"],
               "r8": ["r8", "r8d", "r8w", "r8b"],
               "r9": ["r9", "r9d", "r9w", "r9b"],
               "r10": ["r10", "r10d", "r10w", "r10b"],
               "r11": ["r11", "r11d", "r11w", "r11b"],
               "rbp": ["rbp", "", "", ""],
               "rsp": ["rsp", "", "", ""]}


        self.function_args_map = {}

        self.block_name =  "__main"

    def init_lc(self):
        self.lc_data_map["%d\\n\\0"] = self.LC
        self.asm_code += self.init_string("\"%d\\n\\0\"")
        self.LC += 1
        self.lc_data_map["%s\\n\\0"] = self.LC
        self.asm_code += self.init_string("\"%s\\n\\0\"")
        self.LC += 1

    def init_main_section(self):
        self.asm_code += "\t.text\n"
        self.asm_code += "\t.globl	main\n"
        self.asm_code += "main:\n"

    def init_main_return_value(self):
        self.asm_code += "\t" + "movl $0, %eax\n"
        self.asm_code += "\t" + "leave\n"
        self.asm_code += "\t" + "ret\n"

    def add_to_datasegment(self, data):
            
            if data[0] == 'string':
                data[1] = "\"" + eval(data[1]) + "\\0" + "\""
                if data[1] in self.lc_data_map.keys():
                    return
                else:
                    self.lc_data_map[data[1]] = self.LC
                    self.asm_code += self.init_string(data[1])
                    self.LC += 1

    def var_to_address(self, val):
        if self.var_type_map[val] == 'int':
            val_size = self.int_size
        elif self.var_type_map[val] == 'str':
            val_size = self.string_size
        self.rpb_offset += val_size
        address = " -" + str(self.rpb_offset) + "(%rbp) "
        self.var_address_map[val] = address
        return address

    """
        Init a string
    """
    def init_string(self, string):
        ret = "\n.LC" + str(self.LC) + ":\n\t .ascii " + string + "\n"
        return ret

    def init_block(self):
        ret = "\n.BLOCK" + str(self.BC) + ":\n"
        return ret

    def init_function_block(self, name):
        ret = "\n" + name + ":\n"
        return ret

    def init_main_stack(self):
        self.asm_code += "\t" + "pushq %rbp\n"
        self.asm_code += "\t" + "movq %rsp, %rbp\n"

    def init_stack_size(self):
        self.asm_code += "\t" + "subq $32, %rsp\n"

    def count_stack_size(self):
        if self.rpb_offset != 0:
            self.stack_size += (int(self.rpb_offset / 16) + 1) * 16

    def init_call_main(self):
        self.asm_code += "\tcall __main\n"

    def call_puts(self, lc_index):
        re = ""
        re += "\t" + "leaq .LC" + str(lc_index) + "(%rip), %rcx\n"
        re += "\t" + "call puts\n"
        self.ins.append(re)

    def call_printf(self, lc_index, char_type : bool = False, val : int = None, arg : list = None):
        re = ""
        if lc_index == None and arg != None:
            """
                movq	%rcx, 16(%rbp)
	            movq	16(%rbp), %rcx
            """
            re += "\t" + "movq %rcx, " + self.var_address_map[arg] + "\n"
            re += "\t" + "movq " + self.var_address_map[arg] + ", %rcx\n"
            re += "\t" + "call puts\n" 
        else:
            if not char_type:
                if val is not None:
                    re += "\t" + "movl " + self.var_address_map[val] + ", %eax\n"
                re += "\t" + "movl %eax, %edx\n"
            else:
                re += "\t" + "movq " + self.var_address_map[val] + ", %rax\n"
                re += "\t" + "movq %rax, %rdx\n"
            re += "\t" + "leaq .LC" + str(lc_index) + "(%rip), %rcx\n"
            re += "\t" + "call printf\n"
        self.ins.append(re)

    def call_exit(self):
        re = ""
        re += "\t" + "movl	$1, %ecx\n"
        re += "\t" + "call	exit\n"
        self.ins.append(re)

    def assign_movl(self, var_name, val):
        re = ""
        if var_name[0] == 'expr':
            var_name = ExprEval(var_name[1]).parse().genAsm()

        else:
            var_name = var_name[1]

        if val[0] != 'expr':
            val = val[1]
       
        if isinstance(eval(val), int):
            self.var_type_map[var_name] = 'int'
            re += "\t" + "movl $" + val + "," + self.var_to_address(var_name) + "\n"

        elif isinstance(eval(val), str):
            self.var_type_map[var_name] = 'str'
            self.add_to_datasegment(['string', val])
            re += "\t" + "leaq .LC" + str(self.lc_data_map["\"" + eval(val) + "\\0" + "\""]) + "(%rip), %rax\n"
            re += "\t" + "movq %rax, " + self.var_to_address(var_name) + "\n"
        
        else:
            pass
        
        self.ins.append(re)

    def __function(self, func_name, func_args, func_body):
        code = ''
        if func_args is not None:
            func_parse = AsmBlockParse(func_body, code, self.LC, self.lc_data_map, func_name[1], [func_args])
        else:
            func_parse = AsmBlockParse(func_body, code, self.LC, self.lc_data_map, func_name[1])
        self.func_segment_list.append(func_name)
        print(func_parse.run())
        self.LC = func_parse.LC

    def __return(self, val_node):
        if val_node[0] == 'num':
            self.asm_code += "\t" + "movl $" + val_node[1] + ", %eax\n"
            self.asm_code += "\t" + "ret\n"

        if val_node[0] == 'string':
            self.add_to_datasegment(val_node)
            self.asm_code += "\t" + "leap .LC" + str(self.lc_data_map["\"" + eval(val_node[1]) + "\\0" + "\""]) + \
                "(%rip), %rax\n"
            self.asm_code += "\t" + "ret\n"

    def __call(self, f):
        re = ""
        expr_eval_ret = ExprEval(f, self).parse().genAsm()
        if not expr_eval_ret['has_args']:
            re += "\t" + "call " + expr_eval_ret['func_name'] + "\n"
        else:
            for a in expr_eval_ret['args']:
                self.add_to_datasegment(a)
                re += "\t" + "leaq " + ".LC" + str(self.lc_data_map[a[1]]) + "(%rip), %rcx\n"
            re += "\t" + "call " + expr_eval_ret['func_name'] + "\n"
        self.ins.append(re)

    def add_all_ins(self):
        for item in self.ins:
            self.asm_code += item

    def run_init(self):
        self.asm_code += self.global_head
        self.init_lc()

    def run(self, in_main = True):
        self.ins = []

        for node in self.Nodes:
            if node[0] == "node_print":
                self.add_to_datasegment(node[1])
                if node[1][0] == 'string':
                    self.call_puts(self.lc_data_map[node[1][1]])
                
                elif node[1][0] == 'identifier':
                    if self.var_type_map[node[1][1]] == 'int':
                        self.call_printf(self.lc_data_map["%d\\n\\0"], val = node[1][1])
                    elif self.var_type_map[node[1][1]] == 'str':
                        self.call_printf(self.lc_data_map["%s\\n\\0"], char_type = True, val = node[1][1])
                    elif self.var_type_map[node[1][1]] == 'arg':
                        self.call_printf(None, arg = node[1][1])
                
                elif node[1][0] == 'expr':
                    if hasattr(ExprEval(node[1][1], self).parse(), 'op'):
                        self.ins.append(ExprEval(node[1][1], self).parse().genAsm())
                        self.call_printf(self.lc_data_map["%d\\n\\0"])
                    else:
                        self.call_printf(self.lc_data_map["%d\\n\\0"], val = ExprEval(node[1][1], self).parse().genAsm())
                    

            elif node[0] == 'node_let':
                self.assign_movl(node[1], node[2])

            elif node[0] == 'node_fundef':
                func_name = node[1]
                func_args = node[2]
                func_body = node[3]

                self.__function(func_name, func_args, func_body)

            elif node[0] == 'node_call':
                self.__call(node[1][1])

            elif node[0] == 'node_return':
                self.__return(node[1])

            elif node[0] == "node_exit":
                self.call_exit()

            else:
                pass

        
        self.init_main_section()
        self.init_main_stack()
        self.count_stack_size()
        self.init_stack_size()
        self.init_call_main()
        self.add_all_ins()
        self.init_main_return_value()


        return self.asm_code

    def add_ins(self):
        pass



"""
    A simple function stack structure:
    args 3 (int) <- 20(%rbp)
    args 2 (int) <- 16(%rbp)
    args 1 (int) <- 12(%rbp)
    return address (int) <- 8(%rbp)
    old %rbp <- 0(%rbp)
    variable 1 (int) <- -4(%rbp)
    variable 2 (int) <- -8(%rbp)
    variable 3 (int) <- -12(%rbp)
    not used <- -16(%rbp) and (%rsp)
"""

class AsmBlockParse(AsmRunner):
    def __init__(self, Nodes : list, asm_code : list, lc_index : int, lc_data_map : dict, block_name : str = '', func_args : list = []) -> None:
        super(AsmBlockParse, self).__init__(Nodes, asm_code)
        self.LC = lc_index
        self.lc_data_map = lc_data_map
        self.block_name = block_name

        # Because of the return address, the args need start from 16(%rbp)
        self.args_start_offset = 16
        self.args_map = {}

        self.func_args = func_args

    def stack_add_args(self, arg : str):
        self.var_address_map[arg] = str(self.args_start_offset) + "(%rbp)"
        self.var_type_map[arg] = 'arg'
        self.args_start_offset += 16

    # Override
    def run(self):
        if len(self.func_args) != 0:
            for i in self.func_args:
                self.stack_add_args(i[1])
        return super().run()

    # Override
    def init_main_section(self):
        self.asm_code += "\t.text\n"
        self.asm_code += "\t.globl " + self.block_name + "\n"
        self.asm_code += self.block_name +  ":\n"

    # Override
    def init_call_main(self):
        return

    # Override
    def init_lc(self):
        return

class Compile(object):
    def __init__(self, ast, target, path) -> None:
        self.ast = ast
        self.target = target
        self.path = path
        self.TO_JS_CODE = ""
        self.TO_CPP_CODE = ""
        self.TO_ASM_CODE = ""

        if self.target == "js":
            self.run_js(self.ast)

        if self.target == "cpp":
            self.run_cpp(self.ast)
    
        if self.target == "asm":
            self.run_asm(self.ast)

    def ret(self):
        if self.target == "js":
            return self.TO_JS_CODE, self.path[ : len(self.path) - len('cantonese')] + 'js'

        if self.target == "cpp":
            return self.TO_CPP_CODE, self.path[ : len(self.path) - len('cantonese')] + 'cpp'

        if self.target == "asm":
            return self.TO_ASM_CODE, self.path[ : len(self.path) - len('cantonese')] + 'S'

    # TODO
    def eval_expr(self, expr):
        return expr
    # TODO
    def run_asm(self, Nodes : list, label = '', path = '') -> None:
        asmbler = AsmRunner(Nodes, self.TO_ASM_CODE, path = path)
        asmbler.run_init()
        self.TO_ASM_CODE = asmbler.run()

    def run_cpp(self, Nodes : list, label = '', path = '') -> None:
        for node in Nodes:
            if node[0] == "node_print":
                self.TO_C_CODE += "std::cout<<" + self.eval_expr(node[1][1]) + ";\n"
    
    def run_js(self, Nodes : list, label = '', path = '', in_web = False) -> None:
        for node in Nodes:
            if node[0] == "node_print":
                if in_web:
                    self.TO_JS_CODE += "alert(" + self.eval_expr(node[1][1]) + ");\n"
                else:
                    self.TO_JS_CODE += "console.log(" + self.eval_expr(node[1][1]) + ");\n"
            
            if node[0] == "node_exit":
                self.TO_JS_CODE += "process.exit();\n"

            if node[0] == "node_let":
                self.TO_JS_CODE += node[1][1] + " = " + self.eval_expr(node[2][1]) + ";\n"

            if node[0] == "node_if":
                self.TO_JS_CODE += "if (" + self.eval_expr(node[1][1]) + ") {\n"
                self.run_js(node[2])
                self.TO_JS_CODE += "}"
            
            if node[0] == "node_elif":
                self.TO_JS_CODE += "else if (" + self.eval_expr(node[1][1]) + ") {\n"
                self.run_js(node[2])
                self.TO_JS_CODE += "}"

            if node[0] == "node_else":
                self.TO_JS_CODE += "else{"
                self.run_js(node[1])
                self.TO_JS_CODE += "}"

            if node[0] == "node_call":
                self.TO_JS_CODE += node[1][1] + ";\n"

            if node[0] == "node_fundef":
                if node[2] == 'None':
                    self.TO_JS_CODE += "function " + node[1][1] + "() {\n"
                    self.run_js(node[3])
                    self.TO_JS_CODE += "}\n"
                else:
                    self.TO_JS_CODE += "function " + node[1][1] + "(" + node[2][1] + ") {\n"
                    self.run_js(node[3])
                    self.TO_JS_CODE += "}\n"

class ExprFunctionCall(object):
    def __init__(self, func_name :str, args : list, state : AsmRunner = None) -> None:
        self.func_name = func_name
        self.args = args
        self.state = state

    def genAsm(self) -> str:
        if self.args == None:
            return {'has_args' : False, 'func_name' : self.func_name}
        else:
            return {'has_args' : True, 'func_name' : self.func_name, 'args' : self.args}


class ExprNumOrIdentifier(object):
    def __init__(self, arg : list, state : AsmRunner = None):
        self.arg = arg
        self.state = state

    def genAsm(self):
        return self.arg[1]

class ExprOp(object):
    def __init__(self, op : str, arg1 : list, arg2 : list, state : AsmRunner = None):
        self.op = op
        self.arg1 = arg1
        self.arg2 = arg2
        self.state = state

    def genAsm(self):
        if self.op == '+':
            re = ""
            if self.arg1[0] == 'num':
                if self.arg2[0] == 'identifier': 
                    re += "\t" + "movl " + self.state.var_address_map[self.arg2[1]] + ", %eax\n"
                    re += "\t" + "addl $" + self.arg1[1] + ", %eax\n"

            elif self.arg1[0] == 'identifier':
                if self.arg2[0] == 'num':
                    re += "\t" + "movl " + self.state.var_address_map[self.arg1[1]] + ", %eax\n"
                    re += "\t" + "addl $" + self.arg2[1] + ". %eax\n"

        elif self.op == '-':
            re = ""
            if self.arg1[0] == 'num':
                if self.arg2[0] == 'identifier':
                    re += "\t" + "movl " + self.state.var_address_map[self.arg2[1]] + ", %eax\n"
                    re += "\t" + "subl $" + self.arg1[1] + ", %eax\n"

            elif self.arg1[0] == 'identifier':
                if self.arg2[0] == 'num':
                    re += "\t" + "movl " + self.state.var_address_map[self.arg1[1]] + ", %eax\n"
                    re += "\t" + "subl $" + self.arg2[1] + ". %eax\n"

        return re

    def __str__(self) -> str:
        return str(self.arg1) + " " + self.op + " " + str(self.arg2)

"""
    result_type : 'EXPR_OP' | 'EXPR_VAR_OR_IDENT'
"""
class ExprEval(object):
    def __init__(self, string, state : AsmRunner = None):
        self.string = string
        self.py_ins = []
        self.op = ['+', '-', '*', '/', '%']
        self.stack = []
        self.state = state

    def parse(self):
        # Trans the expr to python vm, then to asm
        # Expr -> Py-Opcode -> Mid-Opcode
        bytecode = dis.Bytecode(self.string)
        for instr in bytecode:
            self.py_ins.append({'opname' : instr.opname, 'args' : instr.argrepr})
            if instr.opname == 'LOAD_NAME':
                self.stack.append(instr.argrepr)
            elif instr.opname == 'LOAD_CONST':
                self.stack.append(instr.argrepr)
            elif instr.opname == 'CALL_FUNCTION':
                self._result_type = "EXPR_CALL"
                return self.__eval_func_call(self.stack)                
            elif instr.opname == 'BINARY_ADD':
                self._result_type = "EXPR_OP"
                return self.__eval_op('+')
            elif instr.opname == 'BINARY_SUBTRACT':
                self._result_type = "EXPR_OP"
                return self.__eval_op('-')
            elif instr.opname == 'RETURN_VALUE' and instr.argrepr == '':
                break
        
        self._result_type = "EXPR_VAR_OR_IDENT"
        return self.__eval()

    def get_type(self, val):
        try:
            v = eval(val)
            if isinstance(v, float) or isinstance(v, int):
                return 'num'
            elif isinstance(v, str):
                return 'string'
        except NameError:
            return 'identifier'

    def __eval_op(self, op : str = ''):
        val1 = self.stack.pop()
        val2 = self.stack.pop()

        if self.get_type(val1) == 'identifier':
            if self.get_type(val2) == 'num':
                return ExprOp(op, ['identifier', val1], ['num', val2], self.state)
            elif self.get_type(val2) == 'identifier':
                return ExprOp(op, ['identifier', val1], ['identifier', val2], self.state)
            elif self.get_type(val2) == 'string':
                return ExprOp(op, ['identifier', val1], ['string', val2], self.state)

        elif self.get_type(val1) == 'num':
            if self.get_type(val2) == 'num':
                return ExprOp(op, ['num', val1], ['num', val2], self.state)
            elif self.get_type(val2) == 'identifier':
                return ExprOp(op, ['num', val1], ['identifier', val2], self.state)
            elif self.get_type(val2) == 'string':
                return ExprOp(op, ['num', val1], ['string', val2], self.state)
        
        elif self.get_type(val1) == 'string':
            if self.get_type(val2) == 'num':
                return ExprOp(op, ['string', val1], ['num', val2], self.state)
            elif self.get_type(val2) == 'identifier':
                return ExprOp(op, ['string', val1], ['identifier', val2], self.state)
            elif self.get_type(val2) == 'string':
                return ExprOp(op, ['string', val1], ['string', val2], self.state)


    def __eval_func_call(self, stack):
        func_name = stack[0]
        args_lst = []
        # If the function has no args
        if len(stack) == 1:
            return ExprFunctionCall(func_name, None, self.state)
        else:
            i = 1
            while i < len(stack):
                args_lst.append([self.get_type(stack[i]), stack[i]])
                i += 1

            return ExprFunctionCall(func_name, args_lst, self.state)

    def __eval(self):
        # Var or identifier?
        if len(self.stack) == 1:
            try:
                val = eval(self.stack[0])
                if isinstance(val, float) or isinstance(val, int):
                    return ExprNumOrIdentifier(['num', self.stack[0]], self.state)
                elif isinstance(val, str):
                    return ExprNumOrIdentifier(['string', self.stack[0]], self.state)
            except NameError:
                return ExprNumOrIdentifier(['identifier', self.stack[0]], self.state)

        else:
            pass

    def result_type(self):
        return self._result_type