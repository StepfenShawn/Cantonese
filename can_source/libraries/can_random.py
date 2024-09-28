from can_source.libraries.lib_gobals import cantonese_func_def


def cantonese_random_init() -> None:
    import random

    cantonese_func_def("求其啦", random.random)
    cantonese_func_def("求其int下啦", random.randint)
    cantonese_func_def("求其嚟個", random.randrange)
    cantonese_func_def("是但揀", random.choice)