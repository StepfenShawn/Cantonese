import sys
from can_source.can_libs.lib_gobals import cantonese_func_def, define_func


def cantonese_pygame_init() -> None:
    import pygame
    import math
    import random
    from pygame.constants import KEYDOWN

    pygame.init()
    pygame.mixer.init()
    pygame.font.init()

    @define_func("屏幕老作")
    def pygame_setmode(size, caption=""):
        if caption != "":
            pygame.display.set_caption(caption)
            return pygame.display.set_mode(size, 0, 32)
        return pygame.display.set_mode(size, 0, 32)

    @define_func("圖片老作")
    def pygame_imgload(path, color=""):
        img = pygame.image.load(path).convert_alpha()
        if color != "":
            img.set_colorkey((color), pygame.RLEACCEL)
        return img

    @define_func("嚟首music")
    def pygame_musicload(path, loop=True, start=0.0):
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
    def object_rect(object, center=""):
        if center == "":
            return object.get_rect()
        return object.get_rect(center=center)

    @define_func("校色")
    def pygame_color(color):
        return pygame.Color(color)

    @define_func("摞掣")
    def pygame_key(e):
        return e.key

    @define_func("上畫")
    def draw(屏幕, obj="", obj_where="", event="", 顏色="", 位置="") -> None:
        if event == "":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
        else:
            event_map = {"KEYDOWN": KEYDOWN}
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
        event_map = {"KEYDOWN": KEYDOWN}
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
    def pygame_rectload(屏幕, 顏色, X, Y, H=20, W=20):
        pygame.draw.rect(屏幕, 顏色, pygame.Rect(X, Y, H, W))

    @define_func("動圖老作")
    def pygame_gif_show(屏幕, 序列, pos=(0, 0), delay=100):
        for i in 序列:
            屏幕.blit(i, pos)
            pygame.time.delay(delay)
            pygame.display.update()

    def text_objects(text, font, color):
        textSurface = font.render(text, True, color)
        return textSurface, textSurface.get_rect()

    @define_func("寫隻字")
    def pygame_text_show(
        screen,
        text,
        display_x,
        display_y,
        style="freesansbold.ttf",
        _delay=100,
        size=115,
        color=(255, 255, 255),
        update=True,
    ):
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
    def sprite_trace(target, tracer, type="", speed=3, speed_y=16, speed_x=16):
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
        def __init__(
            self,
            text,
            color,
            screen,
            display_width=1200,
            display_height=600,
            x=None,
            y=None,
            size=58,
            **kwargs
        ):
            font = pygame.font.Font("freesansbold.ttf", size)
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
