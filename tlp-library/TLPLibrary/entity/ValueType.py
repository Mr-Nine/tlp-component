# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-11 19:03:30
@LastEditTime: 2019-12-18 18:31:43
@Description:
'''

class ValueType():

    INT = "INT"
    FLOAT = "FLOAT"
    DOUBLE = "DOUBLE"
    NUMBER = "NUMBER"
    TEXT = "TEXT"

    @staticmethod
    def check_type(type):
        if not isinstance(type, str):
            return False

        return (type == ValueType.NUMBER or type == ValueType.TEXT)
