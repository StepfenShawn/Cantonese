from llvmlite import ir
import src.can_ast as can_ast


class llvmCompiler(object):
    def __init__(self, path) -> None:
        self.type_map = {
            'int' : ir.IntType(32),
            'bool' : ir.IntType(1),
            'float' : ir.FloatType(),
            'double' : ir.DoubleType(),
            'void' : ir.VoidType(),
            'str' : ir.ArrayType(ir.IntType(8), 1)
        }

        self.module = ir.Module(path)
        self.builder = None
        self.i = 0

    def compile_stat(self, stat):
        pass

    def compile_expr(self, exp):
        if isinstance(exp, can_ast.NumeralExp):
           return ir.Constant(self.type_map['float'], exp.val)
        elif isinstance(exp, can_ast.IdExp):
            return self.builder.load(exp.name)
        elif isinstance(exp, can_ast.BinopExp):
            # try:
            # (exp.exp1)
            # except Exception:
                # pass
            pass