// 粤语编程语言到Python的代码生成器

use crate::ast::{
    expression::{BinaryOperator, Expression, UnaryOperator},
    statement::{Block, ImportPath, Program, Statement},
};

pub struct Codegen {
    code: String,
    indent_level: usize,
    line: usize,
}

impl Codegen {
    pub fn new() -> Self {
        Self {
            code: String::new(),
            indent_level: 0,
            line: 1,
            }
    }

    /// 将程序编译为Python代码
    pub fn compile(&mut self, program: &Program) -> String {
        for statement in &program.statements {
            self.codegen_statement(statement);
        }
        self.code.clone()
    }

    /// 生成缩进
    fn indent(&self) -> String {
        "\t".repeat(self.indent_level)
    }

    /// 输出代码
    fn emit(&mut self, code: &str) {
        let indented = format!("{}{}", self.indent(), code);
        self.line += indented.matches('\n').count();
        self.code.push_str(&indented);
    }

    /// 生成语句代码
    fn codegen_statement(&mut self, statement: &Statement) {
        match statement {
            Statement::PrintStatement { arguments, .. } => {
                let args = self.codegen_args(arguments);
                self.emit(&format!("print({})\n", args));
            }

            Statement::AssignmentStatement {
                var_list, exp_list, ..
            } => {
                let vars = self.codegen_args(var_list);
                let exps = self.codegen_args(exp_list);
                self.emit(&format!("{} = {}\n", vars, exps));
            }

            Statement::AssignmentBlockStatement {
                var_list, exp_list, ..
            } => {
                for (vars, exps) in var_list.iter().zip(exp_list.iter()) {
                    let var_str = self.codegen_args(vars);
                    let exp_str = self.codegen_args(exps);
                    self.emit(&format!("{} = {}\n", var_str, exp_str));
                }
            }

            Statement::ExitStatement { .. } => {
                self.emit("exit()\n");
            }

            Statement::PassStatement { .. } => {
                self.emit("pass\n");
            }

            Statement::BreakStatement { .. } => {
                self.emit("break\n");
            }

            Statement::ContinueStatement { .. } => {
                self.emit("continue\n");
            }

            Statement::IfStatement {
                if_exp,
                if_block,
                elif_exps,
                elif_blocks,
                else_block,
                ..
            } => {
                let cond = self.codegen_expression(if_exp);
                self.emit(&format!("if {}:\n", cond));
                self.codegen_block(if_block);

                for (elif_exp, elif_blk) in elif_exps.iter().zip(elif_blocks.iter()) {
                    let elif_cond = self.codegen_expression(elif_exp);
                    self.emit(&format!("elif {}:\n", elif_cond));
                    self.codegen_block(elif_blk);
                }

                if let Some(else_blk) = else_block {
                    self.emit("else:\n");
                    self.codegen_block(else_blk);
                }
            }

            Statement::TryCatchStatement {
                try_block,
                except_exps,
                catch_blocks,
                finally_block,
                ..
            } => {
                self.emit("try:\n");
                self.codegen_block(try_block);

                for (except_exp, catch_blk) in except_exps.iter().zip(catch_blocks.iter()) {
                    let except_name = self.codegen_expression(except_exp);
                    self.emit(&format!("except {}:\n", except_name));
                    self.codegen_block(catch_blk);
                }

                if let Some(finally_blk) = finally_block {
                    self.emit("finally:\n");
                    self.codegen_block(finally_blk);
                }
            }

            Statement::ThrowStatement { exception, .. } => {
                let exc = self.codegen_expression(exception);
                self.emit(&format!("raise {}\n", exc));
            }

            Statement::WhileStatement { condition, body, .. } => {
                let cond = self.codegen_expression(condition);
                self.emit(&format!("while {}:\n", cond));
                self.codegen_block(body);
            }

            Statement::ForStatement {
                var,
                from_exp,
                to_exp,
                body,
                ..
            } => {
                let var_name = self.codegen_expression(var);
                let from = self.codegen_expression(from_exp);
                let to = self.codegen_expression(to_exp);
                self.emit(&format!("for {} in range({}, {}):\n", var_name, from, to));
                self.codegen_block(body);
            }

            Statement::ForEachStatement {
                id_list,
                exp_list,
                body,
                ..
            } => {
                let ids = self.codegen_args(id_list);
                let exps = self.codegen_args(exp_list);
                self.emit(&format!("for {} in {}:\n", ids, exps));
                self.codegen_block(body);
            }

            Statement::FunctionDeclaration {
                name,
                parameters,
                body,
                ..
            } => {
                let func_name = self.codegen_expression(name);
                let params = self.codegen_args(parameters);
                self.emit(&format!("def {}({}):\n", func_name, params));
                self.codegen_block(body);
            }

            Statement::FunctionCallStatement {
                function,
                arguments,
                ..
            } => {
                let func = self.codegen_expression(function);
                let args = self.codegen_args(arguments);
                self.emit(&format!("{}({})\n", func, args));
            }

            Statement::ImportStatement { path, .. } => {
                let import_code = self.codegen_import(path);
                self.emit(&format!("{}\n", import_code));
            }

            Statement::ReturnStatement { values, .. } => {
                let vals = self.codegen_args(values);
                self.emit(&format!("return {}\n", vals));
            }

            Statement::DeleteStatement { targets, .. } => {
                let tgts = self.codegen_args(targets);
                self.emit(&format!("del {}\n", tgts));
            }

            Statement::TypeStatement { expressions, .. } => {
                if let Some(exp) = expressions.first() {
                    let expr = self.codegen_expression(exp);
                    self.emit(&format!("print(type({}))\n", expr));
                }
            }

            Statement::AssertStatement { expression, .. } => {
                let expr = self.codegen_expression(expression);
                self.emit(&format!("assert {}\n", expr));
            }

            Statement::ClassDeclaration {
                name,
                extends,
                body,
                ..
            } => {
                let class_name = self.codegen_expression(name);
                let extend_classes = if extends.is_empty() {
                    String::new()
                } else {
                    self.codegen_args(extends)
                };
                self.emit(&format!("class {}({}):\n", class_name, extend_classes));
                self.codegen_block(body);
            }

            Statement::MethodDeclaration {
                name,
                parameters,
                body,
                ..
            } => {
                let method_name = self.codegen_expression(name);
                let params = self.codegen_args(parameters);
                self.emit(&format!("def {}({}):\n", method_name, params));
                self.codegen_block(body);
            }

            Statement::AttributeDeclaration { attributes, .. } => {
                let mut names = Vec::new();
                for attr in attributes {
                    if let Expression::AttributeAccessExpression { attribute, .. } = attr {
                        if let Expression::Identifier(name, _) = &**attribute {
                            names.push(name.clone());
                        }
                    }
                }

                if !names.is_empty() {
                    let args_str = names
                        .iter()
                        .map(|n| format!("{}=None", n))
                        .collect::<Vec<_>>()
                        .join(",");
                    let attr_str = names
                        .iter()
                        .map(|n| format!("self.{}={}", n, n))
                        .collect::<Vec<_>>()
                        .join(";");
                    self.emit(&format!("def __init__(self, {}):{};\n", args_str, attr_str));
                }
            }

            Statement::MethodCallStatement {
                object,
                method,
                arguments,
                ..
            } => {
                let obj = self.codegen_expression(object);
                let meth = self.codegen_expression(method);
                let args = self.codegen_args(arguments);
                self.emit(&format!("{}.{}({})\n", obj, meth, args));
            }

            Statement::CommandStatement { arguments, .. } => {
                let args = self.codegen_args(arguments);
                self.emit(&format!("os.system({})\n", args));
            }

            Statement::ExpressionStatement { expression, .. } => {
                let expr = self.codegen_expression(expression);
                self.emit(&format!("{}\n", expr));
            }

            Statement::GlobalStatement { identifiers, .. } => {
                let ids = self.codegen_args(identifiers);
                self.emit(&format!("global {}\n", ids));
            }

            Statement::EmbeddedCodeStatement { code, .. } => {
                for line in code.lines() {
                    self.emit(&format!("{}\n", line));
                }
            }

            Statement::MatchStatement {
                match_id,
                match_val,
                match_block_exp,
                default_block,
                ..
            } => {
                // 简化的match实现，需要根据实际AST结构调整
                let id = self.codegen_expression(match_id);
                let val = self.codegen_expression(match_val);
                self.emit(&format!("if {} == {}:\n", id, val));
                
                if let Expression::ListExpression { elements, .. } = match_block_exp {
                    self.indent_level += 1;
                    for elem in elements {
                        let expr = self.codegen_expression(elem);
                        self.emit(&format!("{}\n", expr));
                    }
                    self.indent_level -= 1;
                }

                if let Some(default_blk) = default_block {
                    self.emit("else:\n");
                    self.codegen_block(default_blk);
                }
            }

            _ => {
                // 其他语句类型的占位符
                self.emit("# TODO: Implement this statement type\n");
            }
        }
    }

    /// 生成表达式代码
    fn codegen_expression(&self, expression: &Expression) -> String {
        match expression {
            Expression::StringLiteral(s, _) => {
                // 转义字符串中的特殊字符
                let escaped = s.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t");
                format!("Str(\"{}\")", escaped)
            }
            Expression::NumberLiteral(n, _) => n.to_string(),
            Expression::BoolLiteral(b, _) => {
                if *b {
                    "True".to_string()
                } else {
                    "False".to_string()
                }
            }
            Expression::NullLiteral(_) => "None".to_string(),
            Expression::Identifier(name, _) => name.clone(),

            Expression::BinaryExpression {
                left,
                operator,
                right,
                ..
            } => {
                let l = self.codegen_expression(left);
                let r = self.codegen_expression(right);
                let op = self.codegen_binop(operator);
                format!("({} {} {})", l, op, r)
            }

            Expression::UnaryExpression {
                operator, operand, ..
            } => {
                let op = self.codegen_unop(operator);
                let operand_str = self.codegen_expression(operand);
                format!("({} {})", op, operand_str)
            }

            Expression::CallExpression {
                callee, arguments, ..
            } => {
                let func = self.codegen_expression(callee);
                let args = self.codegen_args(arguments);
                format!("{}({})", func, args)
            }

            Expression::ListExpression { elements, .. } => {
                let elems = self.codegen_args(elements);
                format!("List([{}])", elems)
            }

            Expression::MapExpression { elements, .. } => {
                let elems = self.codegen_args(elements);
                format!("{{{}}}", elems)
            }

            Expression::ObjectAccessExpression { object, property, .. } => {
                let obj = self.codegen_expression(object);
                let prop = self.codegen_expression(property);
                format!("{}.{}", obj, prop)
            }

            Expression::ListAccessExpression { list, index, .. } => {
                let lst = self.codegen_expression(list);
                let idx = self.codegen_expression(index);
                format!("{}[{}]", lst, idx)
            }

            Expression::AssignExpression { left, right, .. } => {
                let l = self.codegen_expression(left);
                let r = self.codegen_expression(right);
                format!("{} = {}", l, r)
            }

            Expression::LambdaExpression {
                parameters, body, ..
            } => {
                let params = self.codegen_args(parameters);
                let body_str = self.codegen_args(body);
                format!("(lambda {} : {})", params, body_str)
            }

            Expression::ConditionalExpression {
                condition,
                then_branch,
                else_branch,
                ..
            } => {
                let cond = self.codegen_expression(condition);
                let then_expr = self.codegen_expression(then_branch);
                let else_expr = self.codegen_expression(else_branch);
                format!("({} if {} else {})", then_expr, cond, else_expr)
            }

            Expression::AnnotationExpression {
                expression,
                type_id,
                ..
            } => {
                let expr = self.codegen_expression(expression);
                let ty = self.codegen_expression(type_id);
                format!("{}:{}", expr, ty)
            }

            Expression::ParenthesizedExpression { expression, .. } => {
                let expr = self.codegen_expression(expression);
                format!("({})", expr)
            }

            _ => {
                // 其他表达式类型的占位符
                "None".to_string()
            }
        }
    }

    /// 生成二元运算符
    fn codegen_binop(&self, op: &BinaryOperator) -> String {
        match op {
            BinaryOperator::Add => "+".to_string(),
            BinaryOperator::Subtract => "-".to_string(),
            BinaryOperator::Multiply => "*".to_string(),
            BinaryOperator::Divide => "/".to_string(),
            BinaryOperator::Equal => "==".to_string(),
            BinaryOperator::NotEqual => "!=".to_string(),
            BinaryOperator::LessThan => "<".to_string(),
            BinaryOperator::LessThanEqual => "<=".to_string(),
            BinaryOperator::GreaterThan => ">".to_string(),
            BinaryOperator::GreaterThanEqual => ">=".to_string(),
            BinaryOperator::NotGreaterThan => "<".to_string(),
            BinaryOperator::Is => "==".to_string(),
            BinaryOperator::And => "and".to_string(),
            BinaryOperator::Concat => "+".to_string(),
            BinaryOperator::Mapping => ":".to_string(),
        }
    }

    /// 生成一元运算符
    fn codegen_unop(&self, op: &UnaryOperator) -> String {
        match op {
            UnaryOperator::Negative => "-".to_string(),
            UnaryOperator::Not => "not".to_string(),
            UnaryOperator::Len => "len".to_string(),
        }
    }

    /// 生成参数列表
    fn codegen_args(&self, args: &[Expression]) -> String {
        args.iter()
            .map(|arg| self.codegen_expression(arg))
            .collect::<Vec<_>>()
            .join(", ")
    }

    /// 生成代码块
    fn codegen_block(&mut self, block: &Block) {
        self.indent_level += 1;
        if block.statements.is_empty() {
            self.emit("pass\n");
        } else {
            for statement in &block.statements {
                self.codegen_statement(statement);
            }
        }
        self.indent_level -= 1;
    }

    /// 生成导入语句
    fn codegen_import(&self, path: &ImportPath) -> String {
        match path {
            ImportPath::ModuleImport { path } => {
                if path.len() == 1 {
                    format!("import {}", path[0])
                } else {
                    let module = path[..path.len() - 1].join(".");
                    let item = &path[path.len() - 1];
                    format!("from {} import {}", module, item)
                }
            }
            ImportPath::AllImport { path } => {
                let module = path.join(".");
                format!("from {} import *", module)
            }
            ImportPath::GroupImport { base, imports } => {
                let base_path = base.join(".");
                let import_items: Vec<String> = imports
                    .iter()
                    .map(|imp| match imp {
                        ImportPath::ModuleImport { path } => path.last().unwrap().clone(),
                        _ => "*".to_string(),
                    })
                    .collect();
                format!("from {} import {}", base_path, import_items.join(", "))
            }
        }
    }
}
