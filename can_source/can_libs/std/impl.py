import re
from can_source.can_libs.lib_gobals import cantonese_func_def, define_func, lib_env


class List(list):
    @property
    def 長度(self):
        return super().__len__()

    def 摞走(self, value):
        super().remove(value)

    def 散水(self):
        return super().clear()

    def 加啲(self, o):
        super().append(o)


class Str(str):
    @property
    def 長度(self):
        return super().__len__()


def cantonese_lib_init() -> None:

    class aa:
        def __getattr__(self, x):
            return eval(x, lib_env)

    @define_func("開份文件")
    def cantonese_open(file, 模式="r", 解碼=None):
        return open(file, mode=模式, encoding=解碼)

    @define_func("關咗佢")
    def cantonese_close(file) -> None:
        file.close()

    @define_func("睇睇文件名")
    def out_name(file) -> None:
        print(file.name)

    @define_func("睇睇有咩")
    def out_ctx(file, size=None) -> None:
        if size == None:
            print(file.read())
            return
        print(file.read(size))

    @define_func("文件名")
    def get_name(file) -> str:
        return file.name

    @define_func("讀取")
    def cantonese_read(file, size=None) -> str:
        if size == None:
            return file.read()
        return file.read(size)

    @define_func("最尾")
    def get_list_end(lst: list):
        return lst[-1]

    @define_func("排頭位")
    def get_list_beg(lst: list):
        return lst[0]

    @define_func("身位")
    def where(lst: list, index: int, index2=None, index3=None, index4=None):
        if index2 != None and index3 == None and index4 == None:
            return lst[index][index2]
        if index3 != None and index2 != None and index4 == None:
            return lst[index][index2][index3]
        if index4 != None and index2 != None and index3 != None:
            return lst[index][index2][index3][index4]
        return lst[index]

    @define_func("掗位")
    def lst_insert(lst: list, index: int, obj) -> None:
        lst.insert(index, obj)

    @define_func("摞位")
    def list_get(lst: list, index: int):
        return lst[index]

    @define_func("check範圍")
    def lst_range(
        lst: list, range_lst: list, loss, types=1, func=None, func_ret=None
    ) -> bool:
        if types == 2:
            for i in lst:
                if i - loss <= range_lst and i + loss >= range_lst:
                    return True

        else:
            for i in lst:
                if i[0] - loss <= range_lst[0] and i[1] + loss >= range_lst[1]:
                    return True

    @define_func("畀個tuple")
    def make_tuple(*args):
        return tuple(args)

    cantonese_func_def("唔啱", False)
    cantonese_func_def("啱", True)
    cantonese_func_def("桔", None)
    cantonese_func_def("阿", aa())
    cantonese_func_def("List", List)
    cantonese_func_def("Str", Str)
    cantonese_func_def("畀你啲嘢", input)

    cantonese_stack_init()


def cantonese_datetime_init() -> None:
    import datetime

    cantonese_func_def("宜家幾點", datetime.datetime.now)


def cantonese_xml_init() -> None:
    from xml.dom.minidom import parse
    import xml.dom.minidom

    @define_func("剪樖Dom樹")
    def make_dom(file) -> None:
        return xml.dom.minidom.parse(file).documentElement

    @define_func("Dom有嘢")
    def has_attr(docelm, attr) -> bool:
        return docelm.hasAttribute(attr)

    @define_func("睇Dom有咩")
    def get_attr(docelm, attr):
        print(docelm.getAttribute(attr))

    @define_func("用Tag揾")
    @define_func("用Tag揾嘅")
    def getElementsByTag(docelm, tag: str, out=None, ctx=None):
        if out == 1:
            print(docelm.getElementsByTagName(tag))
        if ctx != None:
            print(ctx + docelm.getElementsByTagName(tag)[0].childNodes[0].data)
        return docelm.getElementsByTagName(tag)


def cantonese_smtplib_init() -> None:
    import smtplib

    @define_func("send份郵件")
    def send(
        sender: str, receivers: str, message: str, smtpObj=smtplib.SMTP("localhost")
    ) -> None:
        try:
            smtpObj.sendmail(sender, receivers, message)
            print("Successfully sent email!")
        except Exception:
            print("Error: unable to send email")


def cantonese_stack_init() -> None:
    @define_func("stack")
    class _stack(object):
        def __init__(self):
            self.stack = []

        def __str__(self):
            return "Stack: " + str(self.stack)

        @define_func("我頂")
        def push(self, value):
            self.stack.append(value)

        @define_func("我丟")
        def pop(self):
            if self.stack:
                return self.stack.pop()
            else:
                raise LookupError("stack 畀你丟空咗!")


def cantonese_math_init():
    import math

    class Matrix(object):
        def __init__(self, list_a):
            assert isinstance(list_a, list)
            self.matrix = list_a
            self.shape = (len(list_a), len(list_a[0]))
            self.row = self.shape[0]
            self.column = self.shape[1]

        def __str__(self):
            return "Matrix: " + str(self.matrix)

        def build_zero_value_matrix(self, shape):
            zero_value_mat = []
            for i in range(shape[0]):
                zero_value_mat.append([])
                for j in range(shape[1]):
                    zero_value_mat[i].append(0)
            zero_value_matrix = Matrix(zero_value_mat)
            return zero_value_matrix

        def matrix_addition(self, the_second_mat):
            assert isinstance(the_second_mat, Matrix)
            assert the_second_mat.shape == self.shape
            result_mat = self.build_zero_value_matrix(self.shape)
            for i in range(self.row):
                for j in range(self.column):
                    result_mat.matrix[i][j] = (
                        self.matrix[i][j] + the_second_mat.matrix[i][j]
                    )
            return result_mat

        def matrix_multiplication(self, the_second_mat):
            assert isinstance(the_second_mat, Matrix)
            assert self.shape[1] == the_second_mat.shape[0]
            shape = (self.shape[0], the_second_mat.shape[1])
            result_mat = self.build_zero_value_matrix(shape)
            for i in range(self.shape[0]):
                for j in range(the_second_mat.shape[1]):
                    number = 0
                    for k in range(self.shape[1]):
                        number += self.matrix[i][k] * the_second_mat.matrix[k][j]
                    result_mat.matrix[i][j] = number
            return result_mat

    def corr(a, b):
        if len(a) == 0 or len(b) == 0:
            return None
        a_avg = sum(a) / len(a)
        b_avg = sum(b) / len(b)
        cov_ab = sum([(x - a_avg) * (y - b_avg) for x, y in zip(a, b)])
        sq = math.sqrt(
            sum([(x - a_avg) ** 2 for x in a]) * sum([(x - b_avg) ** 2 for x in b])
        )
        corr_factor = cov_ab / sq
        return corr_factor

    def KNN(inX, dataSet, labels, k):
        m, n = len(dataSet), len(dataSet[0])
        distances = []
        for i in range(m):
            sum = 0
            for j in range(n):
                sum += (inX[j] - dataSet[i][j]) ** 2
            distances.append(sum**0.5)
        sortDist = sorted(distances)
        classCount = {}
        for i in range(k):
            voteLabel = labels[distances.index(sortDist[i])]
            classCount[voteLabel] = classCount.get(voteLabel, 0) + 1
        sortedClass = sorted(classCount.items(), key=lambda d: d[1], reverse=True)
        return sortedClass[0][0]

    def l_reg(testX, X, Y):
        a = b = mxy = sum_x = sum_y = lxy = xiSubSqr = 0.0
        for i in range(len(X)):
            sum_x += X[i]
            sum_y += Y[i]
        x_ave = sum_x / len(X)
        y_ave = sum_y / len(X)
        for i in range(len(X)):
            lxy += (X[i] - x_ave) * (Y[i] - y_ave)
            xiSubSqr += (X[i] - x_ave) * (X[i] - x_ave)
        b = lxy / xiSubSqr
        a = y_ave - b * x_ave
        print("Linear function is:")
        print("y=" + str(b) + "x+" + str(a))
        return b * testX + a

    cantonese_func_def("KNN", KNN)
    cantonese_func_def("l_reg", l_reg)
    cantonese_func_def("corr", corr)
    cantonese_func_def("矩陣", Matrix)
    cantonese_func_def("點積", Matrix.matrix_multiplication)
    cantonese_func_def("相加", Matrix.matrix_addition)
    cantonese_func_def("開根", math.sqrt)
    cantonese_func_def("絕對值", math.fabs)
    cantonese_func_def("正弦", math.sin)
    cantonese_func_def("餘弦", math.cos)
    cantonese_func_def("正切", math.tan)
    cantonese_func_def("PI", math.pi)
    cantonese_func_def("E", math.e)
    cantonese_func_def("+oo", math.inf)


def cantonese_model_new(model, datatest, tab, code) -> str:
    if model == "KNN":
        code += tab + "print(KNN(" + datatest + ", 數據, 標籤, K))"
    elif model == "L_REG":
        code += tab + "print(l_reg(" + datatest + ", X, Y))"
    else:
        print("揾唔到你嘅模型: " + model + "!")
        code = ""
    return code


def cantonese_re_init() -> None:

    @define_func("襯唔襯")
    def can_re_match(pattern: str, string: str, flags=0):
        return re.match(pattern, string, flags)

    @define_func("襯")
    def can_re_match_out(pattern: str, string: str, flags=0) -> None:
        print(re.match(pattern, string, flags).span())


def cantonese_numpy_init() -> None:
    pass


def cantonese_random_init() -> None:
    import random

    cantonese_func_def("求其啦", random.random)
    cantonese_func_def("求其int下啦", random.randint)
    cantonese_func_def("求其嚟個", random.randrange)
    cantonese_func_def("是但揀", random.choice)
