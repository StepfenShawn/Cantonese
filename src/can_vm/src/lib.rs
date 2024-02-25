mod opcodes;
mod can_object;
mod frame;
mod machine;

use opcodes::Opcode;
use can_object::CanObject;
use machine::Machine;
use pyo3::{prelude::*};
use pyo3::types::*;

#[pyfunction]
fn exec_print_stat(py: Python, args: PyObject) -> PyResult<()> {
    // let args: PyObject = stat.getattr(py, "args").unwrap();
    Ok(())
}

#[pymodule]
fn can_vm(py: Python,  module: &PyModule) -> PyResult<()> {
    module.add_function(wrap_pyfunction!(exec_print_stat, module)?);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn it_works() {
        let programm = [
            Opcode::Push(CanObject::Str("Hello World")),
            Opcode::Print,
            Opcode::Push(CanObject::Num(1 as f32)),
            Opcode::Push(CanObject::Num(1 as f32)),
            Opcode::Add,
            Opcode::Print
        ];
        let mut m = Machine::new(&programm);
        m.run();
    }
}