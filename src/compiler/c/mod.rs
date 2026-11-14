use std::collections::HashMap;

use crate::ast::{
    AnnotationExp, AssignBlockStat, AssignExp, AssignStat, AttrDefStat, BinopExp, CallStat,
    ClassDefStat, ConcatExp, Exp, FalseExp, ForEachStat, ForStat, FuncCallExp, FuncCallStat,
    FunctionDefStat, IdExp, IfElseExp, IfStat, ListAccessExp, ListExp, MapExp, MappingExp,
    MethodDefStat, NamesExp, NullExp, NumeralExp, ObjectAccessExp, ParensExp, PrintStat,
    ReturnStat, Stat, StringExp, TrueExp, TypeStat, UnopExp, WhileStat,
};
use crate::lexer::Lexer;
use crate::lexer::span::Span;
use crate::parser::{Parser as CanParser, StatParser};

use super::{CodegenError, LineMap};
mod modules;

pub const RUNTIME_H: &str = include_str!("../../../runtime/runtime.h");
pub const RUNTIME_C: &str = include_str!("../../../runtime/runtime.c");

/// C code generator.
pub struct CCodegen {
    tab: String,
    line: usize,
    code: String,
    line_mmap: LineMap,
    id_map: HashMap<String, String>,
    next_id: usize,
    functions: HashMap<String, String>,
    classes: HashMap<String, String>,
    methods: HashMap<String, String>,
    function_depth: usize,
    temp_id: usize,
}

impl Default for CCodegen {
    fn default() -> Self {
        Self::new()
    }
}

impl CCodegen {
    pub fn new() -> Self {
        Self {
            tab: String::new(),
            line: 1,
            code: String::new(),
            line_mmap: HashMap::new(),
            id_map: HashMap::new(),
            next_id: 0,
            functions: HashMap::new(),
            classes: HashMap::new(),
            methods: HashMap::new(),
            function_depth: 0,
            temp_id: 0,
        }
    }

    /// Consume the generator and return the generated C code and line map.
    pub fn into_code_and_line_map(self) -> (String, LineMap) {
        (self.code, self.line_mmap)
    }

    fn ident(&mut self, name: &str) -> String {
        if let Some(id) = self.id_map.get(name) {
            return id.clone();
        }
        let id = format!("v{}", self.next_id);
        self.next_id += 1;
        self.id_map.insert(name.to_string(), id.clone());
        id
    }

    fn fresh_temp(&mut self, prefix: &str) -> String {
        let id = format!("__{}_{}", prefix, self.temp_id);
        self.temp_id += 1;
        id
    }

    fn push_raw(&mut self, text: &str) {
        self.line += text.bytes().filter(|&b| b == b'\n').count();
        self.code.push_str(text);
    }

    fn emit_line(&mut self, text: &str, span: Option<&Span>) {
        let start = self.line;
        let line = format!("{}{}\n", self.tab, text);
        self.line += 1;
        self.code.push_str(&line);
        if let Some(span) = span {
            for c_line in start..self.line {
                let entry = self.line_mmap.entry(c_line).or_default();
                for can_line in span.start.line..=span.end.line {
                    if !entry.contains(&can_line) {
                        entry.push(can_line);
                    }
                }
            }
        }
    }

    fn emit_stat(&mut self, text: &str, stat: &Stat) {
        self.emit_line(text, stat_span(stat));
    }

    /// Generate a complete C translation unit.
    pub fn codegen_program(&mut self, stats: &[Stat]) -> Result<String, CodegenError> {
        let mut functions: Vec<&FunctionDefStat> = Vec::new();
        for stat in stats {
            if let Stat::FunctionDef(function) = stat {
                let name = match &function.name_exp {
                    Exp::Id(IdExp { name, .. }) => name.clone(),
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "function name must be an identifier".to_string(),
                        ));
                    }
                };
                let id = self.ident(&name);
                let c_name = format!("cantonese_fn_{}", id);
                self.functions.insert(name, c_name);
                functions.push(function);
            }
        }

        let mut classes: Vec<&ClassDefStat> = Vec::new();
        let mut method_definitions: Vec<(String, &MethodDefStat)> = Vec::new();
        for stat in stats {
            if let Stat::ClassDef(class) = stat {
                let class_name = class_name(class)?;
                let class_id = self.ident(&class_name);
                self.classes.insert(class_name.clone(), class_id.clone());
                classes.push(class);

                for block in &class.class_blocks {
                    if let Stat::MethodDef(method) = block {
                        let method_name = method_name(method)?;
                        let key = format!("{}::{}", class_name, method_name);
                        let c_name = format!("cantonese_method_{}", self.fresh_temp("method"));
                        self.methods.insert(key, c_name.clone());
                        method_definitions.push((c_name, method));
                    }
                }
            }
        }

        self.push_raw("/* Generated by the Cantonese C backend. */\n");
        self.push_raw("#include \"runtime.h\"\n\n");

        for function in &functions {
            let name = match &function.name_exp {
                Exp::Id(IdExp { name, .. }) => name,
                _ => unreachable!(),
            };
            let c_name = self.functions.get(name).unwrap();
            self.push_raw(&format!(
                "static CanValue {}(int argc, CanValue *argv);\n",
                c_name
            ));
        }
        if !functions.is_empty() {
            self.push_raw("\n");
        }

        for class in &classes {
            let name = class_name(class)?;
            let id = self.classes.get(&name).unwrap();
            self.push_raw(&format!("static CanValue {};\n", id));
        }
        if !classes.is_empty() {
            self.push_raw("\n");
        }

        for function in &functions {
            self.codegen_function(function)?;
            self.push_raw("\n");
        }

        for (c_name, method) in &method_definitions {
            self.codegen_callable(c_name, &method.args, &method.class_blocks)?;
            self.push_raw("\n");
        }

        self.push_raw("int main(void) {\n");
        let saved_tab = self.tab.clone();
        self.tab = "    ".to_string();

        let body: Vec<Stat> = stats
            .iter()
            .filter(|stat| !matches!(stat, Stat::FunctionDef(_)))
            .cloned()
            .collect();
        let mut vars = Vec::new();
        collect_assigned(&body, &mut vars);
        for var in vars {
            let id = self.ident(&var);
            self.emit_line(&format!("CanValue {} = can_nil();", id), None);
        }
        for stat in &body {
            self.codegen_stat(stat)?;
        }
        self.emit_line("return 0;", None);

        self.tab = saved_tab;
        self.push_raw("}\n");
        Ok(self.code.clone())
    }

    fn function_c_name(&self, function: &FunctionDefStat) -> Result<String, CodegenError> {
        match &function.name_exp {
            Exp::Id(IdExp { name, .. }) => {
                self.functions.get(name).cloned().ok_or_else(|| {
                    CodegenError::Unsupported(format!("unknown function `{}`", name))
                })
            }
            _ => Err(CodegenError::Unsupported(
                "function name must be an identifier".to_string(),
            )),
        }
    }

    fn function_args(&mut self, args: &[Exp]) -> Result<Vec<String>, CodegenError> {
        let mut ids = Vec::new();
        for arg in args {
            let name = match arg {
                Exp::Id(IdExp { name, .. }) => name,
                Exp::Annotation(annotation) => match annotation.exp.as_ref() {
                    Exp::Id(IdExp { name, .. }) => name,
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "function parameter must be an identifier".to_string(),
                        ));
                    }
                },
                _ => {
                    return Err(CodegenError::Unsupported(
                        "function parameter must be an identifier".to_string(),
                    ));
                }
            };
            ids.push(self.ident(name));
        }
        Ok(ids)
    }

    fn codegen_function(&mut self, function: &FunctionDefStat) -> Result<(), CodegenError> {
        let c_name = self.function_c_name(function)?;
        self.codegen_callable(&c_name, &function.args, &function.blocks)
    }

    fn codegen_callable(
        &mut self,
        c_name: &str,
        args: &[Exp],
        blocks: &[Stat],
    ) -> Result<(), CodegenError> {
        let arg_ids = self.function_args(args)?;

        let mut vars = Vec::new();
        collect_assigned(blocks, &mut vars);

        self.push_raw(&format!(
            "static CanValue {}(int argc, CanValue *argv) {{\n",
            c_name
        ));
        let saved_tab = self.tab.clone();
        self.tab = "    ".to_string();

        self.emit_line("(void)argc;", None);
        self.emit_line("(void)argv;", None);
        for (index, arg) in arg_ids.iter().enumerate() {
            self.emit_line(
                &format!(
                    "CanValue {} = argc > {} ? argv[{}] : can_nil();",
                    arg, index, index
                ),
                None,
            );
        }
        for var in vars {
            let id = self.ident(&var);
            if !arg_ids.contains(&id) {
                self.emit_line(&format!("CanValue {} = can_nil();", id), None);
            }
        }

        self.function_depth += 1;
        for stat in blocks {
            self.codegen_stat(stat)?;
        }
        self.function_depth -= 1;

        self.emit_line("return can_nil();", None);
        self.tab = saved_tab;
        self.push_raw("}\n");
        Ok(())
    }

    fn codegen_stat(&mut self, stat: &Stat) -> Result<(), CodegenError> {
        match stat {
            Stat::Print(PrintStat { args, .. }) => {
                let values = self.exprs(args)?;
                if values.is_empty() {
                    self.emit_stat("can_print_values(0, NULL);", stat);
                } else {
                    self.emit_stat(
                        &format!(
                            "can_print_values({}, (CanValue[]){{{}}});",
                            values.len(),
                            values.join(", ")
                        ),
                        stat,
                    );
                }
            }
            Stat::Exit(_) => {
                self.emit_stat("can_exit(0);", stat);
            }
            Stat::Pass(_) => {
                self.emit_stat(";", stat);
            }
            Stat::Break(_) => {
                self.emit_stat("break;", stat);
            }
            Stat::Continue(_) => {
                self.emit_stat("continue;", stat);
            }
            Stat::Assign(AssignStat {
                var_list, exp_list, ..
            })
            | Stat::AssignBlock(AssignBlockStat {
                var_list, exp_list, ..
            }) => {
                for (var, exp) in var_list.iter().zip(exp_list.iter()) {
                    self.codegen_assign(var, exp, stat)?;
                }
            }
            Stat::If(IfStat {
                if_exp,
                if_block,
                elif_exps,
                elif_blocks,
                else_blocks,
                ..
            }) => {
                let cond = self.expr(if_exp)?;
                self.emit_stat(&format!("if (can_truthy({})) {{", cond), stat);
                self.codegen_block(if_block)?;
                for (elif_exp, elif_block) in elif_exps.iter().zip(elif_blocks.iter()) {
                    let cond = self.expr(elif_exp)?;
                    self.emit_line(
                        &format!("}} else if (can_truthy({})) {{", cond),
                        stat_span(stat),
                    );
                    self.codegen_block(elif_block)?;
                }
                if !else_blocks.is_empty() {
                    self.emit_line("} else {", stat_span(stat));
                    self.codegen_block(&else_blocks[0])?;
                }
                self.emit_line("}", stat_span(stat));
            }
            Stat::While(WhileStat {
                cond_exp, blocks, ..
            }) => {
                let cond = self.expr(cond_exp)?;
                self.emit_stat(&format!("while (can_truthy({})) {{", cond), stat);
                self.codegen_block(blocks)?;
                self.emit_line("}", stat_span(stat));
            }
            Stat::For(ForStat {
                var,
                from_exp,
                to_exp,
                blocks,
                ..
            }) => {
                let var_id = match var {
                    Exp::Id(IdExp { name, .. }) => self.ident(name),
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "for-loop variable must be an identifier".to_string(),
                        ));
                    }
                };
                let from = self.expr(from_exp)?;
                let to = self.expr(to_exp)?;
                self.emit_stat(
                    &format!(
                        "for ({} = {}; can_truthy(can_lt({}, {})); {} = can_add({}, can_int(1))) {{",
                        var_id,
                        from,
                        var_id,
                        to,
                        var_id,
                        var_id
                    ),
                    stat,
                );
                self.codegen_block(blocks)?;
                self.emit_line("}", stat_span(stat));
            }
            Stat::ForEach(ForEachStat {
                id_list,
                exp_list,
                blocks,
                ..
            }) => {
                if id_list.len() != 1 || exp_list.len() != 1 {
                    return Err(CodegenError::Unsupported(
                        "only single-target for-each loops are supported by the C backend"
                            .to_string(),
                    ));
                }
                let id = match &id_list[0] {
                    Exp::Id(IdExp { name, .. }) => self.ident(name),
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "for-each variable must be an identifier".to_string(),
                        ));
                    }
                };
                let iterable = self.expr(&exp_list[0])?;
                let iter = self.fresh_temp("iter");
                let index = self.fresh_temp("index");
                self.emit_stat("{", stat);
                let saved_tab = self.tab.clone();
                self.tab.push_str("    ");
                self.emit_line(&format!("CanValue {} = {};", iter, iterable), None);
                self.emit_line(
                    &format!(
                        "if (({}).tag != CAN_LIST) can_panic(\"value is not iterable\");",
                        iter
                    ),
                    None,
                );
                self.emit_line(
                    &format!(
                        "for (size_t {} = 0; {} < ({}).v.list->len; {}++) {{",
                        index, index, iter, index
                    ),
                    None,
                );
                self.tab.push_str("    ");
                self.emit_line(
                    &format!("{} = ({}).v.list->items[{}];", id, iter, index),
                    None,
                );
                for block in blocks {
                    self.codegen_stat(block)?;
                }
                self.tab = saved_tab.clone();
                self.emit_line("}", None);
                self.tab = saved_tab;
                self.emit_line("}", None);
            }
            Stat::FunctionDef(_) => {
                return Err(CodegenError::Unsupported(
                    "nested function definitions are not supported by the C backend".to_string(),
                ));
            }
            Stat::Return(ReturnStat { exps, .. }) => {
                if self.function_depth == 0 {
                    return Err(CodegenError::Unsupported(
                        "`return` outside a function is not supported by the C backend".to_string(),
                    ));
                }
                match exps.len() {
                    0 => self.emit_stat("return can_nil();", stat),
                    1 => {
                        let value = self.expr(&exps[0])?;
                        self.emit_stat(&format!("return {};", value), stat);
                    }
                    _ => {
                        let value = self.make_list_expr(exps)?;
                        self.emit_stat(&format!("return {};", value), stat);
                    }
                }
            }
            Stat::Call(CallStat { exp, .. }) => {
                let value = self.expr(exp)?;
                self.emit_stat(&format!("(void)({});", value), stat);
            }
            Stat::FuncCall(FuncCallStat {
                func_name, args, ..
            }) => {
                let call = self.call_expr(func_name, args)?;
                self.emit_stat(&format!("(void)({});", call), stat);
            }
            Stat::Type(TypeStat { exps, .. }) => {
                if let Some(exp) = exps.first() {
                    let value = self.expr(exp)?;
                    self.emit_stat(
                        &format!(
                            "can_print_values(1, (CanValue[]){{can_string(can_type_name({}))}});",
                            value
                        ),
                        stat,
                    );
                }
            }
            Stat::ClassDef(ClassDefStat {
                class_name: name_exp,
                class_extend,
                class_blocks,
                ..
            }) => {
                let name = match name_exp {
                    Exp::Id(IdExp { name, .. }) => name.clone(),
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "class name must be an identifier".to_string(),
                        ));
                    }
                };
                let class_var = match self.classes.get(&name) {
                    Some(id) => id.clone(),
                    None => self.ident(&name),
                };
                let parent = match class_extend.first() {
                    Some(exp) => match exp {
                        Exp::Id(IdExp { name, .. }) => self
                            .classes
                            .get(name)
                            .cloned()
                            .unwrap_or_else(|| "can_nil()".to_string()),
                        _ => self.expr(exp)?,
                    },
                    None => "can_nil()".to_string(),
                };

                self.emit_stat(&format!("{} = can_nil();", class_var), stat);
                self.emit_line(
                    &format!(
                        "{} = can_class_new({}, {});",
                        class_var,
                        c_escape_string(&name),
                        parent
                    ),
                    stat_span(stat),
                );

                for block in class_blocks {
                    match block {
                        Stat::AttrDef(AttrDefStat { attrs_list, .. }) => {
                            for attr in attrs_list {
                                let attr = attr_def_name(attr)?;
                                self.emit_line(
                                    &format!(
                                        "can_class_add_attr({}, {}, can_nil());",
                                        class_var,
                                        c_escape_string(&attr)
                                    ),
                                    stat_span(stat),
                                );
                            }
                        }
                        Stat::MethodDef(method) => {
                            let method_name = method_name(method)?;
                            let key = format!("{}::{}", name, method_name);
                            let c_name = self.methods.get(&key).cloned().ok_or_else(|| {
                                CodegenError::Unsupported(format!(
                                    "unknown method `{}` on class `{}`",
                                    method_name, name
                                ))
                            })?;
                            self.emit_line(
                                &format!(
                                    "can_class_add_method({}, {}, {});",
                                    class_var,
                                    c_escape_string(&method_name),
                                    c_name
                                ),
                                stat_span(stat),
                            );
                        }
                        Stat::Pass(_) => {}
                        other => {
                            return Err(CodegenError::Unsupported(format!(
                                "class body statement is not supported by the C backend yet: {}",
                                stat_kind(other)
                            )));
                        }
                    }
                }
            }
            other => {
                return Err(CodegenError::Unsupported(format!(
                    "statement is not supported by the C backend yet: {}",
                    stat_kind(other)
                )));
            }
        }
        Ok(())
    }

    fn codegen_assign(&mut self, var: &Exp, exp: &Exp, stat: &Stat) -> Result<(), CodegenError> {
        let value = self.expr(exp)?;
        match var {
            Exp::Id(IdExp { name, .. }) => {
                let id = self.ident(name);
                self.emit_stat(&format!("{} = {};", id, value), stat);
            }
            Exp::ListAccess(ListAccessExp {
                prefix_exp,
                key_exp,
                ..
            }) => {
                let container = self.expr(prefix_exp)?;
                let key = self.expr(key_exp)?;
                self.emit_stat(
                    &format!("can_set_index({}, {}, {});", container, key, value),
                    stat,
                );
            }
            Exp::ObjectAccess(ObjectAccessExp {
                prefix_exp,
                key_exp,
                ..
            }) => {
                let object = self.expr(prefix_exp)?;
                let name = match key_exp.as_ref() {
                    Exp::Id(IdExp { name, .. }) => name,
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "attribute assignment requires an identifier".to_string(),
                        ));
                    }
                };
                let name = c_escape_string(name);
                self.emit_stat(
                    &format!("can_set_attr({}, {}, {});", object, name, value),
                    stat,
                );
            }
            _ => {
                return Err(CodegenError::Unsupported(
                    "unsupported assignment target".to_string(),
                ));
            }
        }
        Ok(())
    }

    fn codegen_block(&mut self, blocks: &[Stat]) -> Result<(), CodegenError> {
        let saved = self.tab.clone();
        self.tab.push_str("    ");
        for stat in blocks {
            self.codegen_stat(stat)?;
        }
        self.tab = saved;
        Ok(())
    }

    fn exprs(&mut self, exps: &[Exp]) -> Result<Vec<String>, CodegenError> {
        exps.iter().map(|exp| self.expr(exp)).collect()
    }

    fn make_list_expr(&mut self, exps: &[Exp]) -> Result<String, CodegenError> {
        let values = self.exprs(exps)?;
        if values.is_empty() {
            Ok("can_list_from(0, NULL)".to_string())
        } else {
            Ok(format!(
                "can_list_from({}, (CanValue[]){{{}}})",
                values.len(),
                values.join(", ")
            ))
        }
    }

    fn call_expr(&mut self, callee: &Exp, args: &[Exp]) -> Result<String, CodegenError> {
        match callee {
            Exp::Id(IdExp { name, .. }) => {
                let c_callee = self.functions.get(name).cloned().ok_or_else(|| {
                    CodegenError::Unsupported(format!(
                        "call to unknown function `{}` is not supported by the C backend",
                        name
                    ))
                })?;
                let values = self.exprs(args)?;
                if values.is_empty() {
                    Ok(format!("{}(0, NULL)", c_callee))
                } else {
                    Ok(format!(
                        "{}({}, (CanValue[]){{{}}})",
                        c_callee,
                        values.len(),
                        values.join(", ")
                    ))
                }
            }
            Exp::ObjectAccess(ObjectAccessExp {
                prefix_exp,
                key_exp,
                ..
            }) => {
                let method = match key_exp.as_ref() {
                    Exp::Id(IdExp { name, .. }) => name.clone(),
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "method name must be an identifier".to_string(),
                        ));
                    }
                };

                let object = self.expr(prefix_exp)?;
                let values = self.exprs(args)?;
                if values.is_empty() {
                    Ok(format!(
                        "can_call_method({}, {}, 0, NULL)",
                        object,
                        c_escape_string(&method)
                    ))
                } else {
                    Ok(format!(
                        "can_call_method({}, {}, {}, (CanValue[]){{{}}})",
                        object,
                        c_escape_string(&method),
                        values.len(),
                        values.join(", ")
                    ))
                }
            }
            _ => Err(CodegenError::Unsupported(
                "indirect function calls are not supported by the C backend".to_string(),
            )),
        }
    }

    fn instantiate_class(&mut self, class: &str, args: &[Exp]) -> Result<String, CodegenError> {
        let class_var = self.classes.get(class).cloned().ok_or_else(|| {
            CodegenError::Unsupported(format!(
                "unknown class `{}` cannot be instantiated by the C backend",
                class
            ))
        })?;

        let mut keys = Vec::new();
        let mut values = Vec::new();
        for arg in args {
            match arg {
                Exp::Assign(AssignExp { exp1, exp2, .. }) => {
                    let key = match exp1.as_ref() {
                        Exp::Id(IdExp { name, .. }) => name.clone(),
                        _ => {
                            return Err(CodegenError::Unsupported(
                                "class constructor keyword must be an identifier".to_string(),
                            ));
                        }
                    };
                    keys.push(c_escape_string(&key));
                    values.push(self.expr(exp2)?);
                }
                _ => {
                    return Err(CodegenError::Unsupported(
                        "class instantiation requires keyword arguments like `field=value`"
                            .to_string(),
                    ));
                }
            }
        }

        if keys.is_empty() {
            Ok(format!(
                "can_class_instantiate({}, 0, NULL, NULL)",
                class_var
            ))
        } else {
            Ok(format!(
                "can_class_instantiate({}, {}, (const char*[]){{{}}}, (CanValue[]){{{}}})",
                class_var,
                keys.len(),
                keys.join(", "),
                values.join(", ")
            ))
        }
    }

    pub fn expr(&mut self, exp: &Exp) -> Result<String, CodegenError> {
        match exp {
            Exp::String(StringExp { s, .. }) => Ok(format!("can_string({})", c_string_literal(s)?)),
            Exp::Numeral(NumeralExp { val, .. }) => Ok(numeral_expr(val)),
            Exp::Id(IdExp { name, .. }) => match name.as_str() {
                "啱" => Ok("can_bool(true)".to_string()),
                "唔啱" => Ok("can_bool(false)".to_string()),
                "桔" => Ok("can_nil()".to_string()),
                _ => Ok(self.ident(name)),
            },
            Exp::True(TrueExp { .. }) => Ok("can_bool(true)".to_string()),
            Exp::False(FalseExp { .. }) => Ok("can_bool(false)".to_string()),
            Exp::Null(NullExp { .. }) => Ok("can_nil()".to_string()),
            Exp::Parens(ParensExp { exp, .. }) => {
                let inner = self.expr(exp)?;
                Ok(format!("({})", inner))
            }
            Exp::Annotation(annotation) => self.expr(&annotation.exp),
            Exp::Binop(BinopExp { op, exp1, exp2, .. }) => {
                let left = self.expr(exp1)?;
                let right = self.expr(exp2)?;
                let op = op.trim();
                let call = match op {
                    "+" => "can_add",
                    "-" => "can_sub",
                    "*" => "can_mul",
                    "/" => "can_div",
                    "//" => "can_floor_div",
                    "%" => "can_mod",
                    "**" => "can_pow",
                    "==" | "!=" => "can_eq",
                    "<" => "can_lt",
                    "<=" => "can_le",
                    ">" => "can_gt",
                    ">=" => "can_ge",
                    "and" => "can_and",
                    "or" => "can_or",
                    _ => {
                        return Err(CodegenError::Unsupported(format!(
                            "binary operator `{}` is not supported by the C backend",
                            op
                        )));
                    }
                };
                if op == "!=" {
                    Ok(format!("can_not(can_eq({}, {}))", left, right))
                } else {
                    Ok(format!("{}({}, {})", call, left, right))
                }
            }
            Exp::Unop(UnopExp { op, exp, .. }) => {
                let value = self.expr(exp)?;
                let call = match op.as_str() {
                    "-" => "can_neg",
                    "not" => "can_not",
                    "~" => "can_bit_not",
                    _ => {
                        return Err(CodegenError::Unsupported(format!(
                            "unary operator `{}` is not supported by the C backend",
                            op
                        )));
                    }
                };
                Ok(format!("{}({})", call, value))
            }
            Exp::Concat(ConcatExp { exps, .. }) => {
                let values = self.exprs(exps)?;
                if values.is_empty() {
                    return Ok("can_string(\"\")".to_string());
                }
                let mut iter = values.into_iter();
                let mut result = iter.next().unwrap();
                for value in iter {
                    result = format!("can_concat({}, {})", result, value);
                }
                Ok(result)
            }
            Exp::List(ListExp { elem_exps, .. }) => self.make_list_expr(elem_exps),
            Exp::Map(MapExp { elem_exps, .. }) => {
                let mut keys = Vec::new();
                let mut values = Vec::new();
                for elem in elem_exps {
                    match elem {
                        Exp::Mapping(MappingExp { exp1, exp2, .. }) => {
                            keys.push(self.expr(exp1)?);
                            values.push(self.expr(exp2)?);
                        }
                        _ => {
                            return Err(CodegenError::Unsupported(
                                "the C backend only supports maps with `key ==> value` entries"
                                    .to_string(),
                            ));
                        }
                    }
                }
                if keys.is_empty() {
                    Ok("can_map_from(0, NULL, NULL)".to_string())
                } else {
                    Ok(format!(
                        "can_map_from({}, (CanValue[]){{{}}}, (CanValue[]){{{}}})",
                        keys.len(),
                        keys.join(", "),
                        values.join(", ")
                    ))
                }
            }
            Exp::Mapping(_) => Err(CodegenError::Unsupported(
                "mapping expressions are only supported inside map literals in the C backend"
                    .to_string(),
            )),
            Exp::ListAccess(ListAccessExp {
                prefix_exp,
                key_exp,
                ..
            }) => {
                let container = self.expr(prefix_exp)?;
                let key = self.expr(key_exp)?;
                Ok(format!("can_index({}, {})", container, key))
            }
            Exp::ObjectAccess(ObjectAccessExp {
                prefix_exp,
                key_exp,
                ..
            }) => {
                let object = self.expr(prefix_exp)?;
                let name = match key_exp.as_ref() {
                    Exp::Id(IdExp { name, .. }) => name,
                    _ => {
                        return Err(CodegenError::Unsupported(
                            "attribute access requires an identifier".to_string(),
                        ));
                    }
                };
                Ok(format!("can_attr({}, {})", object, c_escape_string(name)))
            }
            Exp::FuncCall(FuncCallExp {
                prefix_exp, args, ..
            }) => self.call_expr(prefix_exp, args),
            Exp::IfElse(IfElseExp {
                if_cond_exp,
                if_exp,
                else_exp,
                ..
            }) => {
                let cond = self.expr(if_cond_exp)?;
                let then_value = self.expr(if_exp)?;
                let else_value = self.expr(else_exp)?;
                Ok(format!(
                    "(can_truthy({}) ? {} : {})",
                    cond, then_value, else_value
                ))
            }
            Exp::Assign(_) => Err(CodegenError::Unsupported(
                "assignment expressions are not supported by the C backend".to_string(),
            )),
            Exp::Lambda(_) => Err(CodegenError::Unsupported(
                "lambdas are not supported by the C backend".to_string(),
            )),
            Exp::Names(NamesExp { .. }) => Err(CodegenError::Unsupported(
                "qualified names are not supported by the C backend".to_string(),
            )),
            Exp::VarArg(_) => Err(CodegenError::Unsupported(
                "varargs are not supported by the C backend".to_string(),
            )),
            Exp::AttrAccess(_) => Err(CodegenError::Unsupported(
                "attribute access suffix is not supported by the C backend".to_string(),
            )),
            Exp::MetaId(_) | Exp::PatRep(_) | Exp::BlockRep(_) | Exp::StatExpansion(_) => {
                Err(CodegenError::Unsupported(
                    "macro-related expression node is not supported by the C backend".to_string(),
                ))
            }
        }
    }
}

fn numeral_expr(value: &str) -> String {
    if let Ok(integer) = value.parse::<i64>() {
        return format!("can_int({})", integer);
    }
    if let Some(hex) = value
        .strip_prefix("0x")
        .or_else(|| value.strip_prefix("0X"))
    {
        if let Ok(integer) = i64::from_str_radix(hex, 16) {
            return format!("can_int({})", integer);
        }
    }
    if let Some(binary) = value
        .strip_prefix("0b")
        .or_else(|| value.strip_prefix("0B"))
    {
        if let Ok(integer) = i64::from_str_radix(binary, 2) {
            return format!("can_int({})", integer);
        }
    }
    if let Some(octal) = value
        .strip_prefix("0o")
        .or_else(|| value.strip_prefix("0O"))
    {
        if let Ok(integer) = i64::from_str_radix(octal, 8) {
            return format!("can_int({})", integer);
        }
    }
    if let Ok(float) = value.parse::<f64>() {
        return format!("can_float({:?})", float);
    }
    format!("can_float((double)({}))", value)
}

/// Convert a Cantonese string literal (which includes its surrounding quotes)
/// into a C string literal.  Non-ASCII bytes are emitted as octal escapes so
/// the generated file stays valid regardless of the compiler's source encoding.
fn c_string_literal(raw: &str) -> Result<String, CodegenError> {
    let bytes = raw.as_bytes();
    if bytes.len() < 2 {
        return Err(CodegenError::Unsupported(
            "malformed string literal".to_string(),
        ));
    }
    let quote = bytes[0];
    if (quote != b'"' && quote != b'\'') || bytes[bytes.len() - 1] != quote {
        return Err(CodegenError::Unsupported(
            "malformed string literal".to_string(),
        ));
    }

    Ok(c_escape_string(&raw[1..raw.len() - 1]))
}

/// Escape a plain (unquoted) string as a C string literal.
fn c_escape_string(inner: &str) -> String {
    let mut out = String::from("\"");
    let mut chars = inner.chars().peekable();
    while let Some(ch) = chars.next() {
        match ch {
            '\\' => {
                let next = chars.next();
                match next {
                    Some('n') => out.push_str("\\n"),
                    Some('t') => out.push_str("\\t"),
                    Some('r') => out.push_str("\\r"),
                    Some('0') => out.push_str("\\0"),
                    Some('\\') => out.push_str("\\\\"),
                    Some('"') => out.push_str("\\\""),
                    Some('\'') => out.push_str("\\'"),
                    Some('x') => {
                        let mut hex = String::new();
                        while hex.len() < 2 {
                            match chars.peek() {
                                Some(&c) if c.is_ascii_hexdigit() => {
                                    hex.push(c);
                                    chars.next();
                                }
                                _ => break,
                            }
                        }
                        if let Ok(byte) = u8::from_str_radix(&hex, 16) {
                            out.push_str(&format!("\\{:03o}", byte));
                        } else {
                            out.push_str("\\\\x");
                        }
                    }
                    Some(other) => {
                        out.push('\\');
                        out.push(other);
                    }
                    None => out.push_str("\\\\"),
                }
            }
            '"' => out.push_str("\\\""),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            ch if (ch as u32) < 0x20 || (ch as u32) == 0x7f => {
                out.push_str(&format!("\\{:03o}", ch as u32));
            }
            ch if (ch as u32) > 0x7f => {
                let mut buffer = [0u8; 4];
                for byte in ch.encode_utf8(&mut buffer).bytes() {
                    out.push_str(&format!("\\{:03o}", byte));
                }
            }
            ch => out.push(ch),
        }
    }
    out.push('"');
    out
}

/// Collect every identifier assigned in a block.  The C backend hoists these
/// declarations so values remain visible across nested `if`/loop bodies.
fn collect_assigned(stats: &[Stat], out: &mut Vec<String>) {
    fn add(name: &str, out: &mut Vec<String>) {
        if !out.iter().any(|existing| existing == name) {
            out.push(name.to_string());
        }
    }

    for stat in stats {
        match stat {
            Stat::Assign(AssignStat {
                var_list, exp_list, ..
            })
            | Stat::AssignBlock(AssignBlockStat {
                var_list, exp_list, ..
            }) => {
                for var in var_list {
                    if let Exp::Id(IdExp { name, .. }) = var {
                        add(name, out);
                    }
                }
                for exp in exp_list {
                    collect_expr_assigned(exp, out);
                }
            }
            Stat::If(IfStat {
                if_exp,
                if_block,
                elif_exps,
                elif_blocks,
                else_blocks,
                ..
            }) => {
                collect_expr_assigned(if_exp, out);
                collect_assigned(if_block, out);
                for exp in elif_exps {
                    collect_expr_assigned(exp, out);
                }
                for block in elif_blocks {
                    collect_assigned(block, out);
                }
                for block in else_blocks {
                    collect_assigned(block, out);
                }
            }
            Stat::While(WhileStat {
                cond_exp, blocks, ..
            }) => {
                collect_expr_assigned(cond_exp, out);
                collect_assigned(blocks, out);
            }
            Stat::For(ForStat {
                var,
                from_exp,
                to_exp,
                blocks,
                ..
            }) => {
                if let Exp::Id(IdExp { name, .. }) = var {
                    add(name, out);
                }
                collect_expr_assigned(from_exp, out);
                collect_expr_assigned(to_exp, out);
                collect_assigned(blocks, out);
            }
            Stat::ForEach(ForEachStat {
                id_list,
                exp_list,
                blocks,
                ..
            }) => {
                for id in id_list {
                    if let Exp::Id(IdExp { name, .. }) = id {
                        add(name, out);
                    }
                }
                for exp in exp_list {
                    collect_expr_assigned(exp, out);
                }
                collect_assigned(blocks, out);
            }
            Stat::Print(PrintStat { args, .. }) => {
                for exp in args {
                    collect_expr_assigned(exp, out);
                }
            }
            Stat::Call(CallStat { exp, .. }) => collect_expr_assigned(exp, out),
            Stat::FuncCall(FuncCallStat { args, .. }) => {
                for exp in args {
                    collect_expr_assigned(exp, out);
                }
            }
            Stat::Return(ReturnStat { exps, .. }) => {
                for exp in exps {
                    collect_expr_assigned(exp, out);
                }
            }
            _ => {}
        }
    }
}

fn collect_expr_assigned(exp: &Exp, out: &mut Vec<String>) {
    match exp {
        Exp::Assign(assign) => {
            if let Exp::Id(IdExp { name, .. }) = assign.exp1.as_ref() {
                if !out.iter().any(|existing| existing == name) {
                    out.push(name.clone());
                }
            }
            collect_expr_assigned(&assign.exp2, out);
        }
        Exp::Binop(BinopExp { exp1, exp2, .. }) => {
            collect_expr_assigned(exp1, out);
            collect_expr_assigned(exp2, out);
        }
        Exp::Unop(UnopExp { exp, .. }) => collect_expr_assigned(exp, out),
        Exp::Concat(ConcatExp { exps, .. }) => {
            for exp in exps {
                collect_expr_assigned(exp, out);
            }
        }
        Exp::List(ListExp { elem_exps, .. }) => {
            for exp in elem_exps {
                collect_expr_assigned(exp, out);
            }
        }
        Exp::Map(MapExp { elem_exps, .. }) => {
            for exp in elem_exps {
                collect_expr_assigned(exp, out);
            }
        }
        Exp::Mapping(MappingExp { exp1, exp2, .. }) => {
            collect_expr_assigned(exp1, out);
            collect_expr_assigned(exp2, out);
        }
        Exp::Parens(ParensExp { exp, .. }) | Exp::Annotation(AnnotationExp { exp, .. }) => {
            collect_expr_assigned(exp, out);
        }
        Exp::ListAccess(ListAccessExp {
            prefix_exp,
            key_exp,
            ..
        })
        | Exp::ObjectAccess(ObjectAccessExp {
            prefix_exp,
            key_exp,
            ..
        }) => {
            collect_expr_assigned(prefix_exp, out);
            collect_expr_assigned(key_exp, out);
        }
        Exp::FuncCall(FuncCallExp {
            prefix_exp, args, ..
        }) => {
            collect_expr_assigned(prefix_exp, out);
            for exp in args {
                collect_expr_assigned(exp, out);
            }
        }
        Exp::IfElse(IfElseExp {
            if_cond_exp,
            if_exp,
            else_exp,
            ..
        }) => {
            collect_expr_assigned(if_cond_exp, out);
            collect_expr_assigned(if_exp, out);
            collect_expr_assigned(else_exp, out);
        }
        _ => {}
    }
}

fn class_name(class: &ClassDefStat) -> Result<String, CodegenError> {
    match &class.class_name {
        Exp::Id(IdExp { name, .. }) => Ok(name.clone()),
        _ => Err(CodegenError::Unsupported(
            "class name must be an identifier".to_string(),
        )),
    }
}

fn method_name(method: &MethodDefStat) -> Result<String, CodegenError> {
    match &method.name_exp {
        Exp::Id(IdExp { name, .. }) => Ok(name.clone()),
        _ => Err(CodegenError::Unsupported(
            "method name must be an identifier".to_string(),
        )),
    }
}

fn attr_def_name(attr: &Exp) -> Result<String, CodegenError> {
    match attr {
        Exp::Annotation(AnnotationExp { exp, .. }) => match exp.as_ref() {
            Exp::Id(IdExp { name, .. }) => Ok(name.clone()),
            _ => Err(CodegenError::Unsupported(
                "attribute name must be an identifier".to_string(),
            )),
        },
        Exp::Id(IdExp { name, .. }) => Ok(name.clone()),
        _ => Err(CodegenError::Unsupported(
            "attribute name must be an identifier".to_string(),
        )),
    }
}

fn stat_span(stat: &Stat) -> Option<&Span> {
    match stat {
        Stat::FuncCall(s) => s.pos.as_ref(),
        Stat::If(s) => s.pos.as_ref(),
        Stat::Print(s) => s.pos.as_ref(),
        Stat::Pass(s) => s.pos.as_ref(),
        Stat::Assign(s) => s.pos.as_ref(),
        Stat::AssignBlock(s) => s.pos.as_ref(),
        Stat::For(s) => s.pos.as_ref(),
        Stat::ForEach(s) => s.pos.as_ref(),
        Stat::While(s) => s.pos.as_ref(),
        Stat::ListInit(s) => s.pos.as_ref(),
        Stat::FunctionDef(s) => s.pos.as_ref(),
        Stat::FuncTypeDef(s) => s.pos.as_ref(),
        Stat::MethodDef(s) => s.pos.as_ref(),
        Stat::AttrDef(s) => s.pos.as_ref(),
        Stat::ClassDef(s) => s.pos.as_ref(),
        Stat::Import(s) => s.pos.as_ref(),
        Stat::Raise(s) => s.pos.as_ref(),
        Stat::Try(s) => s.pos.as_ref(),
        Stat::Global(s) => s.pos.as_ref(),
        Stat::Break(s) => s.pos.as_ref(),
        Stat::Continue(s) => s.pos.as_ref(),
        Stat::Type(s) => s.pos.as_ref(),
        Stat::Assert(s) => s.pos.as_ref(),
        Stat::Return(s) => s.pos.as_ref(),
        Stat::Del(s) => s.pos.as_ref(),
        Stat::Cmd(s) => s.pos.as_ref(),
        Stat::MethodCall(s) => s.pos.as_ref(),
        Stat::Call(s) => s.pos.as_ref(),
        Stat::Match(s) => s.pos.as_ref(),
        Stat::Extend(s) => s.pos.as_ref(),
        Stat::Exit(s) => s.pos.as_ref(),
        Stat::MacroDef(s) => s.pos.as_ref(),
    }
}

fn stat_kind(stat: &Stat) -> &'static str {
    match stat {
        Stat::FuncCall(_) => "function call",
        Stat::If(_) => "if",
        Stat::Print(_) => "print",
        Stat::Pass(_) => "pass",
        Stat::Assign(_) => "assign",
        Stat::AssignBlock(_) => "assign block",
        Stat::For(_) => "for",
        Stat::ForEach(_) => "for-each",
        Stat::While(_) => "while",
        Stat::ListInit(_) => "list initialisation",
        Stat::FunctionDef(_) => "function definition",
        Stat::FuncTypeDef(_) => "function type definition",
        Stat::MethodDef(_) => "method definition",
        Stat::AttrDef(_) => "attribute definition",
        Stat::ClassDef(_) => "class definition",
        Stat::Import(_) => "import",
        Stat::Raise(_) => "raise",
        Stat::Try(_) => "try",
        Stat::Global(_) => "global",
        Stat::Break(_) => "break",
        Stat::Continue(_) => "continue",
        Stat::Type(_) => "type",
        Stat::Assert(_) => "assert",
        Stat::Return(_) => "return",
        Stat::Del(_) => "del",
        Stat::Cmd(_) => "shell command",
        Stat::MethodCall(_) => "method call",
        Stat::Call(_) => "expression statement",
        Stat::Match(_) => "match",
        Stat::Extend(_) => "native extension",
        Stat::Exit(_) => "exit",
        Stat::MacroDef(_) => "macro definition",
    }
}

/// Compile Cantonese source into C source and a line map.
pub fn to_c(source: &str, filename: &str) -> Result<(String, LineMap), CodegenError> {
    let mut lexer = Lexer::new(filename.to_string(), source);
    let tokens = lexer.tokenize_all()?;
    let mut parser = CanParser::new(&tokens, filename);
    let stats = StatParser::parse_stats(&mut parser)?;
    let stats = modules::expand_imports(stats, filename)?;
    let mut codegen = CCodegen::new();
    codegen.codegen_program(&stats)?;
    Ok(codegen.into_code_and_line_map())
}
