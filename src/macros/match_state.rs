//! Core types for macro pattern matching state.

use std::collections::HashMap;

use crate::ast::{Exp, IdExp};
use crate::lexer::token::{Pos, Token, TokenType};
use crate::parser::ParseError;

// =============================================================================
// Match failure info
// =============================================================================

#[derive(Debug, Clone)]
pub struct MatchFailure {
    pub pat_idx: usize,
    pub child_idx: usize,
    pub reason: String,
}

// =============================================================================
// Fragment specifier
// =============================================================================

/// Fragment specifier for a meta variable.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum FragSpec {
    Block,
    Expr,
    Ident,
    Literal,
    Stmt,
    Str,
    Tt,
}

impl FragSpec {
    pub fn from_name(name: &str) -> Result<Self, ParseError> {
        match name {
            "id" | "ident" => Ok(FragSpec::Ident),
            "expr" => Ok(FragSpec::Expr),
            "lit" => Ok(FragSpec::Literal),
            "stmt" => Ok(FragSpec::Stmt),
            "block" => Ok(FragSpec::Block),
            "str" => Ok(FragSpec::Str),
            "tt" => Ok(FragSpec::Tt),
            _ => Err(ParseError::syntax(
                &Token::new(Pos::simple(0, 0), TokenType::Identifier, name.to_string()),
                "<macro>",
                format!("唔識嘅 fragment specifier: `{}`", name),
                "可用: id/ident, expr, lit, stmt, block, str, tt",
            )),
        }
    }

    pub fn from_exp(exp: &Exp) -> Result<Self, ParseError> {
        match exp {
            Exp::Id(IdExp { name, .. }) => Self::from_name(name),
            _ => Err(ParseError::syntax(
                &Token::new(Pos::simple(0, 0), TokenType::Identifier, "".to_string()),
                "<macro>",
                "Fragment specifier 必須係 identifier",
                "例如 `$x: expr`",
            )),
        }
    }
}

// =============================================================================
// Meta variables and match state
// =============================================================================

#[derive(Debug, Clone)]
pub struct MetaVar {
    captures: Vec<Vec<Token>>,
    next_idx: usize,
}

impl MetaVar {
    pub fn new(capture: Vec<Token>) -> Self {
        Self {
            captures: vec![capture],
            next_idx: 0,
        }
    }

    pub fn push(&mut self, capture: Vec<Token>) {
        if !self.captures.contains(&capture) {
            self.captures.push(capture);
            self.next_idx = 0;
        }
    }

    pub fn next_capture(&mut self) -> Vec<Token> {
        if self.captures.is_empty() {
            return Vec::new();
        }
        let idx = self.next_idx;
        self.next_idx = (self.next_idx + 1) % self.captures.len();
        self.captures[idx].clone()
    }

    pub fn repetition_times(&self) -> usize {
        self.captures.len()
    }
}

impl PartialEq for MetaVar {
    fn eq(&self, other: &Self) -> bool {
        self.captures == other.captures
    }
}

#[derive(Debug, Clone, Default)]
pub struct MatchState {
    pub vars: HashMap<String, MetaVar>,
}

impl MatchState {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn update(&mut self, name: String, tokens: Vec<Token>) {
        self.vars
            .entry(name)
            .and_modify(|mv| mv.push(tokens.clone()))
            .or_insert_with(|| MetaVar::new(tokens));
    }

    pub fn get(&self, name: &str) -> Option<&MetaVar> {
        self.vars.get(name)
    }

    pub fn get_mut(&mut self, name: &str) -> Option<&mut MetaVar> {
        self.vars.get_mut(name)
    }
}
