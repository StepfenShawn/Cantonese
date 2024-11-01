// 粤语编程语言主程序入口

use std::env;
use std::fs;
use std::io::{self, Result};
use std::path::{Path, PathBuf};
use clap::{Parser, Subcommand};

use crate::parser::ast_builder::AstBuilder;
use crate::macros::expand_macros;

pub mod ast;
pub mod parser;
pub mod macros;
pub mod diagnostics;

use diagnostics::DiagnosticReporter;

/// 粵語編程語言 - Rust 實現
#[derive(Parser)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 解析粵語源代碼文件
    Parse {
        /// 要解析的文件
        file: PathBuf,
        
        /// 輸出JSON格式的AST
        #[arg(short, long)]
        json: bool,
    },
    
    /// 運行粵語程序
    Run {
        /// 要運行的文件
        file: PathBuf,
    },
    
    /// 檢查粵語程序是否有語法錯誤
    Check {
        /// 要檢查的文件
        file: PathBuf,
    },
}

fn main() -> Result<()> {
    let cli = Cli::parse();
    
    match cli.command {
        Commands::Parse { file, json } => {
            parse_file(file, json)?;
        }
        Commands::Run { file } => {
            println!("運行功能正在開發中");
            parse_file(file, false)?;
        }
        Commands::Check { file } => {
            check_file(file)?;
        }
    }
    
    Ok(())
}

/// 解析文件並輸出語法樹
fn parse_file(file: PathBuf, output_json: bool) -> Result<()> {
    let file_path = file.to_string_lossy().to_string();
    let source = fs::read_to_string(&file)?;
    let reporter = DiagnosticReporter::new(source.clone(), file_path.clone());
    
    // 解析源代码为AST
    let ast_builder = AstBuilder::new(&source);
    let program = match ast_builder.parse() {
        Ok(ast) => ast,
        Err(e) => {
            eprintln!("解析錯誤: {}", e);
            return Ok(());
        }
    };
    
    // 展开宏（新增的步骤）
    let expanded_program = expand_macros(program);
    
    if output_json {
        // 输出展开后的AST到JSON文件
        print_program(&expanded_program, &file_path);
    } else {
        println!("成功解析文件: {}", file_path);
        println!("語法樹包含 {} 條語句", expanded_program.statements.len());
    }
    
    Ok(())
}

/// 检查文件语法是否正确
fn check_file(file: PathBuf) -> Result<()> {
    let file_path = file.to_string_lossy().to_string();
    let source = fs::read_to_string(&file)?;
    let reporter = DiagnosticReporter::new(source.clone(), file_path.clone());
    
    // 解析源代码为AST
    let ast_builder = AstBuilder::new(&source);
    match ast_builder.parse() {
        Ok(_) => {
            println!("文件 {} 语法正确", file_path);
            Ok(())
        }
        Err(e) => {
            eprintln!("文件 {} 语法错误: {}", file_path, e);
            Ok(())
        }
    }
}

fn print_program(program: &ast::statement::Program, source_path: &str) {
    let path = Path::new(source_path);
    let file_stem = path.file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("output");
    
    let out_path = format!("{}_ast.json", file_stem);
    
    let json = serde_json::to_string_pretty(program).expect("无法序列化AST");
    fs::write(&out_path, json).expect("无法写入AST文件");
    
    println!("AST已输出到：{}", out_path);
}
