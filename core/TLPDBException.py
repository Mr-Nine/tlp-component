# -- coding: utf-8 --

'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-22 15:08:22
@LastEditTime: 2019-11-22 15:13:23
@Description:
'''

class TLPDBException(RuntimeError):
    def __init__(self, message):
        self.message = message