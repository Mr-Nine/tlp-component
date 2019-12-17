
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 10:19:11
@LastEditTime: 2019-12-13 11:40:46
@Description:
'''

import datetime

class Utils(object):

    @staticmethod
    def __convert_n_bytes(n, b):
        bits = b * 8
        return (n + 2 ** (bits - 1)) % 2 ** bits - 2 ** (bits - 1)

    @staticmethod
    def __convert_4_bytes(n):
        return __convert_n_bytes(n, 4)

    @staticmethod
    def get_str_hashcode(string):
        h = 0
        n = len(string)
        for i, c in enumerate(string):
            h = h + ord(c) * 31 ** (n - 1 - i)

        return __convert_4_bytes(h)

    @staticmethod
    def transform_database_result_2_dict(data_result):
        instance = dict()

        for key in data_result:
                value = data_result[key]
                if isinstance(value, bytes):
                    value = str(value, "utf-8")
                elif isinstance(value, datetime.datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")

                instance[key] = value

        return instance