// use std::path::Path;

use cantonese_rs::lexer::token::Pos;
use cantonese_rs::lexer::{Lexer, LexError};
use cantonese_rs::parser::{ColorChoice, ParseError, Parser as CanParser, StatParser};

// fn parse_cantonese_file(path: &Path) -> Result<Vec<cantonese_rs::ast::Stat>, String> {
//     let source = std::fs::read_to_string(path)
//         .map_err(|e| format!("failed to read {}: {e}", path.display()))?;
//     let path_str = path.to_string_lossy().to_string();
//     let mut lexer = Lexer::new(path_str.clone(), &source);
//     let tokens = lexer
//         .tokenize_all()
//         .map_err(|e| format!("lexer error in {}: {e}", path.display()))?;
//     let mut parser = CanParser::new(&tokens, &path_str);
//     StatParser::parse_stats(&mut parser)
//         .map_err(|e| format!("parser error in {}: {e}", path.display()))
// }

fn lexer_to_parse_error(err: LexError) -> ParseError {
    match err {
        LexError::LexerErr { msg, pos, file } => ParseError::from_lexer(file, pos, msg),
        LexError::UnfinishedString(pos) => {
            ParseError::from_lexer("<標準輸入>", pos, "未閉合字符串字面量")
        }
        LexError::Io(e) => ParseError::from_lexer("<標準輸入>", Pos::simple(0, 0), e.to_string()),
    }
}

fn main() {
    let source_code = r#"
/*
 * Cantonese 实现线性回归算法
*/
{% std::macros::math %}

使下 py::math

|[300.0 , 400.0 , 400.0 , 550.0 , 720.0 , 850.0 , 900.0 , 950.0]| 拍住上 => |X|
|[300.0 , 350.0 , 490.0 , 500.0 , 600.0 , 610.0 , 700.0 , 660.0]| 拍住上 => |Y|
过嚟估下!(L_REG => |900.0|, X, Y,)
"#;

    let mut lex = Lexer::new("<標準輸入>".to_string(), source_code);
    let tokens = match lex.tokenize_all() {
        Ok(tks) => tks,
        Err(e) => {
            eprintln!("{}", lexer_to_parse_error(e).report(source_code, ColorChoice::Auto));
            std::process::exit(1);
        }
    };

    // for tk in &tokens {
    //     println!("{}", tk);
    // }
    // println!("---");
    let mut parser = CanParser::new(&tokens, "<標準輸入>");
    match StatParser::parse_stats(&mut parser) {
        Ok(stats) => {
            for stat in stats {
                println!("{:?}", stat);
            }
        }
        Err(e) => {
            eprintln!("{}", e.report(source_code, ColorChoice::Auto));
            std::process::exit(1);
        }
    }
}
