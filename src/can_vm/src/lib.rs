mod opcodes;
mod can_object;
mod frame;
mod machine;

use opcodes::Opcode;
use can_object::CanObject;
use machine::Machine;
use pyo3::prelude::*;

#[pymodule]
fn can_vm(py: Python,  m: &PyModule) -> PyResult<()> {
    // m.add_function(fun)
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let programm = [
            Opcode::Push(CanObject::Num(1 as f32)),
            Opcode::Print
        ];
        let mut m = Machine::new(&programm);
        m.run();
    }
}