// 粤语编程语言嘅宏解析器模块 - 用於處理宏定義同調用

use crate::ast::{Block, Expression, Position, Span, Statement};
use crate::parser::token_tree::{Token, TokenTree, TokenStream, Delimiter};
use crate::macros::token_matcher::FragmentType;
use thiserror::Error;

/// 宏解析錯誤
#[derive(Debug, Error)]
pub enum MacroError {
    #[error("宏定義錯誤: {0}")]
    Definition(String),

    #[error("宏匹配錯誤: {0}")]
    Matching(String),

    #[error("宏展開錯誤: {0}")]
    Expansion(String),
}

/// 宏解析器
pub struct MacroParser<'a> {
    source: &'a str,
}

impl<'a> MacroParser<'a> {
    /// 創建一個新嘅宏解析器
    pub fn new(source: &'a str) -> Self {
        Self { source }
    }

    /// 解析宏定義
    pub fn parse_macro_definition(
        &self,
        match_patterns: &[Expression],
        body_block: &Block,
    ) -> Result<MacroDefinition, MacroError> {
        let mut patterns = Vec::new();
        let mut bodies = Vec::new();

        // 解析匹配模式
        for pattern in match_patterns {
            match pattern {
                // 解析樹形表達式作為模式
                Expression::MacroMetaRepInPat {
                    token_trees,
                    rep_sep,
                    rep_op,
                    span,
                } => {
                    let pattern_stream = self.build_token_stream(token_trees)?;
                    patterns.push(pattern_stream);
                }
                // 如果唔係樹，就係錯誤
                _ => {
                    return Err(MacroError::Definition(format!(
                        "無效嘅宏模式: {:?}",
                        pattern
                    )));
                }
            }
        }

        // 解析宏體
        for stmt in &body_block.statements {
            if let Statement::ExpressionStatement { expression, .. } = stmt {
                // 将表达式解析为TokenStream
                let body_stream = self.build_token_stream(&[expression.clone()])?;
                bodies.push(body_stream);
            }
        }

        Ok(MacroDefinition {
            patterns,
            bodies,
            span: body_block.span,
        })
    }

    /// 將表達式轉換為TokenStream
    fn build_token_stream(&self, expressions: &[Expression]) -> Result<TokenStream, MacroError> {
        let mut stream = TokenStream::new();

        for expr in expressions {
            match expr {
                // 標識符
                Expression::Identifier(name, span) => {
                    let token = Token::new(name.clone(), crate::parser::token_tree::TokenKind::Identifier, *span);
                    stream.push(TokenTree::Token(token));
                }
                // 字符串字面量
                Expression::StringLiteral(value, span) => {
                    let token = Token::new(format!("\"{}\"", value), crate::parser::token_tree::TokenKind::StringLiteral, *span);
                    stream.push(TokenTree::Token(token));
                }
                // 數字字面量
                Expression::NumberLiteral(value, span) => {
                    let token = Token::new(value.to_string(), crate::parser::token_tree::TokenKind::NumberLiteral, *span);
                    stream.push(TokenTree::Token(token));
                }
                // 元變量 @var:type
                Expression::MacroMetaId { id, frag_spec, span } => {
                    if let Expression::Identifier(name, _) = &**id {
                        let frag_type = if let Expression::Identifier(spec, _) = &**frag_spec {
                            spec.clone()
                        } else {
                            "expr".to_string()
                        };
                        let token_text = format!("@{}:{}", name, frag_type);
                        let token = Token::new(token_text, crate::parser::token_tree::TokenKind::MetaVariable, *span);
                        stream.push(TokenTree::Token(token));
                    }
                }
                // 其他類型的表達式
                _ => {
                    // 對於不支持的表達式類型，返回錯誤
                    return Err(MacroError::Definition(format!(
                        "不支持的表達式類型: {:?}",
                        expr
                    )));
                }
            }
        }

        Ok(stream)
    }

    /// 解析宏調用
    pub fn parse_macro_call(
        &self,
        name: &str,
        arguments: &[Expression],
    ) -> Result<MacroCall, MacroError> {
        // 轉換參數為TokenStream
        let args_stream = self.build_token_stream(arguments)?;
        
        // 創建宏調用
        let span = if let Some(expr) = arguments.first() {
            expr.span()
        } else {
            Span::new(Position::start(), Position::start())
        };
        
        Ok(MacroCall {
            name: name.to_string(),
            args: args_stream,
            span,
        })
    }
}

/// 宏定義
#[derive(Debug, Clone)]
pub struct MacroDefinition {
    /// 宏的模式列表
    pub patterns: Vec<TokenStream>,
    /// 對應的宏主體列表
    pub bodies: Vec<TokenStream>,
    /// 宏定義的位置信息
    pub span: Span,
}

/// 宏調用
#[derive(Debug, Clone)]
pub struct MacroCall {
    /// 宏的名稱
    pub name: String,
    /// 宏調用的參數
    pub args: TokenStream,
    /// 宏調用的位置信息
    pub span: Span,
}
