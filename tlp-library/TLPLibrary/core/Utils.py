# -- coding: utf-8 --

import datetime

class Utils(object):
    '''TLPLibrary的工具类
    '''

    @staticmethod
    def __convert_n_bytes(n, b):
        '''
        '''
        bits = b * 8
        return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)

    @staticmethod
    def __convert_4_bytes(n):
        return __convert_n_bytes(n, 4)

    @staticmethod
    def get_str_hashcode(string):
        '''计算字符串的java版本的hashcode.

        Args:
            string (str): 需要计算hashcode的字符串
        '''
        h = 0
        n = len(string)
        for i, c in enumerate(string):
            h = h + ord(c) * 31 ** (n - 1 - i)

        return __convert_4_bytes(h)

    @staticmethod
    def transform_database_result_2_dict(data_result):
        '''转换数据库的返回结果dict为一个python的dict
        主要是将数据库字符串的byte转为为python的str

        Args:
            data_result (dict): 数据库查询结果的dict对象
        '''
        instance = dict()

        for key in data_result:
                value = data_result[key]
                if isinstance(value, bytes):
                    value = str(value, "utf-8")
                elif isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")

                instance[key] = value

        return instance