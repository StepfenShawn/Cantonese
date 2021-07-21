import register_vm as r_vm
import stack_vm as s_vm

def test_register_vm() -> None:
    CantoneseState = r_vm.CanState("")
    CantoneseState.push_boolean(True)
    CantoneseState.dump()
    CantoneseState.push_integer(10)
    CantoneseState.dump()
    CantoneseState.push_null()
    CantoneseState.dump()
    CantoneseState.push_string("Hello World")
    CantoneseState.dump()
    CantoneseState.push_value(-4)
    CantoneseState.dump()
    CantoneseState.replace(3)
    CantoneseState.dump()
    CantoneseState.set_top(6)
    CantoneseState.dump()
    CantoneseState.remove(-3)
    CantoneseState.dump()
    CantoneseState.set_top(-5)
    CantoneseState.dump()

def test_stack_vm() -> None:
    ins = [
        s_vm.Instruction("OP_LOAD_CONST", 0),
        s_vm.Instruction("OP_PRINT_ITEM", None)
    ]
    code = s_vm.Code()
    code.ins_lst = ins
    code.co_consts = {0 : 'Hello World'}
    cs = s_vm.CanState(code)
    cs._run()


if __name__ == '__main__':
    print("test register vm:")
    test_register_vm()
    print("test stack vm:")
    test_stack_vm()