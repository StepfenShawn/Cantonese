use core::fmt;
use std::{cell::RefCell, collections::HashMap, rc::Rc};

#[derive(Clone, Copy, Debug)]
pub struct Instruction(pub u32);

#[derive(Clone)]
pub enum Value {
    Null,
    Bool(bool),
    Number(f64),
    String(Rc<String>),
    Builtin(fn(&[Value]) -> Vec<Value>)
}

impl fmt::Debug for Value {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Null => write!(f, "Null"),
            Self::Bool(x) =>  write!(f, "{x}"),
            Self::Number(x) => write!(f, "{x}"),
            Self::String(s) => write!(f, "{s:?}"),
            Self::Builtin(_) => write!(f, "builtin")
        }
    }
}

impl fmt::Display for Value {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Null => write!(f, "Null"),
            Self::Bool(x) =>  write!(f, "{x}"),
            Self::Number(x) => write!(f, "{x}"),
            Self::String(s) => write!(f, "{s:?}"),
            Self::Builtin(_) => write!(f, "builtin")
        }
    }
}

#[derive(Clone)]
pub enum UpValue {
    Open { stack_index: usize },
    Closed(Value)
}
pub type UpValueRef = Rc<RefCell<UpValue>>;

pub struct Closure {
    
}

struct Frame {
    closure: Rc<Closure>,
    base: usize,
    pc: usize,
}

pub struct VM {
    stack: Vec<Value>,
    frames: Vec<Frame>,
    open_upvalues: Vec<UpValueRef>,
    pub globals: HashMap<String, Value>
}

