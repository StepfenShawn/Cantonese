import functools

variable: dict = {}

def cantonese_func_def(func_name: str, func) -> None:
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