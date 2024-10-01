from can_source.can_libs.lib_gobals import define_func


def cantonese_urllib_init() -> None:
    import urllib.request

    @define_func("睇網頁")
    def can_urlopen_out(url: str) -> None:
        print(urllib.request.urlopen(url).read())

    @define_func("揾網頁")
    def can_urlopen(url: str):
        return urllib.request.urlopen(url)


def cantonese_requests_init() -> None:
    import requests

    @define_func("噅求")
    def req_get(url: str, data="", json=False):
        headers = {
            "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Mobile Safari/537.36"
        }
        if data != "":
            headers.update(data)
        res = requests.get(url, headers)
        res.encoding = "utf-8"
        if json:
            return res.json()
        return res.text


def cantonese_socket_init() -> None:
    import socket

    @define_func("通電話")
    def s_new():
        return socket.socket()

    @define_func("傾偈")
    def s_connect(s, port, host=socket.gethostname()):
        s.connect((host, port))
        return s

    @define_func("收風")
    def s_recv(s, i: int):
        return s.recv(i)

    @define_func("收線")
    def s_close(s) -> None:
        s.close()
