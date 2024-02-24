use std::collections::{VecDeque, HashMap};
use super::opcodes::Opcode;
use super::frame::Frame;
use super::can_object::CanObject;

pub struct Machine<'a> {
    program: &'a [Opcode<'a>],
    ip: i32,
    stack: VecDeque<CanObject<'a>>,
    exited: bool,
    frames: VecDeque<Frame<'a>>
}

impl<'a> Machine<'a> {
    pub fn run(&mut self) {
        while !self.exited {
            self.step();
        }
    }

    fn step(&mut self) {
        if self.ip < self.program.len() as i32 {
            self.ip += 1;
            self.decode(&self.program[(self.ip - 1) as usize])
        }
    }

    fn check(&self, size: usize) {
        if self.stack.len() < size {
            panic!("Must have at least {} elements on the stack for this operation.", size);
        }
    }

    fn decode(&mut self, instruction: &'a Opcode) {
        match instruction {
            Opcode::Exit => self.exited = true,
            Opcode::Push(x) => {
                self.stack.push_back(*x);
            },
            Opcode::Pop => {
                self.check(1);
                self.stack.pop_back();
            },
            Opcode::Add => {
                self.check(2);
                let s2 = self.stack.pop_back().unwrap();
                let s1 = self.stack.pop_back().unwrap();
                self.stack.push_back(s1 + s2);
            },
            Opcode::Sub => {
                self.check(2);
                let s2 = self.stack.pop_back().unwrap();
                let s1 = self.stack.pop_back().unwrap();
                self.stack.push_back(s1 - s2);
            },
            Opcode::Mul => {
                self.check(2);
                let s2 = self.stack.pop_back().unwrap();
                let s1 = self.stack.pop_back().unwrap();
                self.stack.push_back(s1 * s2);
            },
            Opcode::Div => {
                self.check(2);
                let s2 = self.stack.pop_back().unwrap();
                let s1 = self.stack.pop_back().unwrap();
                self.stack.push_back(s1 / s2);
            },
            Opcode::Print => {
                self.check(1);
                println!("{}", self.stack.pop_back().unwrap());
            },
            Opcode::Store(key) => {
                self.check(1);
                let s1 = self.stack.pop_back().unwrap();
                self.frames.back_mut().unwrap().set_var(key, s1);
            },
            Opcode::Load(key) => {
                self.stack.push_back(self.frames.back_mut().unwrap().get_var(key));
            },
            Opcode::Call(addr) => {
                self.frames.push_back(Frame {
                    vars: HashMap::new(),
                    ret_addr: 0
                });
                self.ip = *addr;
            },
            Opcode::Ret => {
                self.ip = self.frames.pop_back().unwrap().ret_addr;
            }
            _ => panic!("Unknow opcode")
        }
    }

    pub fn new(program: &'a [Opcode<'a>]) -> Machine<'a> {
        let top_frame = Frame {
            vars: HashMap::new(),
            ret_addr: 0,
        };

        let mut frame_stack = VecDeque::new();
        frame_stack.push_back(top_frame);

        Machine { 
            program, 
            ip: 0,
            stack: VecDeque::new(),
            exited: false,
            frames: frame_stack
        }
    }
}