from py_cantonese.can_libs.lib_gobals import cantonese_func_def, define_func


def cantonese_kivy_init() -> None:
    from kivy.app import App
    from kivy.uix.label import Label
    from kivy.uix.button import Button
    from kivy.uix.boxlayout import BoxLayout

    cantonese_func_def("App", App)
    cantonese_func_def("Label", Label)
    cantonese_func_def("Button", Button)

    @define_func("同我show")
    def app_show(ctx, 寬=(0.5, 0.5), 高={"center_x": 0.5, "center_y": 0.5}) -> None:
        return Label(text=ctx, size_hint=寬, pos_hint=高)

    @define_func("App運行")
    def app_run(app_main, build_func) -> None:
        print("The app is running ...")

        def build(self):
            return build_func()

        app_main.build = build
        app_main().run()

    @define_func("開掣")
    def app_button(ctx, 寬=(0.5, 0.5), 高={"center_x": 0.5, "center_y": 0.5}) -> None:
        return Button(text=ctx, size_hint=寬, pos_hint=高)

    @define_func("老作")
    def app_layout(types, 佈局="", 方向="vertical", 間距=15, 內邊距=10):
        if 佈局 == "":
            if types == "Box":
                return BoxLayout(orientation=方向, spacing=間距, padding=內邊距)
        else:
            for i in types.stack:
                佈局.add_widget(i)

    @define_func("睇實佢")
    def button_bind(btn, func) -> None:
        btn.bind(on_press=func)
