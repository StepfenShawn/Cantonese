// 粤语编程语言嘅语句數據結構

use serde::{Deserialize, Serialize};

use crate::parser::token_tree::TokenTree;

use super::expression::Expression;
use super::position::Span;

/// 語句
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Statement {
    // 賦值語句
    AssignmentStatement {
        var_list: Vec<Expression>,
        exp_list: Vec<Expression>,
        span: Span,
    },

    // 塊賦值語句
    AssignmentBlockStatement {
        var_list: Vec<Vec<Expression>>,
        exp_list: Vec<Vec<Expression>>,
        span: Span,
    },

    // 打印語句
    PrintStatement {
        arguments: Vec<Expression>,
        span: Span,
    },

    // 空語句
    PassStatement {
        span: Span,
    },

    // 條件語句
    IfStatement {
        if_exp: Expression,
        if_block: Block,
        elif_exps: Vec<Expression>,
        elif_blocks: Vec<Block>,
        else_block: Option<Block>,
        span: Span,
    },

    // For 循環語句
    ForStatement {
        var: Expression,
        from_exp: Expression,
        to_exp: Expression,
        body: Block,
        span: Span,
    },

    // ForEach 循環語句
    ForEachStatement {
        id_list: Vec<Expression>,
        exp_list: Vec<Expression>,
        body: Block,
        span: Span,
    },

    // While 循環語句
    WhileStatement {
        condition: Expression,
        body: Block,
        span: Span,
    },

    // 列表初始化
    ListInitStatement {
        span: Span,
    },

    // 函數聲明
    FunctionDeclaration {
        name: Expression,
        parameters: Vec<Expression>,
        body: Block,
        span: Span,
    },

    // 函數類型定義
    FunctionTypeDeclaration {
        name: Expression,
        arg_types: Vec<Expression>,
        return_types: Vec<Expression>,
        span: Span,
    },

    // 方法定義
    MethodDeclaration {
        name: Expression,
        parameters: Vec<Expression>,
        body: Block,
        span: Span,
    },

    // 屬性定義
    AttributeDeclaration {
        attributes: Vec<Expression>,
        span: Span,
    },

    // 類定義
    ClassDeclaration {
        name: Expression,
        extends: Vec<Expression>,
        body: Block,
        span: Span,
    },

    // 導入語句
    ImportStatement {
        path: ImportPath,
        span: Span,
    },

    // 異常拋出語句
    ThrowStatement {
        exception: Expression,
        span: Span,
    },

    // 異常捕獲語句
    TryCatchStatement {
        try_block: Block,
        except_exps: Vec<Expression>,
        catch_blocks: Vec<Block>,
        finally_block: Option<Block>,
        span: Span,
    },

    // 全局變量聲明
    GlobalStatement {
        identifiers: Vec<Expression>,
        span: Span,
    },

    // 跳出循環
    BreakStatement {
        span: Span,
    },

    // 繼續循環
    ContinueStatement {
        span: Span,
    },

    // 類型語句
    TypeStatement {
        expressions: Vec<Expression>,
        span: Span,
    },

    // 斷言語句
    AssertStatement {
        expression: Expression,
        span: Span,
    },

    // 返回語句
    ReturnStatement {
        values: Vec<Expression>,
        span: Span,
    },

    // 刪除語句
    DeleteStatement {
        targets: Vec<Expression>,
        span: Span,
    },

    // 命令語句
    CommandStatement {
        arguments: Vec<Expression>,
        span: Span,
    },

    // 方法調用語句
    MethodCallStatement {
        object: Expression,
        method: Expression,
        arguments: Vec<Expression>,
        span: Span,
    },

    // 函數調用語句
    FunctionCallStatement {
        function: Expression,
        arguments: Vec<Expression>,
        span: Span,
    },

    // 表達式語句
    ExpressionStatement {
        expression: Expression,
        span: Span,
    },

    // 模式匹配語句
    MatchStatement {
        match_id: Expression,
        match_val: Expression,
        match_block_exp: Expression,
        default_block: Option<Block>,
        span: Span,
    },

    // 宏定義語句
    MacroDefStatement {
        name: String,
        pattern: Vec<Expression>,
        body: Vec<Expression>,
        span: Span,
    },

    // "咁啦"語句 - 默認行為語句
    ElseStatement {
        body: Block,
        span: Span,
    },

    // 嵌入代碼語句
    EmbeddedCodeStatement {
        code: String,
        span: Span,
    },

    // 退出語句
    ExitStatement {
        span: Span,
    },
}

impl Statement {
    // 獲取語句嘅位置
    pub fn span(&self) -> Span {
        match self {
            Statement::AssignmentStatement { span, .. } => *span,
            Statement::AssignmentBlockStatement { span, .. } => *span,
            Statement::PrintStatement { span, .. } => *span,
            Statement::PassStatement { span } => *span,
            Statement::IfStatement { span, .. } => *span,
            Statement::ForStatement { span, .. } => *span,
            Statement::ForEachStatement { span, .. } => *span,
            Statement::WhileStatement { span, .. } => *span,
            Statement::ListInitStatement { span } => *span,
            Statement::FunctionDeclaration { span, .. } => *span,
            Statement::FunctionTypeDeclaration { span, .. } => *span,
            Statement::MethodDeclaration { span, .. } => *span,
            Statement::AttributeDeclaration { span, .. } => *span,
            Statement::ClassDeclaration { span, .. } => *span,
            Statement::ImportStatement { span, .. } => *span,
            Statement::ThrowStatement { span, .. } => *span,
            Statement::TryCatchStatement { span, .. } => *span,
            Statement::GlobalStatement { span, .. } => *span,
            Statement::BreakStatement { span } => *span,
            Statement::ContinueStatement { span } => *span,
            Statement::TypeStatement { span, .. } => *span,
            Statement::AssertStatement { span, .. } => *span,
            Statement::ReturnStatement { span, .. } => *span,
            Statement::DeleteStatement { span, .. } => *span,
            Statement::CommandStatement { span, .. } => *span,
            Statement::MethodCallStatement { span, .. } => *span,
            Statement::FunctionCallStatement { span, .. } => *span,
            Statement::ExpressionStatement { span, .. } => *span,
            Statement::MatchStatement { span, .. } => *span,
            Statement::MacroDefStatement { span, .. } => *span,
            Statement::ElseStatement { span, .. } => *span,
            Statement::EmbeddedCodeStatement { span, .. } => *span,
            Statement::ExitStatement { span } => *span,
        }
    }
}

/// 代碼塊
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Block {
    pub statements: Vec<Statement>,
    pub span: Span,
}

/// 導入路徑
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ImportPath {
    // 單個模塊導入: std::time::瞓
    ModuleImport {
        path: Vec<String>,
    },

    // 導入所有: std::time::*
    AllImport {
        path: Vec<String>,
    },

    // 集合導入: std::{time::*, date}
    GroupImport {
        base: Vec<String>,
        imports: Vec<ImportPath>,
    },
}

/// 程序
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Program {
    pub statements: Vec<Statement>,
    pub span: Span,
}
