// 粤语编程语言宏处理模块 - 正则表达式

use std::fmt;
use crate::ast::expression::Expression;

/// 片段规范 - 指定元变量可以匹配的内容类型
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum FragSpec {
    /// 标识符
    Ident,
    /// 表达式
    Expr,
    /// 语句
    Stmt,
    /// 字符串字面量
    Str,
    /// 字面量（数字、字符串等）
    Literal,
    /// 其他/未知类型
    Other(String),
}

impl FragSpec {
    /// 从字符串创建片段规范
    pub fn from_str(s: &str) -> Self {
        match s {
            "ident" => FragSpec::Ident,
            "expr" => FragSpec::Expr,
            "stmt" => FragSpec::Stmt,
            "str" => FragSpec::Str,
            "literal" => FragSpec::Literal,
            _ => FragSpec::Other(s.to_string()),
        }
    }
}

/// 重复操作符
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum RepOp {
    /// 零或多次 (*)
    Star,
    /// 零或一次 (?)
    Optional,
    /// 一或多次 (+)
    Plus,
}

impl RepOp {
    /// 从字符串创建重复操作符
    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "*" => Some(RepOp::Star),
            "?" => Some(RepOp::Optional),
            "+" => Some(RepOp::Plus),
            _ => None,
        }
    }
}

/// 正则表达式 - 用于宏模式匹配
#[derive(Debug, Clone)]
pub enum Regex {
    /// 空表达式
    Empty,
    /// 原子表达式（匹配单个标记）
    Atom(String),
    /// 变量表达式（匹配元变量）
    Var {
        name: String,
        spec: FragSpec,
    },
    /// 连接表达式（匹配两个连续的表达式）
    Concat {
        left: Box<Regex>,
        right: Box<Regex>,
    },
    /// 星号表达式（匹配零或多次）
    Star(Box<Regex>),
    /// 可选表达式（匹配零或一次）
    Optional(Box<Regex>),
}

impl Regex {
    /// 创建空表达式
    pub fn empty() -> Self {
        Regex::Empty
    }

    /// 创建原子表达式
    pub fn atom(s: impl Into<String>) -> Self {
        Regex::Atom(s.into())
    }

    /// 创建变量表达式
    pub fn var(name: impl Into<String>, spec: FragSpec) -> Self {
        Regex::Var {
            name: name.into(),
            spec,
        }
    }

    /// 创建连接表达式
    pub fn concat(left: Regex, right: Regex) -> Self {
        Regex::Concat {
            left: Box::new(left),
            right: Box::new(right),
        }
    }

    /// 创建星号表达式
    pub fn star(inner: Regex) -> Self {
        Regex::Star(Box::new(inner))
    }

    /// 创建可选表达式
    pub fn optional(inner: Regex) -> Self {
        Regex::Optional(Box::new(inner))
    }
}

/// 从表达式列表构建正则表达式
pub fn build_regex(expressions: &[Expression]) -> Regex {
    if expressions.is_empty() {
        return Regex::empty();
    }

    // 这里需要根据你的Expression结构实现转换
    // 这只是一个简单的示例框架
    let mut result = Regex::empty();
    
    for expr in expressions {
        // 根据表达式类型构建不同的正则表达式部分
        let part = match expr {
            // 处理不同的表达式类型...
            _ => Regex::atom("未实现"), // 临时占位，实际需要完善
        };
        
        // 将部分连接到结果
        if matches!(result, Regex::Empty) {
            result = part;
        } else {
            result = Regex::concat(result, part);
        }
    }
    
    result
}

impl fmt::Display for Regex {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Regex::Empty => write!(f, "Empty"),
            Regex::Atom(s) => write!(f, "Atom({})", s),
            Regex::Var { name, spec: _ } => write!(f, "Var({:?})", name),
            Regex::Concat { left, right } => write!(f, "Concat({}, {})", left, right),
            Regex::Star(inner) => write!(f, "Star({})", inner),
            Regex::Optional(inner) => write!(f, "Optional({})", inner),
        }
    }
} 