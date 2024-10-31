// 粤语编程语言嘅AST构建器 - 将pest解析树转换为AST

use pest::iterators::{Pair, Pairs};
use thiserror::Error;

use super::CantoneseParser;
use super::Rule;
use super::token_tree::TokenTree;
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

        if var_list_pair.as_rule() == Rule::var_list {
            for var_pair in var_list_pair.into_inner() {
                let var = self.build_expression(var_pair)?;
                var_list.push(var);
            }
        } else {
            // 如果直接是一个标识符，转换为表达式
            let var = self.build_expression(var_list_pair)?;
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
                Rule::var_list => {
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
                Rule::condition => {
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

        let object_pair = inner.next().unwrap();
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
        let mut inner = pair.into_inner();
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

    /// 构建宏定义语句
    fn build_macro_def_statement(
        &self,
        pair: Pair<'_, Rule>,
        span: Span,
    ) -> Result<Statement, ParseError> {
        let mut inner = pair.into_inner();

        // 获取宏的名称
        let name_pair = inner.next().unwrap();
        let name = self.build_expression(name_pair)?;

        // 解析宏的模式和对应的块
        let mut patterns = Vec::new();
        let mut macro_blocks = Vec::new();

        while let Some(next_pair) = inner.next() {
            match next_pair.as_rule() {
                Rule::macro_pattern => {
                    let pattern = self.build_macro_pattern(next_pair)?;
                    patterns.push(pattern);
                }
                Rule::block => {
                    let block = self.build_token_tree(next_pair)?;
                    macro_blocks.push(block);
                }
                _ => return Err(ParseError::InvalidNode(next_pair.as_rule())),
            }
        }

        // 确保模式和块的数量匹配
        if patterns.len() != macro_blocks.len() {
            return Err(ParseError::Custom(
                "宏定义中的模式和块数量不匹配".to_string(),
            ));
        }

        // 合并为一个完整的宏定义
        let match_patterns = patterns;
        let match_block = if let Some(block) = macro_blocks.first() {
            block.clone()
        } else {
            // 如果没有块，创建一个空块
            TokenTree {
                children: Vec::new(),
                open_symbol: '(',
                close_symbol: ')',
                span: Span::from_pest(pair.as_span(), self.source),
            }
        };

        Ok(Statement::MacroDefStatement {
            name: Box::new(name),
            match_patterns,
            match_block,
            span,
        })
    }

    /// 构建宏模式
    fn build_macro_pattern(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        let mut token_trees = Vec::new();
        for inner_pair in pair.into_inner() {
            match inner_pair.as_rule() {
                Rule::token_tree => {
                    let token_tree = self.build_token_tree(inner_pair)?;
                    token_trees.push(token_tree);
                }
                _ => return Err(ParseError::InvalidNode(inner_pair.as_rule())),
            }
        }

        // 将所有token_tree合并为一个表达式
        if token_trees.len() == 1 {
            Ok(token_trees.pop().unwrap())
        } else {
            // 如果有多个token_tree，创建一个ListExpression
            Ok(Expression::ListExpression {
                elements: token_trees,
                span,
            })
        }
    }

    /// 构建token树
    fn build_token_tree(&self, pair: Pair<'_, Rule>) -> Result<TokenTree, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        let mut elements = Vec::new();
        for inner_pair in pair.into_inner() {
            match inner_pair.as_rule() {
                Rule::macro_token => {
                    let token = self.build_macro_token(inner_pair)?;
                    elements.push(token);
                }
                Rule::meta_variable => {
                    let meta_var = self.build_meta_variable(inner_pair)?;
                    elements.push(meta_var);
                }
                Rule::meta_operation => {
                    let meta_op = self.build_meta_operation(inner_pair)?;
                    elements.push(meta_op);
                }
                _ => return Err(ParseError::InvalidNode(inner_pair.as_rule())),
            }
        }

        // 创建TokenTree表达式
        Ok(TokenTree {
            children: [].into(),
            open_symbol: '(',
            close_symbol: ')',
            span,
        })
    }

    /// 构建宏标记
    fn build_macro_token(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);
        let pair_str = pair.as_str().to_string();
        let inner = pair.into_inner().next();

        if let Some(inner_pair) = inner {
            match inner_pair.as_rule() {
                Rule::string_literal
                | Rule::number_literal
                | Rule::bool_literal
                | Rule::null_literal
                | Rule::identifier => self.build_expression(inner_pair),
                _ => {
                    // 处理其他操作符和符号
                    let token_text = inner_pair.as_str().to_string();
                    Ok(Expression::StringLiteral(token_text, span))
                }
            }
        } else {
            // 如果没有内部元素，则使用整个token的文本
            Ok(Expression::StringLiteral(pair_str, span))
        }
    }

    /// 构建元变量
    fn build_meta_variable(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);
        let mut inner = pair.into_inner();

        let id_pair = inner.next().unwrap();
        let id = self.build_expression(id_pair)?;

        // 检查是否有类型说明
        let frag_spec = if let Some(type_pair) = inner.next() {
            self.build_expression(type_pair)?
        } else {
            // 如果没有类型说明，使用默认的"expr"类型
            Expression::Identifier("expr".to_string(), span)
        };

        Ok(Expression::MacroMetaId {
            id: Box::new(id),
            frag_spec: Box::new(frag_spec),
            span,
        })
    }

    /// 构建元操作
    fn build_meta_operation(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);
        let inner_text = pair.as_str();

        let mut inner = pair.into_inner();
        let first_pair = inner.next().unwrap();

        match first_pair.as_rule() {
            // ${identifier,...} 元变量替换
            Rule::identifier if inner_text.starts_with("${") => {
                let mut ids = Vec::new();
                ids.push(self.build_expression(first_pair)?);

                // 添加逗号后的标识符
                while let Some(id_pair) = inner.next() {
                    if id_pair.as_rule() == Rule::identifier {
                        ids.push(self.build_expression(id_pair)?);
                    }
                }

                Ok(Expression::Names { names: ids, span })
            }
            // $(token_tree)* 重复元操作
            Rule::token_tree if inner_text.starts_with("$(") => {
                let token_tree = self.build_token_tree(first_pair)?;
                let rep_op_pair = inner.next().unwrap();
                let rep_op = rep_op_pair.as_str().to_string();

                Ok(Expression::MacroMetaRepInPat {
                    token_trees: vec![],
                    rep_sep: ",".to_string(), // 默认使用逗号作为分隔符
                    rep_op,
                    span,
                })
            }
            // $meta_variable 元变量引用
            Rule::meta_variable if inner_text.starts_with("$@") => {
                let meta_var = self.build_meta_variable(first_pair)?;

                // 获取meta_variable的名称
                let name = match &meta_var {
                    Expression::MacroMetaId { id, .. } => {
                        if let Expression::Identifier(id_name, _) = &**id {
                            format!("${}", id_name)
                        } else {
                            format!("${}", inner_text.trim_start_matches("$@"))
                        }
                    }
                    _ => format!("${}", inner_text.trim_start_matches("$@")),
                };

                Ok(Expression::MacroMeta { name, span })
            }
            _ => Err(ParseError::InvalidNode(first_pair.as_rule())),
        }
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
    fn build_expression(&self, pair: Pair<'_, Rule>) -> Result<Expression, ParseError> {
        let span = Span::from_pest(pair.as_span(), self.source);

        match pair.as_rule() {
            Rule::expression => {
                let mut iter = pair.into_inner();
                let first = iter.next().unwrap();

                // 如果只有一个项，直接处理
                if iter.len() == 0 {
                    return self.build_expression(first);
                }

                // 否则是二元表达式
                let mut left = self.build_expression(first)?;

                while let Some(op_pair) = iter.next() {
                    if op_pair.as_rule() != Rule::binary_operator {
                        return Err(ParseError::InvalidNode(op_pair.as_rule()));
                    }

                    let op_str = op_pair.as_str();
                    let operator = BinaryOperator::from_str(op_str)
                        .ok_or_else(|| ParseError::InvalidOperator(op_str.to_string()))?;

                    let right_pair = iter.next().unwrap();
                    let right = self.build_expression(right_pair)?;

                    let expr_span = Span::new(left.span().start, right.span().end);

                    left = Expression::BinaryExpression {
                        left: Box::new(left),
                        operator,
                        right: Box::new(right),
                        span: expr_span,
                    };
                }

                Ok(left)
            }
            Rule::term => {
                let inner = pair.into_inner().next().unwrap();
                self.build_expression(inner)
            }
            Rule::unary_expression => {
                let mut inner = pair.into_inner();
                let op_pair = inner.next().unwrap();
                let operand_pair = inner.next().unwrap();

                let op_str = op_pair.as_str();
                let operator = UnaryOperator::from_str(op_str)
                    .ok_or_else(|| ParseError::InvalidOperator(op_str.to_string()))?;

                let operand = self.build_expression(operand_pair)?;

                Ok(Expression::UnaryExpression {
                    operator,
                    operand: Box::new(operand),
                    span,
                })
            }
            Rule::parenthesized_expression => {
                let inner = pair.into_inner().next().unwrap();
                let expression = self.build_expression(inner)?;

                Ok(Expression::ParenthesizedExpression {
                    expression: Box::new(expression),
                    span,
                })
            }
            Rule::object_access_expression => {
                let mut inner = pair.into_inner();
                let object_pair = inner.next().unwrap();
                let property_pair = inner.next().unwrap();

                let object = self.build_expression(object_pair)?;
                let property = self.build_expression(property_pair)?;

                Ok(Expression::ObjectAccessExpression {
                    object: Box::new(object),
                    property: Box::new(property),
                    span,
                })
            }
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
}
