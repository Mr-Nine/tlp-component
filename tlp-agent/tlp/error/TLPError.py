# -- coding: utf-8 --

'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-22 15:08:22
@LastEditTime: 2019-11-25 21:09:29
@Description:
'''

import logging
import traceback

class TLPError(BaseException):
    def __init__(self, message):
        self.message = message

    def print_exception_stack(self):
        from io import StringIO
        fp = StringIO()
        traceback.print_exc(file=fp)
        exception_stack = fp.getvalue()
        fp.close()
        exception_stack = self.message + "\n-------------stack info start -----------------\n" + exception_stack + "\n-------------stack info end-----------------\n"
        logging.error(exception_stack)


    def print_exception_message(self):
        logging.error(self.message)
