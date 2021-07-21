import re, sys, traceback

class 层信息:
    def __init__(self, 行号, 有啲咩, 文件名):
        self.行号, self.有啲咩, self.文件名 = 行号, 有啲咩, 文件名

def 提取(各层):
    各行 = []
    for 层号 in range(len(各层) - 1, -1, -1):
        层 = 各层[层号]
        文件名 = 层.filename
        各行.append(层信息(层.lineno, 层.line, 文件名))
    return 各行

def 濑啲咩嘢(错误):
    exc_type, exc_value, 回溯信息 = sys.exc_info()
    各层 = traceback.extract_tb(回溯信息)
    各行 = []

    行信息 = 提取(各层)
    类型 = 错误.__class__.__name__
    咩回事 = str(错误)
    if len(行信息) > 0:
        各行.append(话畀你知(类型, 咩回事))
    return 各行

def 话畀你知(类型, 咩回事):
    if 类型 == 'NameError':
        return re.sub(r"name '(.*)' is not defined", r"唔知‘\1’係咩", 咩回事)
    return 类型 + "：" + 咩回事
