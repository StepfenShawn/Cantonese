from llvmlite import ir
import can_ast as can_ast

class llvmUtils:
    @staticmethod
    def alloc_and_store(builder : ir.IRBuilder, val, typ, name = ''):
        var_addr = builder.alloca(typ, name=name)
        builder.store(val, var_addr)
        return var_addr

    @staticmethod
    def stringz(string):
        n = len(string) + 1
        buf = bytearray((' ' * n).encode('ascii'))
        buf[-1] = 0
        buf[:-1] = string.encode('utf-8')
        return ir.Constant(ir.ArrayType(ir.IntType(8), n), buf)

    @staticmethod
    def const(val, width = None):
        if isinstance(val, int):
            return ir.Constant(ir.IntType(32), val)

    @staticmethod
    def typeToFormat(typ : ir.types):
        fmt = None
        if isinstance(typ, ir.IntType):
            fmt = "%d"
        elif isinstance(typ, ir.FloatType):
            fmt = "%f"
        elif isinstance(typ, ir.DoubleType):
            fmt = "%lf"
        else:
            fmt = "%s"
        return fmt

class llvmCompiler(object):
    def __init__(self, path) -> None:
        # Initialize the code generator.
        self.module = ir.Module()
        self.add_builtin_func()
        self.builder = ir.IRBuilder(ir.Function(self.module, ir.FunctionType(ir.IntType(32), []), "main").
            append_basic_block('entry'))
        # Maps var names to ir.Value
        self.func_symtab = {}
        # Maps var types to ir.Type
        self.type_map = {
            'bool' : ir.IntType(1),
            'int' : ir.IntType(32),
            'float' : ir.FloatType(),
            'double' : ir.DoubleType(),
            'void' : ir.VoidType(),
            'str' : ir.ArrayType(ir.IntType(8), 1)
        }

        self.string_i = -1
        self.block_i = -1
        self.is_break = False
        self.loop_test_blocks = []
        self.loop_end_blocks = []

    def inc_string(self):
        self.string_i += 1
        return self.string_i

    def inc_block(self):
        self.block_i += 1
        return self.block_i

    def main_ret(self):
        self.builder.ret(ir.Constant(ir.IntType(32), 0))

    # -----------------------------------------------------------------
    # builtin functons for Cantonese.
    # -----------------------------------------------------------------

    def print_string(self, string):
        pass

    def print_num(self, num_format, num):
        percent_d = llvmUtils.stringz(num_format)
        percent_d = llvmUtils.alloc_and_store(self.builder, 
                    percent_d, ir.ArrayType(percent_d.type.element, percent_d.type.count))
        percent_d = self.builder.gep(percent_d, 
                [llvmUtils.const(0), llvmUtils.const(0)])
        percent_d = self.builder.bitcast(percent_d, ir.IntType(8).as_pointer())
        self.builder.call(self.module.get_global("printf"), [percent_d, num])
        self.builder.call(self.module.get_global("putchar"), [ir.Constant(ir.IntType(32), 10)])

    def add_builtin_func(self):
        # Add the declaration of exit
        exit_ty = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])
        fn_exit = ir.Function(self.module, exit_ty, 'exit')

        # Add the declaration of `int printf(char* format, ...)`
        printf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        fn_printf = ir.Function(self.module, printf_ty, 'printf')
        
        # Add the declaration of putchar
        putchar_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        fn_putchar = ir.Function(self.module, putchar_ty, 'putchar')
        
        # Add putchard
        putchard_ty = ir.FunctionType(ir.DoubleType(), [ir.DoubleType()])
        fn_putchard = ir.Function(self.module, putchard_ty, 'putchard')
        irbuilder = ir.IRBuilder(fn_putchard.append_basic_block('entry'))
        ival = irbuilder.fptoui(fn_putchard.args[0], ir.IntType(32), 'intcast')
        irbuilder.call(fn_putchar, [ival])
        irbuilder.ret(ir.Constant(ir.DoubleType(), 0))

        puts_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))])
        fn_puts = ir.Function(self.module, puts_ty, 'puts')

        # Add the declaration of getchar
        getchar_ty = ir.FunctionType(ir.IntType(8), [])
        ir.Function(self.module, getchar_ty, 'getchar')

    def create_global_string(self, s: str, name: str):
        s += '\0'
        type_i8_x_len = ir.ArrayType(ir.types.IntType(8), len(s))
        constant = ir.Constant(type_i8_x_len, bytearray(s.encode('utf8')))
        variable = ir.GlobalVariable(self.builder.module, type_i8_x_len, name)
        variable.linkage = 'internal'
        variable.global_constant = True
        variable.initializer = constant
        variable.align = 1

        zero = ir.Constant(ir.types.IntType(32), 0)
        # printf("%d", ...):  can not work now !!!
        # variable_pointer = self.builder.bitcast(variable, ir.IntType(8).as_pointer())
        variable_pointer = self.builder.gep(variable, [zero, zero])
        return variable_pointer

    def _compile(self, ast : list):
        for node in ast:
            self._codegen(node)

    def gen_code(self, node):
        return self._codegen(node)

    def _codegen(self, node):
        method = '_codegen_' + node.__class__.__name__
        return getattr(self, method)(node)

    # -----------------------------------------------------------
    # map cantonese's value to ir.value
    #------------------------------------------------------------

    def _codegen_NumeralExp(self, node : can_ast.NumeralExp):
        return ir.Constant(ir.DoubleType(), float(node.val))

    def _codegen_StringExp(self, node : can_ast.StringExp):
        return self.create_global_string(node.s[1:-1], 's_' + str(self.inc_string()))

    def _codegen_FalseExp(self, node : can_ast.FalseExp):
        return ir.Constant(ir.IntType(1), 0)

    def _codegen_TrueExp(self, node : can_ast.TrueExp):
        return ir.Constant(ir.IntType(1), 1)

    # -----------------------------------------------------------
    # Statements for cantonese
    # -----------------------------------------------------------

    def _codegen_FunctionDefStat(self, node : can_ast.FunctionDefStat):
        name = self.getIdName(node.name_exp)
        params = [self._codegen(arg) for arg in node.args]
        params_ptr = []

        params_type = [self.getIdName(arg_type) for arg_type in node.args_type]
        return_type = self.getIdName(node.ret_type)

        fnty = ir.FunctionType(return_type, params_type)
        func = ir.Function(self.module, fnty, name=name)

        # Define function's block
        block = func.append_basic_block(f'{name}_entry')
        
        # Storing the pointers of each parameter
        for i, typ, in enumerate(params_type):
            ptr = self.builder.alloca(typ)
            self.builder.store(func.args[i], ptr)
            params_ptr.append(ptr)

        previous_builer = self.builder
        self.builder = ir.IRBuilder(block)
        previous_variable = self.func_symtab.copy()
        for i,x in enumerate(zip(params_type, params_ptr)):
            typ = params_type[i]
            ptr = params_ptr[i]

            self.func_symtab[self._codegen(params_ptr)] = ptr

        self._compile(node.blocks)

    def _codegen_IdExp(self, node : can_ast.IdExp):
        ptr = self.func_symtab[node.name]
        return self.builder.load(ptr)

    def _codegen_FuncCallExp(self, node : can_ast.FuncCallExp):
        callee_func = self.module.globals.get(self.getIdName(node.prefix_exp), 
            None)
        if callee_func == None:
            raise Exception("Calling a no exists function: " + self.getIdName(node.prefix_exp))
        call_args = [self._codegen(arg) for arg in node.args]
        return self.builder.call(callee_func, call_args)

    def _codegen_FuncCallStat(self, node : can_ast.FuncCallStat):
        callee_func = self.module.globals.get(self.getIdName(node.func_name), 
            None)
        if callee_func == None:
            raise Exception("Calling a no exists funtion: " + self.getIdName(node.func_name))
        call_args = [self._codegen(arg) for arg in node.args]
        return self.builder.call(callee_func, call_args, 'calltmp')

    def _codegen_ExitStat(self, node : can_ast.ExitStat):
        callee_func = self.module.globals.get('exit', None)
        return self.builder.call(callee_func, [ir.Constant(ir.IntType(32), 1)])

    def _codegen_AssignStat(self, node : can_ast.AssignStat):
        for keys, values in zip(node.var_list, node.exp_list):
            self.visit_assign(self.getIdName(keys), self._codegen(values))

    def _codegen_PrintStat(self, node : can_ast.PrintStat):
        call_args = [self._codegen(arg) for arg in node.args]
        if isinstance(call_args[0].type, ir.DoubleType):
            self.print_num("%lf", call_args[0])
        else:
            callee_func = self.module.globals.get("puts", None)
            return self.builder.call(callee_func, call_args, 'calltmp')

    def _codegen_BreakStat(self, node : can_ast.BreakStat):
        if len(self.loop_end_blocks) == 0:
            raise Exception("Syntax Error: 'break' cannot be used outside of control flow statements")
        self.is_break = True
        return self.builder.branch(self.loop_end_blocks[-1])

    def _codegen_ReturnStat(self, node : can_ast.ReturnStat):
        # TODO: Add function return
        self.builder.ret(ir.Constant(ir.IntType(32), 0))

    def _codegen_IfStat(self, node : can_ast.IfStat):
        orelse = node.else_blocks
        elseif = node.elif_blocks
        cond = self._codegen(node.if_exp)

        if orelse == []:
            if elseif == []:
                with self.builder.if_then(cond):
                    self._compile(node.if_block)
            
            else:
                if_bb = self.builder.function.append_basic_block('then_block_' + str(self.inc_block()))
                elif_bb : list = []
                for elif_exp, block in zip(node.elif_exps, node.elif_blocks):
                    elif_bb.append(ir.Block(self.builder.function, 'then_block_' + str(self.inc_block())))
                self.builder.position_at_start(if_bb)
                self._compile(node.if_block)
                for i, elif_exp, elif_block in zip(elif_bb, node.elif_exps, node.elif_blocks):
                    self.builder.position_at_start(i)
                    self._compile(elif_block)
                    self.builder.cbranch(self._codegen(elif_exp), if_bb, i)

        else:
            if elseif == []:
                with self.builder.if_else(cond) as (true, otherwise):
                    with true:
                        self._compile(node.if_block)
                    with otherwise:
                        self._compile(node.else_blocks)

    # TODO: Fix bug that cannot use 'break' without 'if'
    def _codegen_WhileStat(self, node : can_ast.WhileStat):
        cond = self._codegen(node.cond_exp)
        
        # block where runs if the condition is true
        while_loop_entry = self.builder.append_basic_block("while_block_entry_" + str(self.inc_block()))
        while_loop_otherwise = self.builder.append_basic_block("while_loop_otherwise_" + str(self.inc_block()))
        
        self.loop_test_blocks.append(while_loop_entry)
        self.loop_end_blocks.append(while_loop_otherwise)

        self.builder.cbranch(cond, while_loop_entry, while_loop_otherwise)
        # Setting the builder postion at start
        self.builder.position_at_start(while_loop_entry)
        self._compile(node.blocks)
        cond = self._codegen(node.cond_exp)
        self.builder.cbranch(cond, while_loop_entry, while_loop_otherwise)
        self.builder.position_at_start(while_loop_otherwise)
        self.loop_test_blocks.pop()
        self.loop_end_blocks.pop()

    def gen_logic(self, op : str, lhs, rhs):
        return self.builder.fcmp_ordered(op, lhs, rhs)

    def _codegen_BinopExp(self, node : can_ast.BinopExp):
        lhs = self._codegen(node.exp1)
        rhs = self._codegen(node.exp2)
        
        if node.op == '+':
            return self.builder.fadd(lhs, rhs)
        elif node.op == '-':
            return self.builder.fsub(lhs, rhs)
        elif node.op == '*':
            return self.builder.fmul(lhs, rhs)
        elif node.op == '/':
            return self.builder.fdiv(lhs, rhs)
        elif node.op == '%':
            return self.builder.frem(lhs, rhs)
        elif node.op in ('<', '<=', '>', '>=', '=='):
           return self.gen_logic(node.op, lhs, rhs)
        elif node.op == '&':
            return self.builder.and_(lhs, rhs)
        elif node.op == '|':
            return self.builder.xor(lhs, rhs)
        elif node.op == '>>':
            return self.builder.ashr(lhs, rhs)
        elif node.op == '<<':
            return self.builder.shl(lhs, rhs)
        else:
            raise Exception('Unknown binary operator: ' + node.op)

    def _codegen_UnopExp(self, node : can_ast.UnopExp):
        rhs = self._codegen(node.exp)

        if node.op == '~':
            return self.builder.not_(rhs)
        elif node.op == '-':
            return self.builder.neg(rhs)
        elif node.op == 'not':
            return self.builder.select(
                self.builder.icmp_signed('==', ir.Constant(ir.IntType(1), 0), rhs),
                ir.Constant(ir.IntType(1), 1),
                ir.Constant(ir.IntType(1), 0)
            )

    def getIdName(self, exp : can_ast.IdExp) -> str:
        return exp.name

    def visit_assign(self, name : str, value : ir.Value):
        if not self.func_symtab.__contains__(name):
            # Storing the value to the pointer
            ptr = self.builder.alloca(value.type)
            self.builder.store(value, ptr)
            self.func_symtab[name] = ptr
        
        else:
            ptr = self.func_symtab[name]
            self.builder.store(value, ptr)

    def visist_func_def(self):
        pass