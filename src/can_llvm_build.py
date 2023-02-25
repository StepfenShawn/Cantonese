from llvmlite import ir
import can_ast as can_ast

class llvmCompiler(object):
    def __init__(self, path) -> None:
        # Initialize the code generator.
        self.module = ir.Module()
        self.add_builtin_func()
        self.builder = ir.IRBuilder(ir.Function(self.module, ir.FunctionType(ir.IntType(32), []), "main").
            append_basic_block('entry'))
        self.func_symtab = {}

    def main_ret(self):
        self.builder.ret(ir.Constant(ir.IntType(32), 0))

    def add_builtin_func(self):
        # Add the declaration of exit
        exit_ty = ir.FunctionType(ir.VoidType(), [ir.IntType(32)])
        self.exit = ir.Function(self.module, exit_ty, 'exit')
        # Add the declaration of `int printf(char* format, ...)`
        printf_ty = ir.FunctionType(ir.IntType(32), [ir.PointerType(ir.IntType(8))], var_arg=True)
        self.printf = ir.Function(self.module, printf_ty, 'printf')
        # Add the declaration of putchar
        putchar_ty = ir.FunctionType(ir.IntType(32), [ir.IntType(32)])
        self.putchar = ir.Function(self.module, putchar_ty, 'putchar')
        # Add putchard
        putchard_ty = ir.FunctionType(ir.DoubleType(), [ir.DoubleType()])
        self.putchard = ir.Function(self.module, putchard_ty, 'putchard')
        irbuilder = ir.IRBuilder(self.putchard.append_basic_block('entry'))
        ival = irbuilder.fptoui(self.putchard.args[0], ir.IntType(32), 'intcast')
        irbuilder.call(self.putchar, [ival])
        irbuilder.ret(ir.Constant(ir.DoubleType(), 0))

    def create_global_string(self, s: str, name: str):
        type_i8_x_len = ir.types.ArrayType(ir.types.IntType(8), len(s))
        constant = ir.Constant(type_i8_x_len, bytearray(s.encode('utf-8')))
        variable = ir.GlobalVariable(self.builder.module, type_i8_x_len, name)
        variable.linkage = 'private'
        variable.global_constant = True
        variable.initializer = constant
        variable.align = 1

        zero = ir.Constant(ir.types.IntType(32), 0)
        variable_pointer = self.builder.gep(variable, [zero, zero])
        return variable_pointer

    def gen_code(self, node):
        return self._codegen(node)

    def _codegen(self, node):
        method = '_codegen_' + node.__class__.__name__
        return getattr(self, method)(node)

    def _codegen_NumeralExp(self, node : can_ast.NumeralExp):
        return ir.Constant(ir.DoubleType(), float(node.val))

    def _codegen_StringExp(self, node : can_ast.StringExp):
        return self.create_global_string(node.s, 's')

    def _codegen_CallStat(self, node : can_ast.FuncCallExp):
        # callee_func = self.module.globals.get(node., None)
        return

    def _codegen_ExitStat(self, node : can_ast.ExitStat):
        return self.builder.call(self.exit, [ir.Constant(ir.IntType(32), 1)])

    def _codegen_PrintStat(self, node : can_ast.PrintStat):
        call_args = [self._codegen(arg) for arg in node.args]
        return self.builder.call(self.printf, call_args, 'calltmp')

    def _codegen_BinopExp(self, node : can_ast.BinopExp):
        lhs = self._codegen(node.exp1)
        rhs = self._codegen(node.exp2)
        
        if node.op == '+':
            return self.builder.fadd(lhs, rhs, 'addtmp')
        elif node.op == '-':
            return self.builder.fsub(lhs, rhs, 'subtmp')
        elif node.op == '*':
            return self.builder.fmul(lhs, rhs, 'multmp')
        elif node.op == '<':
            cmp = self.builder.fcmp_unordered('<', lhs, rhs, 'cmptmp')
            return self.builder.uitofp(cmp, ir.DoubleType(), 'booltmp')
        else:
            raise Exception('Unknown binary operator: ' + node.op)