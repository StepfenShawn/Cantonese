// 粤语编程语言嘅AST构建器 - 将pest解析树转换为AST

use pest::iterators::{Pair, Pairs};
use thiserror::Error;

use super::CantoneseParser;
use super::Rule;
use super::token_tree::{Delimiter, Token, TokenKind, TokenStream, TokenTree};
use crate::ast::{
    BinaryOperator, Block, Expression, ImportPath, Program, Span, Statement, UnaryOperator,
};

/// 解析错误
#[derive(Debug, Error)]
pub enum ParseError {
    #[error("語法解析錯誤: {0}")]
    PestError(#[from] pest::error::Error<Rule>),

    #[error("無效嘅運算符: {0}")]
    InvalidOperator(String),

    #[error("無效嘅語法節點: {0:?}")]
    InvalidNode(Rule),

    #[error("無效嘅字面量值: {0}")]
    InvalidLiteral(String),

    #[error("自定義錯誤: {0}")]
    Custom(String),
}

/// AST构建器
pub struct AstBuilder<'a> {
    source: &'a str,
}

impl<'a> AstBuilder<'a> {
    /// 创建一个新的AST构建器
    pub fn new(source: &'a str) -> Self {
        Self { source }
    }

    /// 解析源代码为AST
    pub fn parse(&self) -> Result<Program, ParseError> {
        use pest::Parser;
        let pairs = CantoneseParser::parse(Rule::program, self.source)?;
        self.build_program(pairs)
    }

    /// 构建程序
    fn build_program(&self, pairs: Pairs<'_, Rule>) -> Result<Program, ParseError> {
        let mut statements = Vec::new();
        let mut start_span = None;
        let mut end_span = None;

        for pair in pairs {
            match pair.as_rule() {
                Rule::program => {
                    for inner_pair in pair.into_inner() {
                        if inner_pair.as_rule() == Rule::EOI {
                            continue;
                        }

                        let statement = self.build_statement(inner_pair)?;
                        if start_span.is_none() {
                            start_span = Some(statement.span());
                        }
                        end_span = Some(statement.span());
                        statements.push(statement);
                    }
                }
                Rule::EOI => {}
                _ => return Err(ParseError::InvalidNode(pair.as_rule())),
            }
        }

        let span = match (start_span, end_span) {
            (Some(start), Some(end)) => Span::new(start.start, end.end),
            _ => Span::new(Default::default(), Default::default()),
        };

        Ok(Program { statements, span })
    }

    /// 构建语句
    fn build_statement(&self, pair: Pair<'_, Rule>) -> Result<Statement, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        match pair.as_rule() {
            Rule::assignment_statement => self.build_assignment_statement(pair, span),
            Rule::assignment_block_statement => self.build_assignment_block_statement(pair, span),
            Rule::print_statement => self.build_print_statement(pair, span),
            Rule::if_statement => self.build_if_statement(pair, span),
            Rule::for_statement => self.build_for_statement(pair, span),
            Rule::for_each_statement => self.build_for_each_statement(pair, span),
            Rule::while_statement => self.build_while_statement(pair, span),
            Rule::list_init_statement => self.build_list_init_statement(pair, span),
            Rule::function_declaration => self.build_function_declaration(pair, span),
            Rule::function_type_declaration => self.build_function_type_declaration(pair, span),
            Rule::method_declaration => self.build_method_declaration(pair, span),
            Rule::attribute_declaration => self.build_attribute_declaration(pair, span),
            Rule::class_declaration => self.build_class_declaration(pair, span),
            Rule::import_statement => self.build_import_statement(pair, span),
            Rule::throw_statement => self.build_throw_statement(pair, span),
            Rule::try_catch_statement => self.build_try_catch_statement(pair, span),
            Rule::global_statement => self.build_global_statement(pair, span),
            Rule::break_statement => self.build_break_statement(pair, span),
            Rule::continue_statement => self.build_continue_statement(pair, span),
            Rule::type_statement => self.build_type_statement(pair, span),
            Rule::assert_statement => self.build_assert_statement(pair, span),
            Rule::return_statement => self.build_return_statement(pair, span),
            Rule::delete_statement => self.build_delete_statement(pair, span),
            Rule::command_statement => self.build_command_statement(pair, span),
            Rule::method_call_statement => self.build_method_call_statement(pair, span),
            Rule::function_call_statement => self.build_function_call_statement(pair, span),
            Rule::match_statement => self.build_match_statement(pair, span),
            Rule::macro_def_statement => self.build_macro_def_statement(pair, span),
            Rule::embedded_code_statement => self.build_embedded_code_statement(pair, span),
            Rule::exit_statement => self.build_exit_statement(pair, span),
            Rule::statement => {
                let inner = pair.into_inner().next().unwrap();
                self.build_statement(inner)
            }
            _ => {
                // 如果不是已知的语句，尝试将其构建为表达式语句
                let expression = self.build_expression(pair)?;
                Ok(Statement::ExpressionStatement { expression, span })
            }
        }
    }

    /// 构建赋值语句
    fn build_assignment_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let var_list_pair = inner.next().unwrap();
        let mut var_list = Vec::new();

        for var_pair in var_list_pair.into_inner() {
            let var = self.build_expression(var_pair)?;
            var_list.push(var);
        }

        let exp_list_pair = inner.next().unwrap();
        let mut exp_list = Vec::new();

        if exp_list_pair.as_rule() == Rule::exp_list {
            for exp_pair in exp_list_pair.into_inner() {
                let exp = self.build_expression(exp_pair)?;
                exp_list.push(exp);
            }
        } else {
            // 如果直接是一个表达式
            let exp = self.build_expression(exp_list_pair)?;
            exp_list.push(exp);
        }

        Ok(Statement::AssignmentStatement {
            var_list,
            exp_list,
            span,
        })
    }

    /// 构建块赋值语句
    fn build_assignment_block_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut var_list = Vec::new();
        let mut exp_list = Vec::new();

        for inner_pair in pair.into_inner() {
            match inner_pair.as_rule() {
                Rule::var => {
                    let mut vars = Vec::new();
                    for var_pair in inner_pair.into_inner() {
                        let var = self.build_expression(var_pair)?;
                        vars.push(var);
                    }
                    var_list.push(vars);
                }
                Rule::exp_list => {
                    let mut exps = Vec::new();
                    for exp_pair in inner_pair.into_inner() {
                        let exp = self.build_expression(exp_pair)?;
                        exps.push(exp);
                    }
                    exp_list.push(exps);
                }
                _ => return Err(ParseError::InvalidNode(inner_pair.as_rule())),
            }
        }

        Ok(Statement::AssignmentBlockStatement {
            var_list,
            exp_list,
            span,
        })
    }

    /// 构建打印语句
    fn build_print_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut arguments = Vec::new();

        for expression_pair in pair.into_inner() {
            let expression = self.build_expression(expression_pair)?;
            arguments.push(expression);
        }

        Ok(Statement::PrintStatement { arguments, span })
    }

    /// 构建条件语句
    fn build_if_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let condition_pair = inner.next().unwrap();
        let if_exp = self.build_expression(condition_pair)?;

        let then_block_pair = inner.next().unwrap();
        let if_block = self.build_block(then_block_pair)?;

        let mut elif_exps = Vec::new();
        let mut elif_blocks = Vec::new();
        let mut else_block = None;

        // 处理else if和else部分
        while let Some(next_pair) = inner.next() {
            match next_pair.as_rule() {
                Rule::expression => {
                    let elif_exp = self.build_expression(next_pair)?;
                    elif_exps.push(elif_exp);

                    let elif_block_pair = inner.next().unwrap();
                    let elif_block = self.build_block(elif_block_pair)?;
                    elif_blocks.push(elif_block);
                }
                Rule::block => {
                    else_block = Some(self.build_block(next_pair)?);
                }
                _ => return Err(ParseError::InvalidNode(next_pair.as_rule())),
            }
        }

        Ok(Statement::IfStatement {
            if_exp,
            if_block,
            elif_exps,
            elif_blocks,
            else_block,
            span,
        })
    }

    /// 构建For循环语句
    fn build_for_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let identifier_pair = inner.next().unwrap();
        let var = self.build_expression(identifier_pair)?;

        let start_pair = inner.next().unwrap();
        let from_exp = self.build_expression(start_pair)?;

        let end_pair = inner.next().unwrap();
        let to_exp = self.build_expression(end_pair)?;

        let body_pair = inner.next().unwrap();
        let body = self.build_block(body_pair)?;

        Ok(Statement::ForStatement {
            var,
            from_exp,
            to_exp,
            body,
            span,
        })
    }

    /// 构建For-each循环语句
    fn build_for_each_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let id_pair = inner.next().unwrap();
        let id_list = vec![self.build_expression(id_pair)?];

        let exp_pair = inner.next().unwrap();
        let exp_list = vec![self.build_expression(exp_pair)?];

        let body_pair = inner.next().unwrap();
        let body = self.build_block(body_pair)?;

        Ok(Statement::ForEachStatement {
            id_list,
            exp_list,
            body,
            span,
        })
    }

    /// 构建While循环语句
    fn build_while_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let body_pair = inner.next().unwrap();
        let body = self.build_block(body_pair)?;

        let condition_pair = inner.next().unwrap();
        let condition = self.build_expression(condition_pair)?;

        Ok(Statement::WhileStatement {
            condition,
            body,
            span,
        })
    }

    /// 构建函数声明
    fn build_function_declaration(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let name_pair = inner.next().unwrap();
        let name = self.build_expression(name_pair)?;

        let parameters_pair = inner.next().unwrap();
        let mut parameters = Vec::new();
        for param_pair in parameters_pair.into_inner() {
            let param = self.build_expression(param_pair)?;
            parameters.push(param);
        }

        let body_pair = inner.next().unwrap();
        let mut body_statements = Vec::new();
        for statement_pair in body_pair.clone().into_inner() {
            let statement = self.build_statement(statement_pair)?;
            body_statements.push(statement);
        }
        let body = Block {
            statements: body_statements,
            span: Span::from_pest(body_pair.as_span(), self.source),
        };

        Ok(Statement::FunctionDeclaration {
            name,
            parameters,
            body,
            span,
        })
    }

    /// 构建函数类型声明
    fn build_function_type_declaration(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let name_pair = inner.next().unwrap();
        let name = self.build_expression(name_pair)?;

        let arg_types_pair = inner.next().unwrap();
        let mut arg_types = Vec::new();
        for type_pair in arg_types_pair.into_inner() {
            let arg_type = self.build_expression(type_pair)?;
            arg_types.push(arg_type);
        }

        let return_types_pair = inner.next().unwrap();
        let mut return_types = Vec::new();
        for type_pair in return_types_pair.into_inner() {
            let return_type = self.build_expression(type_pair)?;
            return_types.push(return_type);
        }

        Ok(Statement::FunctionTypeDeclaration {
            name,
            arg_types,
            return_types,
            span,
        })
    }

    /// 构建方法声明
    fn build_method_declaration(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let name_pair = inner.next().unwrap();
        let name = self.build_expression(name_pair)?;

        let params_pair = inner.next().unwrap();
        let mut parameters = Vec::new();
        for param_pair in params_pair.into_inner() {
            let param = self.build_expression(param_pair)?;
            parameters.push(param);
        }

        let body_pair = inner.next().unwrap();
        let body = self.build_block(body_pair)?;

        Ok(Statement::MethodDeclaration {
            name,
            parameters,
            body,
            span,
        })
    }

    /// 构建属性声明
    fn build_attribute_declaration(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut attributes = Vec::new();

        for attr_pair in pair.into_inner() {
            if attr_pair.as_rule() == Rule::attribute_list {
                for attr in attr_pair.into_inner() {
                    let attribute = self.build_expression(attr)?;
                    attributes.push(attribute);
                }
            }
        }

        Ok(Statement::AttributeDeclaration { attributes, span })
    }

    /// 构建类声明
    fn build_class_declaration(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let name_pair = inner.next().unwrap();
        let name = self.build_expression(name_pair)?;

        let mut extends = Vec::new();
        let mut body_statements = Vec::new();

        for next_pair in inner {
            match next_pair.as_rule() {
                Rule::identifier => {
                    let parent = self.build_expression(next_pair)?;
                    extends.push(parent);
                }
                Rule::method_declaration | Rule::attribute_declaration => {
                    let statement = self.build_statement(next_pair)?;
                    body_statements.push(statement);
                }
                _ => return Err(ParseError::InvalidNode(next_pair.as_rule())),
            }
        }

        let body_span = if let Some(first) = body_statements.first() {
            if let Some(last) = body_statements.last() {
                Span::new(first.span().start, last.span().end)
            } else {
                span
            }
        } else {
            span
        };

        let body = Block {
            statements: body_statements,
            span: body_span,
        };

        Ok(Statement::ClassDeclaration {
            name,
            extends,
            body,
            span,
        })
    }

    /// 构建导入语句
    fn build_import_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let import_path_pair = inner.next().unwrap();
        let path = self.build_import_path(import_path_pair)?;

        Ok(Statement::ImportStatement { path, span })
    }

    /// 构建导入路径
    fn build_import_path(&self, pair: Pair<'_, Rule>) -> Result<ImportPath, ParseError> {
        let mut path_parts = Vec::new();
        let mut is_all_import = false;
        let mut group_imports = Vec::new();

        for part in pair.into_inner() {
            match part.as_rule() {
                Rule::identifier => {
                    path_parts.push(part.as_str().to_string());
                }
                _ => {
                    if part.as_str() == "*" {
                        is_all_import = true;
                    } else if part.as_rule() == Rule::import_path {
                        group_imports.push(self.build_import_path(part)?);
                    }
                }
            }
        }

        if !group_imports.is_empty() {
            Ok(ImportPath::GroupImport {
                base: path_parts,
                imports: group_imports,
            })
        } else if is_all_import {
            Ok(ImportPath::AllImport { path: path_parts })
        } else {
            Ok(ImportPath::ModuleImport { path: path_parts })
        }
    }

    /// 构建异常抛出语句
    fn build_throw_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let exception_pair = pair.into_inner().next().unwrap();
        let exception = self.build_expression(exception_pair)?;

        Ok(Statement::ThrowStatement { exception, span })
    }

    /// 构建try-catch-finally语句
    fn build_try_catch_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();

        let try_block_pair = inner.next().unwrap();
        let try_block = self.build_block(try_block_pair)?;

        let mut except_exps = Vec::new();
        let mut catch_blocks = Vec::new();

        let except_pair = inner.next().unwrap();
        let except_exp = self.build_expression(except_pair)?;
        except_exps.push(except_exp);

        let catch_block_pair = inner.next().unwrap();
        let catch_block = self.build_block(catch_block_pair)?;
        catch_blocks.push(catch_block);

        let finally_block = if let Some(finally_block_pair) = inner.next() {
            Some(self.build_block(finally_block_pair)?)
        } else {
            None
        };

        Ok(Statement::TryCatchStatement {
            try_block,
            except_exps,
            catch_blocks,
            finally_block,
            span,
        })
    }

    /// 构建全局变量声明
    fn build_global_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut identifiers = Vec::new();

        for inner_pair in pair.into_inner() {
            if inner_pair.as_rule() == Rule::identifier_list {
                for id_pair in inner_pair.into_inner() {
                    let id = self.build_expression(id_pair)?;
                    identifiers.push(id);
                }
            }
        }

        Ok(Statement::GlobalStatement { identifiers, span })
    }

    /// 构建break语句
    fn build_break_statement(
        &self,
        _pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        Ok(Statement::BreakStatement { span })
    }

    /// 构建continue语句
    fn build_continue_statement(
        &self,
        _pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        Ok(Statement::ContinueStatement { span })
    }

    /// 构建类型语句
    fn build_type_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut expressions = Vec::new();

        for inner_pair in pair.into_inner() {
            let expr = self.build_expression(inner_pair)?;
            expressions.push(expr);
        }

        Ok(Statement::TypeStatement { expressions, span })
    }

    /// 构建断言语句
    fn build_assert_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let expression = self.build_expression(pair.into_inner().next().unwrap())?;

        Ok(Statement::AssertStatement { expression, span })
    }

    /// 构建返回语句
    fn build_return_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut values = Vec::new();

        for inner_pair in pair.into_inner() {
            let value = self.build_expression(inner_pair)?;
            values.push(value);
        }

        Ok(Statement::ReturnStatement { values, span })
    }

    /// 构建删除语句
    fn build_delete_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut targets = Vec::new();

        for inner_pair in pair.into_inner() {
            if inner_pair.as_rule() == Rule::identifier_list {
                for id_pair in inner_pair.into_inner() {
                    let target = self.build_expression(id_pair)?;
                    targets.push(target);
                }
            }
        }

        Ok(Statement::DeleteStatement { targets, span })
    }

    /// 构建命令语句
    fn build_command_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut arguments = Vec::new();

        for inner_pair in pair.into_inner() {
            let arg = self.build_expression(inner_pair)?;
            arguments.push(arg);
        }

        Ok(Statement::CommandStatement { arguments, span })
    }

    /// 构建方法调用语句
    fn build_method_call_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let object_call = pair.into_inner().next().unwrap();
        let mut inner = object_call.into_inner();

        // 获取方法调用链
        let chain_pair = inner.next().unwrap();
        
        // 处理复杂的调用链
        if chain_pair.as_rule() == Rule::object_call_chain {
            let mut chain_inner = chain_pair.into_inner();
            
            // 第一个标识符是对象
            let object_id = chain_inner.next().unwrap();
            let mut object = Expression::Identifier(
                object_id.as_str().to_string(),
                Span::from_pest(object_id.as_span(), self.source)
            );
            
            // 获取剩余的属性链，直到最后一个作为方法
            let mut props = Vec::new();
            for prop in chain_inner {
                props.push(prop);
            }
            
            // 逐步构建链式访问
            for i in 0..props.len()-1 {
                let prop_pair = &props[i];
                let property = Expression::Identifier(
                    prop_pair.as_str().to_string(),
                    Span::from_pest(prop_pair.as_span(), self.source)
                );
                
                object = Expression::ObjectAccessExpression {
                    object: Box::new(object),
                    property: Box::new(property),
                    span: Span::from_pest(prop_pair.as_span(), self.source),
                };
            }
            
            // 最后一个是方法名
            let method = if let Some(last_prop) = props.last() {
                Expression::Identifier(
                    last_prop.as_str().to_string(),
                    Span::from_pest(last_prop.as_span(), self.source)
                )
            } else {
                return Err(ParseError::Custom("方法调用缺少方法名".to_string()));
            };
            
            // 处理参数列表
            let mut arguments = Vec::new();
            if let Some(args_pair) = inner.next() {
                for arg_pair in args_pair.into_inner() {
                    let arg = self.build_expression(arg_pair)?;
                    arguments.push(arg);
                }
            }
            
            return Ok(Statement::MethodCallStatement {
                object,
                method,
                arguments,
                span,
            });
        }
        
        // 如果不是链式调用，回退到原始处理方式
        let object_pair = chain_pair;
        let object = self.build_expression(object_pair)?;

        let method_pair = inner.next().unwrap();
        let method = self.build_expression(method_pair)?;

        let mut arguments = Vec::new();
        if let Some(args_pair) = inner.next() {
            for arg_pair in args_pair.into_inner() {
                let arg = self.build_expression(arg_pair)?;
                arguments.push(arg);
            }
        }

        Ok(Statement::MethodCallStatement {
            object,
            method,
            arguments,
            span,
        })
    }

    /// 构建函数调用语句
    fn build_function_call_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();
        let call_pair = inner.next().unwrap();

        let mut call_inner = call_pair.into_inner();
        let function_pair = call_inner.next().unwrap();
        let function = self.build_expression(function_pair)?;

        let mut arguments = Vec::new();
        if let Some(args_pair) = call_inner.next() {
            for arg_pair in args_pair.into_inner() {
                let arg = self.build_expression(arg_pair)?;
                arguments.push(arg);
            }
        }

        Ok(Statement::FunctionCallStatement {
            function,
            arguments,
            span,
        })
    }

    /// 构建匹配语句
    fn build_match_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        // 克隆pair以避免移动问题
        let pair_clone = pair.clone();
        let mut inner = pair_clone.into_inner();
        let match_id_pair = inner.next().unwrap();
        let match_id = self.build_expression(match_id_pair)?;

        // 默认为空的匹配值和表达式
        let match_val = Expression::NullLiteral(span);
        let match_block_exp = Expression::NullLiteral(span);
        let mut default_block = None;

        // 处理匹配分支
        for branch_pair in inner {
            if branch_pair.as_rule() == Rule::block {
                default_block = Some(self.build_block(branch_pair)?);
            }
        }

        Ok(Statement::MatchStatement {
            match_id,
            match_val,
            match_block_exp,
            default_block,
            span,
        })
    }

    /// 获取Pest Pair的Span
    fn get_span(&self, pair: &Pair<'_, Rule>) -> Span {
        Span::from_pest(pair.as_span(), self.source)
    }

    /// 从字符串中提取字符串字面量的值
    fn extract_string_literal(&self, text: &str) -> String {
        // 移除两边的引号
        if text.starts_with('"') && text.ends_with('"') {
            text[1..text.len() - 1].to_string()
        } else if text.starts_with('「') && text.ends_with('」') {
            text[3..text.len() - 3].to_string()
        } else {
            text.to_string()
        }
    }

    /// 构建宏定义语句
    fn build_macro_def_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner_pairs = pair.into_inner();

        // 获取宏名称
        let name_pair = inner_pairs.next().ok_or_else(|| {
            ParseError::Custom(format!(
                "缺少宏名称 在 {}:{}",
                span.start.line, span.start.column
            ))
        })?;
        let name = name_pair.as_str().to_string();

        // 获取宏模式
        let pattern_pair = inner_pairs.next().ok_or_else(|| {
            ParseError::Custom(format!(
                "缺少宏模式 在 {}:{}",
                span.start.line, span.start.column
            ))
        })?;

        // 解析宏模式为表达式列表
        let pattern_expressions = self.parse_macro_pattern(pattern_pair)?;

        // 获取宏主体
        let body_pair = inner_pairs.next().ok_or_else(|| {
            ParseError::Custom(format!(
                "缺少宏主体 在 {}:{}",
                span.start.line, span.start.column
            ))
        })?;

        // 解析宏主体为表达式列表
        let body_expressions = self.parse_macro_body(body_pair)?;

        Ok(Statement::MacroDefStatement {
            name,
            pattern: pattern_expressions,
            body: body_expressions,
            span,
        })
    }

    /// 解析宏模式
    fn parse_macro_pattern(&self, pair: Pair<'_, Rule>) -> Result<Vec<Expression>, ParseError> {
        let mut expressions = Vec::new();

        // 遍历所有模式标记树
        for pattern_token_tree in pair.into_inner() {
            if pattern_token_tree.as_rule() == Rule::pattern_token_tree {
                let token_expr = self.build_token_stream(pattern_token_tree)?;
                expressions.push(token_expr);
            }
        }

        Ok(expressions)
    }

    /// 解析宏主体
    fn parse_macro_body(&self, pair: Pair<'_, Rule>) -> Result<Vec<Expression>, ParseError> {
        let mut expressions = Vec::new();

        // println!("解析宏主体: {:?}", pair);
        // 遍历所有主体标记树
        for body_token_tree in pair.into_inner() {
            if body_token_tree.as_rule() == Rule::body_token_tree {
                let token_expr = self.build_token_stream(body_token_tree)?;
                expressions.push(token_expr);
            }
        }

        Ok(expressions)
    }

    /// 构建TokenStream表达式
    fn build_token_stream(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = self.get_span(&pair);
        let mut tokens = Vec::new();

        // 遍历所有标记
        for token_pair in pair.into_inner() {
            match token_pair.as_rule() {
                // 标识符
                Rule::identifier => {
                    let id_str = token_pair.as_str().to_string();
                    let id_span = self.get_span(&token_pair);
                    tokens.push(Expression::Identifier(id_str, id_span));
                }
                // 字符串字面量
                Rule::string_literal => {
                    let str_value = self.extract_string_literal(token_pair.as_str());
                    let str_span = self.get_span(&token_pair);
                    tokens.push(Expression::StringLiteral(str_value, str_span));
                }
                // 数字字面量
                Rule::number_literal => {
                    let num_str = token_pair.as_str();
                    let num_span = self.get_span(&token_pair);
                    if let Ok(num) = num_str.parse::<f64>() {
                        tokens.push(Expression::NumberLiteral(num, num_span));
                    } else {
                        return Err(ParseError::Custom(format!("无法解析数字: {}", num_str)));
                    }
                }
                // 元变量
                Rule::pattern_meta_variable | Rule::body_meta_variable => {
                    let meta_var = self.build_meta_variable(token_pair)?;
                    tokens.push(meta_var);
                }
                // 嵌套标记树
                Rule::pattern_token_tree | Rule::body_token_tree => {
                    let nested_stream = self.build_token_stream(token_pair)?;
                    tokens.push(nested_stream);
                }
                // 操作符和其他标记类型
                _ => {
                    let token_str = token_pair.as_str().to_string();
                    let token_span = self.get_span(&token_pair);
                    tokens.push(Expression::Identifier(token_str, token_span));
                }
            }
        }

        Ok(Expression::TokenStream { tokens, span })
    }

    /// 构建元变量表达式
    fn build_meta_variable(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = self.get_span(&pair);
        let meta_text = pair.as_str();

        // 解析元变量格式: @name:type
        let parts: Vec<&str> = meta_text.trim_start_matches('@').split(':').collect();
        let name = parts[0].to_string();
        let fragment_type = if parts.len() > 1 { parts[1] } else { "expr" };

        let name_expr = Box::new(Expression::Identifier(name, span));
        let frag_expr = Box::new(Expression::Identifier(fragment_type.to_string(), span));

        Ok(Expression::MacroMetaId {
            id: name_expr,
            frag_spec: frag_expr,
            span,
        })
    }

    /// 构建嵌入代码语句
    fn build_embedded_code_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let code = pair.as_str().to_string();
        Ok(Statement::EmbeddedCodeStatement { code, span })
    }

    /// 构建退出语句
    fn build_exit_statement(
        &self,
        _pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        Ok(Statement::ExitStatement { span })
    }

    /// 构建表达式
    pub fn build_expression(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);
        let inner_rule = pair.as_rule();

        match inner_rule {
            Rule::expression => self.build_expression(pair.into_inner().next().unwrap()),
            Rule::macro_call_expression => self.build_macro_call_expression(pair, span),
            Rule::term => {
                let inner = pair.into_inner().next().unwrap();
                self.build_expression(inner)
            }
            Rule::parenthesized_expression => {
                let inner = pair.into_inner().next().unwrap();
                let expression = self.build_expression(inner)?;

                Ok(Expression::ParenthesizedExpression {
                    expression: Box::new(expression),
                    span,
                })
            }
            Rule::object_access_expression => self.build_object_access_expression(pair, span),
            Rule::object_access_chain => self.build_object_access_chain(pair, span),
            Rule::list_access_expression => {
                let mut inner = pair.into_inner();
                let list_pair = inner.next().unwrap();
                let index_pair = inner.next().unwrap();

                let list = self.build_expression(list_pair)?;
                let index = self.build_expression(index_pair)?;

                Ok(Expression::ListAccessExpression {
                    list: Box::new(list),
                    index: Box::new(index),
                    span,
                })
            }
            Rule::list_expression => {
                let mut elements = Vec::new();

                for element_pair in pair.into_inner() {
                    let element = self.build_expression(element_pair)?;
                    elements.push(element);
                }

                Ok(Expression::ListExpression { elements, span })
            }
            Rule::map_expression => {
                let mut elements = Vec::new();

                for entry_pair in pair.into_inner() {
                    if entry_pair.as_rule() == Rule::map_entry {
                        let mut entry_inner = entry_pair.into_inner();
                        let key = self.build_expression(entry_inner.next().unwrap())?;
                        let value = self.build_expression(entry_inner.next().unwrap())?;

                        // 存储键值对为两个连续的表达式
                        elements.push(key);
                        elements.push(value);
                    }
                }

                Ok(Expression::MapExpression { elements, span })
            }
            Rule::lambda_expression => {
                let mut inner = pair.into_inner();
                let params_pair = inner.next().unwrap();
                let body_pair = inner.next().unwrap();

                let mut parameters = Vec::new();
                for param_pair in params_pair.into_inner() {
                    let param = self.build_expression(param_pair)?;
                    parameters.push(param);
                }

                let body_expr = self.build_expression(body_pair)?;
                let body = vec![body_expr];

                Ok(Expression::LambdaExpression {
                    parameters,
                    body,
                    span,
                })
            }
            Rule::call_expression => {
                let mut inner = pair.into_inner();
                let callee_pair = inner.next().unwrap();
                let callee = self.build_expression(callee_pair)?;

                let mut arguments = Vec::new();
                if let Some(args_pair) = inner.next() {
                    for arg_pair in args_pair.into_inner() {
                        let arg = self.build_expression(arg_pair)?;
                        arguments.push(arg);
                    }
                }

                Ok(Expression::CallExpression {
                    callee: Box::new(callee),
                    arguments,
                    span,
                })
            }
            Rule::string_literal => {
                let text = pair.as_str();
                // 移除两边的引号
                let value = if text.starts_with('"') && text.ends_with('"') {
                    text[1..text.len() - 1].to_string()
                } else if text.starts_with('「') && text.ends_with('」') {
                    text[3..text.len() - 3].to_string()
                } else {
                    text.to_string()
                };

                Ok(Expression::StringLiteral(value, span))
            }
            Rule::number_literal => {
                let value = pair
                    .as_str()
                    .parse::<f64>()
                    .map_err(|_| ParseError::InvalidLiteral(pair.as_str().to_string()))?;

                Ok(Expression::NumberLiteral(value, span))
            }
            Rule::bool_literal => {
                let value = match pair.as_str() {
                    "啱" | "true" => true,
                    "唔啱" | "false" => false,
                    _ => return Err(ParseError::InvalidLiteral(pair.as_str().to_string())),
                };

                Ok(Expression::BoolLiteral(value, span))
            }
            Rule::null_literal => Ok(Expression::NullLiteral(span)),
            Rule::var_arg => Ok(Expression::VarArg(span)),
            Rule::identifier => Ok(Expression::Identifier(pair.as_str().to_string(), span)),
            _ => Err(ParseError::InvalidNode(pair.as_rule())),
        }
    }

    /// 构建代码块
    fn build_block(&self, pair: Pair<'_, Rule>) -> Result<Block, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);
        let mut statements = Vec::new();

        for inner_pair in pair.into_inner() {
            if inner_pair.as_rule() == Rule::statement
                || inner_pair.as_rule() == Rule::statement_list
            {
                for stmt_pair in inner_pair.into_inner() {
                    let statement = self.build_statement(stmt_pair)?;
                    statements.push(statement);
                }
            } else {
                let statement = self.build_statement(inner_pair)?;
                statements.push(statement);
            }
        }

        Ok(Block { statements, span })
    }

    /// 构建list_init语句
    fn build_list_init_statement(
        &self,
        _pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        Ok(Statement::ListInitStatement { span })
    }

    /// 构建宏调用表达式
    fn build_macro_call_expression(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Expression, ParseError> {
        let mut inner = pair.into_inner();

        // 获取宏名称
        let name_pair = inner.next().unwrap();
        let name = Box::new(self.build_expression(name_pair)?);

        // 获取宏参数
        let args_pair = inner
            .next()
            .ok_or_else(|| ParseError::Custom("找不到宏调用参数".to_string()))?;

        // 将参数解析为TokenStream而不是表达式列表
        let args_span = Span::from_pest(args_pair.as_span(), self.source);
        let token_tree = self.build_token_tree(args_pair, '(', ')')?;

        // 将TokenTree转换为TokenStream表达式
        let tokens_expr = self.token_tree_to_expression(&token_tree)?;

        // 创建TokenStream表达式
        let arguments = vec![tokens_expr];

        Ok(Expression::MacroCallExpression {
            name,
            arguments,
            span,
        })
    }

    /// 构建对象访问表达式
    fn build_object_access_expression(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Expression, ParseError> {
        // 获取对象访问链
        let chain_pair = pair.into_inner().next().unwrap();
        self.build_object_access_chain(chain_pair, span)
    }

    /// 构建对象访问链
    fn build_object_access_chain(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Expression, ParseError> {
        let mut inner = pair.into_inner();
        
        // 获取链的基础对象
        let base_pair = inner.next().unwrap();
        let base_obj = match base_pair.as_rule() {
            Rule::object_base => {
                let obj_pair = base_pair.into_inner().next().unwrap();
                self.build_expression(obj_pair)?
            },
            _ => return Err(ParseError::InvalidNode(base_pair.as_rule())),
        };

        // 获取所有属性标识符并生成链式对象访问
        let mut current_expr = base_obj;
        for prop_pair in inner {
            if prop_pair.as_rule() == Rule::identifier {
                let property = Expression::Identifier(prop_pair.as_str().to_string(), 
                    Span::from_pest(prop_pair.as_span(), self.source));
                
                current_expr = Expression::ObjectAccessExpression {
                    object: Box::new(current_expr),
                    property: Box::new(property),
                    span: Span::from_pest(prop_pair.as_span(), self.source),
                };
            }
        }

        Ok(current_expr)
    }
    
    /// 构建宏体中的元变量
    fn build_body_meta_variable(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        // 克隆pair以避免移动问题
        let pair_clone = pair.clone();
        let mut inner = pair_clone.into_inner();

        // 获取标识符
        let id_pair = inner.next().unwrap();
        let name = id_pair.as_str().to_string();

        Ok(Expression::MacroMeta { name, span })
    }

    /// 构建模式中的元操作
    fn build_pattern_meta_operation(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        // 克隆pair以避免移动问题
        let pair_clone = pair.clone();
        let mut inner = pair_clone.into_inner();

        // 获取token树
        let token_tree_pair = inner.next().unwrap();
        let token_tree = self.build_token_tree(token_tree_pair, '(', ')')?;
        let token_trees = self.token_tree_to_expression(&token_tree)?;

        // 获取重复操作符
        let rep_op_pair = inner.next().unwrap();
        let rep_op = rep_op_pair.as_str().to_string();

        // 获取可能的分隔符
        let rep_sep = if let Some(sep_pair) = inner.next() {
            // 如果分隔符是逗号，记录它
            if sep_pair.as_str() == "," {
                ",".to_string()
            } else {
                sep_pair.as_str().to_string()
            }
        } else {
            "".to_string()
        };

        Ok(Expression::MacroMetaRepInPat {
            token_trees: vec![token_trees],
            rep_sep,
            rep_op,
            span,
        })
    }

    /// 构建宏体中的元操作
    fn build_body_meta_operation(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        // 克隆pair以避免移动问题
        let pair_clone = pair.clone();
        let mut inner = pair_clone.into_inner();

        // 获取token树
        let token_tree_pair = inner.next().unwrap();
        let token_tree = self.build_token_tree(token_tree_pair, '{', '}')?;
        let token_trees = self.token_tree_to_expression(&token_tree)?;

        // 获取重复操作符
        let rep_op_pair = inner.next().unwrap();
        let rep_op = rep_op_pair.as_str().to_string();

        // 获取可能的分隔符
        let rep_sep = if let Some(sep_pair) = inner.next() {
            // 如果分隔符是逗号，记录它
            if sep_pair.as_str() == "," {
                Expression::StringLiteral(",".to_string(), span)
            } else {
                Expression::StringLiteral(sep_pair.as_str().to_string(), span)
            }
        } else {
            Expression::StringLiteral("".to_string(), span)
        };

        Ok(Expression::MacroMetaRepInBlock {
            token_trees: vec![token_trees],
            rep_sep: Box::new(rep_sep),
            rep_op: Box::new(Expression::StringLiteral(rep_op, span)),
            span,
        })
    }
    /// 构建TokenTree
    fn build_token_tree(
        &self,
        pair: Pair<'_, Rule>,
        open_delim: char,
        close_delim: char,
    ) -> Result<TokenTree, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        // 确定分隔符类型
        let delimiter = match open_delim {
            '(' => Delimiter::Parenthesis,
            '{' => Delimiter::Brace,
            '[' => Delimiter::Bracket,
            _ => Delimiter::None,
        };

        // 解析内容为TokenStream
        let mut stream = TokenStream::new();

        // 为每个子表达式创建Token或TokenTree
        for inner_pair in pair.into_inner() {
            match inner_pair.as_rule() {
                // 处理宏相关规则
                Rule::macro_token => {
                    let token_span = Span::from_pest(inner_pair.as_span(), self.source);
                    let token_text = inner_pair.as_str().to_string();
                    stream.push(TokenTree::Token(Token::new(
                        token_text,
                        TokenKind::MacroToken,
                        token_span,
                    )));
                }
                Rule::pattern_meta_variable => {
                    let var_expr = self.build_meta_variable(inner_pair)?;
                    let var_span = var_expr.span();
                    stream.push(TokenTree::Token(Token::new(
                        format!("{:?}", var_expr),
                        TokenKind::MacroMetaVariable,
                        var_span,
                    )));
                }
                Rule::body_meta_variable => {
                    let var_expr = self.build_body_meta_variable(inner_pair)?;
                    let var_span = var_expr.span();
                    stream.push(TokenTree::Token(Token::new(
                        format!("{:?}", var_expr),
                        TokenKind::MacroMetaVariable,
                        var_span,
                    )));
                }
                Rule::pattern_meta_repetition => {
                    let rep_expr = self.build_pattern_meta_operation(inner_pair)?;
                    let rep_span = rep_expr.span();
                    stream.push(TokenTree::Token(Token::new(
                        format!("{:?}", rep_expr),
                        TokenKind::MacroRepetition,
                        rep_span,
                    )));
                }
                Rule::body_meta_repetition => {
                    let rep_expr = self.build_body_meta_operation(inner_pair)?;
                    let rep_span = rep_expr.span();
                    stream.push(TokenTree::Token(Token::new(
                        format!("{:?}", rep_expr),
                        TokenKind::MacroRepetition,
                        rep_span,
                    )));
                }
                Rule::pattern_token_tree => {
                    // 递归处理嵌套的token树
                    let nested_tree = self.build_token_tree(inner_pair, '(', ')')?;
                    stream.push(nested_tree);
                }
                Rule::body_token_tree => {
                    // 递归处理嵌套的token树
                    let nested_tree = self.build_token_tree(inner_pair, '{', '}')?;
                    stream.push(nested_tree);
                }
                Rule::COMMENT => {
                    // 跳过注释
                    continue;
                }
                // 添加更多规则处理...
                _ => {
                    return Err(ParseError::Custom(format!(
                        "无法将规则 {:?} 转换为TokenTree",
                        inner_pair.as_rule()
                    )));
                }
            }
        }

        // 创建一个Group类型的TokenTree
        Ok(TokenTree::Group {
            delimiter,
            stream: Box::new(stream),
            span,
        })
    }

    /// 将TokenTree转换为表达式
    fn token_tree_to_expression(&self, token_tree: &TokenTree) -> Result<Expression, ParseError> {
        let span = match token_tree {
            TokenTree::Token(token) => token.span,
            TokenTree::Group { span, .. } => *span,
        };

        // 将TokenTree转换为TokenStream表达式
        match token_tree {
            TokenTree::Group { stream, .. } => {
                // 提取所有Token
                let tokens: Vec<Expression> = stream
                    .tokens
                    .iter()
                    .map(|tt| {
                        match tt {
                            TokenTree::Token(token) => match token.kind {
                                TokenKind::Identifier => {
                                    Expression::Identifier(token.text.clone(), token.span)
                                }
                                TokenKind::StringLiteral => {
                                    Expression::StringLiteral(token.text.clone(), token.span)
                                }
                                TokenKind::NumberLiteral => {
                                    if let Ok(num) = token.text.parse::<f64>() {
                                        Expression::NumberLiteral(num, token.span)
                                    } else {
                                        Expression::StringLiteral(token.text.clone(), token.span)
                                    }
                                }
                                _ => Expression::StringLiteral(token.text.clone(), token.span),
                            },
                            // 递归处理嵌套TokenTree
                            nested => self
                                .token_tree_to_expression(nested)
                                .unwrap_or(Expression::NullLiteral(span)),
                        }
                    })
                    .collect();

                // 创建TokenStream表达式
                Ok(Expression::TokenStream { tokens, span })
            }
            TokenTree::Token(token) => {
                // 单个Token转换为适当的表达式
                match token.kind {
                    TokenKind::Identifier => {
                        Ok(Expression::Identifier(token.text.clone(), token.span))
                    }
                    TokenKind::StringLiteral => {
                        Ok(Expression::StringLiteral(token.text.clone(), token.span))
                    }
                    TokenKind::NumberLiteral => {
                        if let Ok(num) = token.text.parse::<f64>() {
                            Ok(Expression::NumberLiteral(num, token.span))
                        } else {
                            Ok(Expression::StringLiteral(token.text.clone(), token.span))
                        }
                    }
                    _ => Ok(Expression::StringLiteral(token.text.clone(), token.span)),
                }
            }
        }
    }
}
