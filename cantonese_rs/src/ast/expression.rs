// 粤语编程语言嘅表達式數據結構

use serde::{Deserialize, Serialize};
use std::fmt;

use super::position::Span;

/// 運算符
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum BinaryOperator {
    // 數學運算符
    Add,      // +
    Subtract, // -
    Multiply, // *
    Divide,   // /

    // 比較運算符
    Equal,            // ==
    NotEqual,         // !=
    LessThan,         // <
    LessThanEqual,    // <=
    GreaterThan,      // >
    GreaterThanEqual, // >=
    NotGreaterThan,   // 比唔上

    // 粤语特殊运算符
    Is,      // 係
    And,     // 同
    Concat,  // <->
    Mapping, // ==>
}

/// 一元運算符
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
pub enum UnaryOperator {
    Negative, // -
    Not,      // not/唔係
    Len,      // len/長度
}

impl fmt::Display for BinaryOperator {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        use BinaryOperator::*;
        match self {
            Add => write!(f, "+"),
            Subtract => write!(f, "-"),
            Multiply => write!(f, "*"),
            Divide => write!(f, "/"),
            Equal => write!(f, "=="),
            NotEqual => write!(f, "!="),
            LessThan => write!(f, "<"),
            LessThanEqual => write!(f, "<="),
            GreaterThan => write!(f, ">"),
            GreaterThanEqual => write!(f, ">="),
            NotGreaterThan => write!(f, "比唔上"),
            Is => write!(f, "係"),
            And => write!(f, "同"),
            Concat => write!(f, "<->"),
            Mapping => write!(f, "==>"),
        }
    }
}

impl fmt::Display for UnaryOperator {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        use UnaryOperator::*;
        match self {
            Negative => write!(f, "-"),
            Not => write!(f, "唔係"),
            Len => write!(f, "長度"),
        }
    }
}

impl BinaryOperator {
    // 從字符串解析運算符
    pub fn from_str(s: &str) -> Option<Self> {
        use BinaryOperator::*;
        match s {
            "+" => Some(Add),
            "-" => Some(Subtract),
            "*" => Some(Multiply),
            "/" => Some(Divide),
            "==" => Some(Equal),
            "!=" => Some(NotEqual),
            "<" => Some(LessThan),
            "<=" => Some(LessThanEqual),
            ">" => Some(GreaterThan),
            ">=" => Some(GreaterThanEqual),
            "比唔上" => Some(NotGreaterThan),
            "係" => Some(Is),
            "同" => Some(And),
            "<->" => Some(Concat),
            "==>" => Some(Mapping),
            _ => None,
        }
    }
}

impl UnaryOperator {
    // 從字符串解析運算符
    pub fn from_str(s: &str) -> Option<Self> {
        use UnaryOperator::*;
        match s {
            "-" => Some(Negative),
            "唔係" | "not" => Some(Not),
            "長度" | "len" => Some(Len),
            _ => None,
        }
    }
}

/// 表達式
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Expression {
    // 字面量
    NullLiteral(Span),
    NumberLiteral(f64, Span),
    StringLiteral(String, Span),
    BoolLiteral(bool, Span),
    VarArg(Span), // <*>

    // 標識符
    Identifier(String, Span),

    // 容器類型
    ListExpression {
        elements: Vec<Expression>,
        span: Span,
    },

    MapExpression {
        elements: Vec<Expression>,
        span: Span,
    },

    // 一元表達式
    UnaryExpression {
        operator: UnaryOperator,
        operand: Box<Expression>,
        span: Span,
    },

    // 二元表達式
    BinaryExpression {
        left: Box<Expression>,
        operator: BinaryOperator,
        right: Box<Expression>,
        span: Span,
    },

    // 賦值表達式
    AssignExpression {
        left: Box<Expression>,
        right: Box<Expression>,
        span: Span,
    },

    // 類型註解表達式
    AnnotationExpression {
        expression: Box<Expression>,
        type_id: Box<Expression>,
        span: Span,
    },

    // 括號表達式
    ParenthesizedExpression {
        expression: Box<Expression>,
        span: Span,
    },

    // 物件存取表達式
    ObjectAccessExpression {
        object: Box<Expression>,
        property: Box<Expression>,
        span: Span,
    },

    // 列表存取表達式
    ListAccessExpression {
        list: Box<Expression>,
        index: Box<Expression>,
        span: Span,
    },

    // 屬性存取表達式
    AttributeAccessExpression {
        attribute: Box<Expression>,
        span: Span,
    },

    // 函數調用
    CallExpression {
        callee: Box<Expression>,
        arguments: Vec<Expression>,
        span: Span,
    },

    // Lambda表達式
    LambdaExpression {
        parameters: Vec<Expression>,
        body: Vec<Expression>,
        span: Span,
    },

    // 條件表達式
    ConditionalExpression {
        condition: Box<Expression>,
        then_branch: Box<Expression>,
        else_branch: Box<Expression>,
        span: Span,
    },

    // 名稱列表
    Names {
        names: Vec<Expression>,
        span: Span,
    },

    // 宏相關表達式
    MacroMeta {
        name: String,
        span: Span,
    },

    MacroMetaId {
        id: Box<Expression>,
        frag_spec: Box<Expression>,
        span: Span,
    },

    MacroMetaRepInPat {
        token_trees: Vec<Expression>,
        rep_sep: String,
        rep_op: String,
        span: Span,
    },

    MacroMetaRepInBlock {
        token_trees: Vec<Expression>,
        rep_sep: Box<Expression>,
        rep_op: Box<Expression>,
        span: Span,
    },

    // TokenTree
    TokenTree {
        children: Vec<Expression>,
        open_symbol: char,
        close_symbol: char,
        span: Span,
    },
}

impl Expression {
    // 獲取表達式嘅位置
    pub fn span(&self) -> Span {
        match self {
            Expression::NullLiteral(span) => *span,
            Expression::NumberLiteral(_, span) => *span,
            Expression::StringLiteral(_, span) => *span,
            Expression::BoolLiteral(_, span) => *span,
            Expression::VarArg(span) => *span,
            Expression::Identifier(_, span) => *span,
            Expression::ListExpression { span, .. } => *span,
            Expression::MapExpression { span, .. } => *span,
            Expression::UnaryExpression { span, .. } => *span,
            Expression::BinaryExpression { span, .. } => *span,
            Expression::AssignExpression { span, .. } => *span,
            Expression::AnnotationExpression { span, .. } => *span,
            Expression::ParenthesizedExpression { span, .. } => *span,
            Expression::ObjectAccessExpression { span, .. } => *span,
            Expression::ListAccessExpression { span, .. } => *span,
            Expression::AttributeAccessExpression { span, .. } => *span,
            Expression::CallExpression { span, .. } => *span,
            Expression::LambdaExpression { span, .. } => *span,
            Expression::ConditionalExpression { span, .. } => *span,
            Expression::Names { span, .. } => *span,
            Expression::MacroMeta { span, .. } => *span,
            Expression::MacroMetaId { span, .. } => *span,
            Expression::MacroMetaRepInPat { span, .. } => *span,
            Expression::MacroMetaRepInBlock { span, .. } => *span,
            Expression::TokenTree { span, .. } => *span,
        }
    }
}
