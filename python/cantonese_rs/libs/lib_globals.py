"""Global runtime environment for Cantonese programs."""

import functools
from typing import Callable

lib_env: dict = {"__builtins__": __builtins__}


def cantonese_func_def(func_name: str, func) -> None:
    lib_env[func_name] = func


def define_func(name: str):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        cantonese_func_def(name, wrapper)
        return wrapper

    return decorator
