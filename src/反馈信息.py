import re, sys, traceback

class 层信息:
    def __init__(self, 行号, 内容, 文件名):
        self.行号, self.内容, self.文件名 = 行号, 内容, 文件名

def 提取(各层):
    各行 = []
    for 层号 in range(len(各层) - 1, -1, -1):
        层 = 各层[层号]
        文件名 = 层.filename
        各行.append(层信息(层.lineno, 层.line, 文件名))
    return 各行

def 报错信息(例外):
    exc_type, exc_value, 回溯信息 = sys.exc_info()
    各层 = traceback.extract_tb(回溯信息)
    各行 = []

    行信息 = 提取(各层)
    类型 = 例外.__class__.__name__
    原信息 = str(例外)
    if len(行信息) > 0:
        关键 = 提示(类型, 原信息)
    各行.append(关键)
    return 各行

def 提示(类型, 原信息):
    if 类型 == 'NameError':
        return re.sub(r"name '(.*)' is not defined", r"请先定义‘\1’再使用", 原信息)
    return 类型 + "：" + 原信息
