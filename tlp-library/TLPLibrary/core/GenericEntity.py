# -- coding: utf-8 --

import json

from abc import ABCMeta, abstractclassmethod

class GenericEntity(metaclass=ABCMeta):
    '''通用实体的记类
    '''

    def to_dict(self):
        '''返回对象属性的浅copy内容

        Returns (dict):
            对象属性的字典.
        '''
        return self.__dict__.copy()

    def to_json(self):
        '''返回对象的JSON str的字符串

        Returns (str):
            JSON 格式的对象
        '''
        from TLPLibrary.core import JSONEncoder
        return json.dumps(self.__dict__, cls=JSONEncoder)