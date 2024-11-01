# 粤语编程语言 - Rust实现

本项目是粤语编程语言的Rust实现版本，特别着重于宏系统的设计与实现。

## 宏系统设计

粤语编程语言的宏系统受到Rust的声明宏(Declarative Macros)启发，实现了类似的模式匹配和标记替换功能。主要组件包括：

### 1. TokenTree和TokenStream

类似于Rust的`proc_macro`库，我们实现了以下核心数据结构：

- `TokenTree`: 表示单个标记或标记组，可以是：
  - `Token`: 单个基本标记，如标识符、字符串、数字等
  - `Group`: 由分隔符（括号、大括号、方括号）包围的标记流

- `TokenStream`: 表示一系列有序的TokenTree，构成了宏处理的基本单位

### 2. 宏定义与匹配

宏通过以下语法定义：

```
介紹返 宏名称 係 袋仔的法寶 =>
    | (模式1) => { 展开体1 }
    | (模式2) => { 展开体2 }
    ...
搞掂
```

其中：
- 模式可以包含普通标记和元变量（以@开头），例如 `@变量名:类型`
- 元变量类型可以是`ident`、`expr`、`str`、`block`等
- 支持重复模式，例如 `$(...)*`、`$(...)+`等

### 3. 元变量与片段匹配

每个元变量可以指定一个片段类型，例如：
- `@name:ident`: 匹配标识符
- `@expr:expr`: 匹配表达式
- `@str:str`: 匹配字符串

### 4. 宏展开

宏展开过程分为以下步骤：
1. 收集所有宏定义
2. 检测宏调用，例如 `宏名称!(参数)`
3. 将宏调用的参数解析为TokenStream
4. 尝试用宏定义中的每个模式匹配参数
5. 成功匹配后，使用捕获的元变量替换宏体中的对应引用

## 示例

### 简单问候宏

```
介紹返 sayhello 係 袋仔的法寶 =>
    | (Hello @name: str) => { 
        畀我睇下 "Hello, " + @name + "!" 點樣先?? 
    }
    | () => { 
        畀我睇下 "Hello, world!" 點樣先?? 
    }
搞掂

# 使用
sayhello!(Hello "粵語編程")  # 输出: Hello, 粵語編程!
sayhello!()  # 输出: Hello, world!
```

### 模式匹配宏

```
介紹返 計算 係 袋仔的法寶 =>
    | (同我計 @左: expr 加 @右: expr 好唔好) => { 
        @左 + @右 
    }
    | (同我計 @左: expr 减 @右: expr 好唔好) => { 
        @左 - @右 
    }
搞掂

# 使用
畀我睇下 計算!(同我計 10 加 5 好唔好) 點樣先??  # 输出: 15
畀我睇下 計算!(同我計 10 减 5 好唔好) 點樣先??  # 输出: 5
```

### 重复模式宏

```
介紹返 vec 係 袋仔的法寶 =>
    | ($(@元素:expr),*) => {
        [$(@元素)*]
    }
    | () => {
        []
    }
搞掂

# 使用
介紹返「数组」係 vec!(1, 2, 3, 4, 5)  # 创建数组 [1, 2, 3, 4, 5]
```

## 实现细节

宏系统的核心模块包括：

1. `token_tree.rs`: 定义TokenTree和TokenStream数据结构
2. `token_matcher.rs`: 实现宏模式匹配算法
3. `macro_expander.rs`: 处理宏展开和元变量替换
4. `macro_parser.rs`: 解析宏定义和调用

此外，系统还实现了以下功能：
- 错误处理和诊断
- 元变量的作用域和可见性管理
- 递归展开宏调用

## 未来计划

- 支持更复杂的模式匹配
- 实现过程宏(Procedural Macros)
- 优化宏展开性能
- 提供更丰富的诊断信息

## 特點

- 使用 Rust 語言開發，性能更高、內存安全
- 使用 pest 實現語法解析器，可以輕鬆處理複雜嘅語法規則
- 使用 ariadne 提供友好嘅錯誤信息顯示
- 提供 CLI 工具方便使用

## 安裝方法

首先確保你安裝咗 [Rust 工具鏈](https://www.rust-lang.org/tools/install)，然後運行：

```bash
git clone https://github.com/YourUsername/cantonese_rs.git
cd cantonese_rs
cargo build --release
```

## 使用方法

### 解析粵語程序並顯示語法樹

```bash
cargo run --release -- parse examples/hello.cantonese
```

以 JSON 格式輸出語法樹：

```bash
cargo run --release -- parse examples/hello.cantonese --json
```

### 檢查粵語程序語法

```bash
cargo run --release -- check examples/hello.cantonese
```

### 運行粵語程序 (開發中)

```bash
cargo run --release -- run examples/hello.cantonese
```

## 開發進度

- [x] 詞法分析器 (使用 pest)
- [x] 語法分析器 (使用 pest)
- [x] AST 構建
- [x] 錯誤報告
- [ ] 語義分析
- [ ] 解釋器實現
- [ ] Python 轉換器

## 貢獻指南

歡迎各位粵語同編程愛好者一齊參與開發！可以通過以下方式貢獻：

1. 提交 Issue 報告問題或建議新功能
2. 提交 Pull Request 改進代碼
3. 完善文檔和示例

## 授權協議

本項目遵循 MIT 授權協議。 