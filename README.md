<img src="img/logo.jpg" width="300px">

### Read this in other languages: [English](README-en.md)  
[![pypi](https://img.shields.io/pypi/dm/Cantonese)](https://pypi.org/project/Cantonese/)
[![pypi](https://img.shields.io/pypi/v/Cantonese)](https://pypi.org/project/Cantonese/)   
# 粵語編程語言
想快速入門，請睇[5分鐘學識粵語編程](doc/cantonese.md).  
#### 個 Compiler 大部份係喺我高中时期開發嘅，so the code like a shit(宜家都一樣)，歡迎各個粵語或編程愛好者一齊討論同貢獻！  
# 點樣安裝?
```
pip install Cantonese
```
# 目錄
<a href="#0">引言</a>  
<a href="#1">咋咋淋臨入門</a>  
&emsp;&emsp;<a href="#2">Hello World</a>  
&emsp;&emsp;<a href="#3">賦值語句 </a>  
&emsp;&emsp;<a href="#4">睇下變量嘅類型</a>  
&emsp;&emsp;<a href="#5">循環</a>  
&emsp;&emsp;<a href="#6">條件語句</a>  
&emsp;&emsp;<a href="#7">函數</a>  
&emsp;&emsp;<a href="#8">掟出異常</a>  
&emsp;&emsp;<a href="#9">斷言語句</a>  
&emsp;&emsp;<a href="#10">錯誤捕捉語句</a>  
&emsp;&emsp;<a href="#11">調用庫</a>  
&emsp;&emsp;<a href="#12">面向對象編程</a>  
&emsp;&emsp;<a href="#13">棧嘅使用</a>  
&emsp;&emsp;<a href="#14">袋仔的法寶: 用`Macro`定义自己嘅语法</a>  
<a href="#15">更多例子</a>  
&emsp;&emsp;<a href="#16">睇下時間</a>  
&emsp;&emsp;<a href="#17">暫停</a>  
&emsp;&emsp;<a href="#18">嚟個隨機數</a>  
&emsp;&emsp;<a href="#19">計相關係數</a>  
&emsp;&emsp;<a href="#20">仲可以機械學習?</a>  
&emsp;&emsp;<a href="#21">海龜畫圖</a>  
&emsp;&emsp;<a href="#22">迷宮遊戲仔</a>  
&emsp;&emsp;<a href="#23">各種排序同查找算法</a>  
&emsp;&emsp;<a href="#24">寫個網頁嚟睇下？</a>   
&emsp;&emsp;<a href="#25">用粵語開發一隻 App</a>   
&emsp;&emsp;<a href="#26">數據庫編程都得???(開發緊)</a>  
<a href="#25">點樣運行?</a>  
<a href="#26">TODOs</a>  
# <a name="0">引言</a>
粵語編程語言係乜? 佢係一門用粵語嚟同計算機溝通嘅編程語言。  
喺呢隻语言度，計算機可以讀明你寫嘅粵語。所以話，你可以用粵語嚟操作或虐待計算機。
#### 所有關鍵字可以使用繁體, 或者簡體同繁體混合
# <a name="1">咋咋臨入門</a>
### <a name="2">Hello World</a>
用粵語寫嘅第一個程序 Hello World：  
```Rust
畀我睇下「"Hello World!"」點樣先？
```
### <a name="3">賦值語句</a>
```Rust
介紹返「A」係 1
介紹返「B」係 2
```
或者: 
```Rust
介紹返 =>
    「A」係 1
    「B」係 2
先啦
```
可以用`冇鳩用`或者`冇撚用`嚟delete變量:  
```Rust
冇鳩用 A,B
```
### <a name="4">睇下變量嘅類型</a>
```Rust
介紹返「A」係 1
起底「A」
```
運行結果：  
```
<class 'int'>
```
### <a name="5">循環</a>
打印從 1 到 100, 其中`飲茶先啦`相當於break, `Hea陣先`相當於Continue：  
```Rust
介紹返 =>
    「start」係 0
    「结束」係 唔啱
先啦
落操场玩跑步
    介紹返「start」係「start + 1」
    畀我睇下「start」 點樣先??
    如果 |start >= 100| 嘅话 => {
        飲茶先啦
    }
    Hea陣先
玩到「结束」为止
收工
```
當然用 `For` 循環都得：  
```Rust
「A」从 1 行到 100
    畀我睇下「A」點樣先??
到步
```
### <a name="6">條件語句</a>
```Rust
介紹返「A」係 2
如果 |A 係 2| 嘅话 => {
    畀我睇下「"A 係 2"」點樣先??
}
唔係 嘅话 => {
    畀我睇下「"A 唔係 2"」點樣先??
}
```
仲可以用`match`
```Rust
介紹返 状态 係 404
睇撚住 状态 =>
    | 撞见 400 => { 畀我睇下 "Bad request" 點樣先?? }
    | 撞见 401 => { 畀我睇下 "Unauthorized" 點樣先?? }
    | 撞见 403 => { 畀我睇下 "Forbidden" 點樣先?? }
    | 撞见 404 => { 畀我睇下 "Not found" 點樣先?? }
    | 撞见 418 => { 畀我睇下 "I'm a teapot" 點樣先?? }
    | _ => { 畀我睇下 "乜都唔係" 點樣先?? }
搞掂
```
### <a name="7">函数</a>
返回最大值： 
```Rust
介紹返 $get_max
    |数字1, 数字2| 點部署
        如果 |数字1 比唔上 数字2| 嘅话 => {
            还数「数字2」
        }
        唔係 嘅话 => {
            还数「数字1」
        }
    搞掂
```
調用函數：  
```Rust
介紹返 結果 係 
    get_max 下 -> 23, 17
畀我睇下 結果 點樣先??
```
函數式编程:  
```Rust
畀我睇下 
    |$$ x, y { x + y } 下 -> (2, 2)| 
點樣先??
```
運行結果：
```
4
```
### <a name="8">掟出異常</a>
```Rust
掟个「ImportError」嚟睇下?
```
運行結果：
```
濑嘢!!!: ImportError:
 喺runtime察覺到錯誤!
 --> ../examples/basic/raise.cantonese 4:0
  | 掟个 |ImportError| 嚟睇下?
    ^^^^^^^^^^^^^^^^^^^^^^^^^^ Tips:  幫緊你只不過有心無力:(

:D 不如跟住我嘅tips繼續符碌下?
```
### <a name="9">斷言語句</a>
```Rust
諗下「1 + 1 == 3」?
```  
運行結果：  
```
濑嘢!!!: AssertionError:
 喺runtime察覺到錯誤!
 --> ../examples/basic/assert.cantonese 6:0
  | 諗下 |1 - 1 == 1| ?
    ^^^^^^^^^^^^^^^^^^^^ Tips:  幫緊你只不過有心無力:(

:D 不如跟住我嘅tips繼續符碌下?
```
### <a name="10">錯誤捕捉語句</a>
try-except-finally:  
```Rust
执嘢 => {
    介紹返 |A| 係 |B|
}
揾到「NameError」嘅话 => {
    畀我睇下 "揾到NameError" 點樣先？
}
执手尾 => {
    畀我睇下 "执手尾" 點樣先？
    介紹返 |A| 係 1
    介紹返 |B| 係 1
    畀我睇下 |A, B| 點樣先？
}
``` 
### <a name="11">調用庫</a>
調用 Python 庫:  
```Rust
使下 py::os::*
使下 py::math::*
使下 py::{re::*, pandas}
```
調用 Python 代碼:  
```Rust
我係二五仔 #XD
def add(a, b):
    return a + b
二五仔係我

畀我睇下 |add 下 -> (8, 2)| 點樣先 /* 輸出10 */
```
又或者使用`Macro`調用`Python`和`Rust`:  
```rust
{% std::macros::{Py, Rust} %}

Py!(
def add(a, b):
    return a + b
)
畀我睇下 |add 下 -> (8, 2)| 點樣先

介紹返 add 係 Rust!(
    fn add(a: i32, b: i32) -> i32 {
        a + b
    }
)
畀我睇下 |add 下 -> (8, 2)| 點樣先
```
### <a name="12">面向對象編程</a>
聲明對象 `duck`，繼承至 `object`，分別有兩個方法 `游水` 同埋 `睡觉` ，仲有一個屬性 `性别`：  
```Rust
介紹返 duck 係 乜X {
    佢個老豆叫 object
    佢有啲咩?? => {
        性别: 公家嘢,
        年龄: 私家嘢
    }
    佢識得 游下水 |自己| => {
        畀我睇下 "Duck is swimming" 點樣先??
    }
    佢識得 睡下觉 |自己| => {
        畀我睇下 "Duck is sleeping" 點樣先??
    } 
}
```
創建object:  
```Rust
介紹返 myduck 係 阿->duck(性别="公")
```
調用對象中嘅方法, 两總方式任你揀：   
```Rust
myduck -> 游下水() 啦!
好心 |myduck -> 睡下觉| 啦!
```
運行結果：  
```
Duck is swimming
Duck is sleeping
```

### <a name="13">棧嘅使用</a>
首先創建一個Stack:  
```Rust
有條仆街叫 |Deo哥|
```
或者用返賦值嘅方式:   
```Rust
介紹返 Deo哥 係 條仆街仔()
```
進行操作:  
```Rust
顶你 => |Deo哥| 1
顶你 => |Deo哥| 2
顶你 => |Deo哥| 3
丢你 => |Deo哥|
```
運行結果：  
```
Stack: [1,2]
```
### <a name="14">袋仔的法寶: 用`Macro`定义自己嘅语法</a>
介紹咗咁多, `Cantonese`仲將類似於`Rust`入面嘅宏定義引入, 可以通過宏來擴展我哋嘅語法, 簡單啲講, 就相當於`match`語句, 匹配之後用`@`提取元變量喺編譯期間進行替換:    
```Rust
介紹返 sayhello 係 袋仔的法寶 =>
    | (Hello @s: str) => { 畀我睇下 "Hello " + @s 點樣先?? }
    | () => { 畀我睇下 "Hello" 點樣先?? }
搞掂

sayhello!(Hello "dd")
sayhello!()
sayhello!(1) # 報錯: 無法匹配

介紹返 vec 係 袋仔的法寶 =>
    | ($(@element:expr),*) => {
        [$(@element)*]
    }
    | () => {
        []
    }
搞掂

畀我睇下 vec!("Hello", 1+1, "gg",) 點樣先?? # ['Hello', 2, 'gg']
畀我睇下 vec!() 點樣先?? # []
```
複雜啲嘅例子, 定义新嘅语法:`同我计 XX 乜 XX 好唔好`:  
```Rust
介紹返 計算 係 袋仔的法寶 =>
    | (同我計 @左: lit 加 @右: lit 好唔好) => { 
        @左 + @右 }
    | (同我計 @左: lit 减 @右: lit 好唔好) => { 
        @左 - @右 }
    | (同我計 @左: lit 除 @右: lit 好唔好) => { 
        @左 / @右 }
    | (同我計 @左: lit 乘 @右: lit 好唔好) => { 
        @左 * @右 }
搞掂

畀我睇下 
    計算!(同我計 1 加 2 好唔好) 
點樣先?? # 3

畀我睇下 
    計算!(同我計 2 乘 2 好唔好) 
點樣先?? # 4
```  
標準庫嘅`macro`定義喺晒[依度](can_source/can_libs/std/macros)  

# <a name="15">更多例子</a>
### <a name="16">顯示當前時間</a>
```Rust
使下 std::日期
畀我睇下 |宜家几点()| 點樣先？
```
運行結果：
```
2021-01-17 09:16:20.767191
```
### <a name="17">暫停</a>
```Rust
使下 std::time::瞓

瞓 -> 阵先 啦 /* 暂停2s */
瞓 -> "5s" 啦/* 暂停5s */
```  
### <a name="18">嚟個隨機數</a>
```Rust
使下 std::随机数
介紹返 |A| 係 |求其啦()|
```
運行結果：  
```
0.15008236307867207
```  
### <a name="19">計相關係數</a>
聲明兩個 list，計相關係數：  
```Rust
{% std::macros::math %}
使下 py::math

|[2.165, 1.688, 1.651, 2.229]| 拍住上 => |A|
|[2.060, 1.822, 1.834, 2.799]| 拍住上 => |B|
畀我睇下 秘诀!(A 同 B 有幾襯) 點樣先？
```
運行結果：
```
0.8066499427138474
```
### <a name="20">仲可以机器学习?</a>
首先要搞清楚樣嘢, 喺源代碼`can_libs/macros/math.cantonese`入面, 其實定義咗一個`macro`, 負責簡單地替換函數調用同埋輸出結果:    
```rust
介紹返 过嚟估下 係 袋仔的法寶 =>
    | (@model: id => $(@args: expr),*) => {
        畀我睇下 @model(${@args},*) 點樣先??
    }
    | () => { None }
搞掂
```
前面講過`macro`只係簡單地包裝咗一層語法, 咁我哋可以用`过嚟估下`宏定義去調用底層嘅算法函數喇!  
實現 KNN 算法：
```Rust
{% std::macros::math %}

使下 py::math

|[[5, 1], [4, 0], [1, 3], [0, 4]]| 拍住上 => |数据|
|['动作片', '动作片', '科幻片', '科幻片']| 拍住上 => |标签|
介紹返 |K| 係 3
过嚟估下!(KNN => |[3, 0]|, 数据, 标签, K)
```
運行結果：
```
动作片
```
線性回歸：
```Rust
{% std::macros::math %}

使下 py::math

|[300.0 , 400.0 , 400.0 , 550.0 , 720.0 , 850.0 , 900.0 , 950.0]| 拍住上 => |X|
|[300.0 , 350.0 , 490.0 , 500.0 , 600.0 , 610.0 , 700.0 , 660.0]| 拍住上 => |Y|
过嚟估下!(L_REG => |900.0|, X, Y,)
```
運行結果：
```
Linear function is:
y=0.530960991635149x+189.75347155122432
667.6183640228585
```
### <a name="21">海龜繪圖</a>
```Rust
{% std::macros::ui %}

使下 py::turtle

老作一下!(
    首先 |画个圈(100)|,
    跟住 |写隻字("Made By Cantonese\n", False,'center')|,
    最尾 |听我支笛()|,
)
```  
運行結果：    
<img src="img/turtle_etc.jpg" width="300px">

### <a name="22">迷宮遊戲仔</a>
[代碼](examples/games/game.cantonese)  
運行結果：  
<img src="img/game_result.jpg" width="300px">

### <a name="23">各種排序同查找算法</a>
* [二分查找](examples/algorithms/binary_search.cantonese)
* [线性查找](examples/algorithms/linear_search.cantonese)
* [冒泡排序](examples/algorithms/bubble_sort.cantonese)
* [插入排序](examples/algorithms/insert_sort.cantonese)

### <a name="24">寫個網頁睇下</a>
一個簡單嘅網頁：
```Rust
{% std::macros::net %}
使下 std::net::监视;

介紹返 html 係 HTML老作一下! (
    打标题 => [ "我嘅第一个网页" ]
    拎笔 => [ "Hello World" ]
)

监视 下 -> |html, "127.0.0.1", 80| 啦
```
運行後，打開 `127.0.0.1:80` 就可以睇到運行結果：  
<img src="img/web_result.jpg" width="300px">

### <a href="#25">用粵語開發一隻 App</a>
首先安裝 `kivy`：
```
pip install kivy
```
第一隻 App `HelloWord`：  
```Rust
使下 py::kivy

介紹返 HelloApp 係 乜X {
    佢個老豆叫 App
    佢識得 HelloWorld |自己| => {
        |同我show| 下 -> "Hello World" 就係 |做嘢|
        还数 |做嘢|
    }
}

App运行 下 -> |HelloApp, HelloApp()->HelloWorld| 啦
```
<img src="img/HelloApp.jpg" width="300px">

### <a href="#26">數據庫編程都得(開發緊)</a>
select語句:
```Rust
使下 macros::sql::*;

SQL!{
喺 成績表 度揾 學生哥 邊個 (年紀 大于 10 同埋 名字 係 'dany');

喺 成績表 度揾 最尾 10 个 學生哥;
喺 成績表 度揾 排頭 20 个 學生哥; 
}
/* select * from xx  */
SQL{
    睇下 xx;
}
```

# 仲有啲咩?

[喺呢度](examples/)睇下更多例子.  
所有關鍵字: https://github.com/Cantonese-community/Keywords  

# <a name="27">点样运行?</a>
查看當前版本:  
```shell
cantonese -v
```
如果發覺輸出怪怪地, 咁啱又喺 windows, 咁請先用管理員身份運行指令嚟支援ANSI颜色顯示:    
```cmd
reg add HKCU\Console /v VirtualTerminalLevel /t REG_DWORD /d 1
```
Cantonese 可以用多種方式運行，用 `LLVM`，或者翻譯成 Python 同 HTML 都得！
使用`LLVM`執行 (需安装`llvmlite`同`clang`, 僅支援部分語句):  
```shell
cantonese [-文件名] -llvm
```
用 Python 虛擬機運行（環境净係支援 Python3，因为噉先至符合廣東人先進嘅思想！）：
```shell
cantonese [-文件名]
```
將 Cantonese 轉化成 Python：
```shell
cantonese [文件名] -to_py
```
例如：  
```
cantonese examples/basic/helloworld.cantonese -to_py
```
運行嘅結果係：  
```python
print(" Hello World! ")
exit()
```
生成 HTML：  
```shell
cantonese examples/web/web_hello.cantonese -to_web -compile
```
```html
<html>
<head>
<meta charset="utf-8" />
</head>
<title>我嘅第一个网页</title>
<h1>Hello World</h1>
</html>
```
Vscode插件：https://github.com/Cantonese-community/vscode-cantonese  

# <a name="27">TODOs</a>
歡迎各個粵語同埋編程愛好者一齊討論同貢獻！為粵語文化遺產嘅保護貢獻出自己嘅一份力量!  
send PR 前請睇 [貢獻指南](./CONTRIBUTING.md)

今後要做咩：
* 用D设计模式重构下
* 完善自己嘅虛擬機
* 完全支持`LLVM`同`JIT`

Copyright (C) 2020-2024 StepfenShawn