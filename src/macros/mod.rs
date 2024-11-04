// 粤语编程语言宏处理模块

mod macro_expander;
mod match_state;
mod meta_var;
mod pat_matcher;
pub mod regex;
pub(crate) mod token_matcher;

pub use macro_expander::MacroDefinition;
pub use macro_expander::MacroExpander;
pub use token_matcher::FragmentType;

/// 宏展开函数 - 展开程序中的所有宏调用
pub fn expand_macros(program: crate::ast::statement::Program) -> crate::ast::statement::Program {
    let expander = MacroExpander::new();
    expander.expand_program(program)
}
