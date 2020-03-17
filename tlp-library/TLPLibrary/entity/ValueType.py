# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-11 19:03:30
@LastEditTime: 2020-03-17 16:37:22
@Description:
'''

class ValueType():

    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    NUMBER = "number"
    TEXT = "text"

    @staticmethod
    def check_type(type):
        if not isinstance(type, str):
            return False

        return (type == ValueType.NUMBER or type == ValueType.TEXT)
