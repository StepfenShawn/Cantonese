"""
    Created at 2021/1/16 16:23
    The interpreter for Cantonese    
"""
import cmd
import re
import sys
import os
import argparse
from 濑嘢 import 濑啲咩嘢
from stack_vm import *
from can_lexer import *
import can_parser

_version_ = "Cantonese 1.0.3 Copyright (C) 2020-2023 StepfenShawn"

def cantonese_token(code : str, keywords : str) -> list:
    lex = lexer(code, keywords)
    tokens = []
    while True:
        token = lex.get_token()
        tokens.append(token)
        if token[1] == [TokenType.EOF, 'EOF']:
            break
    return tokens

"""
    Built-in library for Cantonese
"""
def cantonese_lib_import(name : str) -> None:
    if name == "random" or name == "随机数":
        cantonese_random_init()
        return "random"
    elif name == "datetime" or name == "日期":
        cantonese_datetime_init()
        return "datetime"
    elif name == "math" or name == "数学":
        cantonese_math_init()
        return "math"
    elif name == "smtplib" or name == "邮箱":
        cantonese_smtplib_init()
        return "smtplib"
    elif name == "xml" or name == "xml解析":
        cantonese_xml_init()
        return "xml"
    elif name == "csv" or name == "csv解析":
        cantonese_csv_init()
        return "csv"
    elif name == "os" or name == "系统":
        return "os"
    elif name == "re" or name == "正则匹配":
        cantonese_re_init()
        return "re"
    elif name == "urllib" or name == "网页获取":
        cantonese_urllib_init()
        return "urllib"
    elif name == "requests" or name == "网络请求":
        cantonese_requests_init()
        return "requests"
    elif name == "socket" or name == "网络连接":
        cantonese_socket_init()
        return "socket"
    elif name == "kivy" or name == "手机程式":
        cantonese_kivy_init()
        return "kivy"
    elif name == "pygame" or name == "游戏":
        cantonese_pygame_init()
        return "pygame"
    elif name == "json" or name == "json解析":
        cantonese_json_init()
        return "json"
    elif name == "numpy" or name == "数值计算":
        cantonese_numpy_init()
        return "numpy"
    elif name[ : 7] == "python-":
        return name[7 : ]
    else:
        return "Not found"

def cantonese_lib_init() -> None:
    def cantonese_open(file, 模式 = 'r', 解码 = None):
        return open(file, mode = 模式, encoding = 解码)

    def cantonese_close(file) -> None:
        file.close()

    def out_name(file) -> None:
        print(file.name)

    def out_ctx(file, size = None) -> None:
        if size == None:
            print(file.read())
            return
        print(file.read(size))

    def get_name(file) -> str:
        return file.name

    def cantonese_read(file, size = None) -> str:
        if size == None:
            return file.read()
        return file.read(size)
    
    cantonese_func_def("开份文件", cantonese_open)
    cantonese_func_def("关咗佢", cantonese_close)
    cantonese_func_def("睇睇文件名", out_name)
    cantonese_func_def("睇睇有咩", out_ctx)
    cantonese_func_def("文件名", get_name)
    cantonese_func_def("读取", cantonese_read)

    def get_list_end(lst : list):
        return lst[-1]

    def get_list_beg(lst : list):
        return lst[0]

    def where(lst : list, index : int, index2 = None, index3 = None, index4 = None):
        if index2 != None and index3 == None and index4 == None:
            return lst[index][index2]
        if index3 != None and index2 != None and index4 == None:
            return lst[index][index2][index3]
        if index4 != None and index2 != None and index3 != None:
            return lst[index][index2][index3][index4]
        return lst[index]
    
    def lst_insert(lst : list, index : int, obj) -> None:
        lst.insert(index, obj)

    def list_get(lst : list, index : int):
        return lst[index]

    def lst_range(lst : list, range_lst : list, loss, types = 1, func = None, func_ret = None) -> bool:
        if types == 2:
            for i in lst:
                if i - loss <= range_lst and i + loss >= range_lst:
                    return True

        else:
            for i in lst:
                if i[0] - loss <= range_lst[0] and i[1] + loss >= range_lst[1]:
                    return True  


    cantonese_func_def("最尾", get_list_end)
    cantonese_func_def("身位", where)
    cantonese_func_def("挜位", lst_insert)
    cantonese_func_def("排头位", get_list_beg)
    cantonese_func_def("摞位", list_get)
    cantonese_func_def("check范围", lst_range)

    cantonese_func_def("唔啱", False)
    cantonese_func_def("啱", True)

def cantonese_json_init() -> None:
    import json

    def json_load(text):
        return json.loads(text)

    def show_json_load(text):
        print(json.loads(text))
    
    cantonese_func_def("睇下json", show_json_load)
    cantonese_func_def("读取json", json_load)

def cantonese_csv_init() -> None:
    import csv

    def out_csv_read(file):
        for i in csv.reader(file):
            print(i)
    
    def get_csv(file):
        ret = []
        for i in csv.reader(file):
            ret.append(i)
        return i

    cantonese_func_def("睇睇csv有咩", out_csv_read)
    cantonese_func_def("读取csv", get_csv)

def cantonese_random_init() -> None:
    import random
    cantonese_func_def("求其啦", random.random)
    cantonese_func_def("求其int下啦", random.randint)
    cantonese_func_def("求其嚟个", random.randrange)
    cantonese_func_def("是但拣", random.choice)

def cantonese_datetime_init() -> None:
    import datetime
    cantonese_func_def("宜家几点", datetime.datetime.now)

def cantonese_xml_init() -> None:
    from xml.dom.minidom import parse
    import xml.dom.minidom
    
    def make_dom(file) -> None:
        return xml.dom.minidom.parse(file).documentElement

    def has_attr(docelm, attr) -> bool:
        return docelm.hasAttribute(attr)

    def get_attr(docelm, attr):
        print(docelm.getAttribute(attr))
    
    def getElementsByTag(docelm, tag : str, out = None, ctx = None):
        if out == 1:
            print(docelm.getElementsByTagName(tag))
        if ctx != None:
            print(ctx + docelm.getElementsByTagName(tag)[0].childNodes[0].data)
        return docelm.getElementsByTagName(tag)

    cantonese_func_def("整樖Dom树", make_dom)
    cantonese_func_def("Dom有嘢", has_attr)
    cantonese_func_def("睇Dom有咩", get_attr)
    cantonese_func_def("用Tag揾", getElementsByTag)
    cantonese_func_def("用Tag揾嘅", getElementsByTag)

def cantonese_turtle_init() -> None:
    import turtle
    cantonese_func_def("画个圈", turtle.circle)
    cantonese_func_def("写隻字", turtle.write)
    cantonese_func_def("听我支笛", turtle.exitonclick)

def cantonese_smtplib_init() -> None:
    import smtplib
    def send(sender : str, receivers : str,  message : str, 
             smtpObj = smtplib.SMTP('localhost')) -> None:
        try:
            smtpObj.sendmail(sender, receivers, message)         
            print("Successfully sent email!")
        except Exception:
            print("Error: unable to send email")
    cantonese_func_def("send份邮件", send)

def cantonese_stack_init() -> None:
    class _stack(object):
        def __init__(self):
            self.stack = []
        def __str__(self):
            return 'Stack: ' + str(self.stack)
        def push(self, value):
            self.stack.append(value)
        def pop(self):
            if self.stack:
                return self.stack.pop()
            else:
                raise LookupError('stack 畀你丢空咗!')
    cantonese_func_def("stack", _stack)
    cantonese_func_def("我丢", _stack.pop)
    cantonese_func_def("我顶", _stack.push)

def cantonese_func_def(func_name : str, func) -> None:
    variable[func_name] = func

def cantonese_math_init():
    import math
    class Matrix(object):
        def __init__(self, list_a):
            assert isinstance(list_a, list)
            self.matrix = list_a
            self.shape = (len(list_a), len(list_a[0]))
            self.row = self.shape[0]
            self.column = self.shape[1]
        
        def __str__(self):
            return 'Matrix: ' + str(self.matrix)

        def build_zero_value_matrix(self, shape):
            zero_value_mat = []
            for i in range(shape[0]):
                zero_value_mat.append([])
                for j in range(shape[1]):
                    zero_value_mat[i].append(0)
            zero_value_matrix = Matrix(zero_value_mat)
            return zero_value_matrix

        def matrix_addition(self, the_second_mat):
            assert isinstance(the_second_mat, Matrix)
            assert the_second_mat.shape == self.shape
            result_mat = self.build_zero_value_matrix(self.shape)
            for i in range(self.row):
                for j in range(self.column):
                    result_mat.matrix[i][j] = self.matrix[i][j] + the_second_mat.matrix[i][j]
            return result_mat

        def matrix_multiplication(self, the_second_mat):
            assert isinstance(the_second_mat, Matrix)
            assert self.shape[1] == the_second_mat.shape[0]
            shape = (self.shape[0], the_second_mat.shape[1])
            result_mat = self.build_zero_value_matrix(shape)
            for i in range(self.shape[0]):
                for j in range(the_second_mat.shape[1]):
                    number = 0
                    for k in range(self.shape[1]):
                        number += self.matrix[i][k] * the_second_mat.matrix[k][j]
                    result_mat.matrix[i][j] = number
            return result_mat
    
    def corr(a, b):
        if len(a) == 0 or len(b) == 0:
            return None
        a_avg = sum(a) / len(a)
        b_avg = sum(b) / len(b)
        cov_ab = sum([(x - a_avg) * (y - b_avg) for x, y in zip(a, b)])
        sq = math.sqrt(sum([(x - a_avg) ** 2 for x in a]) * sum([(x - b_avg) ** 2 for x in b]))
        corr_factor = cov_ab / sq
        return corr_factor

    def KNN(inX, dataSet, labels, k):
        m, n = len(dataSet), len(dataSet[0])
        distances = []
        for i in range(m):
            sum = 0
            for j in range(n):
                sum += (inX[j] - dataSet[i][j]) ** 2
            distances.append(sum ** 0.5)
        sortDist = sorted(distances)
        classCount = {}
        for i in range(k):
            voteLabel = labels[distances.index(sortDist[i])]
            classCount[voteLabel] = classCount.get(voteLabel, 0) + 1
        sortedClass = sorted(classCount.items(), key = lambda d : d[1], reverse = True)
        return sortedClass[0][0]
    
    def l_reg(testX, X, Y):
        a = b = mxy = sum_x = sum_y = lxy = xiSubSqr = 0.0
        for i in range(len(X)):
            sum_x += X[i]
            sum_y += Y[i]
        x_ave = sum_x / len(X)
        y_ave = sum_y / len(X)
        for i in range(len(X)):
            lxy += (X[i] - x_ave) * (Y[i] - y_ave)
            xiSubSqr += (X[i] - x_ave) * (X[i] - x_ave)
        b = lxy / xiSubSqr
        a = y_ave - b * x_ave
        print("Linear function is:")
        print("y=" + str(b) + "x+"+ str(a))
        return b * testX + a

    cantonese_func_def("KNN", KNN)
    cantonese_func_def("l_reg", l_reg)
    cantonese_func_def("corr", corr)
    cantonese_func_def("矩阵", Matrix)
    cantonese_func_def("点积", Matrix.matrix_multiplication)
    cantonese_func_def("开根", math.sqrt)
    cantonese_func_def("绝对值", math.fabs)
    cantonese_func_def("正弦", math.sin)
    cantonese_func_def("余弦", math.cos)
    cantonese_func_def("正切", math.tan)
    cantonese_func_def("PI", math.pi)
    cantonese_func_def("E", math.e)
    cantonese_func_def("+oo", math.inf)

def cantonese_model_new(model, datatest, tab, code) -> str:
    if model == "KNN":
        code += tab + "print(KNN(" + datatest + ", 数据, 标签, K))"
    elif model == "L_REG":
        code += tab + "print(l_reg(" + datatest + ", X, Y))"
    else:
        print("揾唔到你嘅模型: " + model + "!")
        code = ""
    return code

def cantonese_re_init() -> None:
    def can_re_match(pattern : str, string : str, flags = 0):
        return re.match(pattern, string, flags)
    
    def can_re_match_out(pattern : str, string : str, flags = 0) -> None:
        print(re.match(pattern, string, flags).span())

    cantonese_func_def("衬", can_re_match_out)
    cantonese_func_def("衬唔衬", can_re_match)

def cantonese_urllib_init() -> None:
    import urllib.request
    def can_urlopen_out(url : str) -> None:
        print(urllib.request.urlopen(url).read())

    def can_urlopen(url : str):
        return urllib.request.urlopen(url)

    cantonese_func_def("睇网页", can_urlopen_out)
    cantonese_func_def("揾网页", can_urlopen)

def cantonese_requests_init() -> None:
    import requests

    def req_get(url : str, data = "", json = False):
        headers = {
            'user-agent':
    'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36' \
        }
        if data != "":
            headers.update(data)
        res = requests.get(url, headers)
        res.encoding = 'utf-8'
        if json:
            return res.json()
        return res.text

    cantonese_func_def("𠯠求", req_get)

def cantonese_socket_init() -> None:
    import socket

    def s_new():
        return socket.socket() 

    def s_connect(s, port, host = socket.gethostname()):
        s.connect((host, port))
        return s
    
    def s_recv(s, i : int):
        return s.recv(i)
    
    def s_close(s) -> None:
        s.close()

    cantonese_func_def("倾偈", s_connect)
    cantonese_func_def("收风", s_recv)
    cantonese_func_def("通电话", s_new)
    cantonese_func_def("收线", s_close)

def cantonese_kivy_init() -> None:
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.boxlayout import BoxLayout

    def app_show(ctx, 宽 = (.5, .5), 
        高 = {"center_x": .5, "center_y": .5}) -> None:
        return Label(text = ctx, size_hint = 宽, pos_hint = 高)

    def app_run(app_main, build_func) -> None:
        print("The app is running ...")
        def build(self):
            return build_func()
        app_main.build = build
        app_main().run()

    def app_button(ctx, 宽 = (.5, .5), 
        高 = {"center_x": .5, "center_y": .5}) -> None:
        return Button(text = ctx, size_hint = 宽, pos_hint = 高)

    def app_layout(types, 布局 = "", 方向 = 'vertical', 间距 = 15, 内边距 = 10):
        if 布局 ==  "":
            if types == "Box":
                return BoxLayout(orientation = 方向, 
                spacing = 间距, padding = 内边距)
        else:
            for i in types.stack:
                布局.add_widget(i)
    
    def button_bind(btn, func) -> None:
        btn.bind(on_press = func)

    cantonese_func_def("App", App)
    cantonese_func_def("Label", Label)
    cantonese_func_def("Button", Button)
    cantonese_func_def("App运行", app_run)
    cantonese_func_def("同我show", app_show)
    cantonese_func_def("开掣", app_button)
    cantonese_func_def("老作", app_layout)
    cantonese_func_def("睇实佢", button_bind)

def cantonese_pygame_init() -> None:
    
    import pygame
    import math
    import random
    from pygame.constants import KEYDOWN

    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    def pygame_setmode(size, caption = ""):
        if caption != "":
            pygame.display.set_caption(caption)
            return pygame.display.set_mode(size, 0, 32)
        return pygame.display.set_mode(size, 0, 32)

    def pygame_imgload(path, color = ""):
        img = pygame.image.load(path).convert_alpha()
        if color != "":
            img.set_colorkey((color),pygame.RLEACCEL)
        return img

    def pygame_musicload(path, loop = True, start = 0.0):
        pygame.mixer.music.load(path)
        if loop:
            pygame.mixer.music.play(-1, start)
        else:
            pygame.mixer.music.play(1, start)

    def pygame_soundload(path):
        return pygame.mixer.Sound(path)
    
    def pygame_sound_play(sound):
        sound.play()

    def pygame_sound_stop(sound):
        sound.stop()

    def pygame_move(object, speed):
        return object.move(speed)

    def object_rect(object, center = ""):
        if center == "":
            return object.get_rect()
        return object.get_rect(center = center)

    def pygame_color(color):
        return pygame.Color(color)

    def pygame_key(e):
        return e.key

    def draw(屏幕, obj = "", obj_where = "", event = "", 颜色 = "", 位置 = "") -> None:
        if event == "":
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    sys.exit()
        else:
            event_map = {
                "KEYDOWN" : KEYDOWN
            }
            for events in pygame.event.get():
                for my_ev in event.stack:
                    if events.type == event_map[my_ev[0]]:
                        my_ev[1](events)
                    if events.type == pygame.QUIT: 
                        sys.exit()
        if 颜色 != "":
            屏幕.fill(颜色)
        if obj != "" and obj_where != "":
            屏幕.blit(obj, obj_where)

        pygame.time.delay(2)

    def exec_event(event):
        event_map = {
                "KEYDOWN" : KEYDOWN
            }
        for events in pygame.event.get():
            for my_ev in event.stack:
                if events.type == event_map[my_ev[0]]:
                    my_ev[1](events)
                if events.type == pygame.QUIT: 
                    sys.exit()

    def direction(obj, dir):
        if dir == "左边" or dir == "left":
            return obj.left
        if dir == "右边" or dir == "right":
            return obj.right
        if dir == "上边" or dir == "top":
            return obj.top
        if dir == "下边" or dir == "bottom":
            return obj.bottom

    def time_tick(clock_obj, t):
        clock_obj.tick(t)

    def pygame_rectload(屏幕, 颜色, X, Y, H = 20, W = 20):
        pygame.draw.rect(屏幕, 颜色, pygame.Rect(X, Y, H, W))

    def pygame_gif_show(屏幕, 序列, pos = (0, 0), delay = 100):
        for i in 序列:
            屏幕.blit(i, pos)
            pygame.time.delay(delay)
            pygame.display.update()

    def text_objects(text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    def pygame_text_show(screen, text, display_x, display_y,
                         style = 'freesansbold.ttf', _delay = 100, size = 115,
                         color = (255,255,255), update = True):
        largeText = pygame.font.Font(style, size)
        TextSurf, TextRect = text_objects(text, largeText, color)
        TextRect.center = (display_x, display_y)
        screen.blit(TextSurf, TextRect)
        pygame.time.delay(_delay)
        if update:
            pygame.display.update()

    def screen_fill(screen, color):
        screen.fill(color)

    def img_show(screen, img, where):
        screen.blit(img, where)

    def sprite_add(group, sprite):
        group.add(sprite)

    def sprite_update(group, ticks):
        group.update(ticks)

    def sprite_draw(group, screen):
        group.draw(screen)

    def sprite_kill(sprite):
        sprite.kill()

    def sprite_trace(target, tracer, type = "", speed = 3, speed_y = 16, speed_x = 16):
        """
        x1, y1 = tracer.x, tracer.y
        x2, y2 = target[0], target[1] # TODO use target.x
        dx = x2 - x1
        dy = y1 - y2
        r = math.sqrt(math.pow(dx,2) + math.pow(dy,2))
        if r == 0:
            r = 0.1
        sin = dy / r
        cos = dx / r
        x1 += cos * speed
        y1 -= sin * speed
        """
        if type == "Linear":
            dx, dy = target[0] - tracer.x, target[1] - tracer.y
            dist = math.hypot(dx, dy) + 0.1
            dx, dy = dx / dist, dy / dist  # Normalize.
            # Move along this normalized vector towards the player at current speed.
            """
            tracer.x += dx * speed
            tracer.y += dy * speed
            """
            return (dx * speed, dy * speed)
    """
        display_width : width of the screen
        display_height : height of the screen
    """

    class Button(object):
        def __init__(self, text, color, screen,
                    display_width = 1200, display_height = 600, 
                     x = None, y = None, size = 58, **kwargs):
            font = pygame.font.Font('freesansbold.ttf', size)
            self.surface = text_objects(text, font, color)[0]
            self.WIDTH = self.surface.get_width()
            self.HEIGHT = self.surface.get_height()
            self.screen = screen
            self.display_width = display_width
            self.display_height = display_height
            self.x = x
            self.y = y

        def display(self):
            self.screen.blit(self.surface, (self.x, self.y))

        # For Chinese API
        def 老作(self):
            self.screen.blit(self.surface, (self.x, self.y))

        def check_click(self, position):
            x_match = position[0] > self.x and position[0] < self.x + self.WIDTH
            y_match = position[1] > self.y and position[1] < self.y + self.HEIGHT

            if x_match and y_match:
                return True
            else:
                return False
        
        def 点击(self, position):
            return self.check_click(position)

    cantonese_func_def("屏幕老作", pygame_setmode)
    cantonese_func_def("图片老作", pygame_imgload)
    cantonese_func_def("动图老作", pygame_gif_show)
    cantonese_func_def("矩形老作", pygame_rectload)
    cantonese_func_def("嚟个矩形", pygame.Rect)
    cantonese_func_def("嚟个按钮", Button)
    cantonese_func_def("写隻字", pygame_text_show)
    cantonese_func_def("嚟首music", pygame_musicload)
    cantonese_func_def("嚟首sound", pygame_soundload)
    cantonese_func_def("播放", pygame_sound_play)
    cantonese_func_def("暂停", pygame_sound_stop)
    cantonese_func_def("画图片", img_show)
    cantonese_func_def("玩跑步", pygame_move)
    cantonese_func_def("in边", object_rect)
    cantonese_func_def("上画", draw)
    cantonese_func_def("揾位", direction)
    cantonese_func_def("画公仔", sprite_draw)
    cantonese_func_def("刷新公仔", sprite_update)
    cantonese_func_def("摞公仔", sprite_kill)
    cantonese_func_def("公仔", pygame.sprite.Sprite)
    cantonese_func_def("公仔集", pygame.sprite.Group)
    cantonese_func_def("睇下撞未", pygame.sprite.collide_rect)
    cantonese_func_def("嚟个公仔", sprite_add)
    cantonese_func_def("跟踪", sprite_trace)
    cantonese_func_def("计时器", pygame.time.Clock)
    cantonese_func_def("睇表", time_tick)
    cantonese_func_def("延时", pygame.time.delay)
    cantonese_func_def("校色", pygame_color)
    cantonese_func_def("屏幕校色", screen_fill)
    cantonese_func_def("摞掣", pygame_key)
    cantonese_func_def("check下鼠标", pygame.mouse.get_pos)
    cantonese_func_def("check下点击", pygame.mouse.get_pressed)
    cantonese_func_def("刷新", pygame.display.flip)
    cantonese_func_def("事件驱动", exec_event)
    cantonese_func_def("Say拜拜", pygame.quit)

def cantonese_numpy_init() -> None:
    pass

def cantonese_lib_run(lib_name : str, path : str) -> None:
    pa = os.path.dirname(path) # Return the last file Path
    tokens = []
    code = ""
    found = False
    for dirpath,dirnames,files in os.walk(pa):
        if lib_name + '.cantonese' in files:
            code = open(pa + '/' + lib_name + '.cantonese', encoding = 'utf-8').read()
            code = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', code)
            found = True
    if found == False:
        raise ImportError(lib_name + '.cantonese not found.')
    
    for token in cantonese_token(code, keywords):
        tokens.append(token)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    run(cantonese_parser.Node, path = path)

dump_ast = False
dump_lex = False
to_js = False
to_cpp = False
_S = False
mkfile = False

class Codegen(object):
    def __init__(self, nodes : list, path : str):
        self.nodes = nodes
        self.path = path
        self.tab = ''

    def codegen_expr(self, exp) -> str:
        if isinstance(exp, can_parser.can_ast.StringExp):
            return exp.s
        
        elif isinstance(exp, can_parser.can_ast.NumeralExp):
            return exp.val
        
        elif isinstance(exp, can_parser.can_ast.IdExp):
            return exp.name

        elif isinstance(exp, can_parser.can_ast.FalseExp):
            return "False"
        
        elif isinstance(exp, can_parser.can_ast.TrueExp):
            return "True"
        
        elif isinstance(exp, can_parser.can_ast.NullExp):
            return "None"

        elif isinstance(exp, can_parser.can_ast.BinopExp):
            return '(' + self.codegen_expr(exp.exp1) + exp.op + self.codegen_expr(exp.exp2) + ')'

        elif isinstance(exp, can_parser.can_ast.ObjectAccessExp):
            return self.codegen_expr(exp.prefix_exp) + '.' + self.codegen_expr(exp.key_exp)

        elif isinstance(exp, can_parser.can_ast.ListAccessExp):
            return self.codegen_expr(exp.prefix_exp) + '[' + self.codegen_expr(exp.key_exp) + ']'
        
        elif isinstance(exp, can_parser.can_ast.UnopExp):
            return '(' + exp.op + ' ' + self.codegen_expr(exp.exp) + ')'
        
        elif isinstance(exp, can_parser.can_ast.FuncCallExp):
            return self.codegen_expr(exp.prefix_exp) + '(' + self.codegen_args(exp.args) + ')'

        elif isinstance(exp, can_parser.can_ast.LambdaExp):
            return ' lambda ' + self.codegen_args(exp.id_list) + ' : ' + self.codegen_args(exp.blocks)

        elif isinstance(exp, can_parser.can_ast.ListExp):
            s = '['
            for elem in exp.elem_exps:
                s += self.codegen_expr(elem) + ', '
            s = s[ : -2] + ']'
            return s

        elif isinstance(exp, can_parser.can_ast.ClassSelfExp):
            s = 'self.' + self.codegen_expr(exp.exp)
            return s

        else:
            return ''

    def codegen_args(self, args : list) -> str:
        s = ''
        for arg in args:
            s += ', ' + self.codegen_expr(arg)
        return s[2 : ]

    def codegen_method_args(self, args : list) -> str:
        s = ''
        for arg in args:
            s += ', ' + self.codegen_expr(arg)
        return "self, " + s[2 : ]

    def codegen_varlist(self, lst : list) -> str:
        s = ''
        for l in lst:
            s += ', ' + self.codegen_expr(l)
        return s[2 : ]

    def codegen_stat(self, stat):
        if isinstance(stat, can_parser.can_ast.PrintStat):
            return self.tab + 'print(' + self.codegen_args(stat.args) + ')\n'
        
        elif isinstance(stat, can_parser.can_ast.AssignStat):
            return self.tab + self.codegen_varlist(stat.var_list) + ' = ' + self.codegen_args(stat.exp_list) + '\n'

        elif isinstance(stat, can_parser.can_ast.ExitStat):
            return self.tab + 'exit()\n'

        elif isinstance(stat, can_parser.can_ast.PassStat):
            return self.tab + 'pass\n'

        elif isinstance(stat, can_parser.can_ast.BreakStat):
            return self.tab + 'break\n'

        elif isinstance(stat, can_parser.can_ast.IfStat):
            s = ''
            s += self.tab + 'if ' + self.codegen_expr(stat.if_exp) + ':\n'
            s += self.codegen_block(stat.if_block)
            
            for i in range(len(stat.elif_exps)):
                s += self.tab + 'elif ' + self.codegen_expr(stat.elif_exps[i]) + ':\n'
                s += self.codegen_block(stat.elif_blocks[i])

            if len(stat.else_blocks):
                s += self.tab + 'else:\n'
                s += self.codegen_block(stat.else_blocks)
            
            return s

        elif isinstance(stat, can_parser.can_ast.TryStat):
            s = ''
            s += self.tab + 'try: \n'
            s += self.codegen_block(stat.try_blocks)

            for i in range(len(stat.except_exps)):
                s += self.tab + 'except ' + self.codegen_expr(stat.except_exps[i]) + ':\n'
                s += self.codegen_block(stat.except_blocks[i])

            if len(stat.finally_blocks):
                s += self.tab + 'finally:\n'
                s += self.codegen_block(stat.finally_blocks)

            return s

        elif isinstance(stat, can_parser.can_ast.RaiseStat):
            s = ''
            s += self.tab + 'raise ' + self.codegen_expr(stat.name_exp) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.WhileStat):
            s = ''
            s += self.tab + 'while not ' + self.codegen_expr(stat.cond_exp) + ':\n'
            s += self.codegen_block(stat.blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.ForStat):
            s = ''
            s += self.tab + 'for ' + self.codegen_expr(stat.var) + ' in range('+ self.codegen_expr(stat.from_exp) \
                        + ', ' + self.codegen_expr(stat.to_exp) + '):\n'
            s += self.codegen_block(stat.blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.FunctoinDefStat):
            s = ''
            s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + self.codegen_args(stat.args) + '):\n'
            s += self.codegen_block(stat.blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.FuncCallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.func_name) + '(' + self.codegen_args(stat.args) + ')' + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.ImportStat):
            return self.tab + 'import ' + self.codegen_args(stat.idlist) + '\n'

        elif isinstance(stat, can_parser.can_ast.ReturnStat):
            s = ''
            s += self.tab + 'return ' + self.codegen_args(stat.exps) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.DelStat):
            s = ''
            s += self.tab + 'del ' + self.codegen_args(stat.exps) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.TypeStat):
            s = ''
            s += self.tab + 'print(type(' + self.codegen_expr(stat.exps) + '))\n'
            return s

        elif isinstance(stat, can_parser.can_ast.AssertStat):
            s = ''
            s += self.tab + 'assert ' + self.codegen_expr(stat.exps) + '\n'
            return s

        elif isinstance(stat, can_parser.can_ast.ClassDefStat):
            s = ''
            s += self.tab + 'class ' + self.codegen_expr(stat.class_name) + '(' + self.codegen_args(stat.class_extend) + '):\n'
            s += self.codegen_block(stat.class_blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.MethodDefStat):
            s = ''
            s += self.tab + 'def ' + self.codegen_expr(stat.name_exp) + '(' + self.codegen_method_args(stat.args) + '):\n'
            s += self.codegen_block(stat.class_blocks)
            return s

        elif isinstance(stat, can_parser.can_ast.MethodCallStat):
            s = ''
            s += self.tab + self.codegen_expr(stat.name_exp) + '.' + self.codegen_expr(stat.method) + \
                 '(' + self.codegen_args(stat.args) + ')\n'
            return s

    def codegen_block(self, blocks):
        save = self.tab
        self.tab += '\t'
        s = ''
        for block in blocks:
            s += self.codegen_stat(block)
        self.tab = save
        return s

variable = {}
def cantonese_run(code : str, is_to_py : bool, file : str, 
                    REPL = False, get_py_code = False) -> None:
    
    global dump_ast
    global dump_lex
    global TO_PY_CODE
    tokens = cantonese_token(code, keywords)

    stats = can_parser.StatParser(tokens).parse_stats()
    code_gen = Codegen(stats, file)
    code = ''
    for stat in stats:
        code += code_gen.codegen_stat(stat)


    exec(code, variable)
    # TODO: update for v1.0.3
    
    if dump_lex:
        for token in tokens:
            print("line " + str(token[0]) + ": " + str(token[1]))

    if dump_ast:
        for stat in stats:
            print(stat)
    if to_js:
        """TODO:
        import Compile
        js, fh = Compile.Compile(cantonese_parser.Node, "js", file).ret()
        f = open(fh, 'w', encoding = 'utf-8')
        f.write(js)
        sys.exit(1)
        """
        pass
    if _S:
        """ TODO:
        import Compile
        code, fh = Compile.Compile(cantonese_parser.Node, "asm", file).ret()
        # f = open(fh, 'w', encoding = 'utf-8')
        # f.write(code)
        print(code)
        sys.exit(1)
        """
    """
    run(cantonese_parser.Node, path = file)
    
    cantonese_lib_init()
    """
    if is_to_py:
        print(TO_PY_CODE)

    if mkfile:
        f = open(file[: len(file) - 10] + '.py', 'w', encoding = 'utf-8')
        f.write("###########################################\n")
        f.write("#        Generated by Cantonese           #\n")
        f.write("###########################################\n")
        f.write("# Run it by " + "'cantonese " + file[: len(file) - 10] + '.py' + " -build' \n")
        f.write(TO_PY_CODE)
    """
    if debug:
        import dis
        print(dis.dis(TO_PY_CODE))
    else:
        import traceback
        try:
            c = TO_PY_CODE
            if REPL:
                TO_PY_CODE = "" # reset the global variable in REPL mode
            if get_py_code:
                return c
            exec(TO_PY_CODE, variable)
        except Exception as e:
            print("濑嘢!" + "\n".join(濑啲咩嘢(e)))
    """
class AST(object):
    def __init__(self, Nodes) -> None:
        self.Nodes = Nodes

    def next(self, n) -> None:
        self.Nodes = self.Nodes[n : ]

    def current(self):
        if len(self.Nodes) == 0:
            return [""]
        return self.Nodes[0]

    def check(self, node, v) -> bool:
        return node[0] == v

    def run_if(self):
        elif_part = [[], [], []]
        else_part = [[], []]
        if self.current()[0] == 'node_elif':
            elif_part = self.current()
            self.next(1)
        elif self.current()[0] == 'node_else':
            else_part = self.current()
            self.next(1)
        return elif_part, else_part

    def run_except(self):
        # ["node_except", _except, except_part]
        except_part = [[], [], []]
        finally_part = [[], []]
        if self.current()[0] == 'node_except':
            except_part = self.current()
            self.next(1)
        elif self.current()[0] == 'node_finally':
            except_part = self.current()
            self.next(1)
        return except_part.finally_part


    def get_node(self) -> list:
        
        if len(self.Nodes) == 0:
            return "NODE_END"

        node = self.Nodes[0]
        
        if node[0] == 'node_print':
            self.next(1)
            return PrintStmt(node[1])

        if node[0] == 'node_let':
            self.next(1)
            return AssignStmt(node[1][1], node[2])

        if node[0] == 'node_exit':
            self.next(1)
            return ExitStmt()

        if node[0] == 'node_pass':
            self.next(1)
            return PassStmt()

        if node[0] == 'node_if':
            self.next(1)
            elif_part, else_part = self.run_if()
            return IfStmt([node[1], node[2]], [elif_part[1], elif_part[2]], \
                         [else_part[1]])

        if node[0] == 'node_try':
            self.next(1)
            except_part, finally_part = self.run_except()
            return ExceptStmt([node[1]], [except_part[1], except_part[2]], \
                            [finally_part[1]])

        if node[0] == 'node_call':
            self.next(1)
            return

        if node[0] == 'node_for':
            self.next(1)
            return ForStmt(node[1], node[2], node[3])

        if node[0] == 'node_gettype':
            self.next(1)
            return TypeStmt(node[1])

        if node[0] == 'node_loop':
            self.next(1)
            return WhileStmt(node[1], node[2])

        if node[0] == 'node_break':
            self.next(1)
            return BreakStmt()

        if node[0] == 'node_raise':
            self.next(1)
            return RaiseStmt(node[1])
        

        raise Exception("睇唔明嘅Node: " + str(node))

def make_stmt(Nodes : list, stmts : list) -> list:
    ast = AST(Nodes)
    # Get stmt from AST
    while True:
        stmt = ast.get_node()
        if stmt == "NODE_END":
            break
        stmts.append(stmt)
    return stmts

class PrintStmt(object):
    def __init__(self, expr) -> None:
        self.expr = expr
        self.type = "PrintStmt"

    def __str__(self):
        ret = "print_stmt: " + self.expr

class AssignStmt(object):
    def __init__(self, key, value) -> None:
        self.key = key
        self.value = value
        self.type = "AssignStmt"
    
class PassStmt(object):
    def __init__(self):
        self.type = "PassStmt"

class ExitStmt(object):
    def __init__(self):
        self.type = "ExitStmt"

    def __str__(self):
        return "exit_stmt"

class TypeStmt(object):
    def __init__(self, var):
        self.type = "TypeStmt"
        self.var = var

class IfStmt(object):
    def __init__(self, if_stmt, elif_stmt, else_stmt) -> None:
        self.if_stmt = if_stmt
        self.elif_stmt = elif_stmt
        self.else_stmt = else_stmt
        self.type = "IfStmt"

    def __str__(self):
        ret = "if_stmt:" + str(self.if_stmt) + \
              "elif_stmt:" + str(self.elif_stmt) + \
              "else_stmt: " + str(self.else_stmt)
        return ret

class ForStmt(object):
    def __init__(self, _iter, seq, stmt) -> None:
        self._iter = _iter
        self.seq = seq
        self.stmt = stmt
        self.type = "ForStmt"

class WhileStmt(object):
    def __init__(self, cond, stmt) -> None:
        self.cond = cond
        self.stmt = stmt
        self.type = "WhileStmt"

class BreakStmt(object):
    def __init__(self):
        self.type = "BreakStmt"

class CallStmt(object):
    def __init__(self, func, args) -> None:
        self.type = "CallStmt"

class ExceptStmt(object):
    def __init__(self, try_part, except_part, finally_part) -> None:
        self.type = "ExceptStmt"
        self.try_part = try_part
        self.except_part = except_part
        self.finally_part = finally_part

class RaiseStmt(object):
    def __init__(self, exception) -> None:
        self.type = "RaiseStmt"
        self.exception = exception

ins_idx = 0 # 指令索引
cansts_idx = 0
name_idx = 0
debug = False

def cantonese_run_with_vm(code : str, file : bool) -> None:
    tokens = []
    for token in cantonese_token(code, keywords):
        tokens.append(token)
    cantonese_parser = Parser(tokens, [])
    cantonese_parser.parse()
    if dump_ast:
        print(cantonese_parser.Node)
    if dump_lex:
        print(tokens)
    gen_op_code = []
    stmt = make_stmt(cantonese_parser.Node, [])
    run_with_vm(stmt, gen_op_code, True, path = file)
    code = Code()
    code.ins_lst = gen_op_code
    if debug:
        for j in gen_op_code:
            print(j)
    cs = CanState(code)
    cs._run()
    
def run_with_vm(stmts : list, gen_op_code, end, path = '', state = []) -> None:
    
    global ins_idx

    for stmt in stmts:
        if stmt.type == "PrintStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.expr))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_PRINT_ITEM", None))
        
        if stmt.type == "AssignStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.value))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NEW_NAME", stmt.key))

        if stmt.type == "PassStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_NOP", None))

        if stmt.type == "IfStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.if_stmt[0]))
            s = make_stmt(stmt.if_stmt[1], [])
            # 先将要跳转的地址设置为None
            ins_idx += 1
            start_idx = ins_idx
            gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_FALSE", None))
            run_with_vm(s, gen_op_code, False, path)
            
            # TODO: need test elif stmt
            if stmt.elif_stmt != [[], []]:
                gen_op_code[start_idx - 1].set_args(ins_idx + 1)
                ins_idx += 1
                jmp_start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", None))
                ins_idx += 1
                gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST",  stmt.elif_stmt[0]))
                s = make_stmt(stmt.elif_stmt[1], [])
                ins_idx += 1
                start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_FALSE", None))
                run_with_vm(s, gen_op_code, False, path)
                gen_op_code[jmp_start_idx - 1].set_args(ins_idx - jmp_start_idx)

            elif stmt.else_stmt != [[]]:
                gen_op_code[start_idx - 1].set_args(ins_idx + 1)
                ins_idx += 1
                s = make_stmt(stmt.else_stmt[0], [])
                jmp_start_idx = ins_idx
                gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", None))
                run_with_vm(s, gen_op_code, False, path)
                gen_op_code[jmp_start_idx - 1].set_args(ins_idx - jmp_start_idx)

            else:
                gen_op_code[start_idx - 1].set_args(ins_idx)
        
        if stmt.type == "ForStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", 
                    stmt.seq[stmt.seq.index("(") + 1 : stmt.seq.index(",")]))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", 
                    stmt.seq[stmt.seq.index(",") + 1 : stmt.seq.index(")")]))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_CALL_FUNC", "range"))

        if stmt.type == "TypeStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.var))
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_CALL_FUNC", "type"))
            

        if stmt.type == "WhileStmt":
            current_idx = ins_idx
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_LOAD_CONST", stmt.cond))
            s = make_stmt(stmt.stmt, [])
            ins_idx += 1
            start_idx = ins_idx
            gen_op_code.append(Instruction(ins_idx, "OP_POP_JMP_IF_TRUE", None))
            run_with_vm(s, gen_op_code, False, path)
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_JMP_ABSOLUTE", current_idx))
            gen_op_code[start_idx - 1].set_args(ins_idx)

        if stmt.type == "BreakStmt":
            ins_idx += 1
            # TODO: implement the break stmt
            gen_op_code.append(Instruction(ins_idx, "OP_JMP_FORWARD", 1))

        if stmt.type == "RaiseStmt":
            ins_idx += 1
            gen_op_code.append(Instruction(ins_idx, "OP_RAISE", eval(stmt.exception[1])))

    if end:
        ins_idx += 1
        gen_op_code.append(Instruction(ins_idx, "OP_RETURN", None)) # 结尾指令


class WebParser(object):
    def __init__(self, tokens : list, Node : list) -> None:
        self.tokens = tokens
        self.pos = 0
        self.Node = Node

    def get(self, offset : int) -> list:
        if self.pos + offset >= len(self.tokens):
            return ["", ""]
        return self.tokens[self.pos + offset]
        
    def match(self, name : str) -> bool:
        if self.get(0)[1] == name:
            return True
        return False
    
    def match_type(self, name : str) -> bool:
        if self.get(0)[0] == name:
            return True
        return False
    
    def check(self, a, b) -> None:
        if a == b:
            return
        raise LookupError("Error Token:" + str(b))

    def skip(self, offset) -> None:
            self.pos += offset
    
    def run(self, Nodes : list) -> None:
        for node in Nodes:
            if node[0] == "node_call":
                web_call_new(node[1][0], node[1][1], node[2])
            if node[0] == "node_css":
                style_def(node[1][0], node[1][1], node[1][2])
        
    def parse(self) -> None:
        while True:
            if self.match("老作一下"):
                self.skip(1)
                self.check(self.get(0)[1], "{")
                self.skip(1)
                stmt = []
                node_main = []
                while self.tokens[self.pos][1] != "}":
                    stmt.append(self.tokens[self.pos])
                    self.pos += 1
                self.skip(1)
                WebParser(stmt, node_main).parse()
                self.Node = node_main
                self.run(self.Node)
            elif self.match_type("id"):
                if self.get(1)[0] == "keywords" and self.get(1)[1] == "要点画":
                    id = self.get(0)[1]
                    self.skip(2)
                    style_stmt = []
                    node_style = []
                    while self.tokens[self.pos][1] != "搞掂":
                        style_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    self.cantonese_css_parser(style_stmt, id)
                else:
                    name = self.get(0)[1]
                    self.skip(1)
                    self.check(self.get(0)[1], "=>")
                    self.skip(1)
                    self.check(self.get(0)[1], "[")
                    self.skip(1)
                    args = []
                    while self.tokens[self.pos][1] != "]":
                        args.append(self.tokens[self.pos][1])
                        self.pos += 1
                    self.skip(1)
                    with_style = False
                    if self.match('$'): # case 'style_with'
                        style_id = self.get(1)[1]
                        self.skip(2)
                        args.append(style_id)
                        with_style = True
                    web_ast_new(self.Node, "node_call", [name, args], with_style)
            else:
                break

    def cantonese_css_parser(self, stmt : list, id : str) -> None:
        cssParser(stmt, []).parse(id)

class cssParser(WebParser):
    def parse(self, id : str) -> None:
        while True:
            if self.match_type("id"):
                key = self.get(0)[1]
                self.skip(1)
                self.check(self.get(0)[1], "=>")
                self.skip(1)
                self.check(self.get(0)[1], "[")
                self.skip(1)
                value = []
                while self.tokens[self.pos][1] != "]":
                    value.append(self.tokens[self.pos][1])
                    self.pos += 1
                self.skip(1)
                web_ast_new(self.Node, "node_css", [id, key, value])
            else:
                break
        self.run(self.Node)

def web_ast_new(Node : list, type : str, ctx : list, with_style = True) -> None:
    Node.append([type, ctx, with_style])

def get_str(s : str) -> str:
    return eval("str(" + s + ")")

sym = {}
style_attr = {}
style_value_attr = {}

TO_HTML = "<html>\n"

def title(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        t_beg, t_end = "<title>", "</title>\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        t_beg, t_end = "<title id = \"" + style + "\">", "</title>\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end


def h(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        h_beg, h_end = "<h1>", "</h1>\n"
        TO_HTML += h_beg + get_str(args[0]) + h_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        size = "" if len(args) == 1 else args[1]
        t_beg, t_end = "<h" + size + " id = \"" + style + "\">", "</h" + size + ">\n"
        TO_HTML += t_beg + get_str(args[0]) + t_end

def img(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        i_beg, i_end = "<img src = ", ">\n"
        TO_HTML += i_beg + get_str(args[0]) + i_end
    if len(args) >= 2:
        style = args.pop() if with_style else ""
        i_beg, i_end = "<img id = \"" + style + "\" src = ", ">\n"
        TO_HTML += i_beg + get_str(args[0]) + i_end

def audio(args : list, with_style : bool) -> None:
    global TO_HTML
    if len(args) == 1:
        a_beg, a_end = "<audio src = ", "</audio>\n"
        TO_HTML += a_beg + get_str(args[0]) + a_end

def sym_init() -> None:
    global sym
    global style_attr

    sym['打标题'] = title
    sym['拎笔'] = h
    sym['睇下'] = img
    sym['Music'] = audio
    #sym['画格仔'] = table

    style_attr['要咩色'] = "color"
    style_attr['要咩背景颜色'] = "background-color"
    style_attr['要点对齐'] = "text-align"
    style_attr['要几高'] = 'height'
    style_attr['要几阔'] = 'width'

    style_value_attr['红色'] = "red"
    style_value_attr['黄色'] = "yellow"
    style_value_attr['白色'] = "white"
    style_value_attr['黑色'] = "black"
    style_value_attr['绿色'] = "green"
    style_value_attr['蓝色'] = "blue"
    style_value_attr['居中'] = "centre"

def head_init() -> None:
    global TO_HTML
    TO_HTML += "<head>\n"
    TO_HTML += "<meta charset=\"utf-8\" />\n"
    TO_HTML += "</head>\n"

def web_init() -> None:
    global TO_HTML
    sym_init()
    head_init()

def web_end() -> None:
    global TO_HTML
    TO_HTML += "</html>"

style_sym = {}

def style_def(id : str, key : str, value : list) -> None:
    global style_sym
    if id not in style_sym:
        style_sym[id] = [[key, value]]
        return
    style_sym[id].append([key, value])
    
def style_build(value : list) -> None:
    s = ""
    for item in value:
        if get_str(item[1][0]) not in style_value_attr.keys() and item[0] in style_attr.keys():
            s += style_attr[item[0]] + " : " + get_str(item[1][0]) + ";\n"
        elif get_str(item[1][0]) not in style_value_attr.keys() and item[0] not in style_attr.keys():
            s += item[0] + " : " + get_str(item[1][0]) + ";\n"
        elif get_str(item[1][0]) in style_value_attr.keys() and item[0] not in style_attr.keys():
            s += item[0] + " : " + style_value_attr[get_str(item[1][0])] + ";\n"
        else:
            s += style_attr[item[0]] + " : " + style_value_attr[get_str(item[1][0])] + ";\n"
    return s

def style_exec(sym : dict) -> None:
    global TO_HTML
    gen = ""
    s_beg, s_end = "\n<style type=\"text/css\">\n", "</style>\n"
    for key, value in sym.items():
        gen += "#" +  key + "{\n" + style_build(value) + "}\n"
    TO_HTML += s_beg + gen + s_end

def web_call_new(func : str, args_list : list, with_style = False) -> None:
    if func in sym:
        sym[func](args_list, with_style)
    else:
        func(args_list, with_style)

def get_html_file(name : str) -> str:
    return name[ : len(name) - len('cantonese')] + 'html'

class WebLexer(lexer):
    def __init__(self, code, keywords):
        super().__init__(code, keywords)
        self.re_callfunc, self.re_expr, self.op,\
        self.op_get_code, self.op_gen_code, \
        self.build_in_funcs, self.bif_get_code, \
        self.bif_gen_code = "", "", "", "", "", "", "", ""
    
    def get_token(self):
        self.skip_space()

        if len(self.code) == 0:
            return ['EOF', 'EOF']

        c = self.code[0]
        if self.isChinese(c) or c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return ['keywords', token]
            return ['id', token]

        if c == '=':
            if self.check("=>"):
                self.next(2)
                return ['keywords', "=>"]

        if c in ('\'', '"'):
            return ['string', self.scan_short_string()]
        
        if c == '.' or c.isdigit():
            token = self.scan_number()
            return ['num', token]

        if c == '{':
            self.next(1)
            return ["keywords", c]

        if c == '}':
            self.next(1)
            return ["keywords", c]

        if c == '[':
            self.next(1)
            return ["keywords", c]

        if c == ']':
            self.next(1)
            return ["keywords", c]

        if c == '$':
            self.next(1)
            return ["keywords", c]

        if c == '(':
            self.next(1)
            return ["keywords", c]
        
        if c == ')':
            self.next(1)
            return ["keywords", c]

        self.error("睇唔明嘅Token: " + c)

def cantonese_web_run(code : str, file_name : str, open_serv = True) -> None:
    global TO_HTML
    keywords = ("老作一下", "要点画", "搞掂", "执嘢")
    lex = WebLexer(code, keywords)
    tokens = []
    while True:
        token = lex.get_token()
        tokens.append(token)
        if token == ['EOF', 'EOF']:
            break
    
    web_init()
    WebParser(tokens, []).parse()
    web_end()
        
    if style_sym != {}:
        style_exec(style_sym)
    print(TO_HTML)

    if open_serv:
        import socket
        ip_port = ('127.0.0.1', 80)
        back_log = 10
        buffer_size = 1024
        webserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        webserver.bind(ip_port)
        webserver.listen(back_log)
        print("Cantonese Web Starting at 127.0.0.1:80 ...")
        while True:
            conn, addr = webserver.accept()
            recvdata = conn.recv(buffer_size)
            conn.sendall(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
            conn.sendall(bytes(TO_HTML, "utf-8"))
            conn.close()
            if input("input Y to exit:"):
                print("Cantonese Web exiting...")
                break
    
    else:
        f = open(get_html_file(file_name), 'w', encoding = 'utf-8')
        f.write(TO_HTML)
    sys.exit(0)

class AsmLerxer(lexer):
    def __init__(self, code, keywords, ins):
        super().__init__(code, keywords)
        self.ins = ins
        self.op, self.op_get_code, self.op_gen_code, \
        self.build_in_funcs, self.re_callfunc, self.bif_get_code, \
        self.bif_gen_code = "", "", "", "", "", "", ""
        self.re_register = r"[(](.*?)[)]"

    def scan_register(self):
        return self.scan(self.re_register)

    def get_token(self):
        # TODO
        self.skip_space()
        if len(self.code) == 0:
            return [self.line, ['EOF', 'EOF']]
        
        c = self.code[0]

        if c == '|':
           token = self.scan_expr()
           return [self.line, ['expr', token]]

        if c == '(':
            token = self.scan_register()
            return [self.line, ['register', token]]
        
        if c == '{':
            self.next(1)
            return [self.line, ['keyword', '{']]
        
        if c == '}':
            self.next(1)
            return [self.line, ['keyword', '}']]            

        if self.isChinese(c) or c == '_' or c.isalpha():
            token = self.scan_identifier()
            if token in self.keywords:
                return [self.line, ['keywords', token]]
            if token in self.ins:
                return [self.line, ['ins', token]]
            return [self.line, ['identifier', token]]
        
        if c in ('\'', '"'):
            return [self.line, ['string', self.scan_short_string()]]
        
        if c == '.' or c.isdigit():
            token = self.scan_number()
            return [self.line, ['num', token]]

        if c == '-':
            if self.check('->'):
                self.next(2)
                return [self.line, ['keyword', '->']]
        
        self.error("睇唔明嘅Token: " + c)

TO_ASM = ""

class AsmParser(object):
    def __init__(self, tokens : list, Node : list) -> None:
        self.tokens = tokens
        self.pos = 0
        self.Node = Node

    def get(self, offset : int) -> list:
        if self.pos + offset >= len(self.tokens):
            return [None, ["", ""]]
        return self.tokens[self.pos + offset]
        
    def match(self, name : str) -> bool:
        if self.get(0)[1][1] == name:
            return True
        return False
    
    def match_type(self, name : str) -> bool:
        if self.get(0)[1][0] == name:
            return True
        return False
    
    def check(self, a, b) -> None:
        if a == b:
            return
        raise LookupError("Error Token:" + str(b))

    def skip(self, offset) -> None:
            self.pos += offset

    def get_value(self, token):
        if token[1][0] == 'expr':
            # If is expr, Remove the "|"
            token[1][1] = token[1][1][1 : -1]
        if token[1][0] == 'register':
            token[1][1] = token[1][1][1 : -1]
        return token[1][1]

    def run(self, Nodes) -> None:
        global TO_ASM
        for node in Nodes:
            if node[0] == 'node_data':
                TO_ASM += "section .data\n"
                for d in node[1]:
                    TO_ASM += d[0] + " equ " + d[1] + "\n"

            if node[0] == 'node_mov':
                TO_ASM += "mov " + node[1][0] + ", " + node[1][1] + "\n"

            if node[0] == 'node_int':
                TO_ASM += "int " + node[1][0] + "\n"

            if node[0] == 'node_global':
                TO_ASM += "global " + node[1][0] + "\n"

            if node[0] == 'node_code':
                TO_ASM += node[1][0] + ":\n"
                self.run(node[1][1])

    def parse(self) -> None:
        while True:
            if self.match_type('expr'):
                if self.get(1)[1][1] == "有咩":
                    data_name = self.get(0)[1]
                    self.skip(4)
                    data_stmt = []
                    while self.tokens[self.pos][1][1] != "}":
                        data_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    ret = self.data_parse(data_stmt, data_name)
                    asm_ast_new(self.Node, "node_data", ret)
            
                if self.get(1)[1][1] == "要做咩":
                    code_name = self.get_value(self.get(0))
                    self.skip(4)
                    code_stmt = []
                    while self.tokens[self.pos][1][1] != "}":
                        code_stmt.append(self.tokens[self.pos])
                        self.pos += 1
                    self.skip(1)
                    stmt_node = []
                    AsmParser(code_stmt, stmt_node).parse()
                    asm_ast_new(self.Node, "node_code", [code_name, stmt_node])

                if self.get(1)[1][1] == "排头位":
                    start_name = self.get_value(self.get(0))
                    self.skip(4)
                    asm_ast_new(self.Node, "node_global", [start_name])

            elif self.match_type('register'):
                reg = self.get_value(self.get(0))
                self.skip(1)
                if self.get(0)[1][1] == "收数":
                    self.skip(2)
                    data = self.get_value(self.get(0))
                    asm_ast_new(self.Node, 'node_mov', [reg, data])
                    self.skip(1)
            
            elif self.match("仲要等埋"):
                self.skip(2)
                addr = self.get_value(self.get(0))
                asm_ast_new(self.Node, 'node_int', [addr])
                self.skip(1)

            else:
                break

    def data_parse(self, stmt, name) -> None:
        return dataParser(stmt, []).parse(name)
        
class dataParser(AsmParser):
    def parse(self, name) -> None:
        ret = []
        while True:
            if self.match_type("identifier"):
                key = self.get_value(self.get(0))
                self.skip(1)
                self.check(self.get(0)[1][1], "係")
                self.skip(1)
                val = self.get_value(self.get(0))
                self.skip(1)
                ret.append([key, val])
            else:
                break
        return ret

def asm_ast_new(Node : list, type : str, ctx : list) -> None:
    Node.append([type, ctx])


def Cantonese_asm_run(code : str, file_name : str) -> None:
    global TO_ASM

    ins_mov_from = "收数"
    ins_int = "仲要等埋"
    kw_datadef = "有咩"
    kw_secdef = "要做咩"
    kw_is = "係"
    kw_main = "排头位"
    kw_begin = "开工"

    keywords = (kw_datadef, kw_secdef,
            kw_is, kw_main, kw_begin)
    ins = (ins_mov_from, ins_int)
    lex = AsmLerxer(code, keywords, ins)
    tokens = []

    while True:
        token = lex.get_token()
        tokens.append(token)
        if token[1] == ['EOF', 'EOF']:
            break

    AST = []
    AsmParser(tokens, AST).parse()
    AsmParser(tokens, AST).run(AST)
    print(TO_ASM)
    sys.exit(1)

class 交互(cmd.Cmd):
    def __init__(self):
        super().__init__()
        self.prompt = '> '
    
    def var_def(self, key):
        pass
    
    def run(self, code):
        if code in variable.keys():
            print(variable[code])
        try:
            exec(code, variable)
        except Exception as e:
            print("濑嘢!" + "\n".join(濑啲咩嘢(e)))

    def default(self, code):
        
        global kw_exit_1
        global kw_exit_2
        global kw_exit

        if code is not None:
            if code == kw_exit or code == kw_exit_2 or code == kw_exit_1:
                sys.exit(1)
            c = cantonese_run(code, False, '【标准输入】', 
                REPL = True, get_py_code = True)
            if len(c) == 0:
                c = code
            self.run(c)


def 开始交互():
    global _version_
    print(_version_)
    import time
    交互().cmdloop(str(time.asctime(time.localtime(time.time()))))

def main():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("file", nargs = '?', default = "")
    arg_parser.add_argument("other", nargs = '?', default = "")
    arg_parser.add_argument("-to_py", action = "store_true", help = "Translate Cantonese to Python")
    arg_parser.add_argument("-讲翻py", action = "store_true", help = "Translate Cantonese to Python")
    arg_parser.add_argument("-to_js", action = "store_true", help = "Translate Cantonese to JS")
    arg_parser.add_argument("-to_cpp", action = "store_true", help = "Translate Cantonese to C++")
    arg_parser.add_argument("-to_asm", action = "store_true", help = "Translate Cantonese to assembly")
    arg_parser.add_argument("-to_web", action = "store_true")
    arg_parser.add_argument("-倾偈", action = "store_true")
    arg_parser.add_argument("-compile", action = "store_true")
    arg_parser.add_argument("-讲白啲", action = "store_true")
    arg_parser.add_argument("-build", action = "store_true")
    arg_parser.add_argument("-stack_vm", action = "store_true")
    arg_parser.add_argument("-ast", action = "store_true")
    arg_parser.add_argument("-lex", action = "store_true")
    arg_parser.add_argument("-debug", action = "store_true")
    arg_parser.add_argument("-v", "-verison", action = "store_true", help = "Print the version")
    arg_parser.add_argument("-mkfile", action = "store_true")
    arg_parser.add_argument("-S", action = "store_true")
    arg_parser.add_argument("-s", action = "store_true")
    args = arg_parser.parse_args()

    global dump_ast
    global dump_lex
    global to_js
    global to_cpp
    global _S
    global debug
    global mkfile
    global _version_

    if args.v:
        print(_version_)
        sys.exit(1)

    if not args.file:
        sys.exit(开始交互())

    try:
        with open(args.file, encoding = "utf-8") as f:
            code = f.read()
            # Skip the comment
            code = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', code)
            is_to_py = False
            if args.build:
                cantonese_lib_init()
                exec(code, variable)
                exit()
            if args.to_py or args.讲翻py:
                is_to_py = True
            if args.to_web or args.倾偈:
                if args.compile or args.讲白啲:
                    cantonese_web_run(code, args.file, False)
                else:
                    cantonese_web_run(code, args.file, True)
            if args.ast:
                dump_ast = True
            if args.lex:
                dump_lex = True
            if args.debug:
                debug = True
            if args.stack_vm:
                cantonese_run_with_vm(code, args.file)
                sys.exit(1)
            if args.to_js:
                to_js = True
            if args.to_cpp:
                to_cpp = True
            if args.S or args.s:
                _S = True
            if args.mkfile:
                mkfile = True
            if args.to_asm:
                Cantonese_asm_run(code, args.file)
            cantonese_run(code, is_to_py, args.file)
    except FileNotFoundError:
        print("濑嘢!: 揾唔到你嘅文件 :(")

if __name__ == '__main__':
    main()
