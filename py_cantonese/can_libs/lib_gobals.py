import functools
import py_cantonese as base_env

lib_env: dict = {"can_source": base_env}


def cantonese_func_def(func_name: str, func) -> None:
    global variable
    lib_env[func_name] = func


def define_func(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            return func(*args, **kw)

        cantonese_func_def(name, wrapper)
        return wrapper

    return decorator
