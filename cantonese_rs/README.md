# 粵語編程語言 Rust 實現 (Cantonese Programming Language Rust Implementation)

呢個項目係用 Rust 語言重寫嘅[粵語編程語言](https://github.com/StepfenShawn/Cantonese)解釋器，專注於前端部分嘅實現，包括詞法分析、語法分析、AST生成等。

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