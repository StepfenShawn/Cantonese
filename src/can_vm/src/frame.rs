use std::collections::HashMap;
use crate::can_object::CanObject;

pub struct Frame<'a> {
    pub vars: HashMap<&'a str, CanObject<'a> >,
    pub ret_addr: i32
}

impl<'a> Frame<'a> {
    pub fn get_var(&self, key: &str) -> CanObject<'a>{
        match self.vars.get(&key) {
            Some(&x) => x,
            _ => CanObject::Num(0.0),
        }
    }

    pub fn set_var(&mut self, key: &'a str, value: CanObject<'a>) {
        self.vars.insert(key, value);
    }
}