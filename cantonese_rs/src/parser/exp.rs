//! Expression parser (translated from can_parser/exp/exp_parser.py).
//!
//! Uses Rust `match` on the current token to dispatch parsing, mirroring the
//! precedence-climbing / Pratt-style structure of the original implementation.

use crate::ast::{
    AnnotationExp, AssignExp, BinopExp, ConcatExp, Exp, FalseExp, FuncCallExp, IdExp, IfElseExp,
    LambdaExp, ListAccessExp, ListExp, MapExp, MappingExp, MetaIdExp, NullExp, NumeralExp,
    ObjectAccessExp, ParensExp, Stat, StringExp, TrueExp, UnopExp, VarArgExp,
};
use crate::lexer::keywords::*;
use crate::lexer::token::{Pos, Token, TokenType};
use crate::macros::MacroExpander;
use crate::parser::macro_body::MacroBodyParser;
use crate::parser::macro_pat::MacroPatParser;
use crate::parser::{ParseError, Parser, StatParser};

pub struct ExpParser;

impl ExpParser {
    /// `explist ::= exp {',' exp}`
    pub fn parse_exp_list(parser: &mut Parser) -> Result<Vec<Exp>, ParseError> {
        let mut exps = vec![Self::parse_exp(parser)?];
        while parser.match_kind(TokenType::SepComma) {
            parser.skip();
            exps.push(Self::parse_exp(parser)?);
        }
        Ok(exps)
    }

    /// Entry point: delegates to the lowest-precedence parser.
    pub fn parse_exp(parser: &mut Parser) -> Result<Exp, ParseError> {
        Self::parse_exp13(parser)
    }

    // exp1 ==> exp2
    fn parse_exp13(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp12(parser)?;
        if parser.match_value("==>") {
            parser.skip();
            exp = Exp::Mapping(MappingExp {
                exp1: Box::new(exp),
                exp2: Box::new(Self::parse_exp12(parser)?),
            });
        }
        Ok(exp)
    }

    // exp1 or exp2
    fn parse_exp12(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp11(parser)?;
        while parser.match_any_value(&["or", "或者"]) {
            parser.skip();
            exp = Exp::Binop(BinopExp {
                op: "or".to_string(),
                exp1: Box::new(exp),
                exp2: Box::new(Self::parse_exp11(parser)?),
            });
        }
        Ok(exp)
    }

    // exp1 and exp2
    fn parse_exp11(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp10(parser)?;
        while parser.match_any_value(&["and", "同埋"]) {
            parser.skip();
            exp = Exp::Binop(BinopExp {
                op: "and".to_string(),
                exp1: Box::new(exp),
                exp2: Box::new(Self::parse_exp10(parser)?),
            });
        }
        Ok(exp)
    }

    // Compare
    fn parse_exp10(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp9(parser)?;
        loop {
            match parser.peek_value() {
                Some(v) if matches!(v, ">" | ">=" | "<" | "<=" | "==" | "!=") => {
                    let op = v.to_string();
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op,
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp9(parser)?),
                    });
                }
                Some(v) if v == KW_IS => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "==".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp9(parser)?),
                    });
                }
                Some(v) if matches!(v, "in" | KW_IN) => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: " in ".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp9(parser)?),
                    });
                }
                Some("比唔上") => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "<".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp9(parser)?),
                    });
                }
                _ => break,
            }
        }
        Ok(exp)
    }

    // exp1 <|> exp2
    fn parse_exp9(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp8(parser)?;
        while parser.match_kind(TokenType::OpBor) || parser.match_value("或") {
            parser.skip();
            exp = Exp::Binop(BinopExp {
                op: "|".to_string(),
                exp1: Box::new(exp),
                exp2: Box::new(Self::parse_exp8(parser)?),
            });
        }
        Ok(exp)
    }

    // exp1 ^ exp2
    fn parse_exp8(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp7(parser)?;
        while parser.match_kind(TokenType::OpWave) || parser.match_value("異或") {
            parser.skip();
            exp = Exp::Binop(BinopExp {
                op: "^".to_string(),
                exp1: Box::new(exp),
                exp2: Box::new(Self::parse_exp8(parser)?),
            });
        }
        Ok(exp)
    }

    // exp1 & exp2
    fn parse_exp7(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp6(parser)?;
        while parser.match_kind(TokenType::OpBand) || parser.match_value("與") {
            parser.skip();
            exp = Exp::Binop(BinopExp {
                op: "&".to_string(),
                exp1: Box::new(exp),
                exp2: Box::new(Self::parse_exp8(parser)?),
            });
        }
        Ok(exp)
    }

    // shift
    fn parse_exp6(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp5(parser)?;
        let op = match parser.peek_value() {
            Some("<<") | Some(">>") => parser.peek_value().unwrap().to_string(),
            Some("左移") => "<<".to_string(),
            Some("右移") => ">>".to_string(),
            _ => return Ok(exp),
        };
        parser.skip();
        exp = Exp::Binop(BinopExp {
            op,
            exp1: Box::new(exp),
            exp2: Box::new(Self::parse_exp5(parser)?),
        });
        Ok(exp)
    }

    // exp1 <-> exp2
    fn parse_exp5(parser: &mut Parser) -> Result<Exp, ParseError> {
        let exp = Self::parse_exp4(parser)?;
        if !parser.match_kind(TokenType::OpConcat) {
            return Ok(exp);
        }
        let mut exps = vec![exp];
        while parser.match_kind(TokenType::OpConcat) {
            parser.skip();
            exps.push(Self::parse_exp4(parser)?);
        }
        Ok(Exp::Concat(ConcatExp { exps }))
    }

    // exp1 + / - exp2
    fn parse_exp4(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp3(parser)?;
        loop {
            match parser.peek_value() {
                Some("+") | Some("-") => {
                    let op = parser.peek_value().unwrap().to_string();
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op,
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp3(parser)?),
                    });
                }
                Some("加") => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "+".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp3(parser)?),
                    });
                }
                Some("減") => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "-".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp3(parser)?),
                    });
                }
                _ => break,
            }
        }
        Ok(exp)
    }

    // *, %, /, //
    fn parse_exp3(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp2(parser)?;
        loop {
            match parser.peek_value() {
                Some("*") | Some("%") | Some("/") | Some("//") => {
                    let op = parser.peek_value().unwrap().to_string();
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op,
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp2(parser)?),
                    });
                }
                Some("乘") => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "*".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp2(parser)?),
                    });
                }
                Some("餘") | Some("余") => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "%".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp2(parser)?),
                    });
                }
                Some("整除") => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "//".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp2(parser)?),
                    });
                }
                Some("除") => {
                    parser.skip();
                    exp = Exp::Binop(BinopExp {
                        op: "//".to_string(),
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp2(parser)?),
                    });
                }
                _ => break,
            }
        }
        Ok(exp)
    }

    // unop exp
    fn parse_exp2(parser: &mut Parser) -> Result<Exp, ParseError> {
        match parser.peek_value() {
            Some("not") | Some("-") | Some("~") => {
                let op = parser.peek_value().unwrap().to_string();
                parser.skip();
                Ok(Exp::Unop(UnopExp {
                    op,
                    exp: Box::new(Self::parse_exp2(parser)?),
                }))
            }
            Some("取反") => {
                parser.skip();
                Ok(Exp::Unop(UnopExp {
                    op: "~".to_string(),
                    exp: Box::new(Self::parse_exp2(parser)?),
                }))
            }
            _ => Self::parse_exp1(parser),
        }
    }

    // x ** y
    fn parse_exp1(parser: &mut Parser) -> Result<Exp, ParseError> {
        let mut exp = Self::parse_exp0(parser)?;
        if parser.match_kind(TokenType::OpPow) {
            let op = parser.peek_value().unwrap().to_string();
            parser.skip();
            exp = Exp::Binop(BinopExp {
                op,
                exp1: Box::new(exp),
                exp2: Box::new(Self::parse_exp2(parser)?),
            });
        }
        Ok(exp)
    }

    fn parse_exp0(parser: &mut Parser) -> Result<Exp, ParseError> {
        match parser.peek_value() {
            Some("<*>") => {
                parser.skip();
                Ok(Exp::VarArg(VarArgExp))
            }
            _ => match parser.peek_type() {
                Some(TokenType::Num) => {
                    let tk = parser.next_token().unwrap();
                    Ok(Exp::Numeral(NumeralExp {
                        val: tk.value.clone(),
                    }))
                }
                Some(TokenType::SepLCurly) => Self::parse_mapcons(parser),
                Some(TokenType::Keyword) if parser.match_value(KW_EXPR_IF) => {
                    parser.skip();
                    Self::parse_if_else_expr(parser)
                }
                _ => Self::parse_prefixexp(parser),
            },
        }
    }

    ///
    /// prefixexp ::= var
    ///          | '(' exp ')'
    ///          | '|' exp '|'
    ///          | functioncall
    ///          | id '=' exp
    ///
    /// var ::= id
    ///       | prefixexp '[' exp ']'
    ///       | prefixexp '->' id
    ///       | prefixexp '==>' id
    ///
    pub fn parse_prefixexp(parser: &mut Parser) -> Result<Exp, ParseError> {
        let exp = match parser.peek_type() {
            Some(TokenType::Identifier) => {
                let tk = parser.next_token().unwrap();
                Exp::Id(IdExp {
                    name: tk.value.clone(),
                })
            }
            Some(TokenType::String) => {
                let tk = parser.next_token().unwrap();
                Exp::String(StringExp { s: tk.value.clone() })
            }
            Some(TokenType::SepLBrack) => Self::parse_listcons(parser)?,
            Some(TokenType::Keyword) if parser.match_value("@") => {
                parser.skip();
                let tk = parser.eat_kind(TokenType::Identifier)?;
                Exp::MetaId(MetaIdExp {
                    name: tk.value.clone(),
                })
            }
            Some(TokenType::SepLParen) => Self::parse_parens_exp(parser)?,
            Some(TokenType::Keyword) if parser.match_value("$$") => {
                parser.skip();
                Self::parse_functiondef_expr(parser)?
            }
            Some(TokenType::Keyword) if parser.match_value("$") => {
                return MacroBodyParser::parse_meta_rep_stmt(parser);
            }
            _ => Self::parse_brack_exp(parser)?,
        };
        Self::finish_prefixexp(parser, exp)
    }

    fn parse_parens_exp(parser: &mut Parser) -> Result<Exp, ParseError> {
        parser.eat_kind(TokenType::SepLParen)?;
        let exp = Self::parse_exp(parser)?;
        parser.eat_kind(TokenType::SepRParen)?;
        Ok(Exp::Parens(ParensExp { exp: Box::new(exp) }))
    }

    fn parse_brack_exp(parser: &mut Parser) -> Result<Exp, ParseError> {
        parser.eat_value("|")?;
        let exp = Self::parse_exp(parser)?;
        parser.eat_value("|")?;
        Ok(exp)
    }

    /// listcons := '[' exp_list ']'
    fn parse_listcons(parser: &mut Parser) -> Result<Exp, ParseError> {
        parser.eat_kind(TokenType::SepLBrack)?;
        let elem_exps = if parser.match_kind(TokenType::SepRBrack) {
            parser.skip();
            Vec::new()
        } else {
            let exps = Self::parse_exp_list(parser)?;
            parser.eat_kind(TokenType::SepRBrack)?;
            exps
        };
        Ok(Exp::List(ListExp { elem_exps }))
    }

    /// set_or_mapcons := '{' exp_list '}'
    fn parse_mapcons(parser: &mut Parser) -> Result<Exp, ParseError> {
        parser.eat_kind(TokenType::SepLCurly)?;
        let elem_exps = if parser.match_kind(TokenType::SepRCurly) {
            parser.skip();
            Vec::new()
        } else {
            let exps = Self::parse_exp_list(parser)?;
            parser.eat_kind(TokenType::SepRCurly)?;
            exps
        };
        Ok(Exp::Map(MapExp { elem_exps }))
    }

    fn finish_prefixexp(parser: &mut Parser, mut exp: Exp) -> Result<Exp, ParseError> {
        loop {
            match parser.peek_type() {
                Some(TokenType::SepLBrack) => {
                    parser.skip();
                    let key_exp = Self::parse_exp(parser)?;
                    parser.eat_kind(TokenType::SepRBrack)?;
                    exp = Exp::ListAccess(ListAccessExp {
                        prefix_exp: Box::new(exp),
                        key_exp: Box::new(key_exp),
                    });
                }
                Some(TokenType::SepDot) | _ if parser.match_any_value(&[KW_DOT, "嘅"]) => {
                    parser.skip();
                    let tk = parser.eat_kind(TokenType::Identifier)?;
                    let key_exp = Exp::Id(IdExp {
                        name: tk.value.clone(),
                    });
                    exp = Exp::ObjectAccess(ObjectAccessExp {
                        prefix_exp: Box::new(exp),
                        key_exp: Box::new(key_exp),
                    });
                }
                Some(typ) if typ == TokenType::SepLParen || parser.peek_value() == Some(KW_CALL_BEGIN) => {
                    exp = Self::finish_functioncall_exp(parser, exp)?;
                }
                Some(TokenType::OpAssign) => {
                    parser.skip();
                    exp = Exp::Assign(AssignExp {
                        exp1: Box::new(exp),
                        exp2: Box::new(Self::parse_exp(parser)?),
                    });
                }
                Some(TokenType::Colon) => {
                    parser.skip();
                    exp = Exp::Annotation(AnnotationExp {
                        exp: Box::new(exp),
                        tyid: Box::new(Self::parse_exp(parser)?),
                    });
                    break;
                }
                Some(TokenType::Excl) => {
                    parser.skip();
                    let macro_name = match &exp {
                        Exp::Id(id) => id.name.clone(),
                        _ => {
                            return Err(ParseError::syntax(
                                parser.peek_token().unwrap_or(&Token {
                                    pos: Pos::simple(0, 0),
                                    typ: TokenType::EOF,
                                    value: "EOF".into(),
                                }),
                                parser.file_path,
                                "Macro call must follow an identifier",
                                "例如 `macro! (...)`",
                            ));
                        }
                    };
                    let tokentrees = MacroPatParser::parse_tokentrees(parser)?;
                    let expanded = MacroExpander::expand(parser, &macro_name, tokentrees)?;
                    let mut sub_parser = Parser::new_with_registry(
                        &expanded,
                        parser.file_path,
                        parser.macro_registry.clone(),
                    );
                    let expanded_stat = StatParser::parse(&mut sub_parser)?;
                    return match expanded_stat {
                        Some(Stat::Call(call)) => Ok(call.exp),
                        Some(stat) => Ok(Exp::StatExpansion(Box::new(stat))),
                        None => Err(ParseError::UnexpectedEof),
                    };
                }
                _ => break,
            }
        }
        Ok(exp)
    }

    ///
    /// functioncall ::= prefixexp '下' '->' args
    ///               | prefixexp args
    ///
    fn finish_functioncall_exp(parser: &mut Parser, prefix_exp: Exp) -> Result<Exp, ParseError> {
        if parser.match_value(KW_CALL_BEGIN) {
            parser.skip();
            parser.eat_value(KW_DOT)?;
            let args = Self::parse_args(parser)?;
            Ok(Exp::FuncCall(FuncCallExp {
                prefix_exp: Box::new(prefix_exp),
                args,
            }))
        } else {
            let args = Self::parse_args(parser)?;
            Ok(Exp::FuncCall(FuncCallExp {
                prefix_exp: Box::new(prefix_exp),
                args,
            }))
        }
    }

    ///
    /// idlist ::= id [',', id]
    ///        | '|' id [',', id] '|'
    ///
    pub fn parse_idlist(parser: &mut Parser) -> Result<Option<Vec<Exp>>, ParseError> {
        match parser.peek_type() {
            Some(TokenType::Identifier) => {
                let mut ids = vec![Exp::Id(IdExp {
                    name: parser.next_token().unwrap().value.clone(),
                })];
                while parser.match_kind(TokenType::SepComma) {
                    parser.skip();
                    if parser.peek_type() != Some(TokenType::Identifier) {
                        return Err(ParseError::UnexpectedEof);
                    }
                    ids.push(Exp::Id(IdExp {
                        name: parser.next_token().unwrap().value.clone(),
                    }));
                }
                Ok(Some(ids))
            }
            Some(TokenType::Brack) if parser.match_value("|") => {
                parser.skip();
                let mut ids = vec![Exp::Id(IdExp {
                    name: parser.eat_kind(TokenType::Identifier)?.value.clone(),
                })];
                while parser.match_kind(TokenType::SepComma) {
                    parser.skip();
                    if parser.peek_type() != Some(TokenType::Identifier) {
                        return Err(ParseError::UnexpectedEof);
                    }
                    ids.push(Exp::Id(IdExp {
                        name: parser.next_token().unwrap().value.clone(),
                    }));
                }
                parser.eat_value("|")?;
                Ok(Some(ids))
            }
            _ => Ok(None),
        }
    }

    ///
    /// lambda_functoindef ::= '$$' idlist '{' exp_list '}'
    ///
    fn parse_functiondef_expr(parser: &mut Parser) -> Result<Exp, ParseError> {
        let idlist = Self::parse_idlist(parser)?.unwrap_or_default();
        parser.eat_kind(TokenType::SepLCurly)?;
        let blocks = Self::parse_exp_list(parser)?;
        parser.eat_kind(TokenType::SepRCurly)?;
        Ok(Exp::Lambda(LambdaExp { id_list: idlist, blocks }))
    }

    fn parse_if_else_expr(parser: &mut Parser) -> Result<Exp, ParseError> {
        let if_cond_exp = Self::parse_exp(parser)?;
        parser.eat_value(KW_DOT)?;
        let if_exp = Self::parse_exp(parser)?;
        parser.eat_value(KW_EXPR_ELSE)?;
        parser.eat_value(KW_DOT)?;
        let else_exp = Self::parse_exp(parser)?;
        Ok(Exp::IfElse(IfElseExp {
            if_cond_exp: Box::new(if_cond_exp),
            if_exp: Box::new(if_exp),
            else_exp: Box::new(else_exp),
        }))
    }

    ///
    /// args ::= '|' explist '|'
    ///        | '(' {explist} ')'
    ///        | explist
    ///        | LiteralString
    ///        | Numeral
    ///        | id
    ///
    pub fn parse_args(parser: &mut Parser) -> Result<Vec<Exp>, ParseError> {
        match parser.peek_value() {
            Some("(") => {
                parser.skip();
                let args = if parser.peek_value() == Some(")") {
                    Vec::new()
                } else {
                    Self::parse_exp_list(parser)?
                };
                parser.eat_kind(TokenType::SepRParen)?;
                Ok(args)
            }
            Some("|") => {
                parser.skip();
                let args = if parser.peek_value() == Some("|") {
                    Vec::new()
                } else {
                    Self::parse_exp_list(parser)?
                };
                parser.eat_value("|")?;
                Ok(args)
            }
            _ => Self::parse_exp_list(parser),
        }
    }

    pub fn parse_attrs_def(parser: &mut Parser) -> Result<Vec<Exp>, ParseError> {
        match parser.peek_type() {
            Some(TokenType::Identifier) => {
                let name_tk = parser.next_token().unwrap();
                parser.eat_value(":")?;
                let ty_tk = parser.eat_kind(TokenType::Identifier)?;
                let mut attrs = vec![Exp::Annotation(AnnotationExp {
                    exp: Box::new(Exp::Id(IdExp {
                        name: name_tk.value.clone(),
                    })),
                    tyid: Box::new(Exp::Id(IdExp {
                        name: ty_tk.value.clone(),
                    })),
                })];
                while parser.match_kind(TokenType::SepComma) {
                    parser.skip();
                    if parser.peek_type() != Some(TokenType::Identifier) {
                        break;
                    }
                    let name_tk = parser.next_token().unwrap();
                    parser.eat_value(":")?;
                    let ty_tk = parser.eat_kind(TokenType::Identifier)?;
                    attrs.push(Exp::Annotation(AnnotationExp {
                        exp: Box::new(Exp::Id(IdExp {
                            name: name_tk.value.clone(),
                        })),
                        tyid: Box::new(Exp::Id(IdExp {
                            name: ty_tk.value.clone(),
                        })),
                    }));
                }
                Ok(attrs)
            }
            _ => Ok(Vec::new()),
        }
    }
}

// Helper constructors used by the parser so that `Exp::True`, `Exp::False`,
// `Exp::Null` can be constructed ergonomically.
impl Exp {
    pub fn null() -> Self {
        Exp::Null(NullExp)
    }
    pub fn truelit() -> Self {
        Exp::True(TrueExp)
    }
    pub fn falselit() -> Self {
        Exp::False(FalseExp)
    }
}
