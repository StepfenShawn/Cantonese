// 粤语编程语言宏处理模块 - 宏展开器

use std::collections::HashMap;

use super::token_matcher::{FragmentType, MatchError, MetaVariable, TokenMatcher};
use crate::ast::{
    Block, Expression, Program, Span, Statement,
    position::{self, Position},
};
use crate::parser::ast_builder::ParseError;
use crate::parser::token_tree::{Delimiter, Token, TokenKind, TokenStream, TokenTree};

/// 宏定义
#[derive(Debug, Clone)]
pub struct MacroDefinition {
    /// 宏的名称
    pub name: String,
    /// 宏的模式列表 - 在匹配时会尝试按顺序匹配每个模式
    pub patterns: Vec<TokenStream>,
    /// 对应的宏主体列表 - 用于展开宏
    pub bodies: Vec<TokenStream>,
    /// 宏定义的位置信息
    pub span: Span,
}

/// 宏调用
#[derive(Debug, Clone)]
pub struct MacroCall {
    /// 宏的名称
    pub name: String,
    /// 宏调用的参数
    pub args: TokenStream,
    /// 宏调用的位置信息
    pub span: Span,
}

/// 宏展开错误
#[derive(Debug, thiserror::Error)]
pub enum MacroExpandError {
    #[error("宏无法展开：{0}")]
    CannotExpand(String),

    #[error("解析错误：{0}")]
    ParseError(#[from] ParseError),

    #[error("无法找到匹配的宏模式")]
    NoMatchingPattern,

    #[error("匹配错误：{0}")]
    MatchError(#[from] MatchError),

    #[error("无效的宏调用：{0}")]
    InvalidCall(String),
}

/// 宏展开器 - 负责展开宏调用
#[derive(Debug)]
pub struct MacroExpander {
    /// 已定义的宏
    macros: HashMap<String, MacroDefinition>,
    /// 标记匹配器
    matcher: TokenMatcher,
}

impl MacroExpander {
    /// 创建新的宏展开器
    pub fn new() -> Self {
        Self {
            macros: HashMap::new(),
            matcher: TokenMatcher::new(),
        }
    }

    /// 添加宏定义
    pub fn add_macro(&mut self, macro_def: MacroDefinition) {
        self.macros.insert(macro_def.name.clone(), macro_def);
    }

    /// 获取宏定义
    pub fn get_macro(&self, name: &str) -> Option<&MacroDefinition> {
        self.macros.get(name)
    }

    /// 展开程序
    pub fn expand_program(&self, program: Program) -> Program {
        // 第一步：收集所有宏定义
        let expander = self.collect_macro_definitions(&program);

        // 第二步：展开剩余程序中的宏调用
        let expanded_statements = expander.expand_statements(program.statements);

        Program {
            statements: expanded_statements,
            span: program.span,
        }
    }

    /// 收集宏定义
    fn collect_macro_definitions(&self, program: &Program) -> Self {
        let mut expander = MacroExpander::new();

        // 复制现有宏定义
        for (name, macro_def) in &self.macros {
            expander.macros.insert(name.clone(), macro_def.clone());
        }

        // 收集程序中的新宏定义
        for statement in &program.statements {
            if let Statement::MacroDefStatement {
                name,
                pattern,
                body,
                span,
            } = statement
            {
                // 解析宏定义
                if let Ok(macro_def) = self.parse_macro_definition(name, pattern, body, span) {
                    expander.add_macro(macro_def);
                }
            }
        }

        expander
    }

    /// 解析宏定义
    fn parse_macro_definition(
        &self,
        name: &str,
        patterns: &[Expression],
        bodies: &[Expression],
        span: &Span,
    ) -> Result<MacroDefinition, MacroExpandError> {
        // 从AST表达式解析模式和主体
        let mut pattern_streams = Vec::new();
        let mut body_streams = Vec::new();

        // 处理每一个模式
        for pattern in patterns.iter() {
            // 解析模式为TokenStream
            let pattern_stream = self.expression_to_token_stream(pattern)?;
            pattern_streams.push(pattern_stream);
        }

        // 处理每一个主体
        for body in bodies.iter() {
            // 解析主体为TokenStream
            let body_stream = self.expression_to_token_stream(body)?;
            body_streams.push(body_stream);
        }

        Ok(MacroDefinition {
            name: name.to_string(),
            patterns: pattern_streams,
            bodies: body_streams,
            span: *span,
        })
    }

    /// 展开语句列表
    fn expand_statements(&self, statements: Vec<Statement>) -> Vec<Statement> {
        let mut expanded_statements = Vec::new();

        for statement in statements {
            // 跳过宏定义语句，因为已经收集过了
            if matches!(statement, Statement::MacroDefStatement { .. }) {
                continue;
            }

            // 展开语句
            let expanded = self.expand_statement(statement);
            expanded_statements.push(expanded);
        }

        expanded_statements
    }

    /// 展开单个语句
    fn expand_statement(&self, statement: Statement) -> Statement {
        match statement {
            // 处理表达式语句，可能包含宏调用
            Statement::ExpressionStatement { expression, span } => {
                let expanded_expr = self.expand_expression(expression);
                Statement::ExpressionStatement {
                    expression: expanded_expr,
                    span,
                }
            }
            // 递归处理其他类型的语句
            Statement::IfStatement {
                if_exp,
                if_block,
                elif_exps,
                elif_blocks,
                else_block,
                span,
            } => {
                let expanded_if_exp = self.expand_expression(if_exp);
                let expanded_if_block = self.expand_block(if_block);
                let expanded_elif_exps = elif_exps
                    .into_iter()
                    .map(|expr| self.expand_expression(expr))
                    .collect();
                let expanded_elif_blocks = elif_blocks
                    .into_iter()
                    .map(|block| self.expand_block(block))
                    .collect();
                let expanded_else_block = else_block.map(|block| self.expand_block(block));

                Statement::IfStatement {
                    if_exp: expanded_if_exp,
                    if_block: expanded_if_block,
                    elif_exps: expanded_elif_exps,
                    elif_blocks: expanded_elif_blocks,
                    else_block: expanded_else_block,
                    span,
                }
            }
            // 对其他类型的语句也执行类似的递归展开
            Statement::WhileStatement {
                condition,
                body,
                span,
            } => {
                let expanded_condition = self.expand_expression(condition);
                let expanded_body = self.expand_block(body);

                Statement::WhileStatement {
                    condition: expanded_condition,
                    body: expanded_body,
                    span,
                }
            }
            // 对于不包含表达式或块的语句，直接返回原语句
            _ => statement,
        }
    }

    /// 展开代码块
    fn expand_block(&self, block: Block) -> Block {
        let expanded_statements = self
            .expand_statements(block.statements)
            .into_iter()
            .collect();

        Block {
            statements: expanded_statements,
            span: block.span,
        }
    }

    /// 展开表达式
    fn expand_expression(&self, expression: Expression) -> Expression {
        match expression {
            // 处理宏调用表达式
            Expression::CallExpression {
                callee,
                arguments,
                span,
            } => {
                // 检查是否为宏调用
                if let Expression::Identifier(name, _) = &*callee {
                    if self.macros.contains_key(name) {
                        // 尝试展开宏调用
                        match self.try_expand_macro_call(name, &arguments, span) {
                            Ok(expanded) => {
                                // 从语句中提取表达式
                                if let Statement::ExpressionStatement { expression, .. } = expanded
                                {
                                    return expression;
                                }
                            }
                            Err(_) => {}
                        }
                    }
                }

                // 如果不是宏调用或展开失败，递归展开参数
                let expanded_callee = Box::new(self.expand_expression(*callee));
                let expanded_arguments = arguments
                    .into_iter()
                    .map(|arg| self.expand_expression(arg))
                    .collect();

                Expression::CallExpression {
                    callee: expanded_callee,
                    arguments: expanded_arguments,
                    span,
                }
            }
            // 递归处理其他表达式类型...
            Expression::BinaryExpression {
                left,
                operator,
                right,
                span,
            } => {
                let expanded_left = Box::new(self.expand_expression(*left));
                let expanded_right = Box::new(self.expand_expression(*right));

                Expression::BinaryExpression {
                    left: expanded_left,
                    operator,
                    right: expanded_right,
                    span,
                }
            }
            // 递归处理更多表达式类型...
            // 对于不包含子表达式的基本表达式类型，直接返回原表达式
            _ => expression,
        }
    }

    /// 尝试展开宏调用
    fn try_expand_macro_call(
        &self,
        macro_name: &str,
        arguments: &[Expression],
        span: Span,
    ) -> Result<Statement, MacroExpandError> {
        // 获取宏定义
        let macro_def = self
            .macros
            .get(macro_name)
            .ok_or_else(|| MacroExpandError::InvalidCall(format!("未定义的宏: {}", macro_name)))?;

        // 将参数转换为TokenStream
        let args_stream = self.expressions_to_token_stream(arguments, span)?;

        // 尝试匹配和展开
        self.try_expand_with_macro(macro_def, &args_stream)
    }

    /// 使用宏定义展开TokenStream
    fn try_expand_with_macro(
        &self,
        macro_def: &MacroDefinition,
        args: &TokenStream,
    ) -> Result<Statement, MacroExpandError> {
        // 尝试匹配每个模式
        for (i, pattern) in macro_def.patterns.iter().enumerate() {
            if let Some(body) = macro_def.bodies.get(i) {
                // 尝试匹配当前模式
                match self.matcher.match_pattern(pattern, args) {
                    Ok(Some(match_result)) => {
                        // 模式匹配成功，展开宏体
                        let expanded = self.matcher.expand_macro(body, &match_result.bindings)?;

                        // 将展开后的TokenStream转换回Statement
                        return self.token_stream_to_statement(&expanded);
                    }
                    Ok(None) => {
                        // 当前模式不匹配，继续尝试下一个模式
                        continue;
                    }
                    Err(err) => {
                        // 匹配过程中出错
                        return Err(MacroExpandError::MatchError(err));
                    }
                }
            }
        }

        // 没有匹配的模式
        Err(MacroExpandError::NoMatchingPattern)
    }

    /// 将表达式转换为TokenStream
    fn expression_to_token_stream(
        &self,
        expression: &Expression,
    ) -> Result<TokenStream, MacroExpandError> {
        // 根据表达式类型创建不同的TokenTree
        match expression {
            Expression::Identifier(name, span) => {
                let token = Token::new(name.clone(), TokenKind::Identifier, *span);
                let token_tree = TokenTree::Token(token);
                let mut stream = TokenStream::new();
                stream.push(token_tree);
                Ok(stream)
            }
            Expression::StringLiteral(value, span) => {
                let token = Token::new(format!("\"{}\"", value), TokenKind::StringLiteral, *span);
                let token_tree = TokenTree::Token(token);
                let mut stream = TokenStream::new();
                stream.push(token_tree);
                Ok(stream)
            }
            Expression::NumberLiteral(value, span) => {
                let token = Token::new(value.to_string(), TokenKind::NumberLiteral, *span);
                let token_tree = TokenTree::Token(token);
                let mut stream = TokenStream::new();
                stream.push(token_tree);
                Ok(stream)
            }
            Expression::MacroMetaId {
                id,
                frag_spec,
                span,
            } => {
                // 创建元变量TokenTree
                if let Expression::Identifier(name, _) = &**id {
                    let frag_type = if let Expression::Identifier(spec, _) = &**frag_spec {
                        spec
                    } else {
                        "expr" // 默认类型
                    };
                    let token_text = format!("@{}:{}", name, frag_type);
                    let token = Token::new(token_text, TokenKind::MetaVariable, *span);
                    let token_tree = TokenTree::Token(token);
                    let mut stream = TokenStream::new();
                    stream.push(token_tree);
                    Ok(stream)
                } else {
                    Err(MacroExpandError::CannotExpand("无效的元变量".to_string()))
                }
            }
            // 直接支持TokenStream表达式
            Expression::TokenStream { tokens, span } => {
                let mut stream = TokenStream::new();

                // 遍历所有子表达式，将它们转换为TokenTree
                for token_expr in tokens {
                    // 递归转换子表达式
                    let sub_stream = self.expression_to_token_stream(token_expr)?;
                    // 添加到当前流
                    for token in sub_stream.tokens {
                        stream.push(token);
                    }
                }

                // 设置位置信息
                stream.span = Some(*span);
                Ok(stream)
            }
            // 处理其他类型的表达式...
            _ => {
                // 对于复杂表达式，可能需要递归处理
                Err(MacroExpandError::CannotExpand(format!(
                    "暂不支持将表达式 {:?} 转换为TokenStream",
                    expression
                )))
            }
        }
    }

    /// 将多个表达式转换为TokenStream
    fn expressions_to_token_stream(
        &self,
        expressions: &[Expression],
        span: Span,
    ) -> Result<TokenStream, MacroExpandError> {
        let mut stream = TokenStream::new();

        // 处理每个表达式
        for expr in expressions {
            let expr_stream = self.expression_to_token_stream(expr)?;
            for token in expr_stream.tokens {
                stream.push(token);
            }
        }

        Ok(stream)
    }

    /// 将TokenStream转换为Statement
    fn token_stream_to_statement(
        &self,
        stream: &TokenStream,
    ) -> Result<Statement, MacroExpandError> {
        // 简单实现：将TokenStream视为表达式语句
        // 在实际实现中，这里需要调用Parser将TokenStream解析为完整的AST

        // 创建一个简单的表达式
        let expr = self.token_stream_to_expression(stream)?;
        let span = expr.span();

        Ok(Statement::ExpressionStatement {
            expression: expr,
            span,
        })
    }

    /// 将TokenStream转换为Expression
    fn token_stream_to_expression(
        &self,
        stream: &TokenStream,
    ) -> Result<Expression, MacroExpandError> {
        if stream.tokens.is_empty() {
            // 空的TokenStream，创建一个空值表达式
            let dummy_span = Span::new(Position::start(), Position::start());
            return Ok(Expression::NullLiteral(dummy_span));
        }

        // 简单实现：只处理最基本的情况
        match &stream.tokens[0] {
            TokenTree::Token(token) => {
                match token.kind {
                    TokenKind::Identifier => {
                        Ok(Expression::Identifier(token.text.clone(), token.span))
                    }
                    TokenKind::StringLiteral => {
                        // 去掉引号
                        let text = token.text.trim_matches('"');
                        Ok(Expression::StringLiteral(text.to_string(), token.span))
                    }
                    TokenKind::NumberLiteral => {
                        // 尝试解析为数字
                        if let Ok(num) = token.text.parse::<f64>() {
                            Ok(Expression::NumberLiteral(num, token.span))
                        } else {
                            Err(MacroExpandError::CannotExpand(format!(
                                "无法解析数字: {}",
                                token.text
                            )))
                        }
                    }
                    _ => {
                        // 其他类型的标记暂不支持
                        Err(MacroExpandError::CannotExpand(format!(
                            "不支持转换标记类型: {:?}",
                            token.kind
                        )))
                    }
                }
            }
            TokenTree::Group { .. } => {
                // 分组处理需要更复杂的解析逻辑
                Err(MacroExpandError::CannotExpand(
                    "暂不支持将分组转换为表达式".to_string(),
                ))
            }
        }
    }
}
