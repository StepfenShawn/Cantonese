//! Compile-time function handler.
//!
//! Handles compile-time function calls like `@用下(A::B::C 嘅 法寶)` which
//! imports macros from other Cantonese files at parse time.

use std::path::{Path, PathBuf};

use crate::lexer::{LexError, Lexer};
use crate::parser::stat::StatParser;
use crate::parser::{ParseError, Parser};

/// Resolve a module path (e.g. `A::B::C`) to a file path relative to the current file.
fn resolve_module_path(current_file: &str, module_path: &str) -> Result<PathBuf, String> {
    let current_dir = Path::new(current_file)
        .parent()
        .ok_or_else(|| format!("Cannot get parent directory of: {}", current_file))?;

    // Convert A::B::C to A/B/C
    let relative_path =
        module_path.replace("::", std::path::MAIN_SEPARATOR_STR.to_string().as_str());

    let cantonese_path = current_dir.join(format!("{}.cantonese", relative_path));
    if cantonese_path.exists() {
        return Ok(cantonese_path);
    }

    Err(format!(
        "Cannot find module '{}' (looked for {}.cantonese in {})",
        module_path,
        relative_path,
        current_dir.display()
    ))
}

/// Read a file and return its contents.
fn read_file(path: &Path) -> Result<String, String> {
    std::fs::read_to_string(path).map_err(|e| format!("Failed to read {}: {}", path.display(), e))
}

/// Handle the `@用下` compile-time function.
///
/// Syntax: `@用下(A::B::C 嘅 法寶)` or `@用下(A)`
///
/// This parses the target file and registers all its macros in the current
/// parser's macro registry.
pub fn handle_use_macros(parser: &mut Parser, module_path: &str) -> Result<(), ParseError> {
    let current_file = parser.file_path().to_string();

    let target_path = resolve_module_path(&current_file, module_path).map_err(|msg| {
        ParseError::syntax(
            parser
                .peek_token()
                .unwrap_or(&crate::lexer::token::Token::new(
                    crate::lexer::token::Pos::simple(0, 0),
                    crate::lexer::token::TokenType::EOF,
                    "EOF".into(),
                )),
            parser.file_path(),
            msg,
            "檢查模塊路徑",
        )
    })?;

    let source = read_file(&target_path).map_err(|msg| {
        ParseError::syntax(
            parser
                .peek_token()
                .unwrap_or(&crate::lexer::token::Token::new(
                    crate::lexer::token::Pos::simple(0, 0),
                    crate::lexer::token::TokenType::EOF,
                    "EOF".into(),
                )),
            parser.file_path(),
            msg,
            "檢查文件是否存在",
        )
    })?;

    // Parse the target file to register its macros
    let target_path_str = target_path.to_string_lossy().to_string();
    let mut lexer = Lexer::new(target_path_str.clone(), &source);
    let tokens = lexer.tokenize_all().map_err(|e| match e {
        LexError::LexerErr { msg, pos, file } => ParseError::syntax(
            &crate::lexer::token::Token::new(pos, crate::lexer::token::TokenType::EOF, "".into()),
            &file,
            msg,
            "詞法錯誤",
        ),
        LexError::UnfinishedString(pos) => ParseError::syntax(
            &crate::lexer::token::Token::new(pos, crate::lexer::token::TokenType::EOF, "".into()),
            &target_path_str,
            "未結束嘅字符串",
            "檢查字符串語法",
        ),
        LexError::Io(e) => ParseError::syntax(
            &crate::lexer::token::Token::new(
                crate::lexer::token::Pos::simple(0, 0),
                crate::lexer::token::TokenType::EOF,
                "".into(),
            ),
            &target_path_str,
            format!("IO error: {}", e),
            "檢查文件權限",
        ),
    })?;

    // Parse the file with the same macro registry so macros get registered
    let mut target_parser =
        Parser::new_with_registry(&tokens, &target_path_str, parser.macro_registry.clone());
    let _stats = StatParser::parse_stats(&mut target_parser).map_err(|e| {
        ParseError::syntax(
            parser
                .peek_token()
                .unwrap_or(&crate::lexer::token::Token::new(
                    crate::lexer::token::Pos::simple(0, 0),
                    crate::lexer::token::TokenType::EOF,
                    "EOF".into(),
                )),
            parser.file_path(),
            format!("Error parsing imported module '{}': {}", module_path, e),
            "檢查導入嘅模塊語法",
        )
    })?;

    Ok(())
}
