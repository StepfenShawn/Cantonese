//! Statement parser (translated from can_parser/stat/stat_parser.py).
//!
//! Uses Rust `match` on the current token to dispatch to the corresponding
//! statement parser, mirroring the keyword-driven structure of the original.

use crate::ast::{
    AssertStat, AssignBlockStat, AssignStat, AttrDefStat, BreakStat, CallStat, ClassDefStat,
    CmdStat, ContinueStat, DelStat, ExitStat, Exp, ExtendStat, ForEachStat, ForStat, FuncCallExp,
    FuncCallStat, FunctionDefStat, GlobalStat, IdExp, IfStat, ImportStat, MacroDefStat, MatchStat,
    MethodCallStat, MethodDefStat, PassStat, PrintStat, RaiseStat, ReturnStat, Stat, TryStat,
    TypeStat, UnopExp, WhileStat,
};
use crate::lexer::keywords::*;
use crate::lexer::token::{Pos, Token, TokenType};
use crate::parser::exp::ExpParser;
use crate::parser::macro_body::MacroBodyParser;
use crate::parser::macro_pat::MacroPatParser;
use crate::parser::names::NamesParser;
use crate::parser::{with_pos_stat, ParseError, Parser};

pub struct StatParser;

impl StatParser {
    /// Parse a variable list for assignments.
    pub fn parse_var_list(parser: &mut Parser) -> Result<Vec<Exp>, ParseError> {
        let exp = ExpParser::parse_prefixexp(parser)?;
        let mut var_list = vec![Self::check_var(parser, exp)?];
        while parser.match_kind(TokenType::SepComma) {
            parser.skip();
            let exp = ExpParser::parse_prefixexp(parser)?;
            var_list.push(Self::check_var(parser, exp)?);
        }
        Ok(var_list)
    }

    fn check_var(parser: &mut Parser, exp: Exp) -> Result<Exp, ParseError> {
        match exp {
            Exp::Id(_)
            | Exp::ObjectAccess(_)
            | Exp::ListAccess(_)
            | Exp::Mapping(_)
            | Exp::Annotation(_) => Ok(exp),
            _ => Err(ParseError::syntax(
                parser.peek_token().unwrap_or(&Token {
                    pos: Pos::simple(0, 0),
                    typ: TokenType::EOF,
                    value: "EOF".into(),
                }),
                parser.file_path,
                "Expected a variable in assignment target",
                "變數必須係 identifier、屬性訪問、下標訪問或映射",
            )),
        }
    }

    /// Entry point for parsing a single statement.
    pub fn parse(parser: &mut Parser) -> Result<Option<Stat>, ParseError> {
        with_pos_stat(parser, |p| {
            match (p.peek_type(), p.peek_value()) {
                (Some(TokenType::Keyword), Some(v)) => match v {
                    KW_PRINT => {
                        p.skip();
                        Self::parse_print_stat(p)
                    }
                    KW_EXIT | KW_EXIT_1 | KW_EXIT_2 => {
                        p.skip();
                        Self::parse_exit_stat(p)
                    }
                    KW_ASSIGN => {
                        p.skip();
                        Self::parse_assign_stat(p)
                    }
                    KW_IF => {
                        p.skip();
                        Self::parse_if_stat(p)
                    }
                    KW_IMPORT => {
                        p.skip();
                        Self::parse_import_stat(p)
                    }
                    KW_GLOBAL_SET => {
                        p.skip();
                        Self::parse_global_stat(p)
                    }
                    KW_BREAK => {
                        p.skip();
                        Self::parse_break_stat(p)
                    }
                    KW_CONTINUE => {
                        p.skip();
                        Self::parse_continue_stat(p)
                    }
                    KW_WHILE_DO => {
                        p.skip();
                        Self::parse_while_stat(p)
                    }
                    KW_PASS => {
                        p.skip();
                        Self::parse_pass_stat(p)
                    }
                    KW_RETURN => {
                        p.skip();
                        Self::parse_return_stat(p)
                    }
                    KW_DEL | KW_DEL2 => {
                        p.skip();
                        Self::parse_del_stat(p)
                    }
                    KW_TYPE => {
                        p.skip();
                        Self::parse_type_stat(p)
                    }
                    KW_ASSERT => {
                        p.skip();
                        Self::parse_assert_stat(p)
                    }
                    KW_TRY => {
                        p.skip();
                        Self::parse_try_stat(p)
                    }
                    KW_RAISE => {
                        p.skip();
                        Self::parse_raise_stat(p)
                    }
                    KW_CMD => {
                        p.skip();
                        Self::parse_cmd_stat(p)
                    }
                    KW_STACKINIT => {
                        p.skip();
                        Self::parse_stack_init_stat(p)
                    }
                    KW_PUSH => {
                        p.skip();
                        Self::parse_stack_push_stat(p)
                    }
                    KW_POP => {
                        p.skip();
                        Self::parse_stack_pop_stat(p)
                    }
                    KW_MATCH => {
                        p.skip();
                        Self::parse_match_stat(p)
                    }
                    KW_CALL_NATIVE => {
                        p.skip();
                        Self::parse_call_native_stat(p)
                    }
                    "&&" => {
                        p.skip();
                        Self::parse_for_each_stat(p)
                    }
                    KW_PLS => {
                        p.skip();
                        Self::parse_pls_stat(p)
                    }
                    _ => Self::with_prefix_stats(p),
                },
                (Some(TokenType::EOF), _) => Ok(Stat::Exit(ExitStat { pos: None })),
                _ => Self::with_prefix_stats(p),
            }
        })
        .map(Some)
    }

    /// Parse statements until EOF, returning a vector.
    pub fn parse_stats(parser: &mut Parser) -> Result<Vec<Stat>, ParseError> {
        let mut stats = Vec::new();
        loop {
            if parser.is_eof() {
                break;
            }
            match Self::parse(parser)? {
                Some(stat) => stats.push(stat),
                None => break,
            }
        }
        Ok(stats)
    }

    fn with_prefix_stats(parser: &mut Parser) -> Result<Stat, ParseError> {
        let prefix_exp = ExpParser::parse_exp(parser)?;
        match parser.peek_value() {
            Some(v) if v == KW_FROM => Self::parse_for_stat(parser, prefix_exp),
            Some(v) if v == KW_GET_VALUE => Self::parse_suffix_assign_stat(parser, prefix_exp),
            Some(v) if v == KW_LST_ASSIGN => Self::parse_list_assign_stat(parser, prefix_exp),
            Some(v) if v == KW_SET_ASSIGN => Self::parse_set_assign_stat(parser, prefix_exp),
            Some(v) if v == KW_LAA1 || v == KW_GAMLAA1 => {
                Self::parse_class_method_call_stat(parser, prefix_exp)
            }
            _ => Ok(Stat::Call(CallStat {
                exp: prefix_exp,
                pos: None,
            })),
        }
    }

    // -------------------------------------------------------------------------
    // Individual statement parsers
    // -------------------------------------------------------------------------

    fn parse_print_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let args = ExpParser::parse_args(parser)?;
        parser.eat_value(KW_ENDPRINT)?;
        Ok(Stat::Print(PrintStat { args, pos: None }))
    }

    fn parse_exit_stat(_parser: &mut Parser) -> Result<Stat, ParseError> {
        Ok(Stat::Exit(ExitStat { pos: None }))
    }

    /// Parser for multi-assign block: `介紹返 => ... 先啦`.
    fn parse_assign_block(parser: &mut Parser) -> Result<Stat, ParseError> {
        if parser.match_value(KW_END_ASSIGN) {
            parser.skip();
            return Ok(Stat::Pass(PassStat { pos: None }));
        }
        let mut var_list = Vec::new();
        let mut exp_list = Vec::new();
        while !parser.match_value(KW_END_ASSIGN) {
            var_list.push(Self::parse_var_list(parser)?.into_iter().next().unwrap());
            parser.eat_value(KW_IS)?;
            exp_list.push(ExpParser::parse_exp_list(parser)?.into_iter().next().unwrap());
        }
        parser.eat_value(KW_END_ASSIGN)?;
        Ok(Stat::AssignBlock(AssignBlockStat {
            var_list,
            exp_list,
            pos: None,
        }))
    }

    fn parse_assign_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        match parser.peek_value() {
            Some(v) if v == KW_DO => {
                parser.skip();
                Self::parse_assign_block(parser)
            }
            Some(v) if v == KW_FUNCTION => {
                parser.skip();
                Self::parse_func_def_stat(parser)
            }
            _ => {
                let var_list = Self::parse_var_list(parser)?;
                parser.eat_value(KW_IS)?;
                match parser.peek_value() {
                    Some(v) if v == KW_CLASS_DEF => {
                        parser.skip();
                        Self::parse_class_def(parser, var_list.into_iter().next().unwrap())
                    }
                    Some(v) if v == KW_MACRO_DEF => {
                        parser.skip();
                        Self::parse_macro_def(parser, var_list.into_iter().next().unwrap())
                    }
                    _ => {
                        let exp_list = ExpParser::parse_exp_list(parser)?;
                        Ok(Stat::Assign(AssignStat {
                            var_list,
                            exp_list,
                            pos: None,
                        }))
                    }
                }
            }
        }
    }

    fn parse_if_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let mut elif_exps = Vec::new();
        let mut elif_blocks = Vec::new();
        let mut else_blocks = Vec::new();

        let if_exp = ExpParser::parse_exp(parser)?;
        parser.eat_values(&[KW_THEN, KW_DO, "{"])?;

        let if_blocks = parser.many(
            |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
            |p| p.match_kind(TokenType::SepRCurly),
        )?;
        parser.eat_kind(TokenType::SepRCurly)?;

        while parser.match_value(KW_ELIF) {
            parser.eat_value(KW_ELIF)?;
            elif_exps.push(ExpParser::parse_exp(parser)?);
            parser.eat_values(&[KW_THEN, KW_DO, "{"])?;
            let elif_block = parser.many(
                |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
                |p| p.match_kind(TokenType::SepRCurly),
            )?;
            parser.eat_kind(TokenType::SepRCurly)?;
            elif_blocks.push(elif_block);
        }

        if parser.match_value(KW_ELSE_OR_NOT) {
            parser.eat_values(&[KW_ELSE_OR_NOT, KW_THEN, KW_DO, "{"])?;
            else_blocks = vec![parser.many(
                |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
                |p| p.match_kind(TokenType::SepRCurly),
            )?];
            parser.eat_kind(TokenType::SepRCurly)?;
        }

        Ok(Stat::If(IfStat {
            if_exp,
            if_block: if_blocks,
            elif_exps,
            elif_blocks,
            else_blocks,
            pos: None,
        }))
    }

    fn parse_import_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let names = NamesParser::parse(parser)?;
        Ok(Stat::Import(ImportStat { names, pos: None }))
    }

    fn parse_global_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let idlist = ExpParser::parse_idlist(parser)?.unwrap_or_default();
        Ok(Stat::Global(GlobalStat { idlist, pos: None }))
    }

    fn parse_break_stat(_parser: &mut Parser) -> Result<Stat, ParseError> {
        Ok(Stat::Break(BreakStat { pos: None }))
    }

    fn parse_continue_stat(_parser: &mut Parser) -> Result<Stat, ParseError> {
        Ok(Stat::Continue(ContinueStat { pos: None }))
    }

    fn parse_while_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let blocks = parser.many(
            |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
            |p| p.match_value(KW_WHILE),
        )?;
        parser.eat_value(KW_WHILE)?;
        let cond_exp = ExpParser::parse_exp(parser)?;
        parser.eat_value(KW_WHI_END)?;
        Ok(Stat::While(WhileStat {
            cond_exp: Exp::Unop(UnopExp {
                op: "not".into(),
                exp: Box::new(cond_exp),
            }),
            blocks,
            pos: None,
        }))
    }

    fn parse_pass_stat(_parser: &mut Parser) -> Result<Stat, ParseError> {
        Ok(Stat::Pass(PassStat { pos: None }))
    }

    fn parse_return_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let exps = ExpParser::parse_exp_list(parser)?;
        Ok(Stat::Return(ReturnStat { exps, pos: None }))
    }

    fn parse_del_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let exps = ExpParser::parse_exp_list(parser)?;
        Ok(Stat::Del(DelStat { exps, pos: None }))
    }

    fn parse_type_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let exps = vec![ExpParser::parse_exp(parser)?];
        Ok(Stat::Type(TypeStat { exps, pos: None }))
    }

    fn parse_assert_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let exps = ExpParser::parse_exp(parser)?;
        Ok(Stat::Assert(AssertStat { exps, pos: None }))
    }

    fn parse_try_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        parser.eat_value(KW_DO)?;
        parser.eat_kind(TokenType::SepLCurly)?;

        let try_blocks = parser.many(
            |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
            |p| p.match_kind(TokenType::SepRCurly),
        )?;
        parser.eat_kind(TokenType::SepRCurly)?;
        parser.eat_value(KW_EXCEPT)?;

        let mut except_exps = vec![ExpParser::parse_exp(parser)?];
        parser.eat_value(KW_THEN)?;
        parser.eat_value(KW_DO)?;
        parser.eat_kind(TokenType::SepLCurly)?;
        let mut except_blocks = vec![parser.many(
            |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
            |p| p.match_kind(TokenType::SepRCurly),
        )?];
        parser.eat_kind(TokenType::SepRCurly)?;

        while parser.match_value(KW_EXCEPT) {
            parser.skip();
            parser.eat_value(KW_THEN)?;
            except_exps.push(ExpParser::parse_exp(parser)?);
            parser.eat_value(KW_DO)?;
            parser.eat_kind(TokenType::SepLCurly)?;
            except_blocks.push(parser.many(
                |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
                |p| p.match_kind(TokenType::SepRCurly),
            )?);
            parser.eat_kind(TokenType::SepRCurly)?;
        }

        let finally_blocks = if parser.match_value(KW_FINALLY) {
            parser.skip();
            parser.eat_value(KW_DO)?;
            parser.eat_kind(TokenType::SepLCurly)?;
            let blocks = parser.many(
                |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
                |p| p.match_kind(TokenType::SepRCurly),
            )?;
            parser.eat_kind(TokenType::SepRCurly)?;
            blocks
        } else {
            Vec::new()
        };

        Ok(Stat::Try(TryStat {
            try_blocks,
            except_exps,
            except_blocks,
            finally_blocks,
            pos: None,
        }))
    }

    fn parse_raise_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let name_exp = ExpParser::parse_exp(parser)?;
        parser.eat_value(KW_RAISE_END)?;
        Ok(Stat::Raise(RaiseStat { name_exp, pos: None }))
    }

    fn parse_cmd_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let args = ExpParser::parse_args(parser)?;
        Ok(Stat::Cmd(CmdStat { args, pos: None }))
    }

    fn parse_for_stat(parser: &mut Parser, id: Exp) -> Result<Stat, ParseError> {
        parser.eat_value(KW_FROM)?;
        let from_exp = ExpParser::parse_exp(parser)?;
        parser.eat_value(KW_TO)?;
        let to_exp = ExpParser::parse_exp(parser)?;
        let blocks = parser.many(
            |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
            |p| p.match_value(KW_ENDFOR),
        )?;
        parser.eat_value(KW_ENDFOR)?;
        Ok(Stat::For(ForStat {
            var: id,
            from_exp,
            to_exp,
            blocks,
            pos: None,
        }))
    }

    fn parse_func_def_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let name_tk = parser.eat_kind(TokenType::Identifier)?;
        let args = ExpParser::parse_idlist(parser)?.unwrap_or_default();
        parser.eat_any_value(&[KW_FUNC_BEGIN, KW_DO])?;
        let blocks = parser.many(
            |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
            |p| p.match_value(KW_FUNC_END),
        )?;
        parser.eat_value(KW_FUNC_END)?;
        Ok(Stat::FunctionDef(FunctionDefStat {
            name_exp: Exp::Id(IdExp { name: name_tk.value }),
            args,
            blocks,
            pos: None,
        }))
    }

    fn parse_suffix_assign_stat(parser: &mut Parser, prefix_exp: Exp) -> Result<Stat, ParseError> {
        parser.skip();
        let var_list = Self::parse_var_list(parser)?;
        Ok(Stat::Assign(AssignStat {
            var_list,
            exp_list: vec![prefix_exp],
            pos: None,
        }))
    }

    fn parse_class_method_call_stat(
        parser: &mut Parser,
        prefix_exp: Exp,
    ) -> Result<Stat, ParseError> {
        parser.eat_any_value(&[KW_LAA1, KW_GAMLAA1])?;
        Ok(Stat::Call(CallStat {
            exp: prefix_exp,
            pos: None,
        }))
    }

    fn parse_list_assign_stat(parser: &mut Parser, prefix_exp: Exp) -> Result<Stat, ParseError> {
        parser.eat_value(KW_LST_ASSIGN)?;
        parser.eat_value(KW_DO)?;
        let varlist = Self::parse_var_list(parser)?;
        Ok(Stat::Assign(AssignStat {
            var_list: varlist,
            exp_list: vec![prefix_exp],
            pos: None,
        }))
    }

    fn parse_set_assign_stat(parser: &mut Parser, prefix_exp: Exp) -> Result<Stat, ParseError> {
        parser.eat_value(KW_SET_ASSIGN)?;
        parser.eat_value(KW_DO)?;
        let varlist = Self::parse_var_list(parser)?;
        Ok(Stat::Assign(AssignStat {
            var_list: varlist,
            exp_list: vec![prefix_exp],
            pos: None,
        }))
    }

    fn parse_stack_init_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let exps = ExpParser::parse_exp(parser)?;
        Ok(Stat::Assign(AssignStat {
            var_list: vec![exps.clone()],
            exp_list: vec![Exp::FuncCall(FuncCallExp {
                prefix_exp: Box::new(Exp::Id(IdExp { name: "stack".into() })),
                args: Vec::new(),
            })],
            pos: None,
        }))
    }

    fn parse_stack_push_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        parser.eat_value(KW_DO)?;
        let exps = ExpParser::parse_exp(parser)?;
        let args = ExpParser::parse_args(parser)?;
        Ok(Stat::MethodCall(MethodCallStat {
            name_exp: exps,
            method: Exp::Id(IdExp { name: "push".into() }),
            args,
            pos: None,
        }))
    }

    fn parse_stack_pop_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        parser.eat_value(KW_DO)?;
        let exps = ExpParser::parse_exp(parser)?;
        Ok(Stat::MethodCall(MethodCallStat {
            name_exp: exps,
            method: Exp::Id(IdExp { name: "pop".into() }),
            args: Vec::new(),
            pos: None,
        }))
    }

    fn parse_match_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let mut match_val = Vec::new();
        let mut match_block = Vec::new();
        let mut default_match_block = Vec::new();
        let match_id = ExpParser::parse_exp(parser)?;

        parser.eat_value(KW_DO)?;

        while !parser.match_value(KW_FUNC_END) {
            while parser.match_value("|") {
                parser.skip();
                if parser.match_value(KW_CASE) {
                    parser.skip();
                    match_val.push(ExpParser::parse_exp(parser)?);
                    parser.eat_value(KW_DO)?;
                    parser.eat_kind(TokenType::SepLCurly)?;
                    let block = parser.many(
                        |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
                        |p| p.match_kind(TokenType::SepRCurly),
                    )?;
                    parser.eat_kind(TokenType::SepRCurly)?;
                    match_block.push(block);
                } else if parser.match_value("_") {
                    parser.skip();
                    parser.eat_value(KW_DO)?;
                    parser.eat_kind(TokenType::SepLCurly)?;
                    default_match_block = parser.many(
                        |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
                        |p| p.match_kind(TokenType::SepRCurly),
                    )?;
                    parser.eat_kind(TokenType::SepRCurly)?;
                } else {
                    return Err(ParseError::syntax(
                        parser.peek_token().unwrap_or(&Token {
                            pos: Pos::simple(0, 0),
                            typ: TokenType::EOF,
                            value: "EOF".into(),
                        }),
                        parser.file_path,
                        "MatchBlock只允許`撞見`同`_`",
                        "用 `撞見` 指定 case，或用 `_` 作默認",
                    ));
                }
            }
        }

        parser.eat_value(KW_FUNC_END)?;
        Ok(Stat::Match(MatchStat {
            match_id,
            match_val,
            match_block,
            default_match_block,
            pos: None,
        }))
    }

    fn parse_for_each_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let id_list = ExpParser::parse_idlist(parser)?.unwrap_or_default();
        parser.eat_value(KW_IN)?;
        let exp_list = ExpParser::parse_exp_list(parser)?;
        parser.eat_value(KW_DO)?;
        parser.eat_kind(TokenType::SepLCurly)?;
        let blocks = parser.many(
            |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
            |p| p.match_kind(TokenType::SepRCurly),
        )?;
        parser.eat_kind(TokenType::SepRCurly)?;
        Ok(Stat::ForEach(ForEachStat {
            id_list,
            exp_list,
            blocks,
            pos: None,
        }))
    }

    fn parse_call_native_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let tk = parser.eat_kind(TokenType::CallNativeExpr)?;
        let code = if tk.value.len() > 8 {
            tk.value[3..tk.value.len() - 5].to_string()
        } else {
            tk.value
        };
        Ok(Stat::Extend(ExtendStat { code, pos: None }))
    }

    fn parse_pls_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        let func_name = ExpParser::parse_exp(parser)?;
        parser.eat_value(KW_LAA1)?;
        Ok(Stat::FuncCall(FuncCallStat {
            func_name,
            args: Vec::new(),
            pos: None,
        }))
    }

    fn parse_class_def(parser: &mut Parser, class_name: Exp) -> Result<Stat, ParseError> {
        parser.eat_kind(TokenType::SepLCurly)?;
        let class_extend = if parser.match_value(KW_EXTEND) {
            parser.skip();
            ExpParser::parse_exp_list(parser)?
        } else {
            Vec::new()
        };
        let class_blocks = parser.many(
            |p| Self::parse_class_block(p),
            |p| p.match_kind(TokenType::SepRCurly),
        )?;
        parser.eat_kind(TokenType::SepRCurly)?;
        Ok(Stat::ClassDef(ClassDefStat {
            class_name,
            class_extend,
            class_blocks,
            pos: None,
        }))
    }

    fn parse_class_block(parser: &mut Parser) -> Result<Stat, ParseError> {
        match parser.peek_value() {
            Some(v) if v == KW_METHOD => {
                parser.skip();
                let name_exp = ExpParser::parse_exp(parser)?;
                let args = ExpParser::parse_idlist(parser)?.unwrap_or_default();
                parser.eat_value(KW_DO)?;
                parser.eat_kind(TokenType::SepLCurly)?;
                let blocks = parser.many(
                    |p| Self::parse(p).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
                    |p| p.match_kind(TokenType::SepRCurly),
                )?;
                parser.eat_kind(TokenType::SepRCurly)?;
                Ok(Stat::MethodDef(MethodDefStat {
                    name_exp,
                    args,
                    class_blocks: blocks,
                    pos: None,
                }))
            }
            Some(v) if v == KW_CLASS_ASSIGN => {
                parser.skip();
                Self::parse_class_assign_stat(parser)
            }
            Some(v) if v == KW_CLASS_INIT => {
                parser.skip();
                parser.eat_value(KW_DO)?;
                parser.eat_kind(TokenType::SepLCurly)?;
                let attrs = ExpParser::parse_attrs_def(parser)?;
                parser.eat_kind(TokenType::SepRCurly)?;
                Ok(Stat::AttrDef(AttrDefStat { attrs_list: attrs, pos: None }))
            }
            _ => Self::parse(parser).map(|s| s.unwrap_or(Stat::Pass(PassStat { pos: None }))),
        }
    }

    fn parse_class_assign_stat(parser: &mut Parser) -> Result<Stat, ParseError> {
        Err(ParseError::syntax(
            parser.peek_token().unwrap_or(&Token {
                pos: Pos::simple(0, 0),
                typ: TokenType::EOF,
                value: "EOF".into(),
            }),
            parser.file_path,
            "`parse_class_assign_stat` is not defined in the Python source",
            "please implement class assignment parsing",
        ))
    }

    fn parse_macro_def(parser: &mut Parser, _macro_name: Exp) -> Result<Stat, ParseError> {
        parser.eat_value(KW_DO)?;
        let mut match_rules: Vec<Vec<crate::ast::MacroPatItem>> = Vec::new();
        let mut match_blocks = Vec::new();

        while !parser.match_value(KW_FUNC_END) {
            while parser.match_value("|") {
                parser.skip();
                parser.eat_kind(TokenType::SepLParen)?;
                let cur_match_rules = parser.many(
                    |p| MacroPatParser::parse_macro_rule(p),
                    |p| p.match_kind(TokenType::SepRParen),
                )?;
                parser.eat_kind(TokenType::SepRParen)?;
                match_rules.push(cur_match_rules);
                parser.eat_value(KW_DO)?;
                let body = MacroBodyParser::parse_tokentrees(parser)?;
                match_blocks.push(body);
            }
        }

        parser.eat_value(KW_FUNC_END)?;
        Ok(Stat::MacroDef(MacroDefStat {
            match_pats: match_rules,
            match_block: match_blocks,
            pos: None,
        }))
    }
}
