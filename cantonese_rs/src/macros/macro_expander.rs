// 粤语编程语言宏处理模块 - 宏展开器

use std::collections::HashMap;

use crate::ast::{
    Block, Expression, Span, Statement, Program,
};
use crate::parser::ast_builder::ParseError;
use crate::parser::token_tree::{TokenTree, TokenTreeNode, TokenKind};
use super::match_state::MatchState;
use super::meta_var::MetaVarEnv;
use super::pat_matcher::PatMatcher;
use super::regex::build_regex;

/// 宏定义
#[derive(Debug, Clone)]
pub struct MacroDefinition {
    /// 宏的名称
    pub name: String,
    /// 宏的模式列表
    pub patterns: Vec<Expression>,
    /// 对应的宏主体列表
    pub bodies: Vec<TokenTree>,
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
}

/// 宏展开器 - 负责展开宏调用
#[derive(Debug)]
pub struct MacroExpander {
    /// 已定义的宏
    macros: HashMap<String, MacroDefinition>,
}

impl MacroExpander {
    /// 创建新的宏展开器
    pub fn new() -> Self {
        Self {
            macros: HashMap::new(),
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
            if let Statement::MacroDefStatement { name, match_patterns, match_block, span: _ } = statement {
                if let Expression::Identifier(name_str, _) = &**name {
                    let macro_def = MacroDefinition {
                        name: name_str.clone(),
                        patterns: match_patterns.clone(),
                        bodies: vec![match_block.clone()],
                    };
                    expander.add_macro(macro_def);
                }
            }
        }
        
        expander
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
            // 宏调用语句 - 直接展开
            Statement::MacroCallStatement { name, arguments, span } => {
                if let Expression::Identifier(name_str, _) = &name {
                    if self.macros.contains_key(name_str) {
                        // 获取宏定义
                        let macro_def = self.get_macro(name_str).unwrap();
                        
                        // 尝试展开宏调用
                        match self.try_expand_with_macro(macro_def, &arguments) {
                            Ok(expanded) => return expanded,
                            Err(err) => {
                                // 展开失败，返回一个错误表达式语句
                                return Statement::ExpressionStatement {
                                    expression: Expression::StringLiteral(
                                        format!("宏展开错误: {}", err),
                                        span
                                    ),
                                    span,
                                };
                            }
                        }
                    }
                }
                
                // 如果无法展开，返回原始语句
                Statement::MacroCallStatement { 
                    name, 
                    arguments, 
                    span 
                }
            },
            
            // 递归处理各种包含子语句或表达式的语句类型
            Statement::IfStatement { if_exp, if_block, elif_exps, elif_blocks, else_block, span } => {
                let expanded_if_exp = self.expand_expression(if_exp);
                let expanded_if_block = self.expand_block(if_block);
                let expanded_elif_exps = elif_exps.into_iter()
                    .map(|expr| self.expand_expression(expr))
                    .collect();
                let expanded_elif_blocks = elif_blocks.into_iter()
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
            Statement::WhileStatement { condition, body, span } => {
                let expanded_condition = self.expand_expression(condition);
                let expanded_body = self.expand_block(body);
                
                Statement::WhileStatement {
                    condition: expanded_condition,
                    body: expanded_body,
                    span,
                }
            }
            Statement::ForStatement { var, from_exp, to_exp, body, span } => {
                let expanded_var = self.expand_expression(var);
                let expanded_from = self.expand_expression(from_exp);
                let expanded_to = self.expand_expression(to_exp);
                let expanded_body = self.expand_block(body);
                
                Statement::ForStatement {
                    var: expanded_var,
                    from_exp: expanded_from,
                    to_exp: expanded_to,
                    body: expanded_body,
                    span,
                }
            }
            Statement::ForEachStatement { id_list, exp_list, body, span } => {
                let expanded_id_list = id_list.into_iter()
                    .map(|expr| self.expand_expression(expr))
                    .collect();
                let expanded_exp_list = exp_list.into_iter()
                    .map(|expr| self.expand_expression(expr))
                    .collect();
                let expanded_body = self.expand_block(body);
                
                Statement::ForEachStatement {
                    id_list: expanded_id_list,
                    exp_list: expanded_exp_list,
                    body: expanded_body,
                    span,
                }
            }
            Statement::FunctionDeclaration { name, parameters, body, span } => {
                let expanded_name = self.expand_expression(name);
                let expanded_parameters = parameters.into_iter()
                    .map(|expr| self.expand_expression(expr))
                    .collect();
                let expanded_body = self.expand_block(body);
                
                Statement::FunctionDeclaration {
                    name: expanded_name,
                    parameters: expanded_parameters,
                    body: expanded_body,
                    span,
                }
            }
            Statement::ExpressionStatement { expression, span } => {
                // 检查是否为宏调用表达式
                match &expression {
                    Expression::CallExpression { callee, arguments, span: call_span } => {
                        if let Expression::Identifier(name, _) = &**callee {
                            if self.macros.contains_key(name) {
                                // 尝试展开宏调用
                                match self.try_expand_macro_call(name, arguments, *call_span) {
                                    Ok(expanded) => return expanded,
                                    Err(_) => {
                                        // 如果展开失败，继续作为普通表达式处理
                                        // 这里可以记录日志或发出警告
                                    }
                                }
                            }
                        }
                    }
                    _ => {}
                }
                
                // 不是宏调用或无法展开，则展开表达式
                let expanded_expression = self.expand_expression(expression);
                Statement::ExpressionStatement {
                    expression: expanded_expression,
                    span,
                }
            }
            // 递归处理其他包含表达式的语句类型
            // 遍历语句中所有可能包含表达式的字段
            _ => statement,
        }
    }

    /// 展开代码块
    fn expand_block(&self, block: Block) -> Block {
        let expanded_statements = self.expand_statements(block.statements);
        
        Block {
            statements: expanded_statements,
            span: block.span,
        }
    }

    /// 展开表达式
    fn expand_expression(&self, expression: Expression) -> Expression {
        match expression {
            Expression::CallExpression { callee, arguments, span } => {
                // 检查是否为宏调用
                if let Expression::Identifier(name, _) = &*callee {
                    if self.macros.contains_key(name) {
                        // 尝试展开宏调用
                        match self.try_expand_macro_call(name, &arguments, span) {
                            Ok(Statement::ExpressionStatement { expression, .. }) => {
                                // 如果成功展开为表达式语句，返回表达式
                                return expression;
                            },
                            _ => {
                                // 无法作为表达式展开，继续处理
                            }
                        }
                    }
                }
                
                // 不是宏调用或无法展开，递归展开子表达式
                let expanded_callee = Box::new(self.expand_expression(*callee));
                let expanded_arguments = arguments.into_iter()
                    .map(|arg| self.expand_expression(arg))
                    .collect();
                
                Expression::CallExpression {
                    callee: expanded_callee,
                    arguments: expanded_arguments,
                    span,
                }
            }
            Expression::BinaryExpression { left, operator, right, span } => {
                let expanded_left = Box::new(self.expand_expression(*left));
                let expanded_right = Box::new(self.expand_expression(*right));
                
                Expression::BinaryExpression {
                    left: expanded_left,
                    operator,
                    right: expanded_right,
                    span,
                }
            }
            Expression::UnaryExpression { operator, operand, span } => {
                let expanded_operand = Box::new(self.expand_expression(*operand));
                
                Expression::UnaryExpression {
                    operator,
                    operand: expanded_operand,
                    span,
                }
            }
            Expression::ObjectAccessExpression { object, property, span } => {
                let expanded_object = Box::new(self.expand_expression(*object));
                let expanded_property = Box::new(self.expand_expression(*property));
                
                Expression::ObjectAccessExpression {
                    object: expanded_object,
                    property: expanded_property,
                    span,
                }
            }
            Expression::ListAccessExpression { list, index, span } => {
                let expanded_list = Box::new(self.expand_expression(*list));
                let expanded_index = Box::new(self.expand_expression(*index));
                
                Expression::ListAccessExpression {
                    list: expanded_list,
                    index: expanded_index,
                    span,
                }
            }
            Expression::ListExpression { elements, span } => {
                let expanded_elements = elements.into_iter()
                    .map(|elem| self.expand_expression(elem))
                    .collect();
                
                Expression::ListExpression {
                    elements: expanded_elements,
                    span,
                }
            }
            // 其他表达式类型保持不变
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
        // 查找宏定义
        let macro_def = self.get_macro(macro_name)
            .ok_or_else(|| MacroExpandError::CannotExpand(format!("未找到宏定义: {}", macro_name)))?;
        
        // 将参数转换为TokenTree
        let token_tree = self.expressions_to_token_tree(arguments, span);
        
        // 尝试匹配宏模式并展开
        self.try_expand_with_macro(macro_def, &token_tree)
    }

    /// 使用宏定义展开TokenTree - 参考Python版本的实现
    fn try_expand_with_macro(
        &self,
        macro_def: &MacroDefinition,
        token_tree: &TokenTree,
    ) -> Result<Statement, MacroExpandError> {
        // 遍历所有模式，尝试匹配
        for (pattern_idx, pattern) in macro_def.patterns.iter().enumerate() {
            // 转换模式为正则表达式
            // 这里可以使用更简单的方式，直接进行模式匹配
            let pattern_regex = match pattern {
                Expression::MacroMetaRepInPat { token_trees, .. } => {
                    // 构建对应的正则表达式
                    build_regex(token_trees)
                }
                _ => {
                    // 单个表达式模式
                    build_regex(&[pattern.clone()])
                }
            };
            
            // 获取TokenTree中的表达式
            let expressions = self.token_tree_to_expressions(token_tree);
            
            // 创建匹配状态
            let state = MatchState::new();
            let mut matcher = PatMatcher::new("".to_string()).with_state(state);
            
            // 尝试匹配
            if matcher.matches(&pattern_regex, &expressions) {
                // 匹配成功，获取捕获的元变量
                let mut meta_vars = matcher.state().meta_vars.clone();
                
                // 获取对应的宏主体
                let body = if pattern_idx < macro_def.bodies.len() {
                    &macro_def.bodies[pattern_idx]
                } else if !macro_def.bodies.is_empty() {
                    &macro_def.bodies[0] // 如果模式多于主体，使用第一个主体
                } else {
                    return Err(MacroExpandError::CannotExpand("缺少宏主体".to_string()));
                };
                
                // 展开宏主体
                return self.expand_macro_body(body, &mut meta_vars);
            }
        }
        
        // 没有匹配的模式
        Err(MacroExpandError::NoMatchingPattern)
    }

    /// 展开宏主体 - 参考Python版本的实现
    fn expand_macro_body(
        &self,
        body: &TokenTree,
        meta_vars: &mut MetaVarEnv,
    ) -> Result<Statement, MacroExpandError> {
        // 将宏主体转换为语句
        // 这部分是宏展开的核心，需要处理:
        // 1. 替换元变量引用
        // 2. 处理重复结构 (${...}+)
        // 3. 解析展开后的内容为语句
        
        // 首先将TokenTree转换为字符串
        let mut expanded_tokens = Vec::new();
        
        // 递归处理宏主体中的节点
        for node in &body.children {
            match node {
                TokenTreeNode::Token(token) => {
                    if token.is_meta_variable() {
                        // 处理元变量引用，例如 @identifier
                        let var_name = token.text.trim_start_matches('@').split(':').next().unwrap_or("");
                        // 获取元变量值并替换
                        if let Some(meta_var) = meta_vars.get(var_name) {
                            let value = meta_var.value();
                            expanded_tokens.push(value);
                        } else {
                            // 未找到元变量
                            return Err(MacroExpandError::CannotExpand(
                                format!("未找到元变量: {}", var_name)
                            ));
                        }
                    } else if token.kind == TokenKind::MetaOperation {
                        // 处理元操作，例如 ${identifier}+ 或 $(token_tree)*
                        // 这里需要更复杂的逻辑，暂时简化处理
                        if token.text.starts_with("${") && token.text.ends_with("}+") {
                            // 元变量重复，如 ${id}+
                            let var_name = token.text[2..token.text.len()-2].trim();
                            if let Some(meta_var) = meta_vars.get(var_name) {
                                let rep_count = meta_var.repetition_count();
                                for _ in 0..rep_count {
                                    let value = meta_var.value();
                                    expanded_tokens.push(value);
                                }
                            }
                        } else {
                            // 其他元操作，临时添加为字符串
                            expanded_tokens.push(Expression::StringLiteral(
                                token.text.clone(),
                                token.span,
                            ));
                        }
                    } else {
                        // 普通标记，添加到结果
                        expanded_tokens.push(Expression::StringLiteral(
                            token.text.clone(),
                            token.span,
                        ));
                    }
                }
                TokenTreeNode::Tree(tree) => {
                    // 嵌套树结构，递归处理
                    let nested_result = self.expand_macro_body(tree, meta_vars)?;
                    if let Statement::ExpressionStatement { expression, .. } = nested_result {
                        expanded_tokens.push(expression);
                    } else {
                        // 如果展开结果不是表达式语句，将其作为字符串添加
                        let nested_tree_text = format!("{}{}", tree.open_symbol, tree.close_symbol);
                        expanded_tokens.push(Expression::StringLiteral(
                            nested_tree_text,
                            tree.span,
                        ));
                    }
                }
            }
        }
        
        // 创建一个临时的ExpressionStatement
        // 在实际实现中，我们需要将expanded_tokens解析为语句
        let dummy_expr = if !expanded_tokens.is_empty() {
            expanded_tokens[0].clone()
        } else {
            Expression::StringLiteral("".to_string(), Span::new(Default::default(), Default::default()))
        };
        
        Ok(Statement::ExpressionStatement {
            expression: dummy_expr,
            span: body.span,
        })
    }

    /// 将表达式列表转换为TokenTree
    fn expressions_to_token_tree(&self, expressions: &[Expression], span: Span) -> TokenTree {
        // 转换表达式为TokenTree - 实际应该递归构建
        let mut children = Vec::new();
        
        for expr in expressions {
            match expr {
                Expression::StringLiteral(text, expr_span) => {
                    // 字符串字面量转为标记
                    children.push(TokenTreeNode::Token(
                        crate::parser::token_tree::Token::new(
                            text.clone(),
                            crate::parser::token_tree::TokenKind::StringLiteral,
                            *expr_span,
                        )
                    ));
                }
                Expression::Identifier(name, expr_span) => {
                    // 标识符转为标记
                    children.push(TokenTreeNode::Token(
                        crate::parser::token_tree::Token::new(
                            name.clone(),
                            crate::parser::token_tree::TokenKind::Identifier,
                            *expr_span,
                        )
                    ));
                }
                // 其他表达式类型需要进一步处理
                _ => {
                    // 暂时简化处理，可以根据需要扩展
                }
            }
        }
        
        TokenTree {
            children,
            open_symbol: '(',
            close_symbol: ')',
            span,
        }
    }

    /// 将TokenTree转换为表达式列表
    fn token_tree_to_expressions(&self, token_tree: &TokenTree) -> Vec<Expression> {
        // 将TokenTree转换为表达式列表 - 类似于Python版本中的flatten函数
        let mut result = Vec::new();
        
        for node in &token_tree.children {
            match node {
                TokenTreeNode::Token(token) => {
                    // 根据标记类型创建不同的表达式
                    let expr = match token.kind {
                        crate::parser::token_tree::TokenKind::Identifier => {
                            Expression::Identifier(token.text.clone(), token.span)
                        }
                        crate::parser::token_tree::TokenKind::StringLiteral => {
                            Expression::StringLiteral(token.text.clone(), token.span)
                        }
                        crate::parser::token_tree::TokenKind::NumberLiteral => {
                            // 尝试解析为数字
                            if let Ok(num) = token.text.parse::<f64>() {
                                Expression::NumberLiteral(num, token.span)
                            } else {
                                // 解析失败时作为字符串处理
                                Expression::StringLiteral(token.text.clone(), token.span)
                            }
                        }
                        // 处理其他类型的标记
                        _ => Expression::StringLiteral(token.text.clone(), token.span),
                    };
                    result.push(expr);
                }
                TokenTreeNode::Tree(tree) => {
                    // 递归处理嵌套树
                    let nested_exprs = self.token_tree_to_expressions(tree);
                    result.extend(nested_exprs);
                }
            }
        }
        
        result
    }
} 