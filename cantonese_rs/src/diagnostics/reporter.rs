// 粤语编程語言嘅錯誤報告器

use crate::ast::Span;
use crate::parser::ast_builder::ParseError;
use std::io;

/// 診斷錯誤報告器
pub struct DiagnosticReporter {
    source_code: String,
    file_name: String,
}

impl DiagnosticReporter {
    /// 創建一個新嘅診斷報告器
    pub fn new(source_code: String, file_name: String) -> Self {
        Self {
            source_code,
            file_name,
        }
    }

    /// 報告解析錯誤
    pub fn report_parse_error(&self, error: ParseError) -> Result<(), io::Error> {
        match &error {
            ParseError::PestError(err) => {
                // 將 pest 的錯誤轉換為 簡單錯誤消息
                eprintln!("語法解析錯誤: {}", err);
            }
            ParseError::InvalidOperator(op) => {
                eprintln!("無效嘅操作符: {}", op);
            }
            ParseError::InvalidNode(rule) => {
                eprintln!("無效嘅語法節點: {:?}", rule);
            }
            ParseError::InvalidLiteral(lit) => {
                eprintln!("無效嘅字面量值: {}", lit);
            }
            ParseError::Custom(msg) => {
                eprintln!("自定義錯誤: {}", msg);
            }
        }

        Ok(())
    }

    /// 報告語法錯誤，帶有位置信息
    pub fn report_syntax_error(&self, message: &str, span: Span) -> Result<(), io::Error> {
        let line_start = span.start.line;
        let col_start = span.start.column;
        let line_end = span.end.line;
        let col_end = span.end.column;

        eprintln!(
            "語法錯誤 [{}:{}-{}:{}]: {}",
            line_start, col_start, line_end, col_end, message
        );

        Ok(())
    }

    /// 報告警告信息
    pub fn report_warning(&self, message: &str, span: Span) -> Result<(), io::Error> {
        let line_start = span.start.line;
        let col_start = span.start.column;
        let line_end = span.end.line;
        let col_end = span.end.column;

        eprintln!(
            "警告 [{}:{}-{}:{}]: {}",
            line_start, col_start, line_end, col_end, message
        );

        Ok(())
    }
}
