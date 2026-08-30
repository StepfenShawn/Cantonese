//! PyO3 bindings exposing the Cantonese parser and compiler to Python.

use std::collections::HashMap;

use pyo3::create_exception;
use pyo3::prelude::*;

use crate::compiler::{CodegenError, to_python as compile_to_python};
use crate::lexer::span::Span;
use crate::lexer::{LexError, Lexer};
use crate::parser::ParseError;
use crate::ui::diagnostic::{ColorChoice, Diagnostic, Severity};

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

/// Convert a [`CodegenError`] into a [`Diagnostic`] so it can be pretty-printed.
fn error_to_diagnostic(err: &CodegenError) -> Diagnostic {
    match err {
        CodegenError::Parse(pe) => Diagnostic::from_parse_error(pe),
        CodegenError::Lex(le) => match le {
            LexError::LexerErr { msg, pos, file } => {
                Diagnostic::from_parse_error(&ParseError::from_lexer(file.clone(), *pos, msg.clone()))
            }
            LexError::UnfinishedString(pos) => Diagnostic::from_parse_error(
                &ParseError::from_lexer("<stdin>", *pos, "未閉合字符串字面量"),
            ),
            LexError::Io(e) => Diagnostic {
                severity: Severity::Error,
                message: format!("IO error: {}", e),
                file: "<stdin>".into(),
                span: Span::at(crate::lexer::token::Pos::simple(0, 0)),
                label: String::new(),
                help: String::new(),
            },
        },
        CodegenError::Unsupported(msg) => Diagnostic {
            severity: Severity::Error,
            message: msg.clone(),
            file: "<stdin>".into(),
            span: Span::at(crate::lexer::token::Pos::simple(0, 0)),
            label: String::new(),
            help: String::new(),
        },
    }
}

// ---------------------------------------------------------------------------
// PyDiagnostic – Python-visible wrapper around the internal Diagnostic
// ---------------------------------------------------------------------------

/// A single diagnostic message (error, warning, etc.) produced during
/// compilation.  Use [`compile_diagnostics`] or [`compile_with_diagnostics`]
/// to obtain instances, then call [`PyDiagnostic::render`] to get a formatted
/// multi-line string suitable for terminal display.
#[pyclass(name = "Diagnostic", module = "cantonese_rs._core", skip_from_py_object)]
#[derive(Debug, Clone)]
struct PyDiagnostic {
    inner: Diagnostic,
}

#[pymethods]
impl PyDiagnostic {
    /// Severity level: "濑嘢!!!", "warning", "note", or "tips".
    #[getter]
    fn severity(&self) -> &'static str {
        match self.inner.severity {
            Severity::Error => "濑嘢!!!",
            Severity::Warning => "warning",
            Severity::Note => "note",
            Severity::Help => "tips",
        }
    }

    /// Human-readable message describing the problem.
    #[getter]
    fn message(&self) -> &str {
        &self.inner.message
    }

    /// File path that the diagnostic refers to.
    #[getter]
    fn file(&self) -> &str {
        &self.inner.file
    }

    /// 1-based line number where the error starts.
    #[getter]
    fn start_line(&self) -> usize {
        self.inner.span.start.line
    }

    /// 0-based column offset where the error starts.
    #[getter]
    fn start_column(&self) -> usize {
        self.inner.span.start.offset
    }

    /// 1-based line number where the error ends.
    #[getter]
    fn end_line(&self) -> usize {
        self.inner.span.end.line
    }

    /// 0-based column offset where the error ends.
    #[getter]
    fn end_column(&self) -> usize {
        self.inner.span.end.offset
    }

    /// Optional help / tip text.
    #[getter]
    fn help(&self) -> &str {
        &self.inner.help
    }

    /// Render the diagnostic as a multi-line Rust-compiler-style string.
    ///
    /// Parameters
    /// ----------
    /// source : str
    ///     The original Cantonese source code.
    /// colors : bool, optional
    ///     Whether to include ANSI color codes (default: auto-detect).
    fn render(&self, source: &str, colors: Option<bool>) -> String {
        let cc = match colors {
            Some(true) => ColorChoice::Always,
            Some(false) => ColorChoice::Never,
            None => ColorChoice::Auto,
        };
        self.inner.render(source, cc)
    }

    fn __repr__(&self) -> String {
        format!(
            "Diagnostic({:?}, {:?}, {}:{}-{}:{})",
            self.inner.severity,
            self.inner.message,
            self.inner.file,
            self.inner.span.start.line,
            self.inner.span.start.offset,
            self.inner.span.end.line,
        )
    }
}

// ---------------------------------------------------------------------------
// Compile-time diagnostic helpers
// ---------------------------------------------------------------------------

/// Compile Cantonese source to Python, returning a list of
/// [`PyDiagnostic`] objects (empty on success).
///
/// Unlike [`to_python`], this function never raises – all errors are captured
/// as structured diagnostics that can be inspected and pretty-printed.
#[pyfunction]
#[pyo3(signature = (source, filename = None))]
fn compile_diagnostics(source: &str, filename: Option<&str>) -> Vec<PyDiagnostic> {
    let filename = filename.unwrap_or("<stdin>");
    match compile_to_python(source, filename) {
        Ok(_) => Vec::new(),
        Err(ref e) => vec![PyDiagnostic {
            inner: error_to_diagnostic(e),
        }],
    }
}

/// Compile Cantonese source to Python and return both the generated code and a
/// list of diagnostics.  On success the diagnostics list is empty.
#[pyfunction]
#[pyo3(signature = (source, filename = None))]
fn compile_with_diagnostics(
    source: &str,
    filename: Option<&str>,
) -> (String, Vec<PyDiagnostic>) {
    let filename = filename.unwrap_or("<stdin>");
    match compile_to_python(source, filename) {
        Ok((code, _)) => (code, Vec::new()),
        Err(ref e) => (
            String::new(),
            vec![PyDiagnostic {
                inner: error_to_diagnostic(e),
            }],
        ),
    }
}

// ---------------------------------------------------------------------------
// Runtime diagnostic helper
// ---------------------------------------------------------------------------

/// Render a runtime error as a Rust-style diagnostic string.
///
/// Parameters
/// ----------
/// exc_type : str
///     Exception class name (e.g. ``"ZeroDivisionError"``).
/// exc_value : str
///     Exception message.
/// source : str
///     Original Cantonese source code.
/// line : int
///     1-based line number in the *Cantonese* source where the error occurred.
/// filename : str, optional
///     File path for the diagnostic header.
/// colors : bool, optional
///     Whether to include ANSI color codes (default: auto-detect).
#[pyfunction]
#[pyo3(signature = (exc_type, exc_value, source, line, filename = None, colors = None))]
fn format_runtime_diagnostic(
    exc_type: &str,
    exc_value: &str,
    source: &str,
    line: usize,
    filename: Option<&str>,
    colors: Option<bool>,
) -> String {
    let filename = filename.unwrap_or("<stdin>");
    let cc = match colors {
        Some(true) => ColorChoice::Always,
        Some(false) => ColorChoice::Never,
        None => ColorChoice::Auto,
    };

    let pos = crate::lexer::token::Pos::simple(line, 0);
    let diag = Diagnostic {
        severity: Severity::Error,
        message: format!("{}: {}", exc_type, exc_value),
        file: filename.to_string(),
        span: Span::at(pos),
        label: String::new(),
        help: "幫緊你只不過有心無力:(".to_string(),
    };
    diag.render(source, cc)
}

// ---------------------------------------------------------------------------
// Original API (kept for backward compatibility)
// ---------------------------------------------------------------------------

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
    m.add_class::<PyDiagnostic>()?;
    m.add_function(wrap_pyfunction!(to_python, m)?)?;
    m.add_function(wrap_pyfunction!(to_python_with_line_map, m)?)?;
    m.add_function(wrap_pyfunction!(tokenize, m)?)?;
    m.add_function(wrap_pyfunction!(compile_diagnostics, m)?)?;
    m.add_function(wrap_pyfunction!(compile_with_diagnostics, m)?)?;
    m.add_function(wrap_pyfunction!(format_runtime_diagnostic, m)?)?;
    Ok(())
}
