// 位置信息數據結構 - 用嚟跟蹤代碼嘅位置，幫助錯誤報告

use std::fmt;
use serde::{Serialize, Deserialize};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Default, Serialize, Deserialize)]
pub struct Position {
    pub line: usize,   // 行號，從1開始
    pub column: usize, // 列號，從1開始
    pub offset: usize, // 字符偏移量，從0開始
}

impl Position {
    pub fn new(line: usize, column: usize, offset: usize) -> Self {
        Self { line, column, offset }
    }
    
    // 從字符串創建一個開始位置
    pub fn start() -> Self {
        Self { line: 1, column: 1, offset: 0 }
    }
}

impl fmt::Display for Position {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}:{}", self.line, self.column)
    }
}

// 源代碼嘅範圍
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct Span {
    pub start: Position, // 開始位置
    pub end: Position,   // 結束位置
}

impl Span {
    pub fn new(start: Position, end: Position) -> Self {
        Self { start, end }
    }
    
    // 從 pest 嘅 Span 創建
    pub fn from_pest(span: pest::Span<'_>, source: &str) -> Self {
        let start_offset = span.start();
        let end_offset = span.end();
        
        // 計算行列號
        let mut start_line = 1;
        let mut start_column = 1;
        let mut end_line = 1;
        let mut end_column = 1;
        
        for (idx, c) in source.char_indices() {
            if idx < start_offset {
                if c == '\n' {
                    start_line += 1;
                    start_column = 1;
                } else {
                    start_column += 1;
                }
            }
            
            if idx < end_offset {
                if c == '\n' {
                    end_line += 1;
                    end_column = 1;
                } else {
                    end_column += 1;
                }
            } else if idx >= end_offset {
                break;
            }
        }
        
        Self {
            start: Position::new(start_line, start_column, start_offset),
            end: Position::new(end_line, end_column, end_offset),
        }
    }
}

impl fmt::Display for Span {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}-{}", self.start, self.end)
    }
} 