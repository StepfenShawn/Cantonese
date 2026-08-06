//! Macro expansion (translated from `can_source/can_macros`).
//!
//! Provides pattern matching, meta-variable capture, and body substitution for
//! Cantonese macros.

use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;

use crate::ast::{
    Exp, IdExp, MacroMetaId, MacroMetaRepExpInBlock, MacroMetaRepExpInPat, MacroPatItem, MetaIdExp,
    TokenTree, TokenTreeChild,
};
use crate::lexer::token::{Pos, Token, TokenType};
use crate::parser::exp::ExpParser;
use crate::parser::stat::StatParser;
use crate::parser::{ParseError, Parser};

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
            Exp::Id(IdExp { name }) => Self::from_name(name),
            _ => Err(ParseError::syntax(
                &Token::new(Pos::simple(0, 0), TokenType::Identifier, "".to_string()),
                "<macro>",
                "Fragment specifier 必須係 identifier",
                "例如 `@x: expr`",
            )),
        }
    }
}

// =============================================================================
// Regex-like pattern AST
// =============================================================================

#[derive(Debug, Clone)]
pub enum Regex {
    Empty,
    Atom(Token),
    Var { name: String, spec: FragSpec },
    Concat(Box<Regex>, Box<Regex>),
    Star(Box<Regex>),
    Optional(Box<Regex>),
}

pub fn build_regex(items: &[MacroPatItem]) -> Result<Regex, ParseError> {
    if items.is_empty() {
        return Ok(Regex::Empty);
    }
    let (first, rest) = items.split_first().unwrap();
    let node = match first {
        MacroPatItem::Token(t) => Regex::Atom(t.clone()),
        MacroPatItem::MetaVar(MacroMetaId { id, frag_spec }) => {
            let name = match id {
                Exp::Id(IdExp { name }) => name.clone(),
                _ => String::new(),
            };
            Regex::Var {
                name,
                spec: FragSpec::from_exp(frag_spec)?,
            }
        }
        MacroPatItem::Rep(rep) => build_rep_regex(rep)?,
        _ => {
            return Err(ParseError::syntax(
                &Token::new(Pos::simple(0, 0), TokenType::Identifier, "".to_string()),
                "<macro>",
                "Macro pattern 入面唔應該出現 Tree/MetaId",
                "檢查 macro 模式語法",
            ));
        }
    };
    Ok(Regex::Concat(Box::new(node), Box::new(build_regex(rest)?)))
}

fn build_rep_regex(rep: &MacroMetaRepExpInPat) -> Result<Regex, ParseError> {
    let inner = build_regex(&rep.token_trees)?;
    let sep = rep.rep_sep.as_ref().cloned();
    match rep.rep_op.as_str() {
        "*" => {
            let with_sep = if let Some(s) = sep {
                Regex::Concat(Box::new(inner), Box::new(Regex::Atom(s)))
            } else {
                inner
            };
            Ok(Regex::Star(Box::new(with_sep)))
        }
        "+" => {
            let unit = if let Some(s) = sep {
                Regex::Concat(Box::new(inner.clone()), Box::new(Regex::Atom(s)))
            } else {
                inner.clone()
            };
            Ok(Regex::Concat(
                Box::new(unit.clone()),
                Box::new(Regex::Star(Box::new(unit))),
            ))
        }
        "?" => {
            let optional_sep = if let Some(s) = sep {
                Regex::Optional(Box::new(Regex::Atom(s)))
            } else {
                Regex::Empty
            };
            Ok(Regex::Concat(
                Box::new(Regex::Optional(Box::new(inner))),
                Box::new(optional_sep),
            ))
        }
        _ => Err(ParseError::syntax(
            &Token::new(Pos::simple(0, 0), TokenType::Identifier, rep.rep_op.clone()),
            "<macro>",
            format!("唔識嘅 repetition operator: `{}`", rep.rep_op),
            "可用: *, +, ?",
        )),
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
    vars: HashMap<String, MetaVar>,
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

// =============================================================================
// Pattern matcher
// =============================================================================

#[derive(Debug, Clone)]
pub struct PatRuler {
    state: MatchState,
    registry: Rc<RefCell<MacroRegistry>>,
}

impl PatRuler {
    pub fn new(registry: Rc<RefCell<MacroRegistry>>) -> Self {
        Self {
            state: MatchState::new(),
            registry,
        }
    }

    pub fn with_state(state: MatchState, registry: Rc<RefCell<MacroRegistry>>) -> Self {
        Self { state, registry }
    }

    pub fn into_state(self) -> MatchState {
        self.state
    }

    pub fn matches(&mut self, regex: &Regex, tokens: &[Token]) -> bool {
        match regex {
            Regex::Empty => tokens.is_empty(),
            Regex::Atom(t) => tokens.len() == 1 && tokens[0].value == t.value,
            Regex::Var { name, spec } => self.match_var(name, spec, tokens),
            Regex::Optional(r) => self.matches(r, tokens) || tokens.is_empty(),
            Regex::Concat(l, r) => {
                for (prefix, suffix) in splits(tokens) {
                    let saved = self.state.clone();
                    if self.matches(l, prefix) && self.matches(r, suffix) {
                        if let Regex::Var { name, .. } = l.as_ref() {
                            self.state.update(name.clone(), prefix.to_vec());
                        }
                        if let Regex::Var { name, .. } = r.as_ref() {
                            self.state.update(name.clone(), suffix.to_vec());
                        }
                        return true;
                    }
                    self.state = saved;
                }
                false
            }
            Regex::Star(inner) => {
                if tokens.is_empty() {
                    return true;
                }
                for (prefix, suffix) in prefix_splits(tokens) {
                    let saved = self.state.clone();
                    if self.matches(inner, prefix) && self.matches(regex, suffix) {
                        return true;
                    }
                    self.state = saved;
                }
                false
            }
        }
    }

    fn match_var(&mut self, _name: &str, spec: &FragSpec, tokens: &[Token]) -> bool {
        match spec {
            FragSpec::Ident => tokens.len() == 1 && tokens[0].typ == TokenType::Identifier,
            FragSpec::Str => tokens.len() == 1 && tokens[0].typ == TokenType::String,
            FragSpec::Literal => {
                tokens.len() == 1
                    && (tokens[0].typ == TokenType::String || tokens[0].typ == TokenType::Num)
            }
            FragSpec::Expr => try_parse_expr(tokens, self.registry.clone()),
            FragSpec::Stmt => try_parse_stat(tokens, self.registry.clone()),
            FragSpec::Tt | FragSpec::Block => false,
        }
    }
}

fn splits<T>(xs: &[T]) -> Vec<(&[T], &[T])> {
    let mut res = Vec::with_capacity(xs.len() + 1);
    for i in 0..=xs.len() {
        res.push((&xs[..i], &xs[i..]));
    }
    res
}

fn prefix_splits<T>(xs: &[T]) -> Vec<(&[T], &[T])> {
    let mut res = Vec::with_capacity(xs.len());
    for i in 1..=xs.len() {
        res.push((&xs[..i], &xs[i..]));
    }
    res
}

fn try_parse_expr(tokens: &[Token], registry: Rc<RefCell<MacroRegistry>>) -> bool {
    let mut parser = Parser::new_with_registry(tokens, "<macro>", registry);
    ExpParser::parse_exp(&mut parser).is_ok() && parser.is_eof()
}

fn try_parse_stat(tokens: &[Token], registry: Rc<RefCell<MacroRegistry>>) -> bool {
    let mut parser = Parser::new_with_registry(tokens, "<macro>", registry);
    StatParser::parse(&mut parser).is_ok() && parser.is_eof()
}

// =============================================================================
// Macro registry
// =============================================================================

#[derive(Debug, Clone)]
pub struct Macro {
    pub name: String,
    pub patterns: Vec<Vec<MacroPatItem>>,
    pub bodies: Vec<TokenTree>,
}

impl Macro {
    pub fn try_expand(
        &self,
        tokens: &[Token],
        registry: Rc<RefCell<MacroRegistry>>,
    ) -> Result<(MatchState, TokenTree), ParseError> {
        for (pat, body) in self.patterns.iter().zip(self.bodies.iter()) {
            let regex = build_regex(pat)?;
            let state = MatchState::new();
            let mut ruler = PatRuler::with_state(state, registry.clone());
            if ruler.matches(&regex, tokens) {
                return Ok((ruler.into_state(), body.clone()));
            }
        }
        Err(ParseError::syntax(
            &Token::new(Pos::simple(0, 0), TokenType::Identifier, self.name.clone()),
            "<macro>",
            format!("展開唔到Macro: `{}`", self.name),
            "檢查 macro 調用同模式係咪匹配",
        ))
    }
}

#[derive(Debug, Clone, Default)]
pub struct MacroRegistry {
    macros: HashMap<String, Macro>,
}

impl MacroRegistry {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn register(&mut self, name: String, macro_def: Macro) {
        self.macros.insert(name, macro_def);
    }

    pub fn get(&self, name: &str) -> Option<&Macro> {
        self.macros.get(name)
    }
}

// =============================================================================
// Macro expansion driver
// =============================================================================

pub struct MacroExpander;

impl MacroExpander {
    pub fn expand(
        parser: &mut Parser,
        name: &str,
        tokentrees: TokenTree,
    ) -> Result<Vec<Token>, ParseError> {
        let macro_def = parser
            .macro_registry
            .borrow()
            .get(name)
            .cloned()
            .ok_or_else(|| {
                ParseError::syntax(
                    parser.peek_token().unwrap_or(&Token::new(
                        Pos::simple(0, 0),
                        TokenType::EOF,
                        "EOF".into(),
                    )),
                    parser.file_path(),
                    format!("揾唔到你嘅Macro: `{}`", name),
                    "係咪Macro喺其它文件? 咁就試下 import 啦!",
                )
            })?;
        let input = token_tree_inner_tokens(&tokentrees);
        let (state, body) = macro_def.try_expand(&input, parser.macro_registry.clone())?;
        body.substitute(&state)
    }
}

// =============================================================================
// Token-tree helpers and body substitution
// =============================================================================

pub fn token_tree_to_tokens(tree: &TokenTree) -> Vec<Token> {
    let mut tokens = vec![tree.open_ch.clone()];
    for child in &tree.child {
        match child {
            TokenTreeChild::Token(t) => tokens.push(t.clone()),
            TokenTreeChild::Tree(t) => tokens.extend(token_tree_to_tokens(t)),
            TokenTreeChild::MetaId(MetaIdExp { name }) => {
                tokens.push(Token::new(
                    Pos::simple(0, 0),
                    TokenType::Keyword,
                    "@".to_string(),
                ));
                tokens.push(Token::new(
                    Pos::simple(0, 0),
                    TokenType::Identifier,
                    name.clone(),
                ));
            }
            _ => {}
        }
    }
    tokens.push(tree.close_ch.clone());
    tokens
}

pub fn token_tree_inner_tokens(tree: &TokenTree) -> Vec<Token> {
    tree.child
        .iter()
        .flat_map(|child| match child {
            TokenTreeChild::Token(t) => vec![t.clone()],
            TokenTreeChild::Tree(t) => token_tree_to_tokens(t),
            TokenTreeChild::MetaId(MetaIdExp { name }) => vec![
                Token::new(Pos::simple(0, 0), TokenType::Keyword, "@".to_string()),
                Token::new(Pos::simple(0, 0), TokenType::Identifier, name.clone()),
            ],
            _ => Vec::new(),
        })
        .collect()
}

pub trait MacroSubstitute {
    fn substitute(&self, state: &MatchState) -> Result<Vec<Token>, ParseError>;
}

impl MacroSubstitute for TokenTree {
    fn substitute(&self, state: &MatchState) -> Result<Vec<Token>, ParseError> {
        let mut out = Vec::new();
        for child in &self.child {
            out.extend(substitute_child(child, state)?);
        }
        Ok(out)
    }
}

fn substitute_child(child: &TokenTreeChild, state: &MatchState) -> Result<Vec<Token>, ParseError> {
    match child {
        TokenTreeChild::Token(t) => Ok(vec![t.clone()]),
        TokenTreeChild::MetaId(MetaIdExp { name }) => {
            let mut mv = state.get(name).cloned().ok_or_else(|| {
                ParseError::syntax(
                    &Token::new(Pos::simple(0, 0), TokenType::Identifier, name.clone()),
                    "<macro>",
                    format!("Meta variable `{}` 未匹配", name),
                    "檢查 macro 模式",
                )
            })?;
            Ok(mv.next_capture())
        }
        TokenTreeChild::BlockRep(rep) => yield_repetition(rep, state),
        TokenTreeChild::Tree(tree) => {
            let mut out = vec![tree.open_ch.clone()];
            for c in &tree.child {
                out.extend(substitute_child(c, state)?);
            }
            out.push(tree.close_ch.clone());
            Ok(out)
        }
        _ => Err(ParseError::syntax(
            &Token::new(Pos::simple(0, 0), TokenType::Identifier, "".to_string()),
            "<macro>",
            "Macro body 入面出現唔支援嘅節點",
            "檢查 macro 主體語法",
        )),
    }
}

fn yield_repetition(
    rep: &MacroMetaRepExpInBlock,
    state: &MatchState,
) -> Result<Vec<Token>, ParseError> {
    let (ensure, times) = ensure_repetition(rep, state)?;
    if !ensure {
        return Err(ParseError::syntax(
            &Token::new(Pos::simple(0, 0), TokenType::Identifier, "".to_string()),
            "<macro>",
            "重複組入面嘅 meta 变量次數唔一致",
            "檢查 macro 模式同調用",
        ));
    }

    let op = rep
        .rep_op
        .as_ref()
        .and_then(|e| match e {
            Exp::Id(IdExp { name }) => Some(name.as_str()),
            _ => None,
        })
        .unwrap_or("+");

    match op {
        "+" | "*" => {
            if times == 0 {
                return Ok(Vec::new());
            }
            let mut out = Vec::new();
            for time in 0..times {
                out.extend(rep.token_trees.substitute(state)?);
                if time != times - 1 {
                    if let Some(Exp::Id(IdExp { name })) = &rep.rep_sep {
                        out.push(separator_token(name));
                    }
                }
            }
            Ok(out)
        }
        "?" => {
            if times == 0 {
                Ok(Vec::new())
            } else {
                rep.token_trees.substitute(state)
            }
        }
        _ => Err(ParseError::syntax(
            &Token::new(Pos::simple(0, 0), TokenType::Identifier, op.to_string()),
            "<macro>",
            format!("唔識嘅 repetition operator: `{}`", op),
            "可用: *, +, ?",
        )),
    }
}

fn ensure_repetition(
    rep: &MacroMetaRepExpInBlock,
    state: &MatchState,
) -> Result<(bool, usize), ParseError> {
    ensure_repetition_tree(&rep.token_trees, state)
}

fn ensure_repetition_tree(
    tree: &TokenTree,
    state: &MatchState,
) -> Result<(bool, usize), ParseError> {
    let mut ensure = false;
    let mut times = 0;
    for child in &tree.child {
        let (child_ensure, child_times) = match child {
            TokenTreeChild::MetaId(MetaIdExp { name }) => {
                if let Some(mv) = state.get(name) {
                    (true, mv.repetition_times())
                } else {
                    (true, 0)
                }
            }
            TokenTreeChild::BlockRep(rep) => ensure_repetition(rep, state)?,
            TokenTreeChild::Tree(t) => ensure_repetition_tree(t, state)?,
            _ => (false, 0),
        };
        if child_ensure {
            if !ensure {
                ensure = true;
                times = child_times;
            } else {
                ensure = ensure && (times == child_times);
            }
        }
    }
    Ok((ensure, times))
}

fn separator_token(value: &str) -> Token {
    let typ = match value {
        "," => TokenType::SepComma,
        "|" => TokenType::Brack,
        "." => TokenType::SepDot,
        ";" => TokenType::Keyword,
        _ => TokenType::Keyword,
    };
    Token::new(Pos::simple(0, 0), typ, value.to_string())
}
