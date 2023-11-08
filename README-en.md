![logo](img/logo.jpg)  
[![pypi](https://img.shields.io/pypi/dm/Cantonese)](https://pypi.org/project/Cantonese/)
[![pypi](https://img.shields.io/pypi/v/Cantonese)](https://pypi.org/project/Cantonese/) 
# The Cantonese programming language
If you don't know Cantonese or programming, please see [learn Cantonese while learning programming in 5 minutes](doc/cantonese.md)
# Installation
```
pip install Cantonese
```
# Introduction
<a href="#0">What is Cantonese?</a>  
<a href="#1">Quick Start</a>  
&emsp;&emsp;<a href="#2">Hello World</a>  
&emsp;&emsp;<a href="#3">Assignment statement </a>  
&emsp;&emsp;<a href="#4">Get the type of variable</a>  
&emsp;&emsp;<a href="#5">Loop</a>  
&emsp;&emsp;<a href="#6">If statement</a>  
&emsp;&emsp;<a href="#7">Function</a>  
&emsp;&emsp;<a href="#8">Throw exception</a>  
&emsp;&emsp;<a href="#9">Assertion statement</a>  
&emsp;&emsp;<a href="#10">Catch statement</a>  
&emsp;&emsp;<a href="#11">Call python library</a>  
&emsp;&emsp;<a href="#12">object-oriented programming</a>  
&emsp;&emsp;<a href="#13">Stack</a>  
<a href="#14">More examples</a>  
&emsp;&emsp;<a href="#15">Get the time</a>  
&emsp;&emsp;<a href="#16">Sleep</a>  
&emsp;&emsp;<a href="#17">Get the random number</a>  
&emsp;&emsp;<a href="#18">Calculate the  correlation coefficient</a>  
&emsp;&emsp;<a href="#19">Machine learning</a>  
&emsp;&emsp;<a href="#20">Turtle drawing</a>  
&emsp;&emsp;<a href="#21">Maze game</a>  
&emsp;&emsp;<a href="#22">Various sorting and searching algorithms</a>  
&emsp;&emsp;<a href="#23">Website design</a>   
&emsp;&emsp;<a href="#24">Develop an app in Cantonese</a>   
<a href="#25">How to run?</a>  
<a href="#26">TODOs</a>  
# <a name="0">What is Cantonese programming language?</a>
What is the cantonese programming language? It is a programming language that communicates with computers in [Cantonese](https://en.wikipedia.org/wiki/Cantonese).      
The computer can read the Cantonese you write and you can operate (abuse) the computer in Cantonese.

# <a name="1">Quick Start</a>
### <a name="2">Hello World</a>
The first program written in Cantonese: `Hello World`:  
```
畀我睇下 " Hello World! " 点样先?
```
### <a name="3">Assignment statement </a>
```
讲嘢 |A| 系 1
讲嘢 |B| 系 2
```
### <a name="4">Get the type of variable</a>
```
讲嘢 |A| 系 1
起底: |A|
```
You will get:  
```
<class 'int'>
```
### <a name="5">Loop</a>
Print numbers from 1 to 100:  
```
讲嘢: |start| 系 0
讲嘢: |结束| 系 唔啱
落操场玩跑步
    讲嘢: |start| 系 |start + 1|
    畀我睇下 |start| 点样先?
    如果 |start >= 100| 嘅话 -> {
        饮茶先啦
    }
玩到 |结束| 为止
收工
```
You can also use `For` Loop:  
```
|A| 从 1 行到 100
    畀我睇下 |A| 点样先?
行晒
```
### <a name="6">If statement</a>
```
讲嘢: |A| 系 2
如果 |A 系 2| 嘅话 -> {
    畀我睇下 "A 系 2" 点样先?
}
唔系 嘅话 -> {
    畀我睇下 "A 唔系 2" 点样先?
}
```
### <a name="7">Function</a>
Factorial algorithm in Cantonese:  
```
$factorial |项数| 要做咩:
    如果 |项数 系 0| 嘅话 -> {
        还数 1
    }
    唔系 嘅话 -> {
        还数 |factorial(项数 减 1) 乘 项数|
    }
搞掂
```  
Get the max value:  
```
$get_max |数字1, 数字2| 要做咩:
    如果 |数字1 比唔上 数字2| 嘅话 -> {
        还数 |数字2|
    }
    唔系 嘅话 -> {
        还数 |数字1|
    }
搞掂
```
Call the function:  
```
用下 |get_max(23, 17)|
```
### <a name="8">Throw exception</a>
```
掟个 |ImportError| 嚟睇下?
```
You will get:
```
濑嘢: ImportError()!
```
### <a name="9">Assertion statement</a>
```
谂下: |1 + 1 == 3| ?
```  
You will get:  
```
濑嘢: AssertionError()!
```
### <a name="10">Catch statement</a>
try-except-finally:  
```
执嘢 -> {
    讲嘢: |A| 系 |B|
}
揾到 |NameError| 嘅话 -> {
    畀我睇下 "揾到NameError" 点样先？
}
执手尾 -> {
    畀我睇下 "执手尾" 点样先？
    讲嘢: |A| 系 1
    讲嘢: |B| 系 1
    畀我睇下 |A, B| 点样先？
}
``` 
### <a name="11">Call Python library</a>
```
使下 os
使下 math
```
### <a name="12">object-oriented programming</a>
Declare object `duck` and extend from `object`, define two methods:  `游水` and `睡觉`, and attribute: `性别`
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
Call the methods which in class:  
```
|duck()| -> |游水|: ||
|duck()| -> |睡觉|: ||
```
You will get:  
```
Duck is swimming
Duck is sleeping
```
### <a name="13">Stack</a>
```
有条仆街叫 |Deo哥|
顶你 -> |Deo哥|: 1
顶你 -> |Deo哥|: 2
顶你 -> |Deo哥|: 3
丢你 -> |Deo哥|
```
You will get:  
```
Stack: [1,2]
```
# <a name="14">More examples</a>
### <a name="15">Get the time</a>
```
使下 datetime
畀我睇下 |宜家几点()| 点样先？
```
You will get:  
```
2021-01-17 09:16:20.767191
```
### <a name="16">Sleep</a>
```
瞓阵先 /* 暂停2s */
瞓 5s /* 暂停5s */
```  
### <a name="17">Get the random number</a>
```
使下 random
讲嘢: |A| 就 |求其啦()|
```
You will get:  
```
0.15008236307867207
```  
### <a name="18">Calculate the correlation coefficient</a>
Define two list and calculate the correlation coefficient:  
```
使下 math
|2.165, 1.688, 1.651, 2.229| 拍住上 -> |A|
|2.060, 1.822, 1.834, 2.799| 拍住上 -> |B|
畀我睇下 |A同B有几衬| 点样先？
```
You will get:  
```
0.8066499427138474
```
### <a name="19">Machine learning</a>
KNN algorithm in Cantonese:
```
使下 math
|[5, 1], [4, 0], [1, 3], [0, 4]| 拍住上 -> |数据|
|'动作片', '动作片', '科幻片', '科幻片'| 拍住上 -> |标签|
讲嘢: |K| 系 3
嗌 KNN 过嚟估下 -> |[3, 0]|
```
You will get:
```
动作片
```
Linear regression:  
```
使下 math
|300.0 , 400.0 , 400.0 , 550.0 , 720.0 , 850.0 , 900.0 , 950.0| 拍住上 -> |X|
|300.0 , 350.0 , 490.0 , 500.0 , 600.0 , 610.0 , 700.0 , 660.0| 拍住上 -> |Y|
嗌 L_REG 过嚟估下 -> |900.0|
```
You will get:
```
Linear function is:
y=0.530960991635149x+189.75347155122432
667.6183640228585
```
### <a name="20">Turtle drawing</a>
```
老作一下 -> {
    首先: |画个圈(100)|
    跟住: |写隻字("Made By Cantonese\n")|
    最尾: |听我支笛()|
}
```  
You will get:    
![turtle_result](img/turtle_etc.jpg)  

### <a name="21">Maze game </a>
[Code](examples/games/game.cantonese)  
You will get:  
![game_result](img/game_result.jpg)

### <a name="22">Various sorting and searching algorithms</a>
* [Binary Search](examples/algorithms/binary_search.cantonese)
* [Linear Search](examples/algorithms/linear_search.cantonese)
* [Bubble Sort](examples/algorithms/bubble_sort.cantonese)
* [Insert Sort](examples/algorithms/insert_sort.cantonese)

### <a name="23">A simple web page</a>
This is a simple web page:
```
老作一下 {
    打标题 => [ "我嘅第一个网页" ]
    拎笔 => [ "Hello World" ]
}
```
After running, open '127.0.0.1:80' to view the running results:  
```
python src/cantonese.py ../examples/web/hello_web.cantonese -to_web 
```
![web_result](img/web_result.jpg)

### <a href="#24">Develop an app in Cantonese</a>
At first, you need install `kivy`:
```
pip install kivy
```
The first App `HelloWord` in Cantonese:  
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

# More?

[Here](examples/) you can see more examples.  

# <a name="25">How to run?</a>
The Cantonese language runs on the python virtual machine, and the environment supports Python 3, because it conforms to the advanced ideas of the Cantonese! 
```shell
python src/cantonese.py [-filename]
```
Convert Cantonese to Python:  
```shell
python src/cantonese.py [-filename]] -to_py
```
For example:  
```
python src/cantonese.py examples/basic/helloworld.cantonese -to_py
```
You will get:  
```
print(" Hello World! ")
exit()
```
It can also generate `HTML` code:  
```shell
python src/cantonese.py examples/web/web_hello.cantonese -to_web -compile
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
Run in traditional Chinese:
```
python src/cantonese.py [-filename] -use_tr
```  
Vscode plus for Cantonese:  https://github.com/Cantonese-community/vscode-cantonese  

# <a name="26">TODOs</a>
All cantonese or programming lovers are welcome to discuss and contribute together! Contribute to the protection of Cantonese cultural heritage!
TODOs:   
* Improve and perfect the syntax error checking
* Add more statements
* Improve own virtual machine
