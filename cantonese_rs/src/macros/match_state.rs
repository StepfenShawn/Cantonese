// 粤语编程语言宏处理模块 - 匹配状态

use super::meta_var::MetaVarEnv;
use crate::ast::expression::Expression;

/// 匹配状态 - 跟踪宏匹配过程中的状态
#[derive(Debug, Clone, Default)]
pub struct MatchState {
    /// 元变量环境
    pub meta_vars: MetaVarEnv,
    /// 匹配成功标志
    pub success: bool,
}

impl MatchState {
    /// 创建新的匹配状态
    pub fn new() -> Self {
        Self {
            meta_vars: MetaVarEnv::new(),
            success: false,
        }
    }

    /// 更新元变量
    pub fn update_meta_var(&mut self, name: String, value: Expression) {
        self.meta_vars.add_or_update(name, value);
    }

    /// 标记匹配成功
    pub fn mark_success(&mut self) {
        self.success = true;
    }

    /// 标记匹配失败
    pub fn mark_failure(&mut self) {
        self.success = false;
    }

    /// 检查匹配是否成功
    pub fn is_successful(&self) -> bool {
        self.success
    }
} 