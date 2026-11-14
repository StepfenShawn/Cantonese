use std::collections::HashMap;

use crate::lexer::LexError;
use crate::parser::ParseError;

#[derive(Debug, thiserror::Error)]
pub enum CodegenError {
    #[error("unsupported AST node: {0}")]
    Unsupported(String),
    #[error("parse error: {0}")]
    Parse(#[from] ParseError),
    #[error("lex error: {0}")]
    Lex(#[from] LexError),
}

pub type LineMap = HashMap<usize, Vec<usize>>;

pub mod c;
pub mod py;
