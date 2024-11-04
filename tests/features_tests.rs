//! 粤语编程语言语法特性测试

extern crate cantonese_rs;
use cantonese_rs::parser::ast_builder::AstBuilder;
use std::fs;
use std::path::Path;

// 测试解析函数声明
#[test]
fn test_function_declaration_parsing() {
    let source = r#"
    介紹返 $ add |x, y| 點部署
        還數 x + y
    搞掂
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析函数声明失败: {:?}", result.err());
}

// 测试解析类声明
#[test]
fn test_class_declaration_parsing() {
    let source = r#"
    介紹返 Person 係 乜X {
        佢個老豆叫 Object
        佢識得 say_hello |自己, name| => {
            畀我睇下 "Hello, " + name 點樣先?
        }
        佢有啲咩 => 
            name: 公家嘢,
            age: 私家嘢
    }
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析类声明失败: {:?}", result.err());
}

// 测试解析表达式
#[test]
fn test_expression_parsing() {
    let source = r#"
    介紹返 x 係 1 + 2 * 3
    介紹返 y 係 |x > 10|
    介紹返 z 係 [1, 2, 3]
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析表达式失败: {:?}", result.err());
}

// 测试解析控制流语句
#[test]
fn test_control_flow_parsing() {
    let source = r#"
    介紹返 x 係 10
    如果 |x > 10| 嘅话 => {
        畀我睇下 "x 大于 10" 點樣先?
    } 定係 |x < 5| 嘅话 => {
        畀我睇下 "x 小于 5" 點樣先?
    } 唔係 嘅话 => {
        畀我睇下 "x 介于 5 和 10 之间" 點樣先?
    }
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析控制流语句失败: {:?}", result.err());
}

// 测试解析循环语句
#[test]
fn test_loop_parsing() {
    let source = r#"
    介紹返 i 係 0
    落操场玩跑步 {
        畀我睇下 i 點樣先?
        如果 |i > 10| 嘅话 => {
            飲茶先啦
        }
        介紹返 i 係 i + 1
    } 玩到 i 为止 收工
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析循环语句失败: {:?}", result.err());
}

// 测试解析异常处理
#[test]
fn test_exception_handling_parsing() {
    let source = r#"
    执嘢 => {
        掟個 "发生错误" 嚟睇下?
    } 揾到 e 嘅话 => {
        畀我睇下 "捕获到异常: " + e 點樣先?
    } 执手尾 => {
        畀我睇下 "清理资源" 點樣先?
    }
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析异常处理失败: {:?}", result.err());
}

// 测试解析模式匹配
#[test]
fn test_pattern_matching_parsing() {
    let source = r#"
    介紹返 value 係 1
    睇撚住 value => 
        | 撞见 1 => {
            畀我睇下 "值是 1" 點樣先?
        }
        | 撞见 2 => {
            畀我睇下 "值是 2" 點樣先?
        }
        | _ => {
            畀我睇下 "其他值" 點樣先?
        }
    搞掂
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析模式匹配失败: {:?}", result.err());
}

// 测试解析 Lambda 表达式
#[test]
fn test_lambda_parsing() {
    let source = r#"
    介紹返 square 係 $$ |x| {x * x}
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析 Lambda 表达式失败: {:?}", result.err());
}
