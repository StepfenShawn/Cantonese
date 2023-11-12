"""
    Test script for cantonese examples
    Notes: Must be ran under the test folder
"""

import io
import os
import glob
import datetime
import unittest
import re
import subprocess
from pathlib import Path
import platform

WinExpectation = {
    "..\\examples\\basic\\assign.cantonese": "1\n3\n",
    "..\\examples\\basic\\class.cantonese": "Duck is swimming\nDuck is sleeping\n公\n",
    "..\\examples\\basic\\comment.cantonese": "Run OK\n",
    "..\\exapmles\\basic\\HelloWorld.cantonese": " Hello World! \n",
}

期望值 = {
    "basic/assign.cantonese": "1\n3\n",
    "basic/class.cantonese": "Duck is swimming\nDuck is sleeping\n公\n",
    "basic/comment.cantonese": "Run OK\n",
    "basic/HelloWorld.cantonese": " Hello World! \n",
}

def adb_shell(cmd):
    result = os.popen(cmd).read()
    return result

if platform.system() == 'Windows':
    starttime = datetime.datetime.now()
    file_list = []
    # Get all the file names under examples
    for f in glob.glob(os.path.join('..\examples\*', '*.cantonese')):
        file_list.append(f)
    
    i = 0
    print("==============START TEST================")
    while i < len(file_list) - 3:
        print("Running:" + file_list[i] +  "......")
        #os.system("python ../src/cantonese.py " + file_list[i])
        # If raise an err try to use "python3 ../src/cantonese.py"
        cmd = "python cantonese.py " + file_list[i]
        # TODO: Get the output in command and compare with all the expectation
        ret = adb_shell(cmd)
        try:
            if ret == WinExpectation[file_list[i]] and file_list[i] in WinExpectation:
                print(file_list[i] + "The correct results are output")
        except KeyError:
            pass
        print("End")
        i += 1
    print("=============END=======================")
    endtime = datetime.datetime.now()
    # Count and Output the runtime
    print("Finished in " + str((endtime - starttime).seconds) + "s!")
    
else:
    def 运行代码(源码文件):
        源码文件 = str(Path(源码文件))
        with open(源码文件, 'r', encoding = 'utf-8') as f:
            源码 = f.read()

        参数 = ["python", "cantonese.py", 源码文件]
        return subprocess.Popen(参数, stdout=subprocess.PIPE).communicate()[0]

    # 在 test 下运行 `python -m unittest test.py`
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