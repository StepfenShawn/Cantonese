// 粤语编程语言宏处理模块 - 标记匹配器

use crate::ast::position::Span;
use crate::parser::token_tree::{Token, TokenKind, TokenStream, TokenTree, Delimiter};
use std::collections::HashMap;
use thiserror::Error;

/// 片段类型 - 描述宏中元变量可以匹配的片段类型
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum FragmentType {
    /// 标识符 (ident)
    Ident,
    /// 表达式 (expr)
    Expr,
    /// 语句 (stmt)
    Stmt,
    /// 块 (block)
    Block,
    /// 路径 (path)
    Path,
    /// 类型 (ty)
    Type,
    /// 模式 (pat)
    Pattern,
    /// 标记 (token)
    Token,
    /// 字符串 (str)
    Str,
    /// 字面量 (lit)
    Literal,
    /// 元混合(meta) - 用于属性
    Meta,
    /// 可见性 (vis)
    Visibility,
    /// 生命周期 (lifetime)
    Lifetime,
    /// 项 (item)
    Item,
}

impl FragmentType {
    /// 从字符串创建片段类型
    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "ident" => Some(FragmentType::Ident),
            "expr" => Some(FragmentType::Expr),
            "stmt" => Some(FragmentType::Stmt),
            "block" => Some(FragmentType::Block),
            "path" => Some(FragmentType::Path),
            "ty" => Some(FragmentType::Type),
            "pat" => Some(FragmentType::Pattern),
            "token" => Some(FragmentType::Token),
            "str" => Some(FragmentType::Str),
            "lit" => Some(FragmentType::Literal),
            "meta" => Some(FragmentType::Meta),
            "vis" => Some(FragmentType::Visibility),
            "lifetime" => Some(FragmentType::Lifetime),
            "item" => Some(FragmentType::Item),
            _ => None,
        }
    }
}

/// 匹配结果
#[derive(Debug, Clone)]
pub struct MatchResult {
    /// 绑定的元变量
    pub bindings: HashMap<String, Vec<TokenTree>>,
    /// 匹配的令牌数量
    pub matched_tokens: usize,
}

impl MatchResult {
    /// 创建新的匹配结果
    pub fn new() -> Self {
        Self {
            bindings: HashMap::new(),
            matched_tokens: 0,
        }
    }

    /// 添加绑定
    pub fn add_binding(&mut self, name: String, value: TokenTree) {
        self.bindings.entry(name).or_insert_with(Vec::new).push(value);
    }

    /// 添加多个值的绑定
    pub fn add_binding_multiple(&mut self, name: String, values: Vec<TokenTree>) {
        self.bindings.entry(name).or_insert_with(Vec::new).extend(values);
    }

    /// 获取绑定值
    pub fn get_binding(&self, name: &str) -> Option<&Vec<TokenTree>> {
        self.bindings.get(name)
    }

    /// 合并另一个匹配结果
    pub fn merge(&mut self, other: MatchResult) {
        self.matched_tokens += other.matched_tokens;
        for (name, values) in other.bindings {
            self.bindings.entry(name).or_insert_with(Vec::new).extend(values);
        }
    }
}

/// 元变量结构体 - 表示宏中的元变量
#[derive(Debug, Clone)]
pub struct MetaVariable {
    /// 元变量名称
    pub name: String,
    /// 片段类型
    pub fragment_type: FragmentType,
    /// 位置
    pub span: Span,
}

impl MetaVariable {
    /// 创建新的元变量
    pub fn new(name: String, fragment_type: FragmentType, span: Span) -> Self {
        Self {
            name,
            fragment_type,
            span,
        }
    }

    /// 从标记中提取元变量信息
    pub fn from_token(token: &Token) -> Option<Self> {
        if token.kind != TokenKind::MetaVariable {
            return None;
        }

        let text = &token.text;
        // 移除@前缀
        if !text.starts_with('@') {
            return None;
        }

        // 获取元变量名称 (如果有冒号，则排除冒号后的内容)
        let name_end = text.find(':').unwrap_or(text.len());
        let name = text[1..name_end].to_string();

        // 如果有片段规范，解析它
        let fragment_type = if let Some(colon_pos) = text.find(':') {
            let frag_spec = &text[colon_pos + 1..];
            FragmentType::from_str(frag_spec).unwrap_or(FragmentType::Expr)
        } else {
            // 默认为表达式
            FragmentType::Expr
        };

        Some(Self {
            name,
            fragment_type,
            span: token.span,
        })
    }
}

/// 标记匹配器 - 用于匹配宏模式和输入标记
#[derive(Debug)]
pub struct TokenMatcher;

impl TokenMatcher {
    /// 创建新的标记匹配器
    pub fn new() -> Self {
        Self
    }

    /// 匹配标记流与模式
    pub fn match_pattern(
        &self,
        pattern: &TokenStream,
        input: &TokenStream,
    ) -> Result<Option<MatchResult>, MatchError> {
        let mut result = MatchResult::new();
        let mut pattern_iter = pattern.tokens.iter().peekable();
        let mut input_iter = input.tokens.iter().peekable();

        while let Some(pattern_token) = pattern_iter.next() {
            match pattern_token {
                // 匹配元变量
                TokenTree::Token(token) if token.is_meta_variable() => {
                    if let Some(meta_var) = MetaVariable::from_token(token) {
                        // 获取下一个输入标记
                        if let Some(input_token) = input_iter.next() {
                            // 检查输入标记是否符合元变量的片段类型
                            if self.token_matches_fragment(input_token, &meta_var.fragment_type) {
                                // 添加绑定
                                result.add_binding(meta_var.name, input_token.clone());
                                result.matched_tokens += 1;
                            } else {
                                return Ok(None); // 不匹配
                            }
                        } else {
                            return Ok(None); // 输入标记不足
                        }
                    }
                }
                // 匹配普通标记
                TokenTree::Token(pattern_token) => {
                    if let Some(input_token) = input_iter.next() {
                        if let TokenTree::Token(input_token) = input_token {
                            // 比较标记文本
                            if pattern_token.text != input_token.text {
                                return Ok(None); // 不匹配
                            }
                            result.matched_tokens += 1;
                        } else {
                            return Ok(None); // 不匹配
                        }
                    } else {
                        return Ok(None); // 输入标记不足
                    }
                }
                // 匹配分组
                TokenTree::Group { delimiter, stream, .. } => {
                    if let Some(input_token) = input_iter.next() {
                        if let TokenTree::Group {
                            delimiter: input_delim,
                            stream: input_stream,
                            ..
                        } = input_token
                        {
                            // 检查分隔符是否匹配
                            if delimiter != input_delim {
                                return Ok(None); // 不匹配
                            }

                            // 递归匹配分组内容
                            match self.match_pattern(stream, input_stream) {
                                Ok(Some(nested_result)) => {
                                    // 合并嵌套结果
                                    result.matched_tokens += 1;
                                    result.merge(nested_result);
                                }
                                Ok(None) => return Ok(None), // 不匹配
                                Err(e) => return Err(e),     // 匹配错误
                            }
                        } else {
                            return Ok(None); // 不匹配
                        }
                    } else {
                        return Ok(None); // 输入标记不足
                    }
                }
            }
        }

        // 检查是否已经匹配完所有输入
        if input_iter.peek().is_some() {
            return Ok(None); // 输入标记过多
        }

        Ok(Some(result))
    }

    /// 检查标记是否匹配片段类型
    fn token_matches_fragment(&self, token: &TokenTree, fragment_type: &FragmentType) -> bool {
        match (token, fragment_type) {
            // 标识符片段
            (TokenTree::Token(token), FragmentType::Ident) => token.is_identifier(),
            
            // 字符串片段
            (TokenTree::Token(token), FragmentType::Str) => matches!(token.kind, TokenKind::StringLiteral),
            
            // 字面量片段
            (TokenTree::Token(token), FragmentType::Literal) => {
                matches!(
                    token.kind,
                    TokenKind::StringLiteral | TokenKind::NumberLiteral | TokenKind::BoolLiteral
                )
            },
            
            // 表达式片段 - 几乎所有东西都可以是表达式
            (_, FragmentType::Expr) => true,
            
            // 块片段 - 必须是分组且使用花括号
            (TokenTree::Group { delimiter, .. }, FragmentType::Block) => *delimiter == Delimiter::Brace,
            
            // 默认情况下，我们接受任何标记
            (_, _) => true,
        }
    }

    /// 从标记流中展开宏
    pub fn expand_macro(
        &self,
        template: &TokenStream,
        bindings: &HashMap<String, Vec<TokenTree>>,
    ) -> Result<TokenStream, MatchError> {
        let mut result = TokenStream::new();

        for token in &template.tokens {
            match token {
                // 展开元变量
                TokenTree::Token(token) if token.is_meta_variable() => {
                    if let Some(meta_var) = MetaVariable::from_token(token) {
                        if let Some(bound_values) = bindings.get(&meta_var.name) {
                            // 添加绑定值到结果
                            if !bound_values.is_empty() {
                                for value in bound_values {
                                    result.push(value.clone());
                                }
                            }
                        } else {
                            return Err(MatchError::UnboundMetaVariable(meta_var.name));
                        }
                    }
                }
                // 处理普通标记
                TokenTree::Token(_) => {
                    result.push(token.clone());
                }
                // 递归处理分组
                TokenTree::Group { delimiter, stream, span } => {
                    let expanded_stream = self.expand_macro(stream, bindings)?;
                    result.push(TokenTree::Group {
                        delimiter: *delimiter,
                        stream: Box::new(expanded_stream),
                        span: *span,
                    });
                }
            }
        }

        Ok(result)
    }
}

/// 宏匹配错误
#[derive(Debug, Error)]
pub enum MatchError {
    #[error("未绑定的元变量: {0}")]
    UnboundMetaVariable(String),

    #[error("无效的模式: {0}")]
    InvalidPattern(String),

    #[error("无法展开宏: {0}")]
    CannotExpand(String),
} 