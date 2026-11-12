use std::env;
use std::path::Path;

use cantonese_rs::{
    lexer::{LexError, Lexer},
    parser::{ColorChoice, ParseError, Parser, StatParser},
};

fn lexer_to_parse_error(file_path: &str, err: LexError) -> ParseError {
    match err {
        LexError::LexerErr { msg, pos, file } => ParseError::from_lexer(file, pos, msg),
        LexError::Io(error) => {
            ParseError::from_lexer(file_path, Default::default(), error.to_string())
        }
        LexError::UnfinishedString(pos) => {
            ParseError::from_lexer(file_path, pos, "未閉合字符串字面量")
        }
    }
}

fn parse_cantonese_source(
    path: &Path,
    source: &str,
) -> Result<Vec<cantonese_rs::ast::Stat>, ParseError> {
    let path_str = path.to_string_lossy().to_string();
    let mut lexer = Lexer::new(path_str.clone(), &source);
    let tokens = lexer
        .tokenize_all()
        .map_err(|e| lexer_to_parse_error(&path_str, e))?;
    let mut parser = Parser::new(&tokens, &path_str);
    StatParser::parse_stats(&mut parser)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    if let Some(path) = args.get(1) {
        let source = std::fs::read_to_string(path).expect(&format!("failed to read {}: ", path));
        match parse_cantonese_source(Path::new(path), source.as_str()) {
            Ok(stats) => {
                // for stat in stats {
                //     println!("{:?}", stat);
                // }
                println!("parser OK.");
            }
            Err(e) => {
                eprintln!("{}", e.report(&source, ColorChoice::Auto));
                std::process::exit(1);
            }
        }
    } else {
        println!("Usage: cantonese [file]");
    }
}
