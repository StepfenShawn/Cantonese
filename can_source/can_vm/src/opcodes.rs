use crate::can_object::CanObject;
pub enum Opcode<'a> {
    //ends program
    Exit,

    //stack manipulation
    Push(CanObject<'a>),
    Pop,

    //heap store/load
    Store(String),
    Load(String),

    //arithmetic operations
    Add,
    Sub,
    Mul,
    Div,

    //logical operations
    Not,
    And,
    Or,

    //function call/return
    Call(i32),
    Ret,

    //unconditional and conditional jumps
    Jmp(i32),
    Jif(i32),

    //comparison operators
    Iseq,
    Isge,
    Isgt,

    //io
    Print,

    LoadList(Vec<CanObject<'a>>),
    LoadSet(Vec<CanObject<'a>>),
}