"""
    Exception class for parser
"""


class CompTimeException(Exception):
    pass


class NoTokenException(CompTimeException):
    """
    `Token`长度唔够
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class LexerException(CompTimeException):
    """
    词法分析错误
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class NoParseException(CompTimeException):
    """
    解析错误
    """

    def __init__(self, message, state=None):
        self.message = message
        self.state = state

    def __str__(self):
        return self.message


class ExprParserExceprion(CompTimeException):
    """
    表达式解释错误
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class StatParserException(CompTimeException):
    """
    语句解释错误
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MacroNotFound(CompTimeException):
    """
    找不到宏
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MacroNotMatchException(CompTimeException):
    """
    宏找不到匹配
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class MacroCanNotExpand(CompTimeException):
    """
    宏无法展开
    """

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
