// 粤语编程语言嘅Token Tree模块 - 用於宏处理

use crate::ast::position::Span;
use serde::{Deserialize, Serialize};

/// Token樹 - 代表一個分組嘅語法結構
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TokenTree {
    /// 子節點
    pub children: Vec<TokenTreeNode>,
    /// 开始符號 - '(' 或 '{'
    pub open_symbol: char,
    /// 结束符號 - ')' 或 '}'
    pub close_symbol: char,
    /// 位置信息
    pub span: Span,
}

/// Token樹節點 - 可以係一個標記或者一個子樹
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum TokenTreeNode {
    /// 單個標記
    Token(Token),
    /// 標記樹（分組）
    Tree(TokenTree),
}

/// 單個標記
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Token {
    /// 標記嘅文本
    pub text: String,
    /// 標記嘅類型
    pub kind: TokenKind,
    /// 位置信息
    pub span: Span,
}

/// 標記類型
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum TokenKind {
    /// 標識符
    Identifier,
    /// 字符串字面量
    StringLiteral,
    /// 數字字面量
    NumberLiteral,
    /// 布爾字面量
    BoolLiteral,
    /// 運算符
    Operator,
    /// 點號 (.)
    Dot,
    /// 冒號 (:)
    Colon,
    /// 逗號 (,)
    Comma,
    /// 分號 (;)
    Semicolon,
    /// 左方括號 ([)
    LeftBracket,
    /// 右方括號 (])
    RightBracket,
    /// 元變量（宏變量）
    MetaVariable,
    /// 重複運算符 (例如 * 或 +)
    RepetitionOperator,
    /// 分隔符
    Separator,
    /// 其他標記
    Other,
}

impl TokenTree {
    /// 創建一個新嘅Token樹
    pub fn new(open_symbol: char, close_symbol: char, span: Span) -> Self {
        Self {
            children: Vec::new(),
            open_symbol,
            close_symbol,
            span,
        }
    }

    /// 添加一個子節點
    pub fn add_child(&mut self, node: TokenTreeNode) {
        self.children.push(node);
    }
}

impl Token {
    /// 創建一個新嘅標記
    pub fn new(text: String, kind: TokenKind, span: Span) -> Self {
        Self { text, kind, span }
    }

    /// 判斷標記係唔係一個標識符
    pub fn is_identifier(&self) -> bool {
        matches!(self.kind, TokenKind::Identifier)
    }

    /// 判斷標記係唔係一個元變量（以@開頭）
    pub fn is_meta_variable(&self) -> bool {
        matches!(self.kind, TokenKind::MetaVariable)
    }
}
