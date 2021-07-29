import re, subprocess
from pathlib import Path

def 运行代码(源码文件):
    源码文件 = str(Path(源码文件))
    with open(源码文件, 'r', encoding='utf-8') as f:
        源码 = f.read()

    # 删去注释
    源码 = re.sub(re.compile(r'/\*.*?\*/', re.S), ' ', 源码)

    参数 = ["python", "cantonese.py", 源码文件]
    return subprocess.Popen(参数, stdout=subprocess.PIPE).communicate()[0]
