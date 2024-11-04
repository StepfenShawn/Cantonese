// 粤语编程语言宏处理模块 - 正则表达式

use crate::ast::expression::Expression;
use std::fmt;

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
    CLOSURE,
    /// 零或一次 (?)
    OPRIONAL,
    /// 一或多次 (+)
    PLUS_CLOSE,
}

impl RepOp {
    /// 从字符串创建重复操作符
    pub fn from_str(s: &str) -> Option<Self> {
        match s {
            "*" => Some(RepOp::CLOSURE),
            "?" => Some(RepOp::OPRIONAL),
            "+" => Some(RepOp::PLUS_CLOSE),
            _ => None,
        }
    }

    /// 获取操作符的字符串值
    pub fn value(&self) -> &'static str {
        match self {
            RepOp::CLOSURE => "*",
            RepOp::OPRIONAL => "?",
            RepOp::PLUS_CLOSE => "+",
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
    Var { name: String, spec: FragSpec },
    /// 连接表达式（匹配两个连续的表达式）
    Concat { left: Box<Regex>, right: Box<Regex> },
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

    let mut result = Regex::empty();
    let mut expressions = expressions.to_vec();

    if !expressions.is_empty() {
        let x = expressions.remove(0);
        let mut node = Regex::empty();

        match x {
            Expression::Identifier(name, _) => {
                node = Regex::atom(name);
            }
            Expression::StringLiteral(text, _) => {
                node = Regex::atom(text);
            }
            Expression::MacroMetaId { id, frag_spec, .. } => {
                if let Expression::Identifier(name, _) = *id {
                    if let Expression::Identifier(spec, _) = *frag_spec {
                        node = Regex::var(name, FragSpec::from_str(&spec));
                    }
                }
            }
            Expression::MacroMetaRepInPat {
                token_trees,
                rep_sep,
                rep_op,
                ..
            } => {
                if let Some(op) = RepOp::from_str(&rep_op) {
                    match op {
                        RepOp::CLOSURE => {
                            let inner = build_regex(&token_trees);
                            let inner_with_sep = if rep_sep.is_empty() {
                                inner
                            } else {
                                Regex::concat(inner, Regex::atom(rep_sep))
                            };
                            node = Regex::star(inner_with_sep);
                        }
                        RepOp::OPRIONAL => {
                            let inner = build_regex(&token_trees);
                            let inner_with_sep = if rep_sep.is_empty() {
                                inner
                            } else {
                                Regex::concat(
                                    Regex::optional(inner),
                                    Regex::optional(Regex::atom(rep_sep)),
                                )
                            };
                            node = inner_with_sep;
                        }
                        RepOp::PLUS_CLOSE => {
                            let inner = build_regex(&token_trees);

                            // 创建包含分隔符的表达式
                            let inner_with_sep = if rep_sep.is_empty() {
                                inner.clone()
                            } else {
                                Regex::concat(inner.clone(), Regex::atom(rep_sep.clone()))
                            };

                            // + 等价于 一次 + 零次或多次
                            node = Regex::concat(inner.clone(), Regex::star(inner_with_sep));
                        }
                    }
                }
            }
            _ => {
                // 处理其他类型表达式
            }
        }

        if !expressions.is_empty() {
            result = Regex::concat(node, build_regex(&expressions));
        } else {
            result = node;
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
