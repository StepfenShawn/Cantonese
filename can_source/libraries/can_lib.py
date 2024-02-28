import sys
import re
import functools
from collections import namedtuple

variable: dict = {}

def cantonese_func_def(func_name : str, func) -> None:
    global variable
    variable[func_name] = func

def define_func(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)
        cantonese_func_def(name, wrapper)
        return wrapper
    return decorator

def cantonese_lib_init() -> None:

    @define_func("開份文件")
    def cantonese_open(file, 模式 = 'r', 解碼 = None):
        return open(file, mode = 模式, encoding = 解碼)

    @define_func("關咗佢")
    def cantonese_close(file) -> None:
        file.close()

    @define_func("睇睇文件名")
    def out_name(file) -> None:
        print(file.name)

    @define_func("睇睇有咩")
    def out_ctx(file, size = None) -> None:
        if size == None:
            print(file.read())
            return
        print(file.read(size))

    @define_func("文件名")
    def get_name(file) -> str:
        return file.name

    @define_func("讀取")
    def cantonese_read(file, size = None) -> str:
        if size == None:
            return file.read()
        return file.read(size)

    @define_func("最尾")
    def get_list_end(lst : list):
        return lst[-1]

    @define_func("排頭位")
    def get_list_beg(lst : list):
        return lst[0]

    @define_func("身位")
    def where(lst : list, index : int, index2 = None, index3 = None, index4 = None):
        if index2 != None and index3 == None and index4 == None:
            return lst[index][index2]
        if index3 != None and index2 != None and index4 == None:
            return lst[index][index2][index3]
        if index4 != None and index2 != None and index3 != None:
            return lst[index][index2][index3][index4]
        return lst[index]
    
    @define_func("掗位")
    def lst_insert(lst : list, index : int, obj) -> None:
        lst.insert(index, obj)

    @define_func("摞位")
    def list_get(lst : list, index : int):
        return lst[index]

    @define_func("check範圍")
    def lst_range(lst : list, range_lst : list, loss, types = 1, func = None, func_ret = None) -> bool:
        if types == 2:
            for i in lst:
                if i - loss <= range_lst and i + loss >= range_lst:
                    return True

        else:
            for i in lst:
                if i[0] - loss <= range_lst[0] and i[1] + loss >= range_lst[1]:
                    return True

    @define_func("畀個tuple")
    def make_tuple(*args):
        return tuple(args)

    cantonese_func_def("唔啱", False)
    cantonese_func_def("啱", True)

    cantonese_func_def("畀你啲嘢", input)

    cantonese_stack_init()

def cantonese_json_init() -> None:
    import json

    @define_func("讀取json")
    def json_load(text):
        return json.loads(text)

    @define_func("睇下json")
    def show_json_load(text):
        print(json.loads(text))
    
def cantonese_csv_init() -> None:
    import csv

    @define_func("睇睇csv有咩")
    def out_csv_read(file):
        for i in csv.reader(file):
            print(i)

    @define_func("讀取csv")
    def get_csv(file):
        ret = []
        for i in csv.reader(file):
            ret.append(i)
        return i

def cantonese_random_init() -> None:
    import random
    cantonese_func_def("求其啦", random.random)
    cantonese_func_def("求其int下啦", random.randint)
    cantonese_func_def("求其嚟個", random.randrange)
    cantonese_func_def("是但揀", random.choice)

def cantonese_datetime_init() -> None:
    import datetime
    cantonese_func_def("宜家幾點", datetime.datetime.now)

def cantonese_xml_init() -> None:
    from xml.dom.minidom import parse
    import xml.dom.minidom

    @define_func("剪樖Dom樹")
    def make_dom(file) -> None:
        return xml.dom.minidom.parse(file).documentElement

    @define_func("Dom有嘢")
    def has_attr(docelm, attr) -> bool:
        return docelm.hasAttribute(attr)

    @define_func("睇Dom有咩")
    def get_attr(docelm, attr):
        print(docelm.getAttribute(attr))
    
    @define_func("用Tag揾")
    @define_func("用Tag揾嘅")
    def getElementsByTag(docelm, tag : str, out = None, ctx = None):
        if out == 1:
            print(docelm.getElementsByTagName(tag))
        if ctx != None:
            print(ctx + docelm.getElementsByTagName(tag)[0].childNodes[0].data)
        return docelm.getElementsByTagName(tag)

def cantonese_turtle_init() -> None:
    import turtle
    cantonese_func_def("畫個圈", turtle.circle)
    cantonese_func_def("寫隻字", turtle.write)
    cantonese_func_def("聽我支笛", turtle.exitonclick)

def cantonese_smtplib_init() -> None:
    import smtplib

    @define_func("send份郵件")
    def send(sender : str, receivers : str,  message : str, 
             smtpObj = smtplib.SMTP('localhost')) -> None:
        try:
            smtpObj.sendmail(sender, receivers, message)         
            print("Successfully sent email!")
        except Exception:
            print("Error: unable to send email")

def cantonese_stack_init() -> None:
    @define_func("stack")
    class _stack(object):
        def __init__(self):
            self.stack = []
        def __str__(self):
            return 'Stack: ' + str(self.stack)
        @define_func("我頂")
        def push(self, value):
            self.stack.append(value)
        @define_func("我丟")
        def pop(self):
            if self.stack:
                return self.stack.pop()
            else:
                raise LookupError('stack 畀你丟空咗!')

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
    cantonese_func_def("矩陣", Matrix)
    cantonese_func_def("點積", Matrix.matrix_multiplication)
    cantonese_func_def("相加", Matrix.matrix_addition)
    cantonese_func_def("開根", math.sqrt)
    cantonese_func_def("絕對值", math.fabs)
    cantonese_func_def("正弦", math.sin)
    cantonese_func_def("餘弦", math.cos)
    cantonese_func_def("正切", math.tan)
    cantonese_func_def("PI", math.pi)
    cantonese_func_def("E", math.e)
    cantonese_func_def("+oo", math.inf)

def cantonese_model_new(model, datatest, tab, code) -> str:
    if model == "KNN":
        code += tab + "print(KNN(" + datatest + ", 數據, 標籤, K))"
    elif model == "L_REG":
        code += tab + "print(l_reg(" + datatest + ", X, Y))"
    else:
        print("揾唔到你嘅模型: " + model + "!")
        code = ""
    return code

def cantonese_re_init() -> None:

    @define_func("襯唔襯")
    def can_re_match(pattern : str, string : str, flags = 0):
        return re.match(pattern, string, flags)

    @define_func("襯")
    def can_re_match_out(pattern : str, string : str, flags = 0) -> None:
        print(re.match(pattern, string, flags).span())

def cantonese_urllib_init() -> None:
    import urllib.request

    @define_func("睇網頁")
    def can_urlopen_out(url : str) -> None:
        print(urllib.request.urlopen(url).read())

    @define_func("揾網頁")
    def can_urlopen(url : str):
        return urllib.request.urlopen(url)

def cantonese_requests_init() -> None:
    import requests

    @define_func("噅求")
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

def cantonese_socket_init() -> None:
    import socket

    @define_func("通電話")
    def s_new():
        return socket.socket() 

    @define_func("傾偈")
    def s_connect(s, port, host = socket.gethostname()):
        s.connect((host, port))
        return s
    
    @define_func("收風")
    def s_recv(s, i : int):
        return s.recv(i)
    
    @define_func("收線")
    def s_close(s) -> None:
        s.close()

def cantonese_kivy_init() -> None:
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.boxlayout import BoxLayout

    
    cantonese_func_def("App", App)
    cantonese_func_def("Label", Label)
    cantonese_func_def("Button", Button)

    @define_func("同我show")
    def app_show(ctx, 寬 = (.5, .5), 
        高 = {"center_x": .5, "center_y": .5}) -> None:
        return Label(text = ctx, size_hint = 寬, pos_hint = 高)

    @define_func("App運行")
    def app_run(app_main, build_func) -> None:
        print("The app is running ...")
        def build(self):
            return build_func()
        app_main.build = build
        app_main().run()

    @define_func("開掣")
    def app_button(ctx, 寬 = (.5, .5), 
        高 = {"center_x": .5, "center_y": .5}) -> None:
        return Button(text = ctx, size_hint = 寬, pos_hint = 高)

    @define_func("老作")
    def app_layout(types, 佈局 = "", 方向 = 'vertical', 間距 = 15, 內邊距 = 10):
        if 佈局 ==  "":
            if types == "Box":
                return BoxLayout(orientation = 方向, 
                spacing = 間距, padding = 內邊距)
        else:
            for i in types.stack:
                佈局.add_widget(i)
    
    @define_func("睇實佢")
    def button_bind(btn, func) -> None:
        btn.bind(on_press = func)

def cantonese_pygame_init() -> None:
    
    import pygame
    import math
    import random
    from pygame.constants import KEYDOWN

    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    @define_func("屏幕老作")
    def pygame_setmode(size, caption = ""):
        if caption != "":
            pygame.display.set_caption(caption)
            return pygame.display.set_mode(size, 0, 32)
        return pygame.display.set_mode(size, 0, 32)

    @define_func("圖片老作")
    def pygame_imgload(path, color = ""):
        img = pygame.image.load(path).convert_alpha()
        if color != "":
            img.set_colorkey((color),pygame.RLEACCEL)
        return img

    @define_func("嚟首music")
    def pygame_musicload(path, loop = True, start = 0.0):
        pygame.mixer.music.load(path)
        if loop:
            pygame.mixer.music.play(-1, start)
        else:
            pygame.mixer.music.play(1, start)

    @define_func("嚟首sound")
    def pygame_soundload(path):
        return pygame.mixer.Sound(path)
    
    @define_func("播放")
    def pygame_sound_play(sound):
        sound.play()

    @define_func("暫停")
    def pygame_sound_stop(sound):
        sound.stop()

    @define_func("玩跑步")
    def pygame_move(object, speed):
        return object.move(speed)

    @define_func("喺邊")
    def object_rect(object, center = ""):
        if center == "":
            return object.get_rect()
        return object.get_rect(center = center)

    @define_func("校色")
    def pygame_color(color):
        return pygame.Color(color)

    @define_func("摞掣")
    def pygame_key(e):
        return e.key

    @define_func("上畫")
    def draw(屏幕, obj = "", obj_where = "", event = "", 顏色 = "", 位置 = "") -> None:
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
        if 顏色 != "":
            屏幕.fill(顏色)
        if obj != "" and obj_where != "":
            屏幕.blit(obj, obj_where)

        pygame.time.delay(2)
    
    @define_func("事件驅動")
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

    @define_func("揾位")
    def direction(obj, dir):
        if dir == "左邊" or dir == "left" or dir == "左边":
            return obj.left
        if dir == "右邊" or dir == "right" or dir == "右边":
            return obj.right
        if dir == "上邊" or dir == "top" or dir == "上边":
            return obj.top
        if dir == "下邊" or dir == "bottom" or dir == "下边":
            return obj.bottom

    @define_func("睇表")
    def time_tick(clock_obj, t):
        clock_obj.tick(t)

    @define_func("矩形老作")
    def pygame_rectload(屏幕, 顏色, X, Y, H = 20, W = 20):
        pygame.draw.rect(屏幕, 顏色, pygame.Rect(X, Y, H, W))

    @define_func("動圖老作")
    def pygame_gif_show(屏幕, 序列, pos = (0, 0), delay = 100):
        for i in 序列:
            屏幕.blit(i, pos)
            pygame.time.delay(delay)
            pygame.display.update()

    def text_objects(text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    @define_func("寫隻字")
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

    @define_func("屏幕校色")
    def screen_fill(screen, color):
        screen.fill(color)

    @define_func("畫圖片")
    def img_show(screen, img, where):
        screen.blit(img, where)

    @define_func("嚟個公仔")
    def sprite_add(group, sprite):
        group.add(sprite)

    @define_func("刷新公仔")
    def sprite_update(group, ticks):
        group.update(ticks)

    @define_func("畫公仔")
    def sprite_draw(group, screen):
        group.draw(screen)

    @define_func("摞公仔")
    def sprite_kill(sprite):
        sprite.kill()

    @define_func("跟蹤")
    def sprite_trace(target, tracer, type = "", speed = 3, speed_y = 16, speed_x = 16):
        if type == "Linear":
            dx, dy = target[0] - tracer.x, target[1] - tracer.y
            dist = math.hypot(dx, dy) + 0.1
            dx, dy = dx / dist, dy / dist  # Normalize.
            # Move along this normalized vector towards the player at current speed.
            return (dx * speed, dy * speed)
    """
        display_width : width of the screen
        display_height : height of the screen
    """

    @define_func("嚟個按鈕")
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
        
        def 點擊(self, position):
            return self.check_click(position)

    cantonese_func_def("嚟個矩形", pygame.Rect)
    cantonese_func_def("公仔", pygame.sprite.Sprite)
    cantonese_func_def("公仔集", pygame.sprite.Group)
    cantonese_func_def("睇下撞未", pygame.sprite.collide_rect)
    cantonese_func_def("計時器", pygame.time.Clock)
    cantonese_func_def("延時", pygame.time.delay)
    cantonese_func_def("check下鼠標", pygame.mouse.get_pos)
    cantonese_func_def("check下點擊", pygame.mouse.get_pressed)
    cantonese_func_def("刷新", pygame.display.flip)
    cantonese_func_def("Say拜拜", pygame.quit)

def cantonese_numpy_init() -> None:
    pass

LibRegister = namedtuple('LibRegister', ['names', 'f_init', 'import_res'])

lib_list = [
    LibRegister(["random", "隨機數"], cantonese_random_init, "random"),
    LibRegister(["datetime", "日期"], cantonese_datetime_init, "datetime"),
    LibRegister(["math", "數學"], cantonese_math_init, "math"),
    LibRegister(["smtplib", "郵箱"], cantonese_smtplib_init, "stmplib"),
    LibRegister(["xml", "xml解析"], cantonese_xml_init, "xml"),
    LibRegister(["csv", "csv解析"], cantonese_csv_init, "csv"),
    LibRegister(["os", "系統"], None, "os"),
    LibRegister(["re", "正則匹配"], cantonese_re_init, "re"),
    LibRegister(["urllib", "網頁獲取"], cantonese_urllib_init, "urllib"),
    LibRegister(["requests", "網絡請求"], cantonese_requests_init, "requests"),
    LibRegister(["socket", "網絡連接"], cantonese_socket_init, "socket"),
    LibRegister(["kivy", "手機程式"], cantonese_kivy_init, "kivy"),
    LibRegister(["pygame", "遊戲"], cantonese_pygame_init, "pygame"),
    LibRegister(["json", "json解析"], cantonese_json_init, "json"),
    LibRegister(["numpy", "數值計算"], cantonese_numpy_init, "numpy")
]

"""
    Built-in library for Cantonese
"""
def fix_lib_name(name : str) -> str:
    global lib_list

    # Call function library
    if name[ : 7] == "python_":
        return name[7 : ]

    # Call cantonese build-in library
    for lib in lib_list:
        if name in lib.names:
            if lib.f_init is not None:
                lib.f_init()
            return lib.import_res
    
    # Call other library
    return name