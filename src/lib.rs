// Cantonese AST Python绑定
use pyo3::prelude::*;
use std::collections::HashMap;

pub mod ast;
pub mod python;
pub mod macros;
pub mod parser;

pub use ast::statement::Program;
pub use macros::expand_macros;
pub use parser::ast_builder::AstBuilder;
pub use python::parse_to_ast;

/// Python模块入口点
/// 注意：函数名必须与模块名完全匹配
#[pymodule]
fn cantonese_rs(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(parse_to_ast, m)?)?;
    Ok(())
}
