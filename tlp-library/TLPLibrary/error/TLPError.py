# -- coding: utf-8 --

import logging
import traceback

class TLPError(BaseException):
    '''TLPLibrary的异常定义
    '''

    def __init__(self, message):
        self.message = message

    def print_exception_stack(self):
        '''打印自定义异常信息
        将异常的堆栈信息转换为字符串，方便输出和记类
        '''
        from io import StringIO
        fp = StringIO()
        traceback.print_exc(file=fp)
        exception_stack = fp.getvalue()
        fp.close()
        exception_stack = self.message + "\n-------------stack info start -----------------\n" + exception_stack + "\n-------------stack info end-----------------\n"
        logging.error(exception_stack)


    def print_exception_message(self):
        '''将异常的信息输出到log中，不包含堆栈信息
        '''
        logging.error(self.message)

class ClassCastException(TLPError):
    """在处理张无法将参数转换为某个期望的类型时抛出的异常
    """

class DataBaseException(TLPError):
    """TLP数据库异常，用于封装数据库错误位可读信息
    """

class DataCastException(TLPError):
    """TLP 数据转换错误，用于抛出从数据库查询出来的数据转换位Entity时使用
    """

class DataTypeException(TLPError):
    """TLPLibrary指定的数据类型不匹配
    """

class ParameterNotFoundException(TLPError):
    """TLPLibrary指定的数据类型不匹配
    """

class NotFoundException(TLPError):
    """TLPLibrary指定的数据类型不匹配
    """

class RunTimeException(TLPError):
    """运行时异常
    """