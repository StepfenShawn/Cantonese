use pyo3::types::{PyDict, PyList, PyTuple};
use pyo3::prelude::*;

use crate::{ast, parser};

// 将Rust的Position转换为Python字典
fn position_to_py(py: Python, pos: &ast::Position) -> PyResult<PyObject> {
    let dict = PyDict::new(py);
    dict.set_item("line", pos.line)?;
    dict.set_item("column", pos.column)?;
    dict.set_item("offset", pos.offset)?;
    Ok(dict.into())
}

// 将Rust的Span转换为Python字典
fn span_to_py(py: Python, span: &ast::Span) -> PyResult<PyObject> {
    let dict = PyDict::new(py);
    dict.set_item("start", position_to_py(py, &span.start)?)?;
    dict.set_item("end", position_to_py(py, &span.end)?)?;
    Ok(dict.into())
}

// 将表达式转换为Python对象
fn expression_to_py(py: Python, exp: &ast::Expression) -> PyResult<PyObject> {
    match exp {
        ast::Expression::NullLiteral(span) => {
            let dict = PyDict::new(py);
            dict.set_item("type", "NullExp")?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::BoolLiteral(value, span) => {
            let dict = PyDict::new(py);
            if *value {
                dict.set_item("type", "TrueExp")?;
            } else {
                dict.set_item("type", "FalseExp")?;
            }
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::NumberLiteral(value, span) => {
            let dict = PyDict::new(py);
            dict.set_item("type", "NumeralExp")?;
            dict.set_item("val", value)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::StringLiteral(value, span) => {
            let dict = PyDict::new(py);
            dict.set_item("type", "StringExp")?;
            dict.set_item("s", value)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::Identifier(name, span) => {
            let dict = PyDict::new(py);
            dict.set_item("type", "IdExp")?;
            dict.set_item("name", name)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::ListExpression { elements, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "ListExp")?;
            
            let py_elements = PyList::empty(py);
            for element in elements {
                py_elements.append(expression_to_py(py, element)?)?;
            }
            dict.set_item("elem_exps", py_elements)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::MapExpression { elements, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "MapExp")?;
            
            let py_elements = PyList::empty(py);
            for element in elements {
                py_elements.append(expression_to_py(py, element)?)?;
            }
            dict.set_item("elem_exps", py_elements)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::UnaryExpression { operator, operand, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "UnopExp")?;
            
            let op_str = match operator {
                ast::UnaryOperator::Negative => "-",
                ast::UnaryOperator::Not => "!",
                ast::UnaryOperator::Len => "len",
                _ => "unknown",
            };
            
            dict.set_item("op", op_str)?;
            dict.set_item("exp", expression_to_py(py, operand)?)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::BinaryExpression { left, operator, right, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "BinopExp")?;
            
            let op_str = match operator {
                ast::BinaryOperator::Add => "+",
                ast::BinaryOperator::Subtract => "-",
                ast::BinaryOperator::Multiply => "*",
                ast::BinaryOperator::Divide => "/",
                ast::BinaryOperator::Equal => "==",
                ast::BinaryOperator::NotEqual => "!=",
                ast::BinaryOperator::LessThan => "<",
                ast::BinaryOperator::LessThanEqual => "<=",
                ast::BinaryOperator::GreaterThan => ">",
                ast::BinaryOperator::GreaterThanEqual => ">=",
                ast::BinaryOperator::Is => "is",
                ast::BinaryOperator::And => "and",
                ast::BinaryOperator::Concat => "<->",
                _ => "unknown",
            };
            
            dict.set_item("op", op_str)?;
            dict.set_item("exp1", expression_to_py(py, left)?)?;
            dict.set_item("exp2", expression_to_py(py, right)?)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::CallExpression { callee, arguments, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "FuncCallExp")?;
            dict.set_item("prefix_exp", expression_to_py(py, callee)?)?;
            
            let py_args = PyList::empty(py);
            for arg in arguments {
                py_args.append(expression_to_py(py, arg)?)?;
            }
            
            dict.set_item("args", py_args)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::ObjectAccessExpression { object, property, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "ObjectAccessExp")?;
            dict.set_item("prefix_exp", expression_to_py(py, object)?)?;
            dict.set_item("key_exp", expression_to_py(py, property)?)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Expression::ListAccessExpression { list, index, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "ListAccessExp")?;
            dict.set_item("prefix_exp", expression_to_py(py, list)?)?;
            dict.set_item("key_exp", expression_to_py(py, index)?)?;
            dict.set_item("span", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        _ => {
            // 对于其他类型的表达式，简单返回一个包含类型的字典
            let dict = PyDict::new(py);
            dict.set_item("type", "UnimplementedExp")?;
            Ok(dict.into())
        }
    }
}

// 将语句转换为Python对象
fn statement_to_py(py: Python, stmt: &ast::Statement) -> PyResult<PyObject> {
    match stmt {
        ast::Statement::ExpressionStatement { expression, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "CallStat")?;
            dict.set_item("exp", expression_to_py(py, expression)?)?;
            dict.set_item("pos", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Statement::AssignmentStatement { var_list, exp_list, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "AssignStat")?;
            
            let py_var_list = PyList::empty(py);
            for var in var_list {
                py_var_list.append(expression_to_py(py, var)?)?;
            }
            
            let py_exp_list = PyList::empty(py);
            for exp in exp_list {
                py_exp_list.append(expression_to_py(py, exp)?)?;
            }
            
            dict.set_item("var_list", py_var_list)?;
            dict.set_item("exp_list", py_exp_list)?;
            dict.set_item("pos", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Statement::IfStatement { if_exp, if_block, elif_exps, elif_blocks, else_block, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "IfStat")?;
            dict.set_item("if_exp", expression_to_py(py, if_exp)?)?;
            
            let py_if_block = PyList::empty(py);
            for stmt in &if_block.statements {
                py_if_block.append(statement_to_py(py, stmt)?)?;
            }
            
            let py_elif_exps = PyList::empty(py);
            for cond in elif_exps {
                py_elif_exps.append(expression_to_py(py, cond)?)?;
            }
            
            let py_elif_blocks = PyList::empty(py);
            for block in elif_blocks {
                let py_block = PyList::empty(py);
                for stmt in &block.statements {
                    py_block.append(statement_to_py(py, stmt)?)?;
                }
                py_elif_blocks.append(py_block)?;
            }
            
            let py_else_blocks = PyList::empty(py);
            if let Some(block) = else_block {
                for stmt in &block.statements {
                    py_else_blocks.append(statement_to_py(py, stmt)?)?;
                }
            }
            
            dict.set_item("if_block", py_if_block)?;
            dict.set_item("elif_exps", py_elif_exps)?;
            dict.set_item("elif_blocks", py_elif_blocks)?;
            dict.set_item("else_blocks", py_else_blocks)?;
            dict.set_item("pos", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Statement::PrintStatement { arguments, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "PrintStat")?;
            
            let py_args = PyList::empty(py);
            for arg in arguments {
                py_args.append(expression_to_py(py, arg)?)?;
            }
            
            dict.set_item("args", py_args)?;
            dict.set_item("pos", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        ast::Statement::FunctionDeclaration { name, parameters, body, span } => {
            let dict = PyDict::new(py);
            dict.set_item("type", "FunctionDefStat")?;
            dict.set_item("name_exp", expression_to_py(py, name)?)?;
            
            let py_args = PyList::empty(py);
            for param in parameters {
                py_args.append(expression_to_py(py, param)?)?;
            }
            
            let py_blocks = PyList::empty(py);
            for stmt in &body.statements {
                py_blocks.append(statement_to_py(py, stmt)?)?;
            }
            
            dict.set_item("args", py_args)?;
            dict.set_item("blocks", py_blocks)?;
            dict.set_item("pos", span_to_py(py, span)?)?;
            Ok(dict.into())
        },
        _ => {
            // 对于其他类型的语句，返回一个未实现的声明
            let dict = PyDict::new(py);
            dict.set_item("type", "UnimplementedStat")?;
            Ok(dict.into())
        }
    }
}

// 将程序转换为Python对象
fn program_to_py(py: Python, program: &ast::Program) -> PyResult<PyObject> {
    let py_statements = PyList::empty(py);
    
    for stmt in &program.statements {
        py_statements.append(statement_to_py(py, stmt)?)?;
    }
    
    Ok(py_statements.into())
}

#[pyfunction]
pub fn parse_to_ast(py: Python, code: &str) -> PyResult<PyObject> {
    let ast_builder = parser::ast_builder::AstBuilder::new(code);
    match ast_builder.parse() {
        Ok(program) => program_to_py(py, &program),
        Err(e) => {
            let error_dict = PyDict::new(py);
            error_dict.set_item("error", e.to_string())?;
            Ok(error_dict.into())
        }
    }
}
