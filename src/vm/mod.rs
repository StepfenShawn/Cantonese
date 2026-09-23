pub mod op;

use std::{cell::RefCell, collections::HashMap, rc::Rc};
use thiserror::Error;

use crate::vm::op::Opcode;

pub struct Function {
    pub name: Rc<str>,
    pub num_params: u8,
    pub num_regs: u8,
    pub code: Vec<Opcode>,
    pub constants: Vec<Value>,
}

impl Function {
    pub fn new(name: impl Into<Rc<str>>, num_params: u8, num_regs: u8) -> Self {
        Self {
            name: name.into(),
            num_params,
            num_regs,
            code: Default::default(),
            constants: Default::default(),
        }
    }
}

pub struct Closure {
    pub func: Rc<Function>,
    pub captured: Vec<Value>,
}

pub struct Class {
    pub name: Rc<str>,
    pub methods: HashMap<Rc<str>, Value>,
}

pub struct Instance {
    pub class: Rc<Class>,
    pub fields: RefCell<HashMap<Rc<str>, Value>>,
}

pub struct BoundMethod {
    pub receiver: Value,
    pub method: Value,
}

pub struct NativeFunc {
    pub name: Rc<str>,
    pub func: Box<dyn Fn(&mut Vm, &[Value]) -> VmResult<Value>>,
}

#[derive(Clone)]
pub enum Value {
    Nil,
    Bool(bool),
    Int(i64),
    Float(f64),
    Str(Rc<str>),
    Closure(Rc<Closure>),
    Native(Rc<NativeFunc>),
    Class(Rc<Class>),
    Instance(Rc<Instance>),
    BoundMethod(Rc<BoundMethod>),
}

impl Value {
    pub fn is_truthy(&self) -> bool {
        match self {
            Value::Nil => false,
            Value::Bool(b) => *b,
            Value::Int(i) => *i != 0,
            Value::Float(x) => *x != 0.0,
            Value::Str(s) => !s.is_empty(),
            _ => true,
        }
    }

    pub fn type_name(&self) -> &'static str {
        match self {
            Value::Nil => "nil",
            Value::Bool(_) => "bool",
            Value::Int(_) => "int",
            Value::Float(_) => "float",
            Value::Str(_) => "str",
            Value::Closure(_) | Value::Native(_) | Value::BoundMethod(_) => "function",
            Value::Class(_) => "class",
            Value::Instance(_) => "instance",
        }
    }
}

#[derive(Error, Debug)]
pub enum VmError {
    #[error("StackOverflow")]
    StackUnderflow,
    #[error("Accessed a bad register: {0}")]
    BadRegister(usize),
    #[error("Accessed a bad const: {0}")]
    BadConst(u32),
    #[error("Accessed a bad function: {0}")]
    BadFunction(u32),
    #[error("Accessed a bad string: {0}")]
    BadString(u32),
    #[error("Type invalid: {0}")]
    TypeError(String),
    #[error("AtityMismatch: excepted: {excepted}, got: {got}")]
    ArityMismatch { excepted: usize, got: usize },
    #[error("Undefined global: {0}")]
    UndefinedGlobal(String),
    #[error("Undefined field: {0}")]
    UndefinedField(String),
    #[error("Not callable: {0}")]
    NotCallable(String),
    #[error("DivideByZero")]
    DivideByZero,
    #[error("Overflow")]
    Overflow,
    #[error("VmError: {0}")]
    Message(String),
}

pub type VmResult<T> = Result<T, VmError>;

pub struct Frame {
    func: Rc<Function>,
    regs: Vec<Value>,
    ip: usize,
    ret_dst: Option<u8>,
}

pub struct Vm {
    frames: Vec<Frame>,
    pub functions: Vec<Rc<Function>>,
    pub strings: Vec<Rc<str>>,
    pub globals: HashMap<Rc<str>, Value>,
    pub max_frames: usize,
}

impl Default for Vm {
    fn default() -> Self {
        Self::new()
    }
}

impl Vm {
    pub fn new() -> Self {
        let mut vm = Vm {
            frames: Vec::new(),
            functions: Vec::new(),
            strings: Vec::new(),
            globals: HashMap::new(),
            max_frames: 1024,
        };
        vm
    }
}