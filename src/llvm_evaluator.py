import llvmlite.ir as ir
import llvmlite.binding as llvm
from ctypes import *
from src.can_llvm_build import llvmCompiler

class LLvmEvaluator:
    def __init__(self, path):
        llvm.initialize()
        llvm.initialize_native_target()
        llvm.initialize_native_asmprinter()

        self.codegen = llvmCompiler(path)
        self.target = llvm.Target.from_default_triple()

    def evaluate(self, ast, optimize = True, llvmdump = False):
        self.codegen.gen_code(ast)

        # Convert llvm ir into in-memory representation
        llvmmod = llvm.parse_assembly(str(self.codegen.module))

        # Optimize the module
        if optimize:
            pmb = llvm.create_pass_manager_builder()
            pmb.opt_level = 2
            pm = llvm.create_module_pass_manager()
            pmb.populate(pm)
            pm.run(llvmmod)

            if llvmdump:
                print("========== Optimized LLVM IR ============")
                print(str(llvmmod))

        target_machine = self.target.create_target_machine()
        with llvm.create_mcjit_compiler(llvmmod, target_machine) as ee:
            ee.finalize_object()

            if llvmdump:
                print("========== Machine Code =============")
                print(target_machine.emit_assembly(llvmmod))

            fptr = CFUNCTYPE(c_double)(ee.get_function_address())
            return fptr()