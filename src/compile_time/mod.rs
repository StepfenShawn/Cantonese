//! Compile-time function registry.
pub mod built_in;

use std::collections::HashMap;

use crate::compile_time::built_in::UseMacrosFn;
use crate::parser::{ParseError, Parser};

use crate::ast::Exp;

/// A compile-time function that executes during parsing.
///
/// Implementors parse their own arguments from the token stream (after the
/// opening paren has been consumed) and return an `Exp` that represents the
/// result. For functions that only have side effects (like importing macros),
/// return `Exp::StatExpansion(Box::new(Stat::Pass(...)))`.
pub trait CompileTimeFn {
    /// The function name as written in source (e.g., "用下").
    fn name(&self) -> &str;

    /// Execute the compile-time function.
    ///
    /// At the point of invocation, the `@` token and the function name have
    /// already been consumed. The parser is positioned right after the
    /// function name (i.e., the next token should be `(`).
    ///
    /// Implementations **must** consume all their argument tokens and the
    /// closing `)`.
    fn execute(&self, parser: &mut Parser) -> Result<Exp, ParseError>;
}

/// Registry of all known compile-time functions.
#[derive(Default)]
pub struct CompileTimeRegistry {
    fns: HashMap<String, Box<dyn CompileTimeFn>>,
}

impl CompileTimeRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    /// Build a registry with all built-in compile-time functions registered.
    pub fn with_builtins() -> Self {
        let mut reg = Self::new();
        reg.register(Box::new(UseMacrosFn));
        reg
    }

    pub fn register(&mut self, func: Box<dyn CompileTimeFn>) {
        self.fns.insert(func.name().to_string(), func);
    }

    pub fn get(&self, name: &str) -> Option<&dyn CompileTimeFn> {
        self.fns.get(name).map(|f| f.as_ref())
    }
}
