use std::collections::{VecDeque, HashMap};
use super::opcodes::Opcode;
use super::frame::Frame;
use super::can_object::CanObject;

pub struct Machine<'a> {
    program: &'a [Opcode],
    ip: i32,
    stack: VecDeque<CanObject>,
    exited: bool,
    frames: VecDeque<Frame<'a>>
}

impl <'a> Machine<'a> {
    pub fn run(&mut self) {
        while !self.exited {
            self.step();
        }
    }

    fn step(&mut self) {
        if self.ip < self.program.len() as i32 {
            self.ip += 1;
        }
    }

    pub fn new(program: &[Opcode]) -> Machine {
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