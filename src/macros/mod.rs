//! Macro expansion
//!
//! Provides pattern matching, meta-variable capture, and body substitution for
//! Cantonese macros.

use std::cell::RefCell;
use std::collections::HashMap;
use std::rc::Rc;

use crate::ast::{
    Exp, IdExp, MacroMetaRepExpInBlock, MacroPatItem, MetaIdExp, TokenTree, TokenTreeChild,
};
use crate::lexer::token::{Pos, Token, TokenType};
use crate::parser::{ParseError, Parser};

mod match_state;
mod pattern;

pub use match_state::{FragSpec, MatchFailure, MatchState, MetaVar};
pub use pattern::PatRuler;

// =============================================================================
// Macro definition and registry
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
        let mut failures: Vec<(usize, MatchFailure)> = vec![];
        for (i, (pat, body)) in self.patterns.iter().zip(self.bodies.iter()).enumerate() {
            let state = MatchState::new();
            let mut ruler = PatRuler::with_state(state, registry.clone());
            match ruler.matches_tree(pat, children) {
                Ok(()) => return Ok((ruler.into_state(), body.clone())),
                Err(failure) => failures.push((i, failure)),
            }
        }

        let notes: Vec<String> = failures
            .iter()
            .map(|(rule_idx, failure)| {
                format!(
                    "規則 {} 第 {} 個元素失敗: {}",
                    rule_idx + 1,
                    failure.pat_idx + 1,
                    failure.reason
                )
            })
            .collect();

        Err(ParseError::syntax_with_notes(
            &Token::new(Pos::simple(0, 0), TokenType::Identifier, self.name.clone()),
            "<macro>",
            format!("展開唔到Macro: `{}`", self.name),
            "檢查 macro 調用同模式係咪匹配",
            notes,
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
