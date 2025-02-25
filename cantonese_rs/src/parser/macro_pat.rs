//! Macro pattern parser (translated from can_parser/macro/pattern_parser.py).
//!
//! Parses the input-side of a macro rule, e.g. `$(@v: str, @v: str)+`.

use crate::ast::{
    MacroMetaId, MacroMetaRepExpInPat, MacroPatItem, MetaIdExp, TokenTree, TokenTreeChild,
};
use crate::lexer::token::TokenType;
use crate::parser::{ParseError, Parser};

pub struct MacroPatParser;

impl MacroPatParser {
    /// Parse a meta variable inside a macro pattern: `@v: str`.
    pub fn parse_meta_var(parser: &mut Parser) -> Result<MacroPatItem, ParseError> {
        parser.skip(); // '@'
        let id_tk = parser.eat_kind(TokenType::Identifier)?;
        parser.eat_value(":")?;
        let frag_spec_tk = parser.eat_kind(TokenType::Identifier)?;
        Ok(MacroPatItem::MetaVar(MacroMetaId {
            id: crate::ast::Exp::Id(crate::ast::IdExp {
                name: id_tk.value.clone(),
            }),
            frag_spec: crate::ast::Exp::Id(crate::ast::IdExp {
                name: frag_spec_tk.value.clone(),
            }),
        }))
    }

    /// Parse a repetition group inside a macro pattern: `$(...)+`.
    pub fn parse_meta_rep_exp(parser: &mut Parser) -> Result<MacroPatItem, ParseError> {
        parser.skip(); // '$'
        parser.eat_kind(TokenType::SepLParen)?;
        let mut token_trees = Vec::new();
        while !parser.match_kind(TokenType::SepRParen) {
            token_trees.push(Self::parse_macro_rule(parser)?);
        }
        parser.eat_kind(TokenType::SepRParen)?;
        Ok(MacroPatItem::Rep(Box::new(Self::finish_meta_exp(
            parser, token_trees,
        )?)))
    }

    pub fn parse_macro_rule(parser: &mut Parser) -> Result<MacroPatItem, ParseError> {
        match parser.peek_value() {
            Some("$") => Self::parse_meta_rep_exp(parser),
            Some("@") => Self::parse_meta_var(parser),
            _ => Ok(MacroPatItem::Token(parser.next_token().unwrap().clone())),
        }
    }

    fn finish_meta_exp(
        parser: &mut Parser,
        token_trees: Vec<MacroPatItem>,
    ) -> Result<MacroMetaRepExpInPat, ParseError> {
        let rep_sep = if parser.is_eof() {
            None
        } else {
            Some(parser.next_token().unwrap().clone())
        };
        let op_tk = parser.eat_any_value(&["*", "+", "?"])?;
        Ok(MacroMetaRepExpInPat {
            token_trees,
            rep_sep,
            rep_op: op_tk.value.clone(),
        })
    }

    /// Parse a balanced parenthesised token tree used as a macro pattern.
    pub fn parse_tokentrees(parser: &mut Parser) -> Result<TokenTree, ParseError> {
        let mut children: Vec<TokenTreeChild> = Vec::new();
        let open_ch = parser.eat_kind(TokenType::SepLParen)?.clone();
        while !parser.match_kind(TokenType::SepRParen) {
            match parser.peek_type() {
                Some(TokenType::SepLParen) => {
                    children.push(TokenTreeChild::Tree(Self::parse_tokentrees(parser)?));
                }
                Some(TokenType::Keyword) if parser.match_value("@") => {
                    parser.skip();
                    let meta_var = parser.eat_kind(TokenType::Identifier)?;
                    children.push(TokenTreeChild::MetaId(MetaIdExp {
                        name: meta_var.value.clone(),
                    }));
                }
                _ => {
                    children.push(TokenTreeChild::Token(parser.next_token().unwrap().clone()));
                }
            }
        }
        let close_ch = parser.eat_kind(TokenType::SepRParen)?.clone();
        Ok(TokenTree {
            child: children,
            open_ch,
            close_ch,
        })
    }
}
