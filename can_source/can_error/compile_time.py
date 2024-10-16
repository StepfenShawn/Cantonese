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


class LexerException(Exception):
    """
    词法分析错误
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NoParseException(Exception):
    """
    解析错误
    """

    def __init__(self, message, state=None):
        self.message = message
        self.state = state

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


class MacroCanNotExpand(Exception):
    """
    宏无法展开
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
