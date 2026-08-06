// use std::path::Path;

use cantonese_rs::lexer::Lexer;
use cantonese_rs::parser::{ParseError, Parser as CanParser, StatParser};

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

fn main() -> Result<(), ParseError> {
    let source_code = r#"
介紹返 vec 係 袋仔的法寶 =>
    | ($(@element:expr),+) => {
        [${@element},+]
    }
    | () => {
        []
    }
搞掂

畀我睇下 vec!("Hello", 1+1, "gg",) 點樣先??
畀我睇下 vec!() 點樣先??
"#;

    let mut lex = Lexer::new("<標準輸入>".to_string(), source_code);
    let tokens = lex.tokenize_all().map_err(|e| ParseError::SyntaxError {
        file: "<標準輸入>".into(),
        line: 0,
        offset: 0,
        msg: e.to_string(),
        tip: "lexer 出錯".into(),
    })?;

    for tk in &tokens {
        println!("{}", tk);
    }
    println!("---");
    let mut parser = CanParser::new(&tokens, "<標準輸入>");
    let stats = StatParser::parse_stats(&mut parser)?;
    for stat in stats {
        println!("{:?}", stat);
    }
    Ok(())
}
