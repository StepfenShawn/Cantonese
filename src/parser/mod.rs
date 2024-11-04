// 粤语编程语言嘅解析器模块

use pest_derive::Parser;

pub mod ast_builder;
pub mod macro_parser;
pub mod token_tree;

#[derive(Parser)]
#[grammar = "parser/cantonese.pest"]
pub struct CantoneseParser;

pub use ast_builder::AstBuilder;
