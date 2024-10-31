// 粤语编程语言主程序入口

use anyhow::{Context, Result};
use clap::{Parser, Subcommand};
use std::fs;
use std::path::PathBuf;

mod ast;
mod diagnostics;
mod parser;

use diagnostics::DiagnosticReporter;
use parser::AstBuilder;

/// 粵語編程語言 - Rust 實現
#[derive(Parser)]
#[clap(version, about)]
struct Cli {
    #[clap(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// 解析粵語程序並輸出語法樹
    Parse {
        /// 輸入文件路徑
        #[clap(value_parser)]
        file: PathBuf,

        /// 是否以 JSON 格式輸出
        #[clap(short, long)]
        json: bool,
    },

    /// 運行粵語程序
    Run {
        /// 輸入文件路徑
        #[clap(value_parser)]
        file: PathBuf,
    },

    /// 檢查粵語程序語法
    Check {
        /// 輸入文件路徑
        #[clap(value_parser)]
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
fn parse_file(file_path: PathBuf, output_json: bool) -> Result<()> {
    let file_name = file_path.to_string_lossy().to_string();
    let source =
        fs::read_to_string(&file_path).with_context(|| format!("無法讀取文件 '{}'", file_name))?;

    let ast_builder = AstBuilder::new(&source);
    match ast_builder.parse() {
        Ok(program) => {
            if output_json {
                let json =
                    serde_json::to_string_pretty(&program).context("無法將 AST 轉換為 JSON")?;
                println!("{}", json);
            } else {
                println!("解析成功! AST:\n{:#?}", program);
            }
        }
        Err(e) => {
            let reporter = DiagnosticReporter::new(source, file_name);
            reporter.report_parse_error(e).expect("无法报告解析错误");
            return Err(anyhow::anyhow!("解析失敗"));
        }
    }

    Ok(())
}

/// 檢查文件語法
fn check_file(file_path: PathBuf) -> Result<()> {
    let file_name = file_path.to_string_lossy().to_string();
    let source =
        fs::read_to_string(&file_path).with_context(|| format!("無法讀取文件 '{}'", file_name))?;

    let ast_builder = AstBuilder::new(&source);
    match ast_builder.parse() {
        Ok(_) => {
            println!("✓ 語法檢查通過!");
        }
        Err(e) => {
            let reporter = DiagnosticReporter::new(source, file_name);
            reporter.report_parse_error(e).expect("无法报告解析错误");
            return Err(anyhow::anyhow!("語法檢查失敗"));
        }
    }

    Ok(())
}
