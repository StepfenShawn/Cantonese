use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

use cantonese_rs::compiler::c::{RUNTIME_C, RUNTIME_H, to_c};

struct Options {
    path: PathBuf,
    output: Option<PathBuf>,
}

fn parse_args(args: &[String]) -> Result<Options, String> {
    let mut path = None;
    let mut output = None;
    let mut index = 1;

    while index < args.len() {
        match args[index].as_str() {
            "-o" | "--output" => {
                let value = args
                    .get(index + 1)
                    .ok_or_else(|| "`-o` requires an output path".to_string())?;
                output = Some(PathBuf::from(value));
                index += 2;
            }
            value if value.starts_with('-') => {
                return Err(format!("unknown option: {value}"));
            }
            value => {
                if path.is_some() {
                    return Err(format!("unexpected argument: {value}"));
                }
                path = Some(PathBuf::from(value));
                index += 1;
            }
        }
    }

    let path =
        path.ok_or_else(|| "Usage: cantonese [file] [-compile] [-run] [-o output]".to_string())?;
    Ok(Options { path, output })
}

fn materialise_runtime(dir: &Path) -> Result<(), String> {
    fs::create_dir_all(dir).map_err(|e| format!("failed to create {}: {}", dir.display(), e))?;
    fs::write(dir.join("runtime.h"), RUNTIME_H)
        .map_err(|e| format!("failed to write runtime.h: {}", e))?;
    fs::write(dir.join("runtime.c"), RUNTIME_C)
        .map_err(|e| format!("failed to write runtime.c: {}", e))?;
    Ok(())
}

fn build_c(options: &Options, c_code: &str) -> Result<PathBuf, String> {
    let dir = env::temp_dir().join(format!("cantonese-c-{}", std::process::id()));
    println!("{:?}", dir);
    materialise_runtime(&dir)?;

    let stem = options
        .path
        .file_stem()
        .and_then(|stem| stem.to_str())
        .unwrap_or("main");
    let c_path = dir.join(format!("{stem}.c"));
    fs::write(&c_path, c_code).map_err(|e| format!("failed to write generated C: {}", e))?;

    let executable = match &options.output {
        Some(path) => path.clone(),
        None => PathBuf::from(stem),
    };

    let status = Command::new("gcc")
        .arg(&c_path)
        .arg(dir.join("runtime.c"))
        .arg("-I")
        .arg(&dir)
        .arg("-o")
        .arg(&executable)
        .arg("-lm")
        .status()
        .map_err(|e| format!("failed to invoke `gcc`: {}", e))?;

    if !status.success() {
        return Err(format!("`gcc` exited with status {}", status));
    }
    Ok(executable)
}

fn main() {
    let args: Vec<String> = env::args().collect();
    let options = match parse_args(&args) {
        Ok(options) => options,
        Err(message) => {
            eprintln!("{message}");
            std::process::exit(1);
        }
    };

    let source = match fs::read_to_string(&options.path) {
        Ok(source) => source,
        Err(error) => {
            eprintln!("failed to read {}: {}", options.path.display(), error);
            std::process::exit(1);
        }
    };

    let c_code = match to_c(&source, &options.path.to_string_lossy()) {
        Ok((code, _)) => code,
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(1);
        }
    };

    match build_c(&options, &c_code) {
        Ok(path) => path,
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(1);
        }
    };
}
