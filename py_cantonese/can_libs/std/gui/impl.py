from py_cantonese.can_libs.lib_gobals import cantonese_func_def


def cantonese_turtle_init() -> None:
    import turtle

    cantonese_func_def("畫個圈", turtle.circle)
    cantonese_func_def("寫隻字", turtle.write)
    cantonese_func_def("聽我支笛", turtle.exitonclick)
