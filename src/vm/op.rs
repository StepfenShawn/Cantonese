use std::rc::Rc;

pub enum Opcode {
    LoadConst { dst: u8, const_idx: u32 },
    LoadNull { dst: u8 },
    Move { dst: u8, src: u8 },

    Add { dst: u8, a: u8, b: u8 },
    Sub { dst: u8, a: u8, b: u8 },
    Mul { dst: u8, a: u8, b: u8 },
    Div { dst: u8, a: u8, b: u8 },

    Less { dst: u8, a: u8, b: u8 },
    Equal { dst: u8, a: u8, b: u8 },

    Jmp { offset: i32 },
    JmpIfFalse {reg: u8, offset: i32},

    Call { func: u8, arg_base: u8, arg_count: u8, dst: u8 },

    Return {val: u8},
    MakeClosure { dst: u8, func: u32, captured: Rc<[u8]> },

    MakeClass { dst: u8, name: u32, method_names: Rc<[u32]>},
    MakeBoundMethod { dst: u8, class: u8, method_name: u32, receiver: u8},
    GetField { dst: u8, obj: u8, field: u32},
    SetField { dst: u8, field: u32, value: u8},

    LoadGlobal { dst: u8, name: u32 },
    StoreGlobal { name: u32, value: u8 }
}
