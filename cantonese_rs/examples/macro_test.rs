use cantonese_rs::ast::position::{Position, Span};
use cantonese_rs::ast::{Expression, Statement, Program};
use cantonese_rs::parser::token_tree::{TokenKind, TokenTree, TokenStream, Delimiter, Token};
use cantonese_rs::macros::expand_macros;
use cantonese_rs::parser::ast_builder::AstBuilder;

fn main() {
    println!("粤语编程语言宏测试");
    
    // 测试宏定义和展开
    let source = r#"
/* 宏定义示例（袋仔的法寶） */

# 定义一个简单的问候宏
介紹返 sayhello 係 袋仔的法寶 =>
    | (Hello @name: str) => { 
        畀我睇下 "Hello, " + @name + "!" 點樣先?? 
    }
    | () => { 
        畀我睇下 "Hello, world!" 點樣先?? 
    }
搞掂

# 使用带参数调用宏
sayhello!(Hello "粵語編程")

# 使用无参数调用宏
sayhello!()
"#;
    
    // 构建AST
    let ast_builder = AstBuilder::new(source);
    match ast_builder.build_program() {
        Ok(program) => {
            println!("解析成功!");
            
            // 展开宏
            let expanded_program = expand_macros(program);
            println!("宏展开后的语句数量: {}", expanded_program.statements.len());
            
            // 打印展开后的程序
            for (i, stmt) in expanded_program.statements.iter().enumerate() {
                println!("语句 {}: {:?}", i, stmt);
            }
        }
        Err(e) => {
            println!("解析失败: {:?}", e);
        }
    }
    
    // 手动测试宏匹配和展开
    println!("\n手动测试宏匹配和展开:");
    manual_test_macro();
}

fn manual_test_macro() {
    // 创建一个简单的宏定义
    let macro_name = "sayhello".to_string();
    
    // 创建第一个宏匹配模式: (Hello @name:str)
    let mut pattern1 = TokenStream::new();
    let name_span = Span::new(Position::start(), Position::start());
    
    // 添加Hello标识符
    let hello_token = Token::new("Hello".to_string(), TokenKind::Identifier, name_span);
    pattern1.push(TokenTree::Token(hello_token));
    
    // 添加@name:str元变量
    let name_token = Token::new("@name:str".to_string(), TokenKind::MetaVariable, name_span);
    pattern1.push(TokenTree::Token(name_token));
    
    // 创建宏体: { 畀我睇下 "Hello, " + @name + "!" 點樣先?? }
    let mut body1 = TokenStream::new();
    
    // 添加畀我睇下标识符
    let print_token = Token::new("畀我睇下".to_string(), TokenKind::Identifier, name_span);
    body1.push(TokenTree::Token(print_token));
    
    // 添加"Hello, "字符串
    let hello_str_token = Token::new("\"Hello, \"".to_string(), TokenKind::StringLiteral, name_span);
    body1.push(TokenTree::Token(hello_str_token));
    
    // 添加+运算符
    let plus_token = Token::new("+".to_string(), TokenKind::Operator, name_span);
    body1.push(TokenTree::Token(plus_token));
    
    // 添加@name元变量引用
    let name_var_token = Token::new("@name".to_string(), TokenKind::MetaVariable, name_span);
    body1.push(TokenTree::Token(name_var_token));
    
    // 添加+运算符
    body1.push(TokenTree::Token(plus_token.clone()));
    
    // 添加"!"字符串
    let exclam_token = Token::new("\"!\"".to_string(), TokenKind::StringLiteral, name_span);
    body1.push(TokenTree::Token(exclam_token));
    
    // 添加点樣先??
    let end_token = Token::new("點樣先??".to_string(), TokenKind::Identifier, name_span);
    body1.push(TokenTree::Token(end_token));
    
    // 打印测试的TokenStream
    println!("模式TokenStream: {:?}", pattern1);
    println!("主体TokenStream: {:?}", body1);
    
    // 真正的测试应该创建一个MacroDefinition，添加到MacroExpander，
    // 然后尝试展开宏调用，但这超出了这个简单测试的范围
    println!("这是一个简单的宏示例，展示如何使用TokenStream构建宏定义和宏体。");
    println!("完整测试需要通过AST解析和宏展开来进行。");
} 