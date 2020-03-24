# -- coding: utf-8 --

class ValueType():
    '''label的attribute的值类型常量
    NUMBER:数值类型
    TEXT:文本类型
    CASCADER:多级选择
    '''
    INT = "int"
    FLOAT = "float"
    DOUBLE = "double"
    NUMBER = "number"
    TEXT = "text"
    CASCADER = "cascader"

    @staticmethod
    def check_type(type):
        '''检查当前类型是否是一个合格的ValueType

        Args:
            type (str): 值类型
        '''
        if not isinstance(type, str):
            return False

        return (type == ValueType.NUMBER or type == ValueType.TEXT or type == ValueType.CASCADER)
