# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-11 19:03:30
@LastEditTime: 2019-12-16 17:02:42
@Description:
'''

class ValueType():

    INT = "INT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    TEXT = "TEXT"

    @staticmethod
    def check_type(type):
        if not isinstance(type, str):
            return False

        return (type == ValueType.INT or type == ValueType.FLOAT or type == ValueType.DOUBLE or type == ValueType.TEXT)
