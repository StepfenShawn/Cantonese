//! 粤语编程语言语法解析测试

extern crate cantonese_rs;
use cantonese_rs::parser::ast_builder::AstBuilder;
use std::fs;
use std::path::Path;

// 辅助函数，测试文件是否可以被成功解析
fn test_parse_file(file_path: &str) {
    let source =
        fs::read_to_string(file_path).unwrap_or_else(|_| panic!("无法读取文件: {}", file_path));

    let ast_builder = AstBuilder::new(&source);
    let result = ast_builder.parse();

    assert!(
        result.is_ok(),
        "解析文件 {} 失败: {:?}",
        file_path,
        result.err()
    );
}

#[test]
fn test_hello_world() {
    test_parse_file("examples/basic/HelloWorld.cantonese");
}

#[test]
fn test_assignment() {
    test_parse_file("examples/basic/assign.cantonese");
}

#[test]
fn test_assertion() {
    test_parse_file("examples/basic/assert.cantonese");
}

#[test]
fn test_class() {
    test_parse_file("examples/basic/class.cantonese");
}

#[test]
fn test_call_python() {
    test_parse_file("examples/basic/call_python.cantonese");
}

#[test]
fn test_comment() {
    test_parse_file("examples/basic/comment.cantonese");
}

#[test]
fn test_exit() {
    test_parse_file("examples/basic/exit.cantonese");
}

#[test]
fn test_for() {
    test_parse_file("examples/basic/for.cantonese");
}

#[test]
fn test_function() {
    test_parse_file("examples/basic/function.cantonese");
}

#[test]
fn test_if() {
    test_parse_file("examples/basic/if.cantonese");
}

#[test]
fn test_import() {
    test_parse_file("examples/basic/import.cantonese");
}

#[test]
fn test_input() {
    test_parse_file("examples/basic/input.cantonese");
}

#[test]
fn test_lambda() {
    test_parse_file("examples/basic/lambda.cantonese");
}

#[test]
fn test_list() {
    test_parse_file("examples/basic/list.cantonese");
}

#[test]
fn test_match() {
    test_parse_file("examples/basic/match.cantonese");
}

#[test]
fn test_raise() {
    test_parse_file("examples/basic/raise.cantonese");
}

#[test]
fn test_set() {
    test_parse_file("examples/basic/set.cantonese");
}

#[test]
fn test_try_finally() {
    test_parse_file("examples/basic/try_finally.cantonese");
}

#[test]
fn test_type() {
    test_parse_file("examples/basic/type.cantonese");
}

#[test]
fn test_while() {
    test_parse_file("examples/basic/while.cantonese");
}

// 批量测试所有基本示例文件
#[test]
fn test_all_basic_examples() {
    use std::fs;

    let basic_dir = Path::new("examples/basic");
    assert!(basic_dir.exists(), "基本示例目录不存在");

    let entries = fs::read_dir(basic_dir).expect("无法读取基本示例目录");

    let mut test_count = 0;

    for entry in entries {
        let entry = entry.expect("无法读取目录条目");
        let path = entry.path();

        if path.is_file() && path.extension().map_or(false, |ext| ext == "cantonese") {
            test_parse_file(path.to_str().unwrap());
            test_count += 1;
        }
    }

    assert!(test_count > 0, "未找到任何 .cantonese 文件进行测试");
    println!("成功测试了 {} 个基本示例文件", test_count);
}
