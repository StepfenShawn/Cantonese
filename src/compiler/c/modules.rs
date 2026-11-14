//! Module loading for the C backend.
use std::collections::HashSet;
use std::path::{Path, PathBuf};

use crate::ast::{Exp, IdExp, ImportStat, NamesExp, Stat};
use crate::compiler::CodegenError;
use crate::lexer::Lexer;
use crate::parser::{Parser as CanParser, StatParser};

/// Resolve and inline every import in `stats`.
pub fn expand_imports(stats: Vec<Stat>, filename: &str) -> Result<Vec<Stat>, CodegenError> {
    let path = Path::new(filename);
    let base = path
        .parent()
        .filter(|parent| !parent.as_os_str().is_empty())
        .unwrap_or_else(|| Path::new("."));

    let mut loader = ModuleLoader::new();
    loader.expand(stats, base)
}

struct ModuleLoader {
    loaded: HashSet<PathBuf>,
    loading: Vec<PathBuf>,
    search_roots: Vec<PathBuf>,
}

impl ModuleLoader {
    fn new() -> Self {
        let mut search_roots = Vec::new();
        if let Ok(cwd) = std::env::current_dir() {
            search_roots.push(cwd);
        }
        search_roots.push(PathBuf::from(env!("CARGO_MANIFEST_DIR")));
        if let Ok(exe) = std::env::current_exe() {
            if let Some(dir) = exe.parent() {
                search_roots.push(dir.to_path_buf());
            }
        }

        Self {
            loaded: HashSet::new(),
            loading: Vec::new(),
            search_roots,
        }
    }

    fn expand(&mut self, stats: Vec<Stat>, base: &Path) -> Result<Vec<Stat>, CodegenError> {
        let mut expanded = Vec::new();

        for stat in stats {
            let Stat::Import(ImportStat { names, .. }) = stat else {
                expanded.push(stat);
                continue;
            };

            for trace in names_to_traces(&names) {
                if trace.is_empty() {
                    continue;
                }
                if matches!(trace[0].as_str(), "python" | "py") {
                    // Python modules are not available to the C backend.
                    continue;
                }

                let path = self.resolve(&trace, base)?.ok_or_else(|| {
                    CodegenError::Unsupported(format!(
                        "cannot find Cantonese module `{}`",
                        trace.join("::")
                    ))
                })?;
                let canonical = canonicalize(&path);

                if self.loaded.contains(&canonical) {
                    continue;
                }
                if self.loading.contains(&canonical) {
                    return Err(CodegenError::Unsupported(format!(
                        "circular import detected for `{}`",
                        path.display()
                    )));
                }

                self.loading.push(canonical.clone());
                let source = std::fs::read_to_string(&path).map_err(|error| {
                    CodegenError::Unsupported(format!(
                        "failed to read imported module `{}`: {}",
                        path.display(),
                        error
                    ))
                })?;
                let imported = parse_source(&source, &path)?;
                let imported_base = path
                    .parent()
                    .filter(|parent| !parent.as_os_str().is_empty())
                    .unwrap_or(base)
                    .to_path_buf();
                let imported = self.expand(imported, &imported_base)?;
                self.loading.pop();
                self.loaded.insert(canonical);

                expanded.extend(imported.into_iter().filter(is_module_item));
            }
        }

        Ok(expanded)
    }

    fn resolve(&self, trace: &[String], base: &Path) -> Result<Option<PathBuf>, CodegenError> {
        for split in (1..=trace.len()).rev() {
            let module = trace[..split].join("/");
            let relative = format!("{module}.cantonese");

            for root in self.roots_with(base) {
                let candidate = root.join(&relative);
                if candidate.is_file() {
                    return Ok(Some(candidate));
                }
            }
        }
        Ok(None)
    }

    fn roots_with(&self, base: &Path) -> Vec<PathBuf> {
        let mut roots = vec![base.to_path_buf()];
        for root in &self.search_roots {
            if !roots.contains(root) {
                roots.push(root.clone());
            }
        }
        roots
    }
}

/// Top-level statements from imported modules.  `收工` is dropped so that a
/// library file which is also a valid standalone program can be imported
/// without terminating the importing program.
fn is_module_item(stat: &Stat) -> bool {
    !matches!(stat, Stat::Exit(_))
}

fn parse_source(source: &str, path: &Path) -> Result<Vec<Stat>, CodegenError> {
    let filename = path.to_string_lossy().to_string();
    let mut lexer = Lexer::new(filename.clone(), source);
    let tokens = lexer.tokenize_all()?;
    let mut parser = CanParser::new(&tokens, &filename);
    Ok(StatParser::parse_stats(&mut parser)?)
}

fn canonicalize(path: &Path) -> PathBuf {
    std::fs::canonicalize(path).unwrap_or_else(|_| path.to_path_buf())
}

/// Convert a `NamesExp` into a list of fully-qualified import paths.
fn names_to_traces(exp: &Exp) -> Vec<Vec<String>> {
    match exp {
        Exp::Id(IdExp { name, .. }) => vec![vec![name.clone()]],
        Exp::Names(NamesExp { child, .. }) if !child.is_empty() => {
            let (head, tail) = child.split_first().unwrap();

            // `A::{B, C}` is parsed as NamesExp([A, NamesExp([B, C])]);
            // distribute the alternatives over the prefix.
            if tail.len() == 1 {
                if let Exp::Names(NamesExp {
                    child: set_children,
                    ..
                }) = &tail[0]
                {
                    let mut result = Vec::new();
                    for alternative in set_children {
                        for head_trace in names_to_traces(head) {
                            for alternative_trace in names_to_traces(alternative) {
                                let mut combined = head_trace.clone();
                                combined.extend(alternative_trace);
                                result.push(combined);
                            }
                        }
                    }
                    return result;
                }
            }

            let mut result = Vec::new();
            for head_trace in names_to_traces(head) {
                for tail_trace in names_to_traces_for_list(tail) {
                    let mut combined = head_trace.clone();
                    combined.extend(tail_trace);
                    result.push(combined);
                }
            }
            result
        }
        _ => Vec::new(),
    }
}

fn names_to_traces_for_list(exps: &[Exp]) -> Vec<Vec<String>> {
    if exps.is_empty() {
        return vec![Vec::new()];
    }
    let mut result = Vec::new();
    for exp in exps {
        result.extend(names_to_traces(exp));
    }
    result
}