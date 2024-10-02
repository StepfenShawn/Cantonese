import re

"""
    Exception class for parser
"""


class NoTokenException(Exception):
    """
    `Token`长度唔够
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class ExprParserExceprion(Exception):
    """
    表达式解释错误
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class StatParserException(Exception):
    """
    语句解释错误
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MacroNotMatchException(Exception):
    """
    宏找不到匹配
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def error_stdout(ty, info):
    if ty == "NameError":
        return re.sub(r"name '(.*)' is not defined", r"唔知`\1`係咩", info)
    return f"{ty}:{info}"
