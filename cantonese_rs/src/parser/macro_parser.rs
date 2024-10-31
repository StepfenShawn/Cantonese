// 粤语编程语言嘅宏解析器模块 - 用於處理宏定義同調用

use super::token_tree::TokenTreeNode;
use crate::ast::{Block, Expression, Position, Span, Statement};
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

        // 解析匹配模式
        for pattern in match_patterns {
            match pattern {
                // 解析樹形表達式
                Expression::MacroMetaRepInPat {
                    token_trees,
                    rep_sep,
                    rep_op,
                    span,
                } => {
                    let pattern_tree =
                        self.parse_pattern_tree(token_trees, rep_sep, rep_op, span)?;
                    patterns.push(pattern_tree);
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
        let body = self.parse_macro_body(body_block)?;

        Ok(MacroDefinition {
            patterns,
            body,
            span: body_block.span,
        })
    }

    /// 解析模式樹
    fn parse_pattern_tree(
        &self,
        token_trees: &[Expression],
        rep_sep: &str,
        rep_op: &str,
        span: &Span,
    ) -> Result<MacroPattern, MacroError> {
        // 實際解析器會遞歸地構建模式樹

        let mut elements = Vec::new();

        for tree in token_trees {
            match tree {
                // 元變量，例如 @id:ident
                Expression::MacroMetaId {
                    id,
                    frag_spec,
                    span,
                } => {
                    if let Expression::Identifier(ref name, _) = **id {
                        let element = MacroPatternElement::MetaVariable {
                            name: name.clone(),
                            fragment_spec: match **frag_spec {
                                Expression::Identifier(ref spec, _) => spec.clone(),
                                _ => {
                                    return Err(MacroError::Definition(
                                        "無效嘅片段規格".to_string(),
                                    ));
                                }
                            },
                            span: *span,
                        };
                        elements.push(element);
                    } else {
                        return Err(MacroError::Definition("無效嘅宏元變量".to_string()));
                    }
                }
                // 字面量
                Expression::StringLiteral(s, span) => {
                    elements.push(MacroPatternElement::Literal {
                        value: s.clone(),
                        span: *span,
                    });
                }
                // 標識符
                Expression::Identifier(name, span) => {
                    elements.push(MacroPatternElement::Identifier {
                        name: name.clone(),
                        span: *span,
                    });
                }
                // 嵌套嘅模式樹
                Expression::MacroMetaRepInPat {
                    token_trees,
                    rep_sep,
                    rep_op,
                    span,
                } => {
                    let nested = self.parse_pattern_tree(token_trees, rep_sep, rep_op, span)?;
                    elements.push(MacroPatternElement::Nested(nested));
                }
                _ => {
                    return Err(MacroError::Definition(format!(
                        "不支持嘅宏模式元素: {:?}",
                        tree
                    )));
                }
            }
        }

        Ok(MacroPattern {
            elements,
            repetition_separator: rep_sep.to_string(),
            repetition_operator: rep_op.to_string(),
            span: *span,
        })
    }

    /// 解析宏體
    fn parse_macro_body(&self, block: &Block) -> Result<MacroBody, MacroError> {
        // 實際實現會解析塊內嘅語句同表達式
        let elements = block
            .statements
            .iter()
            .map(|stmt| self.statement_to_macro_element(stmt))
            .collect::<Result<Vec<_>, _>>()?;

        Ok(MacroBody {
            elements,
            span: block.span,
        })
    }

    /// 將語句轉換為宏體元素
    fn statement_to_macro_element(&self, stmt: &Statement) -> Result<MacroBodyElement, MacroError> {
        match stmt {
            // 如果語句係表達式語句，轉換表達式
            Statement::ExpressionStatement { expression, span } => {
                self.expression_to_macro_element(expression, *span)
            }
            // 其他語句暫時保持原樣
            _ => Ok(MacroBodyElement::Statement(stmt.clone())),
        }
    }

    /// 將表達式轉換為宏體元素
    fn expression_to_macro_element(
        &self,
        expr: &Expression,
        _span: Span,
    ) -> Result<MacroBodyElement, MacroError> {
        match expr {
            // 元變量引用，例如 @id
            Expression::MacroMeta { name, span } => Ok(MacroBodyElement::MetaVariableRef {
                name: name.clone(),
                span: *span,
            }),
            // 重複元素，例如 $(@element)*
            Expression::MacroMetaRepInBlock {
                token_trees,
                rep_sep,
                rep_op,
                span,
            } => {
                let mut elements = Vec::new();

                for tree in token_trees {
                    elements.push(self.expression_to_macro_element(tree, *span)?);
                }

                let rep_separator = match **rep_sep {
                    Expression::StringLiteral(ref s, _) => s.clone(),
                    _ => return Err(MacroError::Definition("無效嘅重複分隔符".to_string())),
                };

                let rep_operator = match **rep_op {
                    Expression::StringLiteral(ref s, _) => s.clone(),
                    _ => return Err(MacroError::Definition("無效嘅重複運算符".to_string())),
                };

                Ok(MacroBodyElement::Repetition {
                    elements,
                    separator: rep_separator,
                    operator: rep_operator,
                    span: *span,
                })
            }
            // 其他表達式暫時保持原樣
            _ => Ok(MacroBodyElement::Expression(expr.clone())),
        }
    }

    /// 解析宏調用
    pub fn parse_macro_call(
        &self,
        name: &str,
        token_trees: &[TokenTreeNode],
    ) -> Result<MacroCall, MacroError> {
        // 建立宏調用結構
        let span = Span::new(
            Position::start(), // 真實實現會計算正確嘅位置
            Position::start(),
        );

        Ok(MacroCall {
            name: name.to_string(),
            arguments: token_trees.to_vec(),
            span,
        })
    }

    pub fn build_macro_body_element(
        &self,
        expression: &Expression,
        _span: Span,
    ) -> Result<MacroBodyElement, MacroError> {
        // Implementation of the method
        Ok(MacroBodyElement::Expression(expression.clone()))
    }
}

/// 宏定義
#[derive(Debug, Clone)]
pub struct MacroDefinition {
    pub patterns: Vec<MacroPattern>,
    pub body: MacroBody,
    pub span: Span,
}

/// 宏模式
#[derive(Debug, Clone)]
pub struct MacroPattern {
    pub elements: Vec<MacroPatternElement>,
    pub repetition_separator: String,
    pub repetition_operator: String,
    pub span: Span,
}

/// 宏模式元素
#[derive(Debug, Clone)]
pub enum MacroPatternElement {
    // 元變量，例如 @id:ident
    MetaVariable {
        name: String,
        fragment_spec: String,
        span: Span,
    },
    // 字面量
    Literal {
        value: String,
        span: Span,
    },
    // 標識符
    Identifier {
        name: String,
        span: Span,
    },
    // 嵌套模式
    Nested(MacroPattern),
}

/// 宏體
#[derive(Debug, Clone)]
pub struct MacroBody {
    pub elements: Vec<MacroBodyElement>,
    pub span: Span,
}

/// 宏體元素
#[derive(Debug, Clone)]
pub enum MacroBodyElement {
    // 元變量引用
    MetaVariableRef {
        name: String,
        span: Span,
    },
    // 重複元素
    Repetition {
        elements: Vec<MacroBodyElement>,
        separator: String,
        operator: String,
        span: Span,
    },
    // 一般表達式
    Expression(Expression),
    // 一般語句
    Statement(Statement),
}

/// 宏調用
#[derive(Debug, Clone)]
pub struct MacroCall {
    pub name: String,
    pub arguments: Vec<TokenTreeNode>,
    pub span: Span,
}
