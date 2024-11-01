// 粤语编程语言嘅Token Tree模块 - 用於宏处理

use std::fmt;
use std::iter::FromIterator;
use std::ops::Range;

use crate::ast::position::Span;
use serde::{Deserialize, Serialize};

/// TokenStream - 代表一個標記流（一系列有序嘅標記）
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct TokenStream {
    /// 標記流中嘅標記
    pub tokens: Vec<TokenTree>,
    /// 位置信息
    pub span: Option<Span>,
}

/// TokenTree - 代表解析出嚟嘅標記樹
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum TokenTree {
    /// 單個標記
    Token(Token),
    /// 分組 - 用括號、大括號等包起來嘅標記流
    Group {
        /// 分隔符類型
        delimiter: Delimiter,
        /// 分組內嘅標記流
        stream: Box<TokenStream>,
        /// 位置信息
        span: Span,
    },
}

/// 分隔符類型
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum Delimiter {
    /// 圓括號 ()
    Parenthesis,
    /// 大括號 {}
    Brace,
    /// 方括號 []
    Bracket,
    /// 無分隔符
    None,
}

impl Delimiter {
    /// 獲取開始分隔符
    pub fn open(&self) -> Option<char> {
        match self {
            Delimiter::Parenthesis => Some('('),
            Delimiter::Brace => Some('{'),
            Delimiter::Bracket => Some('['),
            Delimiter::None => None,
        }
    }

    /// 獲取結束分隔符
    pub fn close(&self) -> Option<char> {
        match self {
            Delimiter::Parenthesis => Some(')'),
            Delimiter::Brace => Some('}'),
            Delimiter::Bracket => Some(']'),
            Delimiter::None => None,
        }
    }
    
    /// 從字符創建分隔符
    pub fn from_char(c: char) -> Option<Self> {
        match c {
            '(' => Some(Delimiter::Parenthesis),
            '{' => Some(Delimiter::Brace),
            '[' => Some(Delimiter::Bracket),
            _ => None,
        }
    }
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
    /// 元變量（宏變量）- 以@開頭
    MetaVariable,
    /// 重複運算符 (例如 * 或 +)
    RepetitionOperator,
    /// 分隔符
    Separator,
    /// 其他標記
    Other,
}

impl TokenStream {
    /// 創建一個新嘅空標記流
    pub fn new() -> Self {
        Self {
            tokens: Vec::new(),
            span: None,
        }
    }
    
    /// 從迭代器創建標記流
    pub fn from_iter<I>(iter: I) -> Self
    where
        I: IntoIterator<Item = TokenTree>,
    {
        let tokens: Vec<TokenTree> = iter.into_iter().collect();
        Self {
            tokens,
            span: None,
        }
    }
    
    /// 將標記流轉換為字符串
    pub fn to_string(&self) -> String {
        let mut result = String::new();
        for token in &self.tokens {
            match token {
                TokenTree::Token(token) => {
                    result.push_str(&token.text);
                    result.push(' ');
                }
                TokenTree::Group { delimiter, stream, .. } => {
                    if let Some(open) = delimiter.open() {
                        result.push(open);
                    }
                    result.push_str(&stream.to_string());
                    if let Some(close) = delimiter.close() {
                        result.push(close);
                    }
                    result.push(' ');
                }
            }
        }
        result
    }
    
    /// 添加一個標記到流尾部
    pub fn push(&mut self, token: TokenTree) {
        self.tokens.push(token);
    }
    
    /// 获取标记流中的标记数量
    pub fn len(&self) -> usize {
        self.tokens.len()
    }
    
    /// 检查标记流是否为空
    pub fn is_empty(&self) -> bool {
        self.tokens.is_empty()
    }
    
    /// 获取标记流的迭代器
    pub fn iter(&self) -> impl Iterator<Item = &TokenTree> {
        self.tokens.iter()
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
    
    /// 获取标记文本
    pub fn text(&self) -> &str {
        &self.text
    }
}

impl fmt::Display for TokenTree {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TokenTree::Token(token) => write!(f, "{}", token.text),
            TokenTree::Group { delimiter, stream, .. } => {
                if let Some(open) = delimiter.open() {
                    write!(f, "{}", open)?;
                }
                write!(f, "{}", stream)?;
                if let Some(close) = delimiter.close() {
                    write!(f, "{}", close)?;
                }
                Ok(())
            }
        }
    }
}

impl fmt::Display for TokenStream {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for token in &self.tokens {
            write!(f, "{} ", token)?;
        }
        Ok(())
    }
}

impl FromIterator<TokenTree> for TokenStream {
    fn from_iter<I: IntoIterator<Item = TokenTree>>(iter: I) -> Self {
        Self {
            tokens: iter.into_iter().collect(),
            span: None,
        }
    }
}

// 实现IntoIterator
impl IntoIterator for TokenStream {
    type Item = TokenTree;
    type IntoIter = std::vec::IntoIter<TokenTree>;

    fn into_iter(self) -> Self::IntoIter {
        self.tokens.into_iter()
    }
}

// 添加一些辅助函数来创建常见的TokenTree
impl TokenTree {
    /// 创建标识符标记
    pub fn ident(name: &str, span: Span) -> Self {
        TokenTree::Token(Token::new(
            name.to_string(),
            TokenKind::Identifier,
            span,
        ))
    }
    
    /// 创建字符串字面量标记
    pub fn string(value: &str, span: Span) -> Self {
        TokenTree::Token(Token::new(
            format!("\"{}\"", value),
            TokenKind::StringLiteral,
            span,
        ))
    }
    
    /// 创建数字字面量标记
    pub fn number(value: &str, span: Span) -> Self {
        TokenTree::Token(Token::new(
            value.to_string(),
            TokenKind::NumberLiteral,
            span,
        ))
    }
    
    /// 创建元变量标记
    pub fn meta_var(name: &str, span: Span) -> Self {
        TokenTree::Token(Token::new(
            format!("@{}", name),
            TokenKind::MetaVariable,
            span,
        ))
    }
    
    /// 创建分组
    pub fn group(delimiter: Delimiter, stream: TokenStream, span: Span) -> Self {
        TokenTree::Group {
            delimiter,
            stream: Box::new(stream),
            span,
        }
    }
}
