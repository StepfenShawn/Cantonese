
use crate::parser::{MacroPatParser, ParseError};
use crate::{
    ast::{Exp, StringExp, TokenTree},
    compile_time::CompileTimeFn,
};
// ---------------------------------------------------------------------------
// Built-in compile-time function: @扮字
// ---------------------------------------------------------------------------
pub struct StringfyFn;

impl CompileTimeFn for StringfyFn {
    fn name(&self) -> &str {
        "扮字"
    }

    fn execute(&self, parser: &mut crate::parser::Parser) -> Result<crate::ast::Exp, ParseError> {
        let token_tree = MacroPatParser::parse_tokentrees(parser)?;
        let stringify = format!("\"{}\"", token_tree_to_string(&token_tree));
        Ok(Exp::String(StringExp {
            s: stringify,
            pos: None,
        }))
    }
}

fn token_tree_to_string(token_tree: &TokenTree) -> String {
    let mut result = "".to_string();
    for child in token_tree.child.iter() {
        match child {
            crate::ast::TokenTreeChild::Token(token) => {
                result += &format!(" {} ", token.value).to_string()
            }
            crate::ast::TokenTreeChild::Tree(token_tree) => {
                result += &token_tree_to_string(token_tree);
            }
            _ => unreachable!("MacroPatParser::parse_tokentrees just return "),
        }
    }
    result
}
