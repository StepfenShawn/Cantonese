// 粤语编程语言宏处理模块 - 元变量

use crate::ast::expression::Expression;
use std::collections::HashMap;
// 删除未使用的导入
//use crate::parser::token_tree::{Token, TokenTree, TokenTreeNode};

/// 元变量 - 宏匹配过程中捕获的变量
#[derive(Debug, Clone)]
pub struct MetaVar {
    /// 捕获的表达式列表（对于重复匹配的情况会有多个值）
    values: Vec<Expression>,
    /// 当前迭代索引
    current_index: usize,
}

impl MetaVar {
    /// 创建新的元变量
    pub fn new(value: Expression) -> Self {
        Self {
            values: vec![value],
            current_index: 0,
        }
    }

    /// 获取元变量的值
    pub fn value(&mut self) -> Expression {
        if self.values.is_empty() {
            panic!("元变量中没有值");
        }

        let value = self.values[self.current_index].clone();
        self.current_index = (self.current_index + 1) % self.values.len();
        value
    }

    /// 重置迭代器
    pub fn reset(&mut self) {
        self.current_index = 0;
    }

    /// 更新元变量的值
    pub fn update(&mut self, value: Expression) {
        if !self.values.contains(&value) {
            self.values.push(value);
        }
    }

    /// 获取重复次数
    pub fn repetition_count(&self) -> usize {
        self.values.len()
    }
}

/// 元变量环境 - 存储宏展开过程中的所有元变量
#[derive(Debug, Clone, Default)]
pub struct MetaVarEnv {
    vars: HashMap<String, MetaVar>,
}

impl MetaVarEnv {
    /// 创建新的元变量环境
    pub fn new() -> Self {
        Self {
            vars: HashMap::new(),
        }
    }

    /// 添加或更新元变量
    pub fn add_or_update(&mut self, name: String, value: Expression) {
        if let Some(var) = self.vars.get_mut(&name) {
            var.update(value);
        } else {
            self.vars.insert(name, MetaVar::new(value));
        }
    }

    /// 获取元变量
    pub fn get(&mut self, name: &str) -> Option<&mut MetaVar> {
        self.vars.get_mut(name)
    }

    /// 检查元变量是否存在
    pub fn contains(&self, name: &str) -> bool {
        self.vars.contains_key(name)
    }

    /// 获取元变量的重复次数
    pub fn get_repetition_count(&self, name: &str) -> usize {
        self.vars.get(name).map_or(0, |var| var.repetition_count())
    }

    /// 获取所有元变量的名称和引用
    pub fn iter(&self) -> impl Iterator<Item = (&String, &MetaVar)> {
        self.vars.iter()
    }
}
