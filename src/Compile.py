import dis
from re import L

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
        self.var_type_map = {}
        self.var_address_map = {}

        self.int_size = 4
        self.string_size = 8 # char* type

        self.register = ['a', 'b', 'c', 'd']

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

            elif data[0] == 'identifier':
                if self.var_type_map[data[1]] == 'int':
                    if "%d\\n\\0" not in self.lc_data_map.keys():
                        self.lc_data_map["%d\\n\\0"] = self.LC
                        self.asm_code += self.init_string("\"%d\\n\\0\"")
                        self.LC += 1
                elif self.var_type_map[data[1]] == 'str':
                    if "%s\\n\\0" not in self.lc_data_map.keys():
                        self.lc_data_map["%s\\n\\0"] = self.LC
                        self.asm_code += self.init_string("\"%s\\n\\0\"")
                        self.LC += 1

            elif data[0] == 'expr':
                if "%d\\n\\0" not in self.lc_data_map.keys():
                    self.lc_data_map["%d\\n\\0"] = self.LC
                    self.asm_code += self.init_string("\"%d\\0\"")
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

    def init_main_stack(self):
        self.asm_code += "\t" + "pushq %rbp\n"
        self.asm_code += "\t" + "movq %rsp, %rbp\n"

    def init_stack_size(self):
        self.asm_code += "\t" + "subq $32, %rsp\n"

    def count_stack_size(self):
        if self.rpb_offset != 0:
            self.stack_size += (int(self.rpb_offset / 16) + 1) * 16

    def call_puts(self, lc_index):
        re = ""
        re += "\t" + "leaq .LC" + str(lc_index) + "(%rip), %rcx\n"
        re += "\t" + "call puts\n"
        self.ins.append(re)

    def call_printf(self, lc_index, char_type : bool = False, val : int = None):
        re = ""
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

    def add_all_ins(self):
        for item in self.ins:
            self.asm_code += item

    def run(self):
        self.ins = []
        self.asm_code += self.global_head
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
                elif node[1][0] == 'expr':
                    if hasattr(ExprEval(node[1][1], self).parse(), 'op'):
                        self.ins.append(ExprEval(node[1][1], self).parse().genAsm())
                        self.call_printf(self.lc_data_map["%d\\n\\0"])
                    else:
                        self.call_printf(self.lc_data_map["%d\\n\\0"], val = ExprEval(node[1][1], self).parse().genAsm())
                    

            elif node[0] == 'node_let':
                self.assign_movl(node[1][1], node[2][1])
            
            elif node[0] == "node_exit":
                self.call_exit()
            
            else:
                pass

        self.init_main_section()
        self.init_main_stack()
        self.count_stack_size()
        self.init_stack_size()
        self.asm_code += "\tcall __main\n"
        self.add_all_ins()
        self.init_main_return_value()
        return self.asm_code

    def add_ins(self):
        pass

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
        self.TO_ASM_CODE = AsmRunner(Nodes, self.TO_ASM_CODE, path = path).run()

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
                    re += "\t" + "movl " + self.state.var_address_map[self.arg1[1]] + ", %eax\n";
                    re += "\t" + "addl $" + self.arg2[1] + ". %eax\n"

        return re

    def __str__(self) -> str:
        return str(self.arg1) + " " + self.op + " " + str(self.arg2)

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
            elif instr.opname == 'BINARY_ADD':
                return self.__eval_add()
            elif instr.opname == 'RETURN_VALUE' and instr.argrepr == '':
                break

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

    def __eval_add(self):
        val1 = self.stack.pop()
        val2 = self.stack.pop()

        if self.get_type(val1) == 'identifier':
            if self.get_type(val2) == 'num':
                return ExprOp('+', ['identifier', val1], ['num', val2], self.state)
            elif self.get_type(val2) == 'identifier':
                return ExprOp('+', ['identifier', val1], ['identifier', val2], self.state)
            elif self.get_type(val2) == 'string':
                return ExprOp('+', ['identifier', val1], ['string', val2], self.state)

        elif self.get_type(val1) == 'num':
            if self.get_type(val2) == 'num':
                return ExprOp('+', ['num', val1], ['num', val2], self.state)
            elif self.get_type(val2) == 'identifier':
                return ExprOp('+', ['num', val1], ['identifier', val2], self.state)
            elif self.get_type(val2) == 'string':
                return ExprOp('+', ['num', val1], ['string', val2], self.state)
        
        elif self.get_type(val1) == 'string':
            if self.get_type(val2) == 'num':
                return ExprOp('+', ['string', val1], ['num', val2], self.state)
            elif self.get_type(val2) == 'identifier':
                return ExprOp('+', ['string', val1], ['identifier', val2], self.state)
            elif self.get_type(val2) == 'string':
                return ExprOp('+', ['string', val1], ['string', val2], self.state)


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