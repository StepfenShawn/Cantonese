"""Cantonese runtime library registry and bootstrap."""

import importlib
from collections import namedtuple
from typing import Tuple

from .lib_globals import cantonese_func_def, define_func, lib_env

# Optional standard-library wrappers; failures to import are tolerated.
try:
    from .std.app.impl import cantonese_kivy_init
except Exception:
    cantonese_kivy_init = None

try:
    from .std.csv.impl import cantonese_csv_init
except Exception:
    cantonese_csv_init = None

try:
    from .std.game.impl import cantonese_pygame_init
except Exception:
    cantonese_pygame_init = None

try:
    from .std.gui.impl import cantonese_turtle_init
except Exception:
    cantonese_turtle_init = None

try:
    from .std.https.impl import (
        cantonese_requests_init,
        cantonese_socket_init,
        cantonese_urllib_init,
    )
except Exception:
    cantonese_requests_init = None
    cantonese_socket_init = None
    cantonese_urllib_init = None

try:
    from .std.json.impl import cantonese_json_init
except Exception:
    cantonese_json_init = None

try:
    from .std.impl import (
        cantonese_datetime_init,
        cantonese_math_init,
        cantonese_numpy_init,
        cantonese_random_init,
        cantonese_re_init,
        cantonese_smtplib_init,
        cantonese_xml_init,
        cantonese_lib_init,
    )
except Exception:
    cantonese_lib_init = None
    cantonese_datetime_init = None
    cantonese_math_init = None
    cantonese_numpy_init = None
    cantonese_random_init = None
    cantonese_re_init = None
    cantonese_smtplib_init = None
    cantonese_xml_init = None

LibRegister = namedtuple("LibRegister", ["names", "f_init", "import_res"])

lib_list = [
    LibRegister(["random", "隨機數"], cantonese_random_init, "random"),
    LibRegister(["datetime", "日期"], cantonese_datetime_init, "datetime"),
    LibRegister(["math", "數學"], cantonese_math_init, "math"),
    LibRegister(["smtplib", "郵箱"], cantonese_smtplib_init, "smtplib"),
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


def fix_lib_name(name: str) -> Tuple[str, bool]:
    """Map a Cantonese library alias to its Python import name.

    Returns (import_name, is_third_party). For built-in libraries the init
    function is invoked as a side effect so that runtime functions are
    registered in `lib_env`.
    """
    for lib in lib_list:
        if name in lib.names:
            if lib.f_init is not None:
                lib.f_init()
            return lib.import_res, False
    return name, True


def __cantonese_import__(alias: str):
    """Runtime helper for built-in Cantonese library aliases.

    The Rust compiler emits calls to this function instead of a plain
    `import` statement. It resolves the Cantonese alias and triggers any
    Cantonese wrapper initialization before importing the underlying Python
    module.
    """
    import importlib.machinery

    import_name, _ = fix_lib_name(alias)

lib_env["__cantonese_import__"] = __cantonese_import__


def bootstrap() -> None:
    """Initialize the core Cantonese runtime environment.

    Only the core built-ins (List, Str, file helpers, etc.) are loaded here.
    Standard-library wrappers are initialized lazily when their corresponding
    module is imported via `fix_lib_name`.
    """
    if cantonese_lib_init is not None:
        cantonese_lib_init()


def get_globals() -> dict:
    """Return a fresh globals dictionary with the Cantonese runtime loaded."""
    bootstrap()
    return lib_env.copy()
