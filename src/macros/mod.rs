//! Macro expansion
//!
//! Provides pattern matching, meta-variable capture, and body substitution for
//! Cantonese macros.

use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;

use crate::ast::{
    Exp, IdExp, MacroMetaRepExpInBlock, MacroMetaRepExpInPat, MacroPatItem, MetaIdExp, TokenTree,
    TokenTreeChild,
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

    pub fn matches_tree(&mut self, pattern: &[MacroPatItem], children: &[TokenTreeChild]) -> bool {
        self.match_items(pattern, 0, children, 0, true)
    }

    fn match_items(
        &mut self,
        pattern: &[MacroPatItem],
        pat_idx: usize,
        children: &[TokenTreeChild],
        child_idx: usize,
        require_full: bool,
    ) -> bool {
        if pat_idx >= pattern.len() {
            return if require_full {
                child_idx >= children.len()
            } else {
                true
            };
        }
        if child_idx >= children.len() {
            return false;
        }

        match &pattern[pat_idx] {
            MacroPatItem::Token(t) => match &children[child_idx] {
                TokenTreeChild::Token(ct) => {
                    if t.value == ct.value {
                        self.match_items(
                            pattern,
                            pat_idx + 1,
                            children,
                            child_idx + 1,
                            require_full,
                        )
                    } else {
                        false
                    }
                }
                _ => false,
            },
            MacroPatItem::MetaVar(var) => {
                let name = match &var.id {
                    Exp::Id(IdExp { name, .. }) => name.clone(),
                    _ => return false,
                };
                let spec = match FragSpec::from_exp(&var.frag_spec) {
                    Ok(s) => s,
                    Err(_) => return false,
                };
                self.match_meta_var(
                    &name,
                    &spec,
                    pattern,
                    pat_idx + 1,
                    children,
                    child_idx,
                    require_full,
                )
            }
            MacroPatItem::Rep(rep) => {
                self.match_repetition(rep, pattern, pat_idx + 1, children, child_idx, require_full)
            }
            MacroPatItem::Tree(pat_tree) => match &children[child_idx] {
                TokenTreeChild::Tree(child_tree) => {
                    if self.match_tokentree(pat_tree, child_tree) {
                        self.match_items(
                            pattern,
                            pat_idx + 1,
                            children,
                            child_idx + 1,
                            require_full,
                        )
                    } else {
                        false
                    }
                }
                _ => false,
            },
            MacroPatItem::MetaId(pat_id) => {
                // MetaId inside a pattern TokenTree captures all remaining
                // children as the value of this meta variable (like $:tt).
                let remaining = &children[child_idx..];
                if remaining.is_empty() {
                    return false;
                }
                let tokens: Vec<Token> = remaining
                    .iter()
                    .flat_map(|c| match c {
                        TokenTreeChild::Token(t) => vec![t.clone()],
                        TokenTreeChild::Tree(t) => token_tree_to_tokens(t),
                        _ => vec![],
                    })
                    .collect();
                self.state.update(pat_id.name.clone(), tokens);
                // MetaId is the last item in the pattern tree, so we're done.
                self.match_items(pattern, pat_idx + 1, children, children.len(), require_full)
            }
        }
    }

    fn match_meta_var(
        &mut self,
        name: &str,
        spec: &FragSpec,
        pattern: &[MacroPatItem],
        pat_idx: usize,
        children: &[TokenTreeChild],
        child_idx: usize,
        require_full: bool,
    ) -> bool {
        match spec {
            FragSpec::Ident => {
                if let TokenTreeChild::Token(t) = &children[child_idx] {
                    if t.typ == TokenType::Identifier {
                        self.state.update(name.to_string(), vec![t.clone()]);
                        return self.match_items(
                            pattern,
                            pat_idx,
                            children,
                            child_idx + 1,
                            require_full,
                        );
                    }
                }
                false
            }
            FragSpec::Str => {
                if let TokenTreeChild::Token(t) = &children[child_idx] {
                    if t.typ == TokenType::String {
                        self.state.update(name.to_string(), vec![t.clone()]);
                        return self.match_items(
                            pattern,
                            pat_idx,
                            children,
                            child_idx + 1,
                            require_full,
                        );
                    }
                }
                false
            }
            FragSpec::Literal => {
                if let TokenTreeChild::Token(t) = &children[child_idx] {
                    if t.typ == TokenType::String || t.typ == TokenType::Num {
                        self.state.update(name.to_string(), vec![t.clone()]);
                        return self.match_items(
                            pattern,
                            pat_idx,
                            children,
                            child_idx + 1,
                            require_full,
                        );
                    }
                }
                false
            }
            FragSpec::Expr => {
                let (consumed, tokens) = self.gather_expr(children, child_idx);
                if !tokens.is_empty() && try_parse_expr(&tokens, self.registry.clone()) {
                    self.state.update(name.to_string(), tokens);
                    return self.match_items(
                        pattern,
                        pat_idx,
                        children,
                        child_idx + consumed,
                        require_full,
                    );
                }
                false
            }
            FragSpec::Stmt => {
                let (consumed, tokens) = self.gather_stmt(children, child_idx);
                if !tokens.is_empty() && try_parse_stat(&tokens, self.registry.clone()) {
                    self.state.update(name.to_string(), tokens);
                    return self.match_items(
                        pattern,
                        pat_idx,
                        children,
                        child_idx + consumed,
                        require_full,
                    );
                }
                false
            }
            FragSpec::Tt => {
                if let TokenTreeChild::Tree(t) = &children[child_idx] {
                    let tokens = token_tree_to_tokens(t);
                    self.state.update(name.to_string(), tokens);
                    return self.match_items(
                        pattern,
                        pat_idx,
                        children,
                        child_idx + 1,
                        require_full,
                    );
                }
                false
            }
            FragSpec::Block => {
                if let TokenTreeChild::Tree(t) = &children[child_idx] {
                    if t.open_ch.value == "{" && t.close_ch.value == "}" {
                        let tokens = token_tree_to_tokens(t);
                        self.state.update(name.to_string(), tokens);
                        return self.match_items(
                            pattern,
                            pat_idx,
                            children,
                            child_idx + 1,
                            require_full,
                        );
                    }
                }
                false
            }
        }
    }

    fn gather_expr(&self, children: &[TokenTreeChild], start: usize) -> (usize, Vec<Token>) {
        let mut tokens = Vec::new();
        let mut i = start;
        let mut depth = 0;
        let mut last_valid_tokens: Vec<Token> = Vec::new();
        let mut last_valid_i = start;

        while i < children.len() {
            match &children[i] {
                TokenTreeChild::Token(t) => {
                    if depth == 0
                        && (t.value == "," || t.value == ";" || t.value == "=>" || t.value == "}")
                    {
                        break;
                    }
                    if t.typ == TokenType::SepLParen
                        || t.typ == TokenType::SepLBrack
                        || t.typ == TokenType::SepLCurly
                    {
                        depth += 1;
                    } else if t.typ == TokenType::SepRParen
                        || t.typ == TokenType::SepRBrack
                        || t.typ == TokenType::SepRCurly
                    {
                        depth -= 1;
                    }
                    tokens.push(t.clone());
                    i += 1;
                }
                TokenTreeChild::Tree(t) => {
                    tokens.extend(token_tree_to_tokens(t));
                    i += 1;
                }
                _ => break,
            }

            if depth == 0 && !tokens.is_empty() && try_parse_expr(&tokens, self.registry.clone()) {
                last_valid_tokens = tokens.clone();
                last_valid_i = i;
            }
        }

        (last_valid_i - start, last_valid_tokens)
    }

    fn gather_stmt(&self, children: &[TokenTreeChild], start: usize) -> (usize, Vec<Token>) {
        self.gather_expr(children, start)
    }

    fn match_tokentree(&mut self, pat: &TokenTree, child: &TokenTree) -> bool {
        if pat.open_ch.value != child.open_ch.value || pat.close_ch.value != child.close_ch.value {
            return false;
        }
        self.match_items(&pat_to_pat_items(&pat.child), 0, &child.child, 0, true)
    }

    fn match_repetition(
        &mut self,
        rep: &MacroMetaRepExpInPat,
        pattern: &[MacroPatItem],
        pat_idx: usize,
        children: &[TokenTreeChild],
        child_idx: usize,
        require_full: bool,
    ) -> bool {
        let sep_value = rep.rep_sep.as_ref().map(|t| t.value.clone());
        let op = rep.rep_op.as_str();

        let mut times = 0;
        let mut current_child = child_idx;

        loop {
            if current_child >= children.len() {
                break;
            }

            let saved = self.state.clone();
            if self.match_items(&rep.token_trees, 0, children, current_child, false) {
                let consumed = self.count_consumed(&rep.token_trees, children, current_child);
                if consumed == 0 {
                    self.state = saved;
                    break;
                }
                times += 1;
                current_child += consumed;

                if let Some(sep) = &sep_value {
                    if current_child < children.len() {
                        if let TokenTreeChild::Token(t) = &children[current_child] {
                            if t.value == *sep {
                                current_child += 1;
                                continue;
                            }
                        }
                    }
                }
                continue;
            }
            self.state = saved;
            break;
        }

        match op {
            "+" if times >= 1 => {
                self.match_items(pattern, pat_idx, children, current_child, require_full)
            }
            "*" => self.match_items(pattern, pat_idx, children, current_child, require_full),
            "?" if times <= 1 => {
                self.match_items(pattern, pat_idx, children, current_child, require_full)
            }
            _ => false,
        }
    }

    fn count_consumed(
        &self,
        pattern: &[MacroPatItem],
        children: &[TokenTreeChild],
        start: usize,
    ) -> usize {
        let mut child_idx = start;
        for pat in pattern {
            if child_idx >= children.len() {
                return 0;
            }
            match pat {
                MacroPatItem::Token(_) => {
                    child_idx += 1;
                }
                MacroPatItem::MetaVar(var) => {
                    let spec = match FragSpec::from_exp(&var.frag_spec) {
                        Ok(s) => s,
                        Err(_) => return 0,
                    };
                    match spec {
                        FragSpec::Ident
                        | FragSpec::Str
                        | FragSpec::Literal
                        | FragSpec::Tt
                        | FragSpec::Block => {
                            child_idx += 1;
                        }
                        FragSpec::Expr | FragSpec::Stmt => {
                            let (consumed, _) = self.gather_expr(children, child_idx);
                            child_idx += consumed;
                        }
                    }
                }
                MacroPatItem::Rep(rep) => {
                    let sep_value = rep.rep_sep.as_ref().map(|t| t.value.clone());
                    loop {
                        if child_idx >= children.len() {
                            break;
                        }
                        let inner_consumed =
                            self.count_consumed(&rep.token_trees, children, child_idx);
                        if inner_consumed == 0 {
                            break;
                        }
                        child_idx += inner_consumed;
                        if let Some(sep) = &sep_value {
                            if child_idx < children.len() {
                                if let TokenTreeChild::Token(t) = &children[child_idx] {
                                    if t.value == *sep {
                                        child_idx += 1;
                                        continue;
                                    }
                                }
                            }
                        }
                        break;
                    }
                }
                MacroPatItem::Tree(_) => {
                    child_idx += 1;
                }
                MacroPatItem::MetaId(_) => {
                    // MetaId captures all remaining children
                    child_idx = children.len();
                }
            }
        }
        child_idx - start
    }
}

fn pat_to_pat_items(children: &[TokenTreeChild]) -> Vec<MacroPatItem> {
    children
        .iter()
        .map(|c| match c {
            TokenTreeChild::Token(t) => MacroPatItem::Token(t.clone()),
            TokenTreeChild::MetaId(id) => MacroPatItem::MetaId(id.clone()),
            TokenTreeChild::Tree(tree) => MacroPatItem::Tree(tree.clone()),
            TokenTreeChild::PatRep(rep) => MacroPatItem::Rep(rep.clone()),
            _ => MacroPatItem::Token(Token::new(Pos::simple(0, 0), TokenType::EOF, String::new())),
        })
        .collect()
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
    pub fn try_expand_tree(
        &self,
        children: &[TokenTreeChild],
        registry: Rc<RefCell<MacroRegistry>>,
    ) -> Result<(MatchState, TokenTree), ParseError> {
        for (pat, body) in self.patterns.iter().zip(self.bodies.iter()) {
            let state = MatchState::new();
            let mut ruler = PatRuler::with_state(state, registry.clone());
            if ruler.matches_tree(pat, children) {
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

    pub fn get_names(&self) -> Vec<String> {
        self.macros.keys().cloned().collect()
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
                    "係咪Macro喺其它文件? 咁就試下 用 `@用下(...)` import 啦!",
                )
            })?;
        let (mut state, body) =
            macro_def.try_expand_tree(&tokentrees.child, parser.macro_registry.clone())?;
        body.substitute(&mut state)
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
            TokenTreeChild::MetaId(MetaIdExp { name, .. }) => {
                tokens.push(Token::new(
                    Pos::simple(0, 0),
                    TokenType::Keyword,
                    "$".to_string(),
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
            TokenTreeChild::MetaId(MetaIdExp { name, .. }) => vec![
                Token::new(Pos::simple(0, 0), TokenType::Keyword, "$".to_string()),
                Token::new(Pos::simple(0, 0), TokenType::Identifier, name.clone()),
            ],
            _ => Vec::new(),
        })
        .collect()
}

pub trait MacroSubstitute {
    fn substitute(&self, state: &mut MatchState) -> Result<Vec<Token>, ParseError>;
}

impl MacroSubstitute for TokenTree {
    fn substitute(&self, state: &mut MatchState) -> Result<Vec<Token>, ParseError> {
        let mut out = Vec::new();
        for child in &self.child {
            out.extend(substitute_child(child, state)?);
        }
        Ok(out)
    }
}

fn substitute_child(
    child: &TokenTreeChild,
    state: &mut MatchState,
) -> Result<Vec<Token>, ParseError> {
    match child {
        TokenTreeChild::Token(t) => Ok(vec![t.clone()]),
        TokenTreeChild::MetaId(MetaIdExp { name, .. }) => {
            let mv = state.get_mut(name).ok_or_else(|| {
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
    state: &mut MatchState,
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
            Exp::Id(IdExp { name, .. }) => Some(name.as_str()),
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
                    if let Some(Exp::Id(IdExp { name, .. })) = &rep.rep_sep {
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
            TokenTreeChild::MetaId(MetaIdExp { name, .. }) => {
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
