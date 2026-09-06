//! Pattern matching engine for macro invocations.

use std::cell::RefCell;
use std::rc::Rc;

use crate::ast::{Exp, IdExp, MacroMetaRepExpInPat, MacroPatItem, TokenTree, TokenTreeChild};
use crate::lexer::token::{Pos, Token, TokenType};
use crate::parser::Parser;
use crate::parser::exp::ExpParser;
use crate::parser::stat::StatParser;

use super::match_state::{FragSpec, MatchFailure, MatchState};
use super::{MacroRegistry, token_tree_to_tokens};

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

    fn remaining_patterns_are_optional(pattern: &[MacroPatItem], pat_idx: usize) -> bool {
        pattern[pat_idx..].iter().all(
            |item| matches!(item, MacroPatItem::Rep(rep) if rep.rep_op == "?" || rep.rep_op == "*"),
        )
    }

    pub fn matches_tree(
        &mut self,
        pattern: &[MacroPatItem],
        children: &[TokenTreeChild],
    ) -> Result<(), MatchFailure> {
        self.match_items(pattern, 0, children, 0, true)
    }

    fn match_items(
        &mut self,
        pattern: &[MacroPatItem],
        pat_idx: usize,
        children: &[TokenTreeChild],
        child_idx: usize,
        require_full: bool,
    ) -> Result<(), MatchFailure> {
        if pat_idx >= pattern.len() {
            return if require_full {
                if child_idx >= children.len() {
                    Ok(())
                } else {
                    Err(MatchFailure {
                        pat_idx,
                        child_idx,
                        reason: format!(
                            "Input 喺第 {} 個位置仲有剩餘 token，但 pattern 已經結束",
                            child_idx
                        ),
                    })
                }
            } else {
                Ok(())
            };
        }
        if child_idx >= children.len() {
            if Self::remaining_patterns_are_optional(pattern, pat_idx) {
                return Ok(());
            }
            return Err(MatchFailure {
                pat_idx,
                child_idx,
                reason: format!("Input 喺匹配第 {} 個 pattern 元素時已經用晒", pat_idx + 1),
            });
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
                        Err(MatchFailure {
                            pat_idx,
                            child_idx,
                            reason: format!("期望 `{}`，但係搵到 `{}`", t.value, ct.value),
                        })
                    }
                }
                _ => Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!("期望 token `{}`，但係搵到唔係 token", t.value),
                }),
            },
            MacroPatItem::MetaVar(var) => {
                let name = match &var.id {
                    Exp::Id(IdExp { name, .. }) => name.clone(),
                    _ => {
                        return Err(MatchFailure {
                            pat_idx,
                            child_idx,
                            reason: "Meta variable 名稱唔係 identifier".to_string(),
                        });
                    }
                };
                let spec = match FragSpec::from_exp(&var.frag_spec) {
                    Ok(s) => s,
                    Err(_) => {
                        return Err(MatchFailure {
                            pat_idx,
                            child_idx,
                            reason: format!("唔識嘅 fragment specifier: `${}`", name),
                        });
                    }
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
                    if let Err(e) = self.match_tokentree(pat_tree, child_tree) {
                        Err(MatchFailure {
                            pat_idx,
                            child_idx,
                            reason: format!("TokenTree 匹配失敗: {}", e.reason),
                        })
                    } else {
                        self.match_items(
                            pattern,
                            pat_idx + 1,
                            children,
                            child_idx + 1,
                            require_full,
                        )
                    }
                }
                _ => Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: "期望 TokenTree (括號 group)，但係搵到 token".to_string(),
                }),
            },
            MacroPatItem::MetaId(pat_id) => {
                let remaining = &children[child_idx..];
                if remaining.is_empty() {
                    return Err(MatchFailure {
                        pat_idx,
                        child_idx,
                        reason: format!(
                            "MetaId `{}` 需要至少一個 token，但係 input 已經用晒",
                            pat_id.name
                        ),
                    });
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
    ) -> Result<(), MatchFailure> {
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
                Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!(
                        "`${}: ident` 需要 identifier，但係喺位置 {} 搵唔到",
                        name, child_idx
                    ),
                })
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
                Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!(
                        "`${}: str` 需要 string literal，但係喺位置 {} 搵唔到",
                        name, child_idx
                    ),
                })
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
                Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!(
                        "`${}: lit` 需要 literal (string 或 number)，但係喺位置 {} 搵唔到",
                        name, child_idx
                    ),
                })
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
                Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!(
                        "`${}: expr` 需要有效嘅 expression，但係喺位置 {} 搵唔到",
                        name, child_idx
                    ),
                })
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
                Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!(
                        "`${}: stmt` 需要有效嘅 statement，但係喺位置 {} 搵唔到",
                        name, child_idx
                    ),
                })
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
                Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!(
                        "`${}: tt` 需要 token tree (括號 group)，但係喺位置 {} 搵唔到",
                        name, child_idx
                    ),
                })
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
                Err(MatchFailure {
                    pat_idx,
                    child_idx,
                    reason: format!(
                        "`${}: block` 需要 `{{}}` block，但係喺位置 {} 搵唔到",
                        name, child_idx
                    ),
                })
            }
        }
    }

    fn gather_expr(&self, children: &[TokenTreeChild], start: usize) -> (usize, Vec<Token>) {
        let mut tokens = Vec::new();
        let mut i = start;
        let mut last_valid_tokens: Vec<Token> = Vec::new();
        let mut last_valid_i = start;

        while i < children.len() {
            match &children[i] {
                TokenTreeChild::Token(t) => {
                    tokens.push(t.clone());
                    i += 1;
                }
                TokenTreeChild::Tree(t) => {
                    tokens.extend(token_tree_to_tokens(t));
                    i += 1;
                }
                _ => break,
            }

            if !tokens.is_empty() && try_parse_expr(&tokens, self.registry.clone()) {
                last_valid_tokens = tokens.clone();
                last_valid_i = i;
            }
        }

        (last_valid_i - start, last_valid_tokens)
    }

    fn gather_stmt(&self, children: &[TokenTreeChild], start: usize) -> (usize, Vec<Token>) {
        self.gather_expr(children, start)
    }

    fn match_tokentree(&mut self, pat: &TokenTree, child: &TokenTree) -> Result<(), MatchFailure> {
        if pat.open_ch.value != child.open_ch.value || pat.close_ch.value != child.close_ch.value {
            return Err(MatchFailure {
                pat_idx: 0,
                child_idx: 0,
                reason: format!(
                    "括號唔匹配: 期望 `{}...{}`，但係搵到 `{}...{}`",
                    pat.open_ch.value,
                    pat.close_ch.value,
                    child.open_ch.value,
                    child.close_ch.value
                ),
            });
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
    ) -> Result<(), MatchFailure> {
        let sep_value = rep.rep_sep.as_ref().map(|t| t.value.clone());
        let op = rep.rep_op.as_str();

        let mut times = 0;
        let mut current_child = child_idx;

        loop {
            if current_child >= children.len() {
                break;
            }

            let saved = self.state.clone();
            if self
                .match_items(&rep.token_trees, 0, children, current_child, false)
                .is_ok()
            {
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
            "+" => Err(MatchFailure {
                pat_idx,
                child_idx,
                reason: format!("重複模式 `+` 至少需要匹配一次，但係只匹配到 {} 次", times),
            }),
            "?" => Err(MatchFailure {
                pat_idx,
                child_idx,
                reason: format!("重複模式 `?` 最多匹配一次，但係匹配到 {} 次", times),
            }),
            _ => Err(MatchFailure {
                pat_idx,
                child_idx,
                reason: format!("唔識嘅 repetition operator: `{}`", op),
            }),
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
                    child_idx = children.len();
                }
            }
        }
        child_idx - start
    }
}

// =============================================================================
// Helper functions
// =============================================================================

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
