//! Macro body parser (translated from can_parser/macro/body_parser.py).
//!
//! Parses the output-side of a macro rule, e.g. `${ @v + @v }+`.

use crate::ast::{MacroMetaRepExpInBlock, MetaIdExp, TokenTree, TokenTreeChild};
use crate::lexer::token::TokenType;
use crate::parser::{ParseError, Parser};

pub struct MacroBodyParser;

impl MacroBodyParser {
    /// Parse a repetition group inside a macro body: `${...}+`.
    pub fn parse_meta_rep_stmt(parser: &mut Parser) -> Result<crate::ast::Exp, ParseError> {
        parser.skip(); // '$'
        let token_tree = Self::parse_tokentrees(parser)?;
        Ok(crate::ast::Exp::BlockRep(Box::new(Self::finish_meta_exp(
            parser, token_tree,
        )?)))
    }

    fn finish_meta_exp(
        parser: &mut Parser,
        token_trees: TokenTree,
    ) -> Result<MacroMetaRepExpInBlock, ParseError> {
        let rep_sep = if parser.match_any_value(&["*", "+", "?"]) {
            None
        } else {
            Some(crate::ast::Exp::Id(crate::ast::IdExp {
                name: parser.next_token().unwrap().value.clone(),
            }))
        };
        let op_tk = parser.eat_any_value(&["*", "+", "?"])?;
        let rep_op = Some(crate::ast::Exp::Id(crate::ast::IdExp {
            name: op_tk.value.clone(),
        }));
        Ok(MacroMetaRepExpInBlock {
            token_trees,
            rep_sep,
            rep_op,
        })
    }

    /// Parse a balanced curly-braced token tree used as a macro body.
    pub fn parse_tokentrees(parser: &mut Parser) -> Result<TokenTree, ParseError> {
        let mut children: Vec<TokenTreeChild> = Vec::new();
        let open_ch = parser.eat_kind(TokenType::SepLCurly)?.clone();
        while !parser.match_kind(TokenType::SepRCurly) {
            match parser.peek_type() {
                Some(TokenType::SepLCurly) => {
                    children.push(TokenTreeChild::Tree(Self::parse_tokentrees(parser)?));
                }
                Some(TokenType::Keyword) if parser.match_value("@") => {
                    parser.skip();
                    let meta_var = parser.eat_kind(TokenType::Identifier)?;
                    children.push(TokenTreeChild::MetaId(MetaIdExp {
                        name: meta_var.value.clone(),
                    }));
                }
                Some(TokenType::Keyword) if parser.match_value("$") => {
                    let rep = Self::parse_meta_rep_stmt(parser)?;
                    if let crate::ast::Exp::BlockRep(r) = rep {
                        children.push(TokenTreeChild::BlockRep(r));
                    }
                }
                _ => {
                    children.push(TokenTreeChild::Token(parser.next_token().unwrap().clone()));
                }
            }
        }
        let close_ch = parser.eat_kind(TokenType::SepRCurly)?.clone();
        Ok(TokenTree {
            child: children,
            open_ch,
            close_ch,
        })
    }
}
