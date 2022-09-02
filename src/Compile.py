import dis

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
                    if "%d\\0" not in self.lc_data_map.keys():
                        self.lc_data_map["%d"] = self.LC
                        self.asm_code += self.init_string("\"%d\\0\"")
                        self.LC += 1
                elif self.var_type_map[data[1]] == 'str':
                    if "%c\\0" not in self.lc_data_map.keys():
                        self.lc_data_map["%c"] = self.LC
                        self.asm_code += self.init_string("\"%c\\0\"")
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

    def call_printf(self, lc_index):
        re = ""
        re += "\t" + "movl %eax, %edx\n"
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
            re += "\t" + "movq %rax, " + self.var_address_map(var_name) + "\n"
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
                        self.call_printf(self.lc_data_map["%d"])
                    elif self.var_type_map[node[1][1]] == 'str':
                        self.call_printf(self.lc_data_map["%c"])
                elif node[1][0] == 'expr':
                    bytecode = ExprEval(node[1][1]).parse()


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


class ExprEval(object):
    def __init__(self, string):
        self.string = string
        self.py_ins = []

    def parse(self):
        # Trans the expr to python vm, then to asm
        # Expr -> Py-Opcode -> Mid-Opcode
        bytecode = dis.Bytecode(self.string)
        for instr in bytecode: 
            self.py_ins.append({'opname' : instr.opname, 'args' : instr.argrepr})
        print(self.py_ins)