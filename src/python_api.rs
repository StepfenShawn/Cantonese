//! PyO3 bindings exposing the Cantonese parser and compiler to Python.

use std::collections::HashMap;

use pyo3::create_exception;
use pyo3::prelude::*;

use crate::compiler::{CodegenError, to_python as compile_to_python};
use crate::lexer::{LexError, Lexer};

create_exception!(
    /// Python exception type for Cantonese compilation errors.
    cantonese_rs,
    CantoneseCompileError,
    pyo3::exceptions::PyException,
    "Error compiling Cantonese source code."
);

fn compile_error_to_py(err: CodegenError) -> PyErr {
    PyErr::new::<CantoneseCompileError, _>(format!("{}", err))
}

/// Compile Cantonese source into Python source.
#[pyfunction]
#[pyo3(signature = (source, filename = None))]
fn to_python(source: &str, filename: Option<&str>) -> PyResult<String> {
    let filename = filename.unwrap_or("<stdin>");
    compile_to_python(source, filename)
        .map(|(code, _)| code)
        .map_err(compile_error_to_py)
}

/// Compile Cantonese source into Python source and a line map.
#[pyfunction]
#[pyo3(signature = (source, filename = None))]
fn to_python_with_line_map(
    source: &str,
    filename: Option<&str>,
) -> PyResult<(String, HashMap<usize, Vec<usize>>)> {
    let filename = filename.unwrap_or("<stdin>");
    compile_to_python(source, filename).map_err(compile_error_to_py)
}

/// Tokenize Cantonese source and return token strings for debugging.
#[pyfunction]
#[pyo3(signature = (source, filename = None))]
fn tokenize(source: &str, filename: Option<&str>) -> PyResult<Vec<String>> {
    let filename = filename.unwrap_or("<stdin>");
    let mut lexer = Lexer::new(filename.to_string(), source);
    let tokens = lexer.tokenize_all().map_err(|e| match e {
        LexError::LexerErr { msg, pos, file } => PyErr::new::<CantoneseCompileError, _>(format!(
            "lexer error at {}:{}:{}: {}",
            file, pos.line, pos.offset, msg
        )),
        LexError::UnfinishedString(pos) => PyErr::new::<CantoneseCompileError, _>(format!(
            "unfinished string at {}:{}",
            pos.line, pos.offset
        )),
        LexError::Io(e) => PyErr::new::<CantoneseCompileError, _>(format!("io error: {}", e)),
    })?;
    Ok(tokens.into_iter().map(|t| t.to_string()).collect())
}

/// PyO3 module entry point. Maturin will expose this as `cantonese_rs._core`.
#[pymodule]
fn _core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add(
        "CantoneseCompileError",
        m.py().get_type::<CantoneseCompileError>(),
    )?;
    m.add_function(wrap_pyfunction!(to_python, m)?)?;
    m.add_function(wrap_pyfunction!(to_python_with_line_map, m)?)?;
    m.add_function(wrap_pyfunction!(tokenize, m)?)?;
    Ok(())
}
