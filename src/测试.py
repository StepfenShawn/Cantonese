from 期望值表 import 期望值
from 运行 import 运行代码
from pathlib import Path
import unittest

# 在 src 下运行 `python -m unittest 测试.py`
class test所有(unittest.TestCase):

    def test(self):
        测试目录 = '../examples/'
        全部通过 = True
        失败表 = {}

        for 文件 in 期望值:
            路径 = 测试目录 + 文件
            实际值 = 运行代码(路径)
            预期值 = 期望值[文件].encode('utf-8')

            if 实际值 != 预期值:
                失败表[文件] = 实际值
                全部通过 = False

        for 文件 in 失败表:
            print(f"失败： {文件} 期望：{期望值[文件]} 实际：{失败表[文件]}")
        self.assertTrue(全部通过, "以上用例未通过！")
