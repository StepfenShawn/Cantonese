from collections import namedtuple
from typing import Tuple

from can_source.can_libs.std.app.impl import cantonese_kivy_init
from can_source.can_libs.std.csv.impl import cantonese_csv_init
from can_source.can_libs.std.game.impl import cantonese_pygame_init
from can_source.can_libs.std.gui.impl import cantonese_turtle_init
from can_source.can_libs.std.https.impl import (
    cantonese_requests_init,
    cantonese_socket_init,
    cantonese_urllib_init,
)
from can_source.can_libs.std.json.impl import cantonese_json_init
from can_source.can_libs.std.impl import (
    cantonese_datetime_init,
    cantonese_math_init,
    cantonese_numpy_init,
    cantonese_random_init,
    cantonese_re_init,
    cantonese_smtplib_init,
    cantonese_xml_init,
    cantonese_lib_init,
)
from can_source.can_libs.lib_gobals import lib_env

LibRegister = namedtuple("LibRegister", ["names", "f_init", "import_res"])

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
    LibRegister(["numpy", "數值計算"], cantonese_numpy_init, "numpy"),
    LibRegister(["turtle", "gui", "画图"], cantonese_turtle_init, "turtle"),
]

"""
    Built-in library for Cantonese
"""


def fix_lib_name(name: str) -> Tuple[str, bool]:
    global lib_list

    # Call cantonese build-in library
    for lib in lib_list:
        if name in lib.names:
            if lib.f_init is not None:
                lib.f_init()
            return lib.import_res, False

    # Call other library
    return name, True
