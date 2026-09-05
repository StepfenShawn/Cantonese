//! Macro pattern parser

use crate::ast::{
    MacroMetaId, MacroMetaRepExpInPat, MacroPatItem, MetaIdExp, TokenTree, TokenTreeChild,
};
use crate::lexer::token::TokenType;
use crate::parser::{ParseError, Parser};

pub struct MacroPatParser;

impl MacroPatParser {
    /// Parse a meta variable inside a macro pattern: `$v: str`.
    pub fn parse_meta_var(parser: &mut Parser) -> Result<MacroPatItem, ParseError> {
        let id_tk = parser.eat_kind(TokenType::Identifier)?;
        parser.eat_value(":")?;
        let frag_spec_tk = parser.eat_kind(TokenType::Identifier)?;
        Ok(MacroPatItem::MetaVar(MacroMetaId {
            id: crate::ast::Exp::Id(crate::ast::IdExp {
                name: id_tk.value.clone(),
                pos: None,
            }),
            frag_spec: crate::ast::Exp::Id(crate::ast::IdExp {
                name: frag_spec_tk.value.clone(),
                pos: None,
            }),
        }))
    }

    /// Parse a repetition group inside a macro pattern: `$(...)+`.
    pub fn parse_meta_rep_exp(parser: &mut Parser) -> Result<MacroPatItem, ParseError> {
        parser.eat_kind(TokenType::SepLParen)?;
        let mut token_trees = Vec::new();
        while !parser.match_kind(TokenType::SepRParen) {
            token_trees.push(Self::parse_macro_rule(parser)?);
        }
        parser.eat_kind(TokenType::SepRParen)?;
        Ok(MacroPatItem::Rep(Box::new(Self::finish_meta_exp(
            parser,
            token_trees,
        )?)))
    }

    pub fn parse_macro_rule(parser: &mut Parser) -> Result<MacroPatItem, ParseError> {
        match parser.peek_value() {
            Some("$") => {
                parser.skip(); // '$'
                if Some(TokenType::Identifier) == parser.peek_type() {
                    Self::parse_meta_var(parser)
                } else {
                    Self::parse_meta_rep_exp(parser)
                }
            }
            Some("(") => Self::parse_tokentrees_in_pat(parser),
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

    fn parse_tokentrees_in_pat(parser: &mut Parser) -> Result<MacroPatItem, ParseError> {
        let mut children: Vec<TokenTreeChild> = Vec::new();
        let open_ch = parser.eat_kind(TokenType::SepLParen)?.clone();
        while !parser.match_kind(TokenType::SepRParen) {
            match parser.peek_type() {
                Some(TokenType::SepLParen) => {
                    children.push(TokenTreeChild::Tree(Self::parse_tokentrees(parser)?));
                }
                _ => {
                    let item = Self::parse_macro_rule(parser)?;
                    children.push(Self::pat_item_to_tree_child(item));
                }
            }
        }
        let close_ch = parser.eat_kind(TokenType::SepRParen)?.clone();
        Ok(MacroPatItem::Tree(TokenTree {
            child: children,
            open_ch,
            close_ch,
        }))
    }

    fn pat_item_to_tree_child(item: MacroPatItem) -> TokenTreeChild {
        match item {
            MacroPatItem::Token(tk) => TokenTreeChild::Token(tk),
            MacroPatItem::MetaId(id) => TokenTreeChild::MetaId(id),
            MacroPatItem::Tree(tree) => TokenTreeChild::Tree(tree),
            MacroPatItem::Rep(rep) => TokenTreeChild::PatRep(rep),
            MacroPatItem::MetaVar(mv) => TokenTreeChild::MetaId(MetaIdExp {
                name: match mv.id {
                    crate::ast::Exp::Id(id) => id.name,
                    _ => String::new(),
                },
                pos: None,
            }),
        }
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
