# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-29 11:10:10
@LastEditTime: 2019-12-04 17:10:59
@Description:
'''


class PreprocessingContext(object):

    __instance = None
    __connections = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
            cls.__connections = {}

        return cls.__instance


    def set_connect(self, id, connection):
        self.__connections[id] = connection


    def get_connect(self, id):
        return self.__connections.get(id)


    def get_connect_dict(self):
        return self.__connections

