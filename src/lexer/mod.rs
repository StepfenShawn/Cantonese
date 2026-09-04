pub mod keywords;
pub mod span;
pub mod token;

use keywords::*;
use thiserror::Error;
use token::{Pos, Token, TokenType};
use unicode_xid::UnicodeXID;
use zhconv::{Variant, zhconv};

// =============================================================================
// Lexer Error
// =============================================================================
#[derive(Error, Debug)]
pub enum LexError {
    #[error("[詞法錯誤] {msg}\n位置: {}:{}", pos.line, pos.offset)]
    LexerErr { msg: String, pos: Pos, file: String },
    #[error("IO讀檔失敗 {0}")]
    Io(#[from] std::io::Error),
    #[error("未閉合字符串字面量")]
    UnfinishedString(Pos),
}

pub struct Lexer<'a> {
    file_path: String,
    source: &'a str,
    iter: std::str::CharIndices<'a>,
    peeked: Option<(usize, char)>,

    line: usize,
    offset: usize,
    start_byte: usize,
}

impl<'a> Lexer<'a> {
    /// 构造lexer
    pub fn new(file: String, src: &'a str) -> Self {
        Self {
            file_path: file,
            source: src,
            iter: src.char_indices(),
            peeked: None,
            line: 1,
            offset: 0,
            start_byte: 0,
        }
    }

    /// 获取当前位置
    pub fn cur_pos(&self) -> Pos {
        Pos::simple(self.line, self.offset)
    }

    /// 构造 token 的结束位置（当前 lexer 位置作为 end）。
    fn token_end_pos(&self, start_pos: Pos) -> Pos {
        let end = self.cur_pos();
        start_pos.with_end(end.line, end.offset)
    }

    /// 使用起始位置和当前 lexer 位置构造一个带 end 的 Token。
    fn mk_token(&self, start_pos: Pos, typ: TokenType, value: impl Into<String>) -> Token {
        Token::new(self.token_end_pos(start_pos), typ, value.into())
    }

    /// 向前预看1个字符，不消耗
    fn peek(&mut self) -> Option<char> {
        if self.peeked.is_none() {
            self.peeked = self.iter.next();
        }
        self.peeked.map(|(_, c)| c)
    }

    /// 消耗下一个字符
    fn next_char(&mut self) -> Option<char> {
        let (byte, c) = match self.peeked.take() {
            Some(v) => v,
            None => self.iter.next()?,
        };
        // 换行处理
        if c == '\n' {
            self.line += 1;
            self.offset = 0;
        } else {
            self.offset += 1;
        }
        self.start_byte = byte;
        Some(c)
    }

    /// 检测接下来字符串是否匹配前缀（基于当前 peek 位置）
    fn starts_with(&mut self, s: &str) -> bool {
        // 确保 peeked 已填充，从而拿到当前字符的字节位置
        if self.peeked.is_none() {
            let _ = self.peek();
        }
        let start_byte = self
            .peeked
            .map(|(byte, _)| byte)
            .unwrap_or(self.source.len());
        let mut chars = self.source[start_byte..].chars();
        for target in s.chars() {
            match chars.next() {
                Some(c) if c == target => continue,
                _ => return false,
            }
        }
        true
    }

    /// 一次性吃掉N个字符（运算符匹配后使用）
    fn consume_many(&mut self, n: usize) {
        for _ in 0..n {
            let _ = self.next_char();
        }
    }

    /// 判断空白字符
    fn is_whitespace(c: char) -> bool {
        matches!(c, '\t' | '\n' | '\r' | ' ')
    }

    /// 判断是否中文字符
    fn is_chinese(c: char) -> bool {
        ('\u{4e00}'..='\u{9fff}').contains(&c)
    }

    /// 跳过空格、注释
    pub fn skip_whitespace_and_comment(&mut self) -> Result<(), LexError> {
        loop {
            match self.peek() {
                // 块注释 /* */
                Some('/') if self.starts_with("/*") => {
                    self.consume_many(2);
                    self.scan_block_comment()?;
                }
                // #XD 是内嵌python标记，不能当作单行注释
                Some('#') if self.starts_with("#XD") => break,
                // 单行注释 #xxxx
                Some('#') => {
                    self.consume_many(1);
                    while let Some(c) = self.peek() {
                        if c == '\n' {
                            break;
                        }
                        let _ = self.next_char();
                    }
                }
                // 特殊符号
                Some('：') | Some('？') | Some('「') | Some('」') => {
                    self.next_char();
                }
                Some('?') if self.starts_with("??") => {
                    self.consume_many(2);
                }
                Some(c) if Self::is_whitespace(c) => {
                    self.next_char();
                }
                _ => break,
            }
        }
        Ok(())
    }

    /// 扫描块注释 /* ... */
    fn scan_block_comment(&mut self) -> Result<(), LexError> {
        loop {
            match self.peek() {
                None => {
                    return Err(LexError::LexerErr {
                        msg: "未闭合块注释 /* */".into(),
                        pos: self.cur_pos(),
                        file: self.file_path.clone(),
                    });
                }
                Some('*') if self.starts_with("*/") => {
                    self.consume_many(2);
                    return Ok(());
                }
                _ => {
                    self.next_char();
                }
            }
        }
    }

    /// 扫描字符串 'xxx' / "xxx"
    fn scan_string(&mut self, quote: char) -> Result<String, LexError> {
        let start_pos = self.cur_pos();
        let mut buf = String::new();
        self.next_char(); // 吃掉开头引号

        loop {
            match self.peek() {
                None | Some('\n') => return Err(LexError::UnfinishedString(start_pos)),
                Some(c) if c == quote => {
                    self.next_char();
                    buf.insert(0, quote);
                    buf.push(quote);
                    return Ok(buf);
                }
                Some('\\') => {
                    // 简易转义，和原版正则保持兼容
                    buf.push(self.next_char().unwrap());
                    if let Some(esc) = self.peek() {
                        buf.push(esc);
                        self.next_char();
                    }
                }
                Some(c) => {
                    buf.push(c);
                    self.next_char();
                }
            }
        }
    }

    /// 扫描标识符（中文、字母、下划线）
    fn scan_ident(&mut self) -> String {
        let mut buf = String::new();
        while let Some(c) = self.peek() {
            if Self::is_chinese(c)
                || c == '_'
                || c.is_ascii_alphanumeric()
                || UnicodeXID::is_xid_continue(c)
            {
                buf.push(c);
                self.next_char();
            } else {
                break;
            }
        }
        let converted = zhconv(&buf, Variant::ZhHK);
        converted.replace("僕", "仆")
    }

    /// 扫描数字字面量（整数、浮点数、十六进制）
    fn scan_number(&mut self) -> String {
        let mut buf = String::new();
        while let Some(c) = self.peek() {
            if c.is_ascii_alphanumeric()
                || c == '.'
                || c == '+'
                || c == '-'
                || c == 'p'
                || c == 'P'
                || c == 'e'
                || c == 'E'
            {
                buf.push(c);
                self.next_char();
            } else {
                break;
            }
        }
        buf
    }

    /// 扫描 #XD 二五仔係我 python内嵌代码
    fn scan_python_inline(&mut self) -> String {
        let mut buf = String::new();
        while let Some(c) = self.peek() {
            buf.push(c);
            self.next_char();
            if buf.ends_with("二五仔係我") {
                break;
            }
        }
        buf
    }

    pub fn consume_token(&mut self) -> Result<Token, LexError> {
        self.skip_whitespace_and_comment()?;
        self.start_byte = self
            .peeked
            .map(|(byte, _)| byte)
            .unwrap_or(self.source.len());
        let start_pos = self.cur_pos();

        let c = match self.peek() {
            Some(ch) => ch,
            None => return Ok(self.mk_token(start_pos, TokenType::EOF, "EOF".to_string())),
        };

        let token = match c {
            '&' => {
                if self.starts_with("&&") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::Keyword, "&&")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::OpBand, "&")
                }
            }
            '|' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::Brack, "|")
            }
            '?' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::Mark, "?")
            }
            ':' => {
                if self.starts_with("::") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::DColon, "::")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::Colon, ":")
                }
            }
            '%' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::OpMod, "%")
            }
            '~' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::OpNot, "~")
            }
            '-' => {
                if self.starts_with("->") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::Keyword, KW_DOT)
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::OpMinus, "-")
                }
            }
            '=' => {
                if self.starts_with("==>") {
                    self.consume_many(3);
                    self.mk_token(start_pos, TokenType::Keyword, "==>")
                } else if self.starts_with("=>") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::Keyword, KW_DO)
                } else if self.starts_with("==") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpEq, "==")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::OpAssign, "=")
                }
            }
            '$' => {
                if self.starts_with("$$") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::Keyword, "$$")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::Keyword, "$")
                }
            }
            '<' => {
                if self.starts_with("<*>") {
                    self.consume_many(3);
                    self.mk_token(start_pos, TokenType::VarArg, "<*>")
                } else if self.starts_with("<|>") {
                    self.consume_many(3);
                    self.mk_token(start_pos, TokenType::OpBor, "<|>")
                } else if self.starts_with("<->") {
                    self.consume_many(3);
                    self.mk_token(start_pos, TokenType::OpConcat, "<->")
                } else if self.starts_with("<=") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpLe, "<=")
                } else if self.starts_with("<<") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpShl, "<<")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::OpLt, "<")
                }
            }
            '>' => {
                if self.starts_with(">=") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpGe, ">=")
                } else if self.starts_with(">>") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpShr, ">>")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::OpGt, ">")
                }
            }
            '!' => {
                if self.starts_with("!=") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpNe, "!=")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::Excl, "!")
                }
            }
            '@' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::Keyword, "@")
            }
            '{' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepLCurly, "{")
            }
            '}' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepRCurly, "}")
            }
            '(' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepLParen, "(")
            }
            ')' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepRParen, ")")
            }
            '[' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepLBrack, "[")
            }
            ']' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepRBrack, "]")
            }
            '.' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepDot, ".")
            }
            '\'' | '"' => {
                let s = self.scan_string(c)?;
                self.mk_token(start_pos, TokenType::String, s)
            }
            '0'..='9' => {
                let num = self.scan_number();
                self.mk_token(start_pos, TokenType::Num, num)
            }
            '+' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::OpAdd, "+")
            }
            '*' => {
                if self.starts_with("**") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpPow, "**")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::OpMul, "*")
                }
            }
            '/' => {
                if self.starts_with("//") {
                    self.consume_many(2);
                    self.mk_token(start_pos, TokenType::OpIDiv, "//")
                } else {
                    self.next_char();
                    self.mk_token(start_pos, TokenType::OpDiv, "/")
                }
            }
            '^' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::OpWave, "^")
            }
            ',' => {
                self.next_char();
                self.mk_token(start_pos, TokenType::SepComma, ",")
            }
            '#' => {
                if self.starts_with("#XD") {
                    let s = self.scan_python_inline();
                    self.mk_token(start_pos, TokenType::CallNativeExpr, s)
                } else {
                    unreachable!("# 应该被注释分支提前跳过");
                }
            }
            ch if Self::is_chinese(ch) || ch == '_' || ch.is_ascii_alphabetic() => {
                let ident = self.scan_ident();
                if KEYWORDS.contains(&ident.as_str()) {
                    self.mk_token(start_pos, TokenType::Keyword, ident)
                } else {
                    self.mk_token(start_pos, TokenType::Identifier, ident)
                }
            }
            unknown => {
                return Err(LexError::LexerErr {
                    msg: format!("濑嘢!!! 睇唔明嘅Token: `{unknown}`"),
                    pos: start_pos,
                    file: self.file_path.clone(),
                });
            }
        };

        Ok(token)
    }

    /// 迭代取出全部token直到EOF
    pub fn tokenize_all(&mut self) -> Result<Vec<Token>, LexError> {
        let mut tokens = Vec::new();
        loop {
            let tk = self.consume_token()?;
            let is_eof = matches!(tk.typ, TokenType::EOF);
            tokens.push(tk);
            if is_eof {
                break;
            }
        }
        Ok(tokens)
    }
}
