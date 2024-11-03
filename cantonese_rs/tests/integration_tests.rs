//! 粤语编程语言集成测试

use cantonese_rs::parser::ast_builder::AstBuilder;
use std::fs;
use std::path::Path;

// 测试复杂的函数和类组合
#[test]
fn test_complex_function_and_class() {
    let source = r#"
    # 定义一个Person类
    介紹返 Person 係 乜X {
        佢有啲咩 => 
            name: 公家嘢,
            age: 私家嘢
            
        佢識得 say_hello |自己| => {
            畀我睇下 "Hello, my name is " + 自己->name 點樣先?
        }
        
        佢識得 get_age |自己| => {
            還數 自己->age
        }
    }
    
    # 定义一个函数来创建Person对象
    介紹返 $ create_person |name, age| 點部署
        介紹返 p 係 Person
        介紹返 p->name 係 name
        介紹返 p->age 係 age
        還數 p
    搞掂
    
    # 使用函数和类
    介紹返 p 係 create_person 下 -> "Alice", 30
    p->say_hello()啦!
    畀我睇下 "Age: " + p->get_age() 點樣先?
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(
        result.is_ok(),
        "解析复杂函数和类组合失败: {:?}",
        result.err()
    );
}

// 测试嵌套控制流
#[test]
fn test_nested_control_flow() {
    let source = r#"
    介紹返 x 係 10
    介紹返 y 係 5
    
    如果 |x > 5| 嘅话 => {
        如果 |y > 0| 嘅话 => {
            畀我睇下 "x 大于 5，y 大于 0" 點樣先?
            
            落操场玩跑步 {
                畀我睇下 i 點樣先?
                如果 |i >= 3| 嘅话 => {
                    飲茶先啦
                }
                介紹返 i 係 i + 1
            } 玩到 i 为止 收工
        } 唔係 嘅话 => {
            畀我睇下 "x 大于 5，y 不大于 0" 點樣先?
        }
    } 唔係 嘅话 => {
        畀我睇下 "x 不大于 5" 點樣先?
    }
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析嵌套控制流失败: {:?}", result.err());
}

// 测试数据结构和操作
#[test]
fn test_data_structures_and_operations() {
    let source = r#"
    # 列表操作
    介紹返 numbers 係 [1, 2, 3, 4, 5]
    介紹返 first 係 numbers[0]
    介紹返 numbers[2] 係 10
    
    # 映射
    介紹返 person 係 {"name": "张三", "age": 30, "city": "香港"}
    介紹返 name 係 person["name"]
    介紹返 person["age"] 係 31
    
    # 列表操作函数
    介紹返 $ sum_list |list| 點部署
        介紹返 total 係 0
        i 喺 list => {
            介紹返 total 係 total + i
        }
        還數 total
    搞掂
    
    畀我睇下 sum_list 下 -> numbers 點樣先?
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析数据结构和操作失败: {:?}", result.err());
}

// 测试异常处理和模式匹配组合
#[test]
fn test_exception_and_pattern_matching() {
    let source = r#"
    介紹返 $ divide |a, b| 點部署
        如果 |b == 0| 嘅话 => {
            掟個 "除数不能为零" 嚟睇下?
        }
        還數 a / b
    搞掂
    
    执嘢 => {
        介紹返 result 係 divide 下 -> 10, 0
        畀我睇下 result 點樣先?
    } 揾到 e 嘅话 => {
        睇撚住 e => 
            | 撞见 "除数不能为零" => {
                畀我睇下 "处理除零错误" 點樣先?
            }
            | _ => {
                畀我睇下 "处理其他错误: " + e 點樣先?
            }
        搞掂
    }
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(
        result.is_ok(),
        "解析异常处理和模式匹配组合失败: {:?}",
        result.err()
    );
}

// 测试导入和使用
#[test]
fn test_import_and_usage() {
    let source = r#"
    # 导入模块
    使下 math::pi
    使下 utils::{format_string, parse_number}
    
    介紹返 $ calculate_area |radius| 點部署
        還數 pi * radius * radius
    搞掂
    
    介紹返 area 係 calculate_area 下 -> 5
    介紹返 formatted 係 format_string 下 -> "面积: {}", area
    畀我睇下 formatted 點樣先?
    "#;

    let ast_builder = AstBuilder::new(source);
    let result = ast_builder.parse();

    assert!(result.is_ok(), "解析导入和使用失败: {:?}", result.err());
}
