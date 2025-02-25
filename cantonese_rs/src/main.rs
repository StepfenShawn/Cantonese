mod ast;
mod lexer;
mod parser;

use lexer::Lexer;
use parser::{StatParser, Parser as CanParser, ParseError};

fn main() -> Result<(), ParseError> {
    let source_code = r#"如果 1 > 2 嘅話 => {
    畀我睇下 "Hello" 點樣先
} 唔係 嘅話 => {
    畀我睇下 123 點樣先
}
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
