// 粤语编程语言宏处理模块 - 模式匹配器

use super::match_state::MatchState;
use super::regex::{FragSpec, Regex};
use crate::ast::expression::Expression;
use crate::ast::position::Span;
use crate::parser::CantoneseParser;
use crate::parser::Rule;
use crate::parser::ast_builder::ParseError;
use pest::Parser;

/// 模式匹配器 - 用于匹配宏模式和输入
#[derive(Debug)]
pub struct PatMatcher {
    /// 匹配状态
    state: MatchState,
    /// 源代码
    source: String,
}

impl PatMatcher {
    /// 创建新的模式匹配器
    pub fn new(source: String) -> Self {
        Self {
            state: MatchState::new(),
            source,
        }
    }

    /// 设置匹配状态
    pub fn with_state(mut self, state: MatchState) -> Self {
        self.state = state;
        self
    }

    /// 获取匹配状态
    pub fn state(&self) -> &MatchState {
        &self.state
    }

    /// 获取可变的匹配状态
    pub fn state_mut(&mut self) -> &mut MatchState {
        &mut self.state
    }

    /// 匹配变量
    pub fn match_var(&mut self, name: &str, spec: &FragSpec, expressions: &[Expression]) -> bool {
        if expressions.is_empty() {
            return false;
        }

        // 根据片段规范类型验证表达式
        let valid = match spec {
            FragSpec::Ident => {
                // 验证是否为标识符
                expressions.len() == 1 && matches!(expressions[0], Expression::Identifier(_, _))
            }
            FragSpec::Expr => {
                // 任何表达式都可以
                expressions.len() >= 1
            }
            FragSpec::Stmt => {
                // 验证是否为有效语句
                // 这里需要简化处理，因为在匹配阶段很难验证语句
                expressions.len() >= 1
            }
            FragSpec::Str => {
                // 验证是否为字符串字面量
                expressions.len() == 1 && matches!(expressions[0], Expression::StringLiteral(_, _))
            }
            FragSpec::Literal => {
                // 验证是否为字面量（字符串、数字等）
                expressions.len() == 1
                    && (matches!(expressions[0], Expression::StringLiteral(_, _))
                        || matches!(expressions[0], Expression::NumberLiteral(_, _))
                        || matches!(expressions[0], Expression::BoolLiteral(_, _)))
            }
            FragSpec::Other(_) => {
                // 未知类型，假设匹配
                true
            }
        };

        if valid {
            // 如果是单个表达式，直接添加
            if expressions.len() == 1 {
                self.state_mut()
                    .update_meta_var(name.to_string(), expressions[0].clone());
            } else {
                // 如果是多个表达式，创建一个列表表达式
                // 创建一个空的位置信息
                let span = if let Some(first) = expressions.first() {
                    if let Some(last) = expressions.last() {
                        Span::new(first.span().start, last.span().end)
                    } else {
                        Span::new(Default::default(), Default::default())
                    }
                } else {
                    Span::new(Default::default(), Default::default())
                };

                let list_expr = Expression::ListExpression {
                    elements: expressions.to_vec(),
                    span,
                };
                self.state_mut()
                    .update_meta_var(name.to_string(), list_expr);
            }
            return true;
        }

        false
    }

    /// 分割输入序列为多种可能的前缀和后缀
    fn split_input<'a>(
        &self,
        input: &'a [Expression],
    ) -> Vec<(&'a [Expression], &'a [Expression])> {
        let mut result = Vec::new();

        // 考虑所有可能的分割点
        for i in 0..=input.len() {
            let (prefix, suffix) = input.split_at(i);
            result.push((prefix, suffix));
        }

        result
    }

    /// 专门用于前缀匹配的分割
    fn prefix_split<'a>(
        &self,
        input: &'a [Expression],
    ) -> Vec<(&'a [Expression], &'a [Expression])> {
        let mut result = Vec::new();

        // 从最长的前缀开始尝试
        for i in (0..=input.len()).rev() {
            let (prefix, suffix) = input.split_at(i);
            result.push((prefix, suffix));
        }

        result
    }

    /// 判断当前regex是否匹配input
    pub fn matches(&mut self, regex: &Regex, inputs: &[Expression]) -> bool {
        match regex {
            Regex::Empty => inputs.is_empty(),
            Regex::Atom(s) => {
                if inputs.len() == 1 {
                    if let Expression::StringLiteral(text, _) = &inputs[0] {
                        text == s
                    } else if let Expression::Identifier(name, _) = &inputs[0] {
                        name == s
                    } else {
                        false
                    }
                } else {
                    false
                }
            }
            Regex::Var { name, spec } => {
                // 匹配元变量
                self.match_var(name, spec, inputs)
            }
            Regex::Concat { left, right } => {
                // 尝试不同的分割方式
                let splits = self.split_input(inputs);

                // 记录当前状态
                let backup_state = self.state.clone();

                for (prefix, suffix) in splits {
                    // 匹配左侧
                    if self.matches(left, prefix) {
                        // 如果左侧匹配成功，继续匹配右侧
                        if self.matches(right, suffix) {
                            return true;
                        }
                    }

                    // 这种分割方式不成功，恢复状态
                    self.state = backup_state.clone();
                }

                false
            }
            Regex::Star(inner) => {
                // 匹配零或多次
                if inputs.is_empty() {
                    return true;
                }

                // 尝试不同的前缀匹配
                let splits = self.prefix_split(inputs);

                for (prefix, suffix) in splits {
                    if prefix.is_empty() {
                        continue;
                    }

                    // 记录当前状态
                    let backup_state = self.state.clone();

                    // 匹配前缀
                    if self.matches(inner, prefix) {
                        // 对剩余部分递归应用Star匹配
                        if self.matches(&Regex::Star(inner.clone()), suffix) {
                            return true;
                        }
                    }

                    // 恢复状态
                    self.state = backup_state;
                }

                false
            }
            Regex::Optional(inner) => {
                // 匹配零或一次
                inputs.is_empty() || self.matches(inner, inputs)
            }
        }
    }

    /// 尝试解析表达式
    pub fn try_parse_expression(&self, input: &str) -> Result<Expression, ParseError> {
        // 使用Pest解析器解析表达式
        let pairs = CantoneseParser::parse(Rule::expression, input)?;
        let pair = pairs
            .into_iter()
            .next()
            .ok_or_else(|| ParseError::Custom("无法解析表达式".to_string()))?;

        // 使用AST构建器构建表达式
        let ast_builder = crate::parser::ast_builder::AstBuilder::new(input);
        ast_builder.build_expression(pair)
    }
}
