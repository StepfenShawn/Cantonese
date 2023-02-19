from llvmlite import ir
import src.can_ast as can_ast

class llvmCompiler(object):
    def __init__(self, path) -> None:
        # Initialize the code generator.
        self.module = ir.Module()
        self.builder = None
        self.func_symtab = {}

    def generate_code(self, node):
        return self._codegen(node)

    def _codegen(self, node):
        method = '_codegen_' + node.__class__.__name__
        return getattr(self, method)(node)

    def _codegen_NumeralExp(self, node : can_ast.NumeralExp):
        return ir.Constant(ir.DoubleType(), float(node.val))

    def _codegen_StringExp(self, node : can_ast.StringExp):
        # TODO
        return ir.Constant(ir.MetaDataString())

    def _codegen_PrintStat(self, node : can_ast.PrintStat):
        callee_func = self.module.globals.get("print", None)
        call_args = [self._codegen(arg) for arg in node.args]
        return self.builder.call(callee_func, call_args, 'calltmp')

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