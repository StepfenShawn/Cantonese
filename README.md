![logo](img/logo.jpg)  
### Read this in other languages: [English](README-en.md)  
[![pypi](https://img.shields.io/pypi/dm/Cantonese)](https://pypi.org/project/Cantonese/)
[![pypi](https://img.shields.io/pypi/v/Cantonese)](https://pypi.org/project/Cantonese/)   
# 粵語編程語言
如果你唔識粵語或者編程，請睇[5分钟边学编程边学粤语](doc/cantonese.md)。  
### 個 Compiler 係喺我讀高中時開發嘅，所以代碼寫得好屎(宜家都係一撚樣)，歡迎各個粵語同埋編程愛好者一齊討論同貢獻！  
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
&emsp;&emsp;<a href="#11">調用 Python 庫</a>  
&emsp;&emsp;<a href="#12">面向對象編程</a>  
&emsp;&emsp;<a href="#13">棧嘅使用</a>  
<a href="#14">更多例子</a>  
&emsp;&emsp;<a href="#15">睇下時間</a>  
&emsp;&emsp;<a href="#16">暫停</a>  
&emsp;&emsp;<a href="#17">嚟個隨機數</a>  
&emsp;&emsp;<a href="#18">計相關系數</a>  
&emsp;&emsp;<a href="#19">仲可以機械學習?</a>  
&emsp;&emsp;<a href="#20">海龜畫圖</a>  
&emsp;&emsp;<a href="#21">迷宮遊戲仔</a>  
&emsp;&emsp;<a href="#22">各種排序同查找算法</a>  
&emsp;&emsp;<a href="#23">寫個網頁嚟睇下？</a>   
&emsp;&emsp;<a href="#24">用粵語開發一隻 App</a>   
<a href="#25">點樣運行?</a>  
<a href="#26">TODOs</a>  
# <a name="0">引言</a>
粵語編程語言係乜嘢? 佢係一門用粵語嚟同計算機溝通嘅編程語言。  
喺呢隻语言度，計算機可以讀明你寫嘅粵語。所以話，你可以用粵語嚟操作(虐待)計算機。
#### 所有關鍵字可以使用繁體, 或者簡體同繁體混合
# <a name="1">咋咋臨入門</a>
### <a name="2">Hello World</a>
用粵語寫嘅第一個程序 Hello World：  
```
畀我睇下「"Hello World!"」點樣先？
```
### <a name="3">賦值語句</a>
```
讲嘢:「A」系 1
讲嘢:「B」系 2
```
可以用`冇鳩用`嚟delete變量:  
```
冇鳩用: A,B
```
### <a name="4">睇下變量嘅類型</a>
```
讲嘢 「A」系 1
起底:「A」
```
運行結果：  
```
<class 'int'>
```
### <a name="5">循環</a>
打印從 1 到 100：  
```
讲嘢:「start」系 0
讲嘢:「结束」系 唔啱
落操场玩跑步
    讲嘢:「start」系「start + 1」
    畀我睇下「start」 点样先?
    如果 |start >= 100| 嘅话 -> {
        饮茶先啦
    }
玩到「结束」为止
收工
```
當然用 `For` 循環都得：  
```
「A」从 1 行到 100
    畀我睇下「A」点样先?
行晒
```
### <a name="6">條件語句</a>
```
讲嘢:「A」系 2
如果 |A 系 2| 嘅话 -> {
    畀我睇下「"A 系 2"」点样先?
}
唔系 嘅话 -> {
    畀我睇下「"A 唔系 2"」点样先?
}
```
仲可以用`match`
```
讲嘢:「状态」係 404
match下 状态 -> {
    撞见 400 -> {
        畀我睇下「"Bad request"」点样先?
    }
    撞见 404 -> {
        畀我睇下「"Not found"」点样先?
    }
}
```
### <a name="7">函数</a>
用 Cantonese 實現嘅階乘：  
```
<$> factorial 1 即係 => 1 搞掂
<$> factorial |项数| 即係 => 项数 * factorial(项数 - 1) 搞掂
```  
返回最大值：  
```
<<< int, int 收皮 :: int  >>>
$get_max |数字1, 数字2| 要做咩:
    如果 |数字1 比唔上 数字2| 嘅话 -> {
        还数「数字2」
    }
    唔系 嘅话 -> {
        还数「数字1」
    }
搞掂
```
調用函數：  
```
用下 |get_max(23, 17)|
```
函數式编程:  
```
$$ x -> |x * x| 搞掂 @ f
畀我睇下 |f(2)| 点样先?
```
運行結果：
```
4
```
### <a name="8">掟出異常</a>
```
掟个「ImportError」来睇下?
```
運行結果：
```
濑嘢: ImportError()!
```
### <a name="9">斷言語句</a>
```
谂下:「1 + 1 == 3」?
```  
運行結果：  
```
濑嘢: AssertionError()!
```
### <a name="10">錯誤捕捉語句</a>
try-except-finally:  
```
执嘢 -> {
    讲嘢: |A| 系 |B|
}
揾到「NameError」嘅话 -> {
    畀我睇下 "揾到NameError" 点样先？
}
执手尾 -> {
    畀我睇下 "执手尾" 点样先？
    讲嘢: |A| 系 1
    讲嘢: |B| 系 1
    畀我睇下 |A, B| 点样先？
}
``` 
### <a name="11">調用 Python 庫</a>
```
使下 python_os
使下 python_math
```
### <a name="12">面向對象編程</a>
聲明對象 `duck`，繼承至 `object`，分別有兩個方法 `游水` 同埋 `睡觉` ，仲有一個屬性 `性别`：  
```
咩系 |duck|?
    佢个老豆叫 |object|
    佢嘅 |性别| 系 "公"
    佢识得 |游水| -> {
        畀我睇下 "Duck is swimming" 点样先？
    }
    佢识得 |睡觉| -> {
        畀我睇下 "Duck is sleeping" 点样先？
    }
明白未啊?
```  
調用類中嘅方法：  
```
|duck()| -> |游水|: ||
|duck()| -> |睡觉|: ||
```
運行結果：  
```
Duck is swimming
Duck is sleeping
```
### <a name="13">棧嘅使用</a>
```
有条仆街叫 |Deo哥|
顶你 -> |Deo哥|: 1
顶你 -> |Deo哥|: 2
顶你 -> |Deo哥|: 3
丢你 -> |Deo哥|
```
運行結果：  
```
Stack: [1,2]
```
# <a name="14">更多例子</a>
### <a name="15">顯示當前時間</a>
```
使下 datetime
畀我睇下 |宜家几点()| 点样先？
```
運行結果：
```
2021-01-17 09:16:20.767191
```
### <a name="16">暫停</a>
```
瞓 阵先 /* 暂停2s */
瞓 5s  /* 暂停5s */
```  
### <a name="17">嚟個隨機數</a>
```
使下 随机数
讲嘢: |A| 就 |求其啦()|
```
運行結果：  
```
0.15008236307867207
```  
### <a name="18">計相關系數</a>
聲明兩個 list，計相關系數：  
```
使下 math
|2.165, 1.688, 1.651, 2.229| 拍住上 -> |A|
|2.060, 1.822, 1.834, 2.799| 拍住上 -> |B|
畀我睇下 <| A同B有几衬 |> 点样先？
```
運行結果：
```
0.8066499427138474
```
### <a name="19">仲可以机器学习?</a>
實現 KNN 算法：
```
使下 math
|[5, 1], [4, 0], [1, 3], [0, 4]| 拍住上 -> |数据|
|'动作片', '动作片', '科幻片', '科幻片'| 拍住上 -> |标签|
讲嘢: |K| 系 3
嗌 KNN 过嚟估下 -> |[3, 0]|
```
運行結果：
```
动作片
```
線性回歸：
```
使下 math
|300.0 , 400.0 , 400.0 , 550.0 , 720.0 , 850.0 , 900.0 , 950.0| 拍住上 -> |X|
|300.0 , 350.0 , 490.0 , 500.0 , 600.0 , 610.0 , 700.0 , 660.0| 拍住上 -> |Y|
嗌 L_REG 过嚟估下 -> |900.0|
```
運行結果：
```
Linear function is:
y=0.530960991635149x+189.75347155122432
667.6183640228585
```
### <a name="20">海龜繪圖</a>
```
老作一下 -> {
    首先: |画个圈(100)|
    跟住: |写隻字("Made By Cantonese\n")|
    最尾: |听我支笛()|
}
```  
運行結果：    
![turtle_result](img/turtle_etc.jpg)  

### <a name="21">迷宮遊戲仔</a>
[代碼](examples/games/game.cantonese)  
運行結果：  
![game_result](img/game_result.jpg)

### <a name="22">各種排序同查找算法</a>
* [二分查找](examples/algorithms/binary_search.cantonese)
* [线性查找](examples/algorithms/linear_search.cantonese)
* [冒泡排序](examples/algorithms/bubble_sort.cantonese)
* [插入排序](examples/algorithms/insert_sort.cantonese)

### <a name="23">寫個網頁睇下</a>
一個簡單嘅網頁：
```
老作一下 {
    打标题 => [ "我嘅第一个网页" ]
    拎笔 => [ "Hello World" ]
}
```
運行後，打開 `127.0.0.1:80` 就可以睇到運行結果：  
```
cantonese examples/web/hello_web.cantonese -to_web 
```
![web_result](img/web_result.jpg)

### <a href="#24">用粵語開發一隻 App</a>
首先安裝 `kivy`：
```
pip install kivy
```
第一隻 App `HelloWord`：  
```
使下 kivy
咩系 HelloApp?
    佢个老豆叫 App
    佢识得 |HelloWorld| -> {
        |同我show| 下 -> "Hello World" @ |做嘢|
        还数 |做嘢|
    }
明白未啊?

|App运行| 下 -> |HelloApp, HelloApp().HelloWorld|
```
![App](img/HelloApp.jpg)  

# 仲有啲咩?

[喺呢度](examples/)睇下更多例子.  

# <a name="25">点样运行?</a>
Cantonese 可以用多種方式運行，用自己嘅虛擬機，用 `LLVM`，或者翻譯成 Python 同 HTML 都得！
使用虛擬機執行（僅支援部分語句）：   
```shell
cantonese [-文件名] -stack_vm
```
查睇生產嘅指令：
```shell
cantonese [-文件名] -stack_vm -debug
```
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

# <a name="26">TODOs</a>
歡迎各個粵語同埋編程愛好者一齊討論同貢獻！為粵語文化遺產嘅保護貢獻出自己嘅一份力量!  
send PR 前請睇 [貢獻指南](./CONTRIBUTING.md)

今後要做咩：
* 加多啲語句
* 完善自己嘅虛擬機
* 完全支持`LLVM`同`JIT`

Copyright (C) 2020-2023 StepfenShawn