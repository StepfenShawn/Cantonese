//! Recursive-descent parser for the Cantonese language.

#![allow(dead_code)]

use std::cell::RefCell;
use std::rc::Rc;

use crate::ast::{Exp, Stat};
use crate::lexer::token::{Pos, Token, TokenType};
use crate::lexer::span::Span;
use crate::macros::MacroRegistry;
pub use crate::ui::diagnostic::{ColorChoice, Diagnostic};

pub mod exp;
pub mod macro_body;
pub mod macro_pat;
pub mod names;
pub mod stat;

pub use exp::ExpParser;
#[allow(unused_imports)]
pub use macro_body::MacroBodyParser;
#[allow(unused_imports)]
pub use macro_pat::MacroPatParser;
#[allow(unused_imports)]
pub use names::NamesParser;
#[allow(unused_imports)]
pub use stat::StatParser;

/// Parser error type.
#[derive(Debug)]
pub enum ParseError {
    SyntaxError {
        file: String,
        span: Span,
        msg: String,
        tip: String,
    },
    UnexpectedEof {
        file: String,
        pos: Pos,
    },
}

impl ParseError {
    pub fn syntax(
        token: &Token,
        file: &str,
        msg: impl Into<String>,
        tip: impl Into<String>,
    ) -> Self {
        ParseError::SyntaxError {
            file: file.to_string(),
            span: Span::from_token_pos(token.pos),
            msg: msg.into(),
            tip: tip.into(),
        }
    }

    pub fn unexpected_eof(file: impl Into<String>, pos: Pos) -> Self {
        ParseError::UnexpectedEof {
            file: file.into(),
            pos,
        }
    }

    pub fn from_lexer(file: impl Into<String>, pos: Pos, msg: impl Into<String>) -> Self {
        ParseError::SyntaxError {
            file: file.into(),
            span: Span::at(pos),
            msg: msg.into(),
            tip: "詞法錯誤".into(),
        }
    }

    /// Render a full Rust-style diagnostic report for this error.
    pub fn report(&self, source: &str, colors: ColorChoice) -> String {
        Diagnostic::from_parse_error(self).render(source, colors)
    }
}

impl std::fmt::Display for ParseError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ParseError::SyntaxError { file, span, msg, .. } => {
                write!(
                    f,
                    "error: {} at {}:{}:{}",
                    msg, file, span.start.line, span.start.offset
                )
            }
            ParseError::UnexpectedEof { file, pos } => {
                write!(f, "error: unexpected end of input at {}:{}:{}", file, pos.line, pos.offset)
            }
        }
    }
}

impl std::error::Error for ParseError {}

/// Shared token-stream state used by all parsers.
///
/// Equivalent to Python's `ParserFn`, but backed by a token vector and an index
/// rather than an iterator + lookahead buffer. This makes backtracking and
/// lookahead trivial and lets us use Rust's `match` extensively on the current
/// token.
pub struct Parser<'a> {
    tokens: &'a [Token],
    index: usize,
    last_token: Option<Token>,
    file_path: &'a str,
    pub macro_registry: Rc<RefCell<MacroRegistry>>,
}

impl<'a> Parser<'a> {
    /// Create a new parser from a token slice.
    pub fn new(tokens: &'a [Token], file_path: &'a str) -> Self {
        Self {
            tokens,
            index: 0,
            last_token: None,
            file_path,
            macro_registry: Rc::new(RefCell::new(MacroRegistry::new())),
        }
    }

    /// Create a parser that shares an existing macro registry.
    pub fn new_with_registry(
        tokens: &'a [Token],
        file_path: &'a str,
        macro_registry: Rc<RefCell<MacroRegistry>>,
    ) -> Self {
        Self {
            tokens,
            index: 0,
            last_token: None,
            file_path,
            macro_registry,
        }
    }

    /// Position of the next token to be consumed.
    pub fn cur_pos(&self) -> Pos {
        self.peek_token().map(|t| t.pos).unwrap_or_else(|| {
            self.last_token
                .as_ref()
                .map(|t| t.pos)
                .unwrap_or_else(|| Pos::simple(0, 0))
        })
    }

    /// The source file path used for diagnostics.
    pub fn file_path(&self) -> &'a str {
        self.file_path
    }

    /// Position of the previously consumed token (used for end-of-AST spans).
    pub fn last_pos(&self) -> Pos {
        self.last_token
            .as_ref()
            .map(|t| t.pos)
            .unwrap_or_else(|| self.cur_pos())
    }

    /// Look at the next token without consuming it.
    pub fn peek_token(&self) -> Option<&Token> {
        self.tokens.get(self.index)
    }

    /// Peek the token type of the next token, if any.
    pub fn peek_type(&self) -> Option<TokenType> {
        self.peek_token().map(|t| t.typ)
    }

    /// Peek the string value of the next token, if any.
    pub fn peek_value(&self) -> Option<&str> {
        self.peek_token().map(|t| t.value.as_str())
    }

    /// Check whether we are at EOF.
    pub fn is_eof(&self) -> bool {
        matches!(self.peek_type(), Some(TokenType::EOF) | None)
    }

    /// Consume and return the next token.
    pub fn next_token(&mut self) -> Option<Token> {
        let tk = self.tokens.get(self.index)?;
        self.index += 1;
        self.last_token = Some(tk.clone());
        Some(tk.clone())
    }

    /// Skip one token without returning it.
    pub fn skip(&mut self) {
        let _ = self.next_token();
    }

    /// Match the next token's type without consuming it.
    pub fn match_kind(&self, kind: TokenType) -> bool {
        self.peek_type() == Some(kind)
    }

    /// Match the next token's value without consuming it.
    pub fn match_value(&self, value: &str) -> bool {
        self.peek_value() == Some(value)
    }

    /// Match any of the provided token types.
    pub fn match_any_kind(&self, kinds: &[TokenType]) -> bool {
        if let Some(kind) = self.peek_type() {
            kinds.contains(&kind)
        } else {
            false
        }
    }

    /// Match any of the provided token values.
    pub fn match_any_value(&self, values: &[&str]) -> bool {
        if let Some(value) = self.peek_value() {
            values.contains(&value)
        } else {
            false
        }
    }

    /// Require the next token to have the given type and consume it.
    pub fn eat_kind(&mut self, kind: TokenType) -> Result<Token, ParseError> {
        let tk = self.peek_token().ok_or_else(|| {
            ParseError::unexpected_eof(self.file_path, self.cur_pos())
        })?.clone();
        if tk.typ != kind {
            return Err(ParseError::syntax(
                &tk,
                self.file_path,
                format!("睇唔明嘅语法: `{}`", tk.value),
                format!("不妨嘗試下 `{}` 類型??", kind),
            ));
        }
        self.index += 1;
        self.last_token = Some(tk.clone());
        Ok(tk)
    }

    /// Require the next token to have the given value and consume it.
    pub fn eat_value(&mut self, value: &str) -> Result<Token, ParseError> {
        let tk = self.peek_token().ok_or_else(|| {
            ParseError::unexpected_eof(self.file_path, self.cur_pos())
        })?.clone();
        if tk.value != value {
            return Err(ParseError::syntax(
                &tk,
                self.file_path,
                format!("睇唔明嘅语法: `{}`", tk.value),
                format!("係咪 `{}` ??", value),
            ));
        }
        self.index += 1;
        self.last_token = Some(tk.clone());
        Ok(tk)
    }

    /// Require the next token to have one of the given values and consume it.
    pub fn eat_any_value(&mut self, values: &[&str]) -> Result<Token, ParseError> {
        let tk = self.peek_token().ok_or_else(|| {
            ParseError::unexpected_eof(self.file_path, self.cur_pos())
        })?.clone();
        if !values.contains(&tk.value.as_str()) {
            return Err(ParseError::syntax(
                &tk,
                self.file_path,
                format!("睇唔明嘅语法: `{}`", tk.value),
                format!("係咪 `{}` ??", values.join(", ")),
            ));
        }
        self.index += 1;
        self.last_token = Some(tk.clone());
        Ok(tk)
    }

    /// Consume a sequence of tokens by value.
    pub fn eat_values(&mut self, values: &[&str]) -> Result<(), ParseError> {
        for v in values {
            self.eat_value(v)?;
        }
        Ok(())
    }

    /// Consume tokens while `parse_item` succeeds and `stop` is false.
    pub fn many<T>(
        &mut self,
        mut parse_item: impl FnMut(&mut Self) -> Result<T, ParseError>,
        mut stop: impl FnMut(&Self) -> bool,
    ) -> Result<Vec<T>, ParseError> {
        let mut out = Vec::new();
        while !stop(self) {
            out.push(parse_item(self)?);
        }
        Ok(out)
    }

    /// Consume one or more items.
    pub fn one_plus<T>(
        &mut self,
        mut parse_item: impl FnMut(&mut Self) -> Result<T, ParseError>,
        stop: impl FnMut(&Self) -> bool,
    ) -> Result<Vec<T>, ParseError> {
        let mut out = vec![parse_item(self)?];
        out.extend(self.many(parse_item, stop)?);
        Ok(out)
    }
}

/// Attach source-position span to an AST expression.
///
/// Equivalent to Python's `@pos_tracker` decorator.
pub fn with_pos<F>(parser: &mut Parser, mut f: F) -> Result<Exp, ParseError>
where
    F: FnMut(&mut Parser) -> Result<Exp, ParseError>,
{
    let start_pos = parser.cur_pos();
    let mut exp = f(parser)?;
    let end_pos = parser.last_pos();
    exp.set_pos(Some(start_pos.span_to(end_pos)));
    Ok(exp)
}

/// Attach source-position span to an AST statement.
pub fn with_pos_stat<F>(parser: &mut Parser, mut f: F) -> Result<Stat, ParseError>
where
    F: FnMut(&mut Parser) -> Result<Stat, ParseError>,
{
    let start_pos = parser.cur_pos();
    let mut stat = f(parser)?;
    let end_pos = parser.last_pos();
    stat.set_pos(Some(start_pos.span_to(end_pos)));
    Ok(stat)
}
