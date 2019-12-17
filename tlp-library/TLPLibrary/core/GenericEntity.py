
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-25 10:08:44
@LastEditTime: 2019-12-12 19:11:08
@Description:
'''

import json

from abc import ABCMeta, abstractclassmethod

class GenericEntity(metaclass=ABCMeta):

    def to_dict(self):
        '''
        @description: 返回对象属性的浅copy内容
        @return: {dict} 对象属性的字典
        '''
        return self.__dict__.copy()

    def to_json(self):
        from TLPLibrary.core import JSONEncoder
        return json.dumps(self.__dict__, cls=JSONEncoder)