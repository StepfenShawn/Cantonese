//! Qualified-name parser (translated from can_parser/exp/names_parser.py).
//!
//! Parses import paths like `A::B::C` or `A::{B, C::*}` into a nested
//! `NamesExp` structure.

use crate::ast::{Exp, IdExp, NamesExp};
use crate::lexer::token::{Pos, Token, TokenType};
use crate::parser::{ParseError, Parser};

pub struct NamesParser;

impl NamesParser {
    pub fn parse(parser: &mut Parser) -> Result<Exp, ParseError> {
        let name_tk = parser.eat_kind(TokenType::Identifier)?;
        let root = Exp::Id(IdExp {
            name: name_tk.value,
        });
        Self::finish(parser, root)
    }

    fn finish(parser: &mut Parser, root: Exp) -> Result<Exp, ParseError> {
        if !parser.match_kind(TokenType::DColon) {
            return Ok(root);
        }
        parser.skip();
        let mut chain = Exp::Names(NamesExp {
            child: vec![root, Self::parse_next(parser)?],
        });

        while parser.match_kind(TokenType::DColon) {
            parser.skip();
            chain = Exp::Names(NamesExp {
                child: vec![chain, Self::parse_next(parser)?],
            });
        }

        Ok(chain)
    }

    fn parse_next(parser: &mut Parser) -> Result<Exp, ParseError> {
        match (parser.peek_type(), parser.peek_value()) {
            (Some(TokenType::Identifier), _) => {
                let tk = parser.eat_kind(TokenType::Identifier)?;
                Ok(Exp::Id(IdExp { name: tk.value }))
            }
            (Some(TokenType::OpMul), _) | (_, Some("*")) => {
                parser.skip();
                Ok(Exp::Id(IdExp { name: "*".into() }))
            }
            (Some(TokenType::SepLCurly), _) => {
                parser.skip();
                let set = Self::parse_names_set(parser)?;
                parser.eat_kind(TokenType::SepRCurly)?;
                Ok(Exp::Names(NamesExp { child: set }))
            }
            _ => Err(ParseError::syntax(
                parser.peek_token().unwrap_or(&Token {
                    pos: Pos::simple(0, 0),
                    typ: TokenType::EOF,
                    value: "EOF".into(),
                }),
                parser.file_path,
                "Expected identifier, `*`, or `{` after `::`",
                "例如 `A::B` 或 `A::*`",
            )),
        }
    }

    fn parse_names_set(parser: &mut Parser) -> Result<Vec<Exp>, ParseError> {
        let mut ret = vec![Self::parse(parser)?];
        while parser.match_kind(TokenType::SepComma) {
            parser.skip();
            ret.push(Self::parse(parser)?);
        }
        Ok(ret)
    }
}
