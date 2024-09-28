from can_source.libraries.can_lib import define_func

def cantonese_json_init() -> None:
    import json

    @define_func("讀取json")
    def json_load(text):
        return json.loads(text)

    @define_func("睇下json")
    def show_json_load(text):
        print(json.loads(text))

