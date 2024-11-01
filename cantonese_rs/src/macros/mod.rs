// 粤语编程语言宏处理模块

mod meta_var;
mod match_state;
mod regex;
mod pat_matcher;
mod macro_expander;

pub use macro_expander::MacroExpander;
pub use macro_expander::MacroDefinition;

/// 宏展开函数 - 展开程序中的所有宏调用
pub fn expand_macros(program: crate::ast::statement::Program) -> crate::ast::statement::Program {
    let expander = MacroExpander::new();
    expander.expand_program(program)
} 