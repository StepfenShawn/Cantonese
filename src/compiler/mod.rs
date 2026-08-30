//! Python code generator for the Cantonese language.

use std::collections::HashMap;

use crate::ast::{
    AnnotationExp, AssertStat, AssignBlockStat, AssignExp, AssignStat, AttrDefStat, BinopExp,
    BreakStat, CallStat, ClassDefStat, CmdStat, ConcatExp, ContinueStat, DelStat, ExitStat, Exp,
    ExtendStat, FalseExp, ForEachStat, ForStat, FuncCallExp, FuncCallStat, FuncTypeDefStat,
    FunctionDefStat, GlobalStat, IdExp, IfElseExp, IfStat, ImportStat, LambdaExp, ListAccessExp,
    ListExp, ListInitStat, MapExp, MappingExp, MatchStat, MethodCallStat, MethodDefStat, NamesExp,
    NullExp, NumeralExp, ObjectAccessExp, ParensExp, PassStat, PrintStat, RaiseStat, ReturnStat,
    Stat, StringExp, TrueExp, TryStat, TypeStat, UnopExp, WhileStat,
};
use crate::lexer::{LexError, Lexer};
use crate::parser::{ParseError, Parser as CanParser, StatParser};

pub type LineMap = HashMap<usize, Vec<usize>>;

/// Error that can occur during Python code generation.
#[derive(Debug, thiserror::Error)]
pub enum CodegenError {
    #[error("unsupported AST node: {0}")]
    Unsupported(String),
    #[error("parse error: {0}")]
    Parse(#[from] ParseError),
    #[error("lex error: {0}")]
    Lex(#[from] LexError),
}

/// Python code generator.
pub struct Codegen {
    tab: String,
    line: usize,
    code: String,
    line_mmap: LineMap,
}

impl Default for Codegen {
    fn default() -> Self {
        Self::new()
    }
}

impl Codegen {
    pub fn new() -> Self {
        Self {
            tab: String::new(),
            line: 1,
            code: String::new(),
            line_mmap: HashMap::new(),
        }
    }

    /// Consume the generator and return the generated Python code and line map.
    pub fn into_code_and_line_map(self) -> (String, LineMap) {
        (self.code, self.line_mmap)
    }

    /// Generate Python code for a list of statements.
    pub fn codegen_stats(&mut self, stats: &[Stat]) -> Result<String, CodegenError> {
        for stat in stats {
            self.codegen_stat(stat)?;
        }
        Ok(self.code.clone())
    }

    fn update_line_map(&mut self, stat: &Stat, s: &str) {
        let start = self.line;
        self.line += s.chars().filter(|&c| c == '\n').count();
        let end = self.line;
        let pos = match stat {
            Stat::FuncCall(s) => s.pos.clone(),
            Stat::If(s) => s.pos.clone(),
            Stat::Print(s) => s.pos.clone(),
            Stat::Pass(s) => s.pos.clone(),
            Stat::Assign(s) => s.pos.clone(),
            Stat::AssignBlock(s) => s.pos.clone(),
            Stat::For(s) => s.pos.clone(),
            Stat::ForEach(s) => s.pos.clone(),
            Stat::While(s) => s.pos.clone(),
            Stat::ListInit(s) => s.pos.clone(),
            Stat::FunctionDef(s) => s.pos.clone(),
            Stat::FuncTypeDef(s) => s.pos.clone(),
            Stat::MethodDef(s) => s.pos.clone(),
            Stat::AttrDef(s) => s.pos.clone(),
            Stat::ClassDef(s) => s.pos.clone(),
            Stat::Import(s) => s.pos.clone(),
            Stat::Raise(s) => s.pos.clone(),
            Stat::Try(s) => s.pos.clone(),
            Stat::Global(s) => s.pos.clone(),
            Stat::Break(s) => s.pos.clone(),
            Stat::Continue(s) => s.pos.clone(),
            Stat::Type(s) => s.pos.clone(),
            Stat::Assert(s) => s.pos.clone(),
            Stat::Return(s) => s.pos.clone(),
            Stat::Del(s) => s.pos.clone(),
            Stat::Cmd(s) => s.pos.clone(),
            Stat::MethodCall(s) => s.pos.clone(),
            Stat::Call(s) => s.pos.clone(),
            Stat::Match(s) => s.pos.clone(),
            Stat::Extend(s) => s.pos.clone(),
            Stat::Exit(s) => s.pos.clone(),
            Stat::MacroDef(s) => s.pos.clone(),
        };
        if let Some(span) = pos {
            for py_lineno in start..end {
                let entry = self.line_mmap.entry(py_lineno).or_default();
                for can_lineno in span.start.line..=span.end.line {
                    if !entry.contains(&can_lineno) {
                        entry.push(can_lineno);
                    }
                }
            }
        }
    }

    fn emit(&mut self, s: &str, stat: &Stat) {
        let s = format!("{}{}", self.tab, s);
        self.update_line_map(stat, &s);
        self.code.push_str(&s);
    }

    pub fn codegen_expr(&mut self, exp: &Exp) -> Result<String, CodegenError> {
        match exp {
            Exp::String(StringExp { s, .. }) => Ok(format!("Str({})", s)),
            Exp::Numeral(NumeralExp { val, .. }) => Ok(val.clone()),
            Exp::Id(IdExp { name, .. }) => Ok(name.clone()),
            Exp::False(FalseExp { .. }) => Ok("False".to_string()),
            Exp::True(TrueExp { .. }) => Ok("True".to_string()),
            Exp::Null(NullExp { .. }) => Ok("None".to_string()),
            Exp::Annotation(AnnotationExp { exp, tyid, .. }) => {
                let exp_s = self.codegen_expr(exp)?;
                let tyid_s = self.codegen_expr(tyid)?;
                Ok(format!("{}:{}", exp_s, tyid_s))
            }
            Exp::Binop(BinopExp { op, exp1, exp2, .. }) => {
                let left = self.codegen_expr(exp1)?;
                let right = self.codegen_expr(exp2)?;
                Ok(format!("({} {} {})", left, op, right))
            }
            Exp::Mapping(MappingExp { exp1, exp2, .. }) => {
                let left = self.codegen_expr(exp1)?;
                let right = self.codegen_expr(exp2)?;
                Ok(format!("{}:{}", left, right))
            }
            Exp::ObjectAccess(ObjectAccessExp {
                prefix_exp,
                key_exp,
                ..
            }) => {
                let prefix = self.codegen_expr(prefix_exp)?;
                let key = self.codegen_expr(key_exp)?;
                Ok(format!("{}.{}", prefix, key))
            }
            Exp::ListAccess(ListAccessExp {
                prefix_exp,
                key_exp,
                ..
            }) => {
                let prefix = self.codegen_expr(prefix_exp)?;
                let key = self.codegen_expr(key_exp)?;
                Ok(format!("{}[{}]", prefix, key))
            }
            Exp::Unop(UnopExp { op, exp, .. }) => {
                let exp_s = self.codegen_expr(exp)?;
                Ok(format!("({} {})", op, exp_s))
            }
            Exp::FuncCall(FuncCallExp {
                prefix_exp, args, ..
            }) => {
                let prefix = self.codegen_expr(prefix_exp)?;
                let args_s = self.codegen_args(args)?;
                Ok(format!("{}({})", prefix, args_s))
            }
            Exp::Lambda(LambdaExp {
                id_list, blocks, ..
            }) => {
                let args_s = self.codegen_args(id_list)?;
                let body_s = self.codegen_args(blocks)?;
                Ok(format!("(lambda {} : {})", args_s, body_s))
            }
            Exp::IfElse(IfElseExp {
                if_cond_exp,
                if_exp,
                else_exp,
                ..
            }) => {
                let cond = self.codegen_expr(if_cond_exp)?;
                let then_ = self.codegen_expr(if_exp)?;
                let else_ = self.codegen_expr(else_exp)?;
                Ok(format!("({} if {} else {})", then_, cond, else_))
            }
            Exp::List(ListExp { elem_exps, .. }) => {
                let elems = self.codegen_args(elem_exps)?;
                Ok(format!("List([{}])", elems))
            }
            Exp::Map(MapExp { elem_exps, .. }) => {
                let elems = self.codegen_args(elem_exps)?;
                Ok(format!("{{{}}}", elems))
            }
            Exp::Assign(AssignExp { exp1, exp2, .. }) => {
                let left = self.codegen_expr(exp1)?;
                let right = self.codegen_expr(exp2)?;
                Ok(format!("{} = {}", left, right))
            }
            Exp::Parens(ParensExp { exp, .. }) => {
                let inner = self.codegen_expr(exp)?;
                Ok(format!("({})", inner))
            }
            Exp::Names(names) => {
                let parts: Vec<String> = names
                    .child
                    .iter()
                    .map(|c| self.codegen_expr(c))
                    .collect::<Result<Vec<_>, _>>()?;
                Ok(parts.join("."))
            }
            Exp::Concat(ConcatExp { exps, .. }) => {
                let parts = self.codegen_args(exps)?;
                Ok(format!("''.join(map(str, [{}]))", parts))
            }
            Exp::VarArg(_) => Ok("*args".to_string()),
            Exp::AttrAccess(_) => Err(CodegenError::Unsupported(
                "attribute access suffix in expression context".to_string(),
            )),
            Exp::MetaId(_) | Exp::PatRep(_) | Exp::BlockRep(_) | Exp::StatExpansion(_) => Err(
                CodegenError::Unsupported("macro-related expression node".to_string()),
            ),
        }
    }

    fn codegen_args(&mut self, args: &[Exp]) -> Result<String, CodegenError> {
        let mut s = String::new();
        for (i, arg) in args.iter().enumerate() {
            if i > 0 {
                s.push_str(", ");
            }
            s.push_str(&self.codegen_expr(arg)?);
        }
        Ok(s)
    }

    /// Extract the parameter name from an attribute definition.
    ///
    /// Attributes are written as `name: type` in Cantonese, but Python's
    /// `__init__` only needs the parameter name.
    fn attr_def_name(&mut self, attr: &Exp) -> Result<String, CodegenError> {
        match attr {
            Exp::Annotation(AnnotationExp { exp, .. }) => self.codegen_expr(exp),
            _ => self.codegen_expr(attr),
        }
    }

    pub fn codegen_stat(&mut self, stat: &Stat) -> Result<(), CodegenError> {
        match stat {
            Stat::Print(PrintStat { args, .. }) => {
                let args_s = self.codegen_args(args)?;
                self.emit(&format!("print({})\n", args_s), stat);
            }
            Stat::Assign(AssignStat {
                var_list, exp_list, ..
            }) => {
                let vars_s = self.codegen_args(var_list)?;
                let exps_s = self.codegen_args(exp_list)?;
                self.emit(&format!("{} = {}\n", vars_s, exps_s), stat);
            }
            Stat::AssignBlock(AssignBlockStat {
                var_list, exp_list, ..
            }) => {
                for (var, exp) in var_list.iter().zip(exp_list.iter()) {
                    let var_s = self.codegen_expr(var)?;
                    let exp_s = self.codegen_expr(exp)?;
                    self.emit(&format!("{} = {}\n", var_s, exp_s), stat);
                }
            }
            Stat::Exit(ExitStat { .. }) => {
                self.emit("exit()\n", stat);
            }
            Stat::Pass(PassStat { .. }) => {
                self.emit("pass\n", stat);
            }
            Stat::Break(BreakStat { .. }) => {
                self.emit("break\n", stat);
            }
            Stat::Continue(ContinueStat { .. }) => {
                self.emit("continue\n", stat);
            }
            Stat::If(IfStat {
                if_exp,
                if_block,
                elif_exps,
                elif_blocks,
                else_blocks,
                ..
            }) => {
                let cond_s = self.codegen_expr(if_exp)?;
                self.emit(&format!("if {}:\n", cond_s), stat);
                self.codegen_block(if_block)?;
                for (elif_exp, elif_block) in elif_exps.iter().zip(elif_blocks.iter()) {
                    let elif_s = self.codegen_expr(elif_exp)?;
                    self.emit(&format!("elif {}:\n", elif_s), stat);
                    self.codegen_block(elif_block)?;
                }
                if !else_blocks.is_empty() {
                    self.emit("else:\n", stat);
                    self.codegen_block(&else_blocks[0])?;
                }
            }
            Stat::Try(TryStat {
                try_blocks,
                except_exps,
                except_blocks,
                finally_blocks,
                ..
            }) => {
                self.emit("try:\n", stat);
                self.codegen_block(try_blocks)?;
                for (except_exp, except_block) in except_exps.iter().zip(except_blocks.iter()) {
                    let except_s = self.codegen_expr(except_exp)?;
                    self.emit(&format!("except {}:\n", except_s), stat);
                    self.codegen_block(except_block)?;
                }
                if !finally_blocks.is_empty() {
                    self.emit("finally:\n", stat);
                    self.codegen_block(finally_blocks)?;
                }
            }
            Stat::Raise(RaiseStat { name_exp, .. }) => {
                let exp_s = self.codegen_expr(name_exp)?;
                self.emit(&format!("raise {}\n", exp_s), stat);
            }
            Stat::While(WhileStat {
                cond_exp, blocks, ..
            }) => {
                let cond_s = self.codegen_expr(cond_exp)?;
                self.emit(&format!("while {}:\n", cond_s), stat);
                self.codegen_block(blocks)?;
            }
            Stat::For(ForStat {
                var,
                from_exp,
                to_exp,
                blocks,
                ..
            }) => {
                let var_s = self.codegen_expr(var)?;
                let from_s = self.codegen_expr(from_exp)?;
                let to_s = self.codegen_expr(to_exp)?;
                self.emit(
                    &format!("for {} in range({}, {}):\n", var_s, from_s, to_s),
                    stat,
                );
                self.codegen_block(blocks)?;
            }
            Stat::FunctionDef(FunctionDefStat {
                name_exp,
                args,
                blocks,
                ..
            }) => {
                let name_s = self.codegen_expr(name_exp)?;
                let args_s = self.codegen_args(args)?;
                self.emit(&format!("def {}({}):\n", name_s, args_s), stat);
                self.codegen_block(blocks)?;
            }
            Stat::FuncCall(FuncCallStat {
                func_name, args, ..
            }) => {
                let name_s = self.codegen_expr(func_name)?;
                let args_s = self.codegen_args(args)?;
                self.emit(&format!("{}({})\n", name_s, args_s), stat);
            }
            Stat::Import(ImportStat { names, .. }) => {
                let imports = self.codegen_import(names)?;
                for import in imports {
                    self.emit(&format!("{}\n", import), stat);
                }
            }
            Stat::Return(ReturnStat { exps, .. }) => {
                let exps_s = self.codegen_args(exps)?;
                self.emit(&format!("return {}\n", exps_s), stat);
            }
            Stat::Del(DelStat { exps, .. }) => {
                let exps_s = self.codegen_args(exps)?;
                self.emit(&format!("del {}\n", exps_s), stat);
            }
            Stat::Type(TypeStat { exps, .. }) => {
                if let Some(exp) = exps.first() {
                    let exp_s = self.codegen_expr(exp)?;
                    self.emit(&format!("print(type({}))\n", exp_s), stat);
                }
            }
            Stat::Assert(AssertStat { exps, .. }) => {
                let exp_s = self.codegen_expr(exps)?;
                self.emit(&format!("assert {}\n", exp_s), stat);
            }
            Stat::ClassDef(ClassDefStat {
                class_name,
                class_extend,
                class_blocks,
                ..
            }) => {
                let name_s = self.codegen_expr(class_name)?;
                let extend_s = if class_extend.is_empty() {
                    String::new()
                } else {
                    self.codegen_args(class_extend)?
                };
                self.emit(&format!("class {}({}):\n", name_s, extend_s), stat);
                self.codegen_block(class_blocks)?;
            }
            Stat::MethodDef(MethodDefStat {
                name_exp,
                args,
                class_blocks,
                ..
            }) => {
                let name_s = self.codegen_expr(name_exp)?;
                let args_s = self.codegen_args(args)?;
                self.emit(&format!("def {}({}):\n", name_s, args_s), stat);
                self.codegen_block(class_blocks)?;
            }
            Stat::AttrDef(AttrDefStat { attrs_list, .. }) => {
                let names: Vec<String> = attrs_list
                    .iter()
                    .map(|attr| self.attr_def_name(attr))
                    .collect::<Result<Vec<_>, _>>()?;
                let args_str = names
                    .iter()
                    .map(|name| format!("{}=None", name))
                    .collect::<Vec<_>>()
                    .join(", ");
                let attr_str = names
                    .iter()
                    .map(|name| format!("自己.{}={}", name, name))
                    .collect::<Vec<_>>()
                    .join(";");
                self.emit(
                    &format!("def __init__(自己, {}):{}\n", args_str, attr_str),
                    stat,
                );
            }
            Stat::MethodCall(MethodCallStat {
                name_exp,
                method,
                args,
                ..
            }) => {
                let name_s = self.codegen_expr(name_exp)?;
                let method_s = match method {
                    Exp::Id(IdExp { name, .. }) => name.clone(),
                    _ => self.codegen_expr(method)?,
                };
                let args_s = self.codegen_args(args)?;
                self.emit(&format!("{}.{}({})\n", name_s, method_s, args_s), stat);
            }
            Stat::Cmd(CmdStat { args, .. }) => {
                let args_s = self.codegen_args(args)?;
                self.emit(&format!("os.system({})\n", args_s), stat);
            }
            Stat::Call(CallStat { exp, .. }) => {
                let exp_s = self.codegen_expr(exp)?;
                self.emit(&format!("{}\n", exp_s), stat);
            }
            Stat::Global(GlobalStat { idlist, .. }) => {
                let ids_s = self.codegen_args(idlist)?;
                self.emit(&format!("global {}\n", ids_s), stat);
            }
            Stat::Extend(ExtendStat { code, .. }) => {
                for line in code.split('\n') {
                    self.emit(&format!("{}\n", line), stat);
                }
            }
            Stat::Match(MatchStat {
                match_id,
                match_val,
                match_block,
                default_match_block,
                ..
            }) => {
                for (i, (val, block)) in match_val.iter().zip(match_block.iter()).enumerate() {
                    let keyword = if i == 0 { "if" } else { "elif" };
                    let match_s = self.codegen_expr(match_id)?;
                    let val_s = self.codegen_expr(val)?;
                    self.emit(&format!("{} {} == {}:\n", keyword, match_s, val_s), stat);
                    self.codegen_block(block)?;
                }
                if !default_match_block.is_empty() {
                    self.emit("else:\n", stat);
                    self.codegen_block(default_match_block)?;
                }
            }
            Stat::ForEach(ForEachStat {
                id_list,
                exp_list,
                blocks,
                ..
            }) => {
                let ids_s = self.codegen_args(id_list)?;
                let exps_s = self.codegen_args(exp_list)?;
                self.emit(&format!("for {} in {}:\n", ids_s, exps_s), stat);
                self.codegen_block(blocks)?;
            }
            Stat::ListInit(ListInitStat { .. }) => {
                // No-op; used only as a syntactic marker.
            }
            Stat::FuncTypeDef(FuncTypeDefStat { .. }) => {
                // Type signatures are not emitted as Python code.
            }
            Stat::MacroDef(_) => {
                // Macros are expanded at parse time; nothing to emit.
            }
        }
        Ok(())
    }

    fn codegen_block(&mut self, blocks: &[Stat]) -> Result<(), CodegenError> {
        let saved = self.tab.clone();
        self.tab.push('\t');
        if blocks.is_empty() {
            // Emit a pass without a source span to avoid line-map noise.
            self.code.push_str(&format!("{}pass\n", self.tab));
            self.line += 1;
        } else {
            for block in blocks {
                self.codegen_stat(block)?;
            }
        }
        self.tab = saved;
        Ok(())
    }

    /// Generate Python import statements from a `NamesExp`.
    fn codegen_import(&mut self, names: &Exp) -> Result<Vec<String>, CodegenError> {
        let traces = names_to_traces(names);
        let mut out = Vec::new();
        for resolved in traces {
            if resolved.is_empty() {
                continue;
            }
            if resolved[0] == "python" || resolved[0] == "py" {
                // python::xxx becomes `import xxx`; python::a::b becomes
                // `from a import b`; python::a::* becomes `from a import *`.
                if resolved.len() == 2 {
                    out.push(format!("import {}", resolved[1]));
                } else if resolved.len() > 2 {
                    let module = resolved[1..resolved.len() - 1].join(".");
                    let name = &resolved[resolved.len() - 1];
                    if name == "*" {
                        out.push(format!("from {} import *", module));
                    } else {
                        out.push(format!("from {} import {}", module, name));
                    }
                }
                continue;
            }

            if resolved[0] == "std" {
                if resolved.len() == 2 {
                    out.push(format!("__cantonese_import__('{}')", resolved[1]));
                }
                // TODO: fix here
                // else if resolved.len() > 2 {
                //     let module = resolved[1..resolved.len() - 1].join(".");
                //     let name = &resolved[resolved.len() - 1];
                //     if name == "*" {
                //         out.push(format!("from __cantonese_import__('{}') import *", module));
                //     } else {
                //         out.push(format!("from __cantonese_import__('{}') import {}", module, name));
                //     }
                // }
                continue;
            }

            out.push(import_stmt(&resolved));
        }
        Ok(out)
    }
}

/// Convert a `NamesExp` into a list of fully-qualified import paths.
fn names_to_traces(exp: &Exp) -> Vec<Vec<String>> {
    match exp {
        Exp::Id(IdExp { name, .. }) => vec![vec![name.clone()]],
        Exp::Names(NamesExp { child, .. }) if !child.is_empty() => {
            let (head, tail) = child.split_first().unwrap();

            // Special case: `A::{B, C}` is parsed as
            // NamesExp([A, NamesExp([B, C])]). Distribute over the alternatives.
            if tail.len() == 1 {
                if let Exp::Names(NamesExp {
                    child: set_children,
                    ..
                }) = &tail[0]
                {
                    let mut result = Vec::new();
                    for alt in set_children {
                        for head_trace in names_to_traces(head) {
                            for alt_trace in names_to_traces(alt) {
                                let mut combined = head_trace.clone();
                                combined.extend(alt_trace);
                                result.push(combined);
                            }
                        }
                    }
                    return result;
                }
            }

            let mut result = Vec::new();
            for head_trace in names_to_traces(head) {
                for tail_trace in names_to_traces_for_list(tail) {
                    let mut combined = head_trace.clone();
                    combined.extend(tail_trace);
                    result.push(combined);
                }
            }
            result
        }
        _ => Vec::new(),
    }
}

fn names_to_traces_for_list(exps: &[Exp]) -> Vec<Vec<String>> {
    if exps.is_empty() {
        return vec![Vec::new()];
    }
    let mut result = Vec::new();
    for exp in exps {
        for trace in names_to_traces(exp) {
            result.push(trace);
        }
    }
    result
}

fn import_stmt(path: &[String]) -> String {
    if path.is_empty() {
        return String::new();
    }
    if path.len() == 1 {
        format!("import {}", path[0])
    } else {
        format!(
            "from {} import {}",
            path[..path.len() - 1].join("."),
            path[path.len() - 1]
        )
    }
}

/// Compile Cantonese source into Python source and a line map.
pub fn to_python(source: &str, filename: &str) -> Result<(String, LineMap), CodegenError> {
    let mut lexer = Lexer::new(filename.to_string(), source);
    let tokens = lexer.tokenize_all()?;
    let mut parser = CanParser::new(&tokens, filename);
    let stats = StatParser::parse_stats(&mut parser)?;
    let mut codegen = Codegen::new();
    codegen.codegen_stats(&stats)?;
    Ok(codegen.into_code_and_line_map())
}

#[cfg(test)]
mod tests {
    use super::*;

    fn compile(source: &str) -> String {
        to_python(source, "<test>").unwrap().0
    }

    #[test]
    fn test_print() {
        assert_eq!(compile("畀我睇下 5 點樣先？\n"), "print(5)\n");
    }

    #[test]
    fn test_assign() {
        assert_eq!(compile("介紹返 x 係 5\n"), "x = 5\n");
    }

    #[test]
    fn test_python_import_single() {
        assert_eq!(compile("使下 python::math\n"), "import math\n");
    }

    #[test]
    fn test_python_import_nested() {
        assert_eq!(
            compile("使下 python::math::sqrt\n"),
            "from math import sqrt\n"
        );
    }

    #[test]
    fn test_python_import_braced() {
        assert_eq!(
            compile("使下 python::{math::sqrt, re::*}\n"),
            "from math import sqrt\nfrom re import *\n"
        );
    }

    #[test]
    fn test_class_def() {
        assert_eq!(
            compile(
                "介紹返 Duck 係 乜X {\n佢個老豆叫 |object|\n佢有啲咩?? => { 性別: 公家嘢 }\n佢識得 游 |自己| => {\n畀我睇下 1 點樣先？\n}\n}\n"
            ),
            "class Duck(object):\n\tdef __init__(自己, 性別=None):自己.性別=性別\n\tdef 游(自己):\n\t\tprint(1)\n"
        );
    }
}
