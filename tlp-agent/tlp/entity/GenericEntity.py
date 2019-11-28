
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-25 10:08:44
@LastEditTime: 2019-11-26 17:09:47
@Description:
'''

import json
import datetime

from abc import ABCMeta, abstractclassmethod

from tlp.error import DataCastException

class GenericEntity(metaclass=ABCMeta):

    def __init__(self, **kwargs):
         self.__dict__.update(kwargs)


    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]

        return None


    def __setattr__(self, name, value):
        self.__dict__[name] = value


    def to_dict(self):
        '''
        @description: 返回对象属性的浅copy内容
        @return: {dict} 对象属性的字典
        '''
        return self.__dict__.copy()


    @classmethod
    def create_by_database_result(cls, data_result):
        if not isinstance(data_result, dict):
            raise DataCastException(message="data base result cast entity error")

        instance = cls.__new__(cls)
        for key in data_result:
            value = data_result[key]
            if isinstance(value, bytes):
                value = str(value, "utf-8")
            elif isinstance(value, datetime.datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")

            instance.__setattr__(key, value)

        return instance


    def to_json(self):
        return json.dumps(self.__dict__)


    @abstractclassmethod
    def convert_database_result_2_dict(cls, data_result):
        pass

    def to_value_list(self, property_list):
        value_list = []

        for property_name in property_list:
            value_list.append(self.__dict__[property_name])

        return value_list