# -- coding: utf-8 --
'''
@Project:TLP
@Team:DCP team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-17 21:14:41
@LastEditTime: 2020-03-19 19:16:36
@Description:TLP模块上下文对象
'''

class TLPContext(object):

    __instance = None
    __cache_project_dict = None
    __connects_dict = None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
            cls.__cache_project_dict = dict()
            cls.__connects_dict = dict()
            cls.__default_attributes = None

        return cls.__instance


    def get_project_dict(self):
        return self.__cache_project_dict

    def get_project(self, project_id):
        if project_id in self.__cache_project_dict:
            return self.__cache_project_dict.get(project_id)
        return None

    def set_project(self, project):
        self.__cache_project_dict[project.id] = project


    def get_connect_dict(self):
        return self.__connects_dict

    def get_connect(self, connect_id):
        if connect_id in self.__connects_dict:
            return self.__connects_dict[connect_id]
        return None

    def set_connect(self, connect_id, connect_info):
        self.__connects_dict[connect_id] = connect_info

    def get_publisher(self, connect_id):
        if connect_id in self.__connects_dict and 'publisher' in self.__connects_dict[connect_id]:
            return self.__connects_dict[connect_id]['publisher']

        return None


    def set_default_attribute(self, defautl_attribute):
        self.__default_attributes = defautl_attribute

    def get_default_attribute(self):
        return self.__default_attributes

    def notice(self, message, projectId=None, userId=None):
        '''
        @description: 项目内发送消息通知，可以指定项目级别和用户两个范围
        @param {core.Message} messge:要通知的消息对象
        @param {string} projectId:需要通知的项目ID
        @param {string} userId:需要通知的用户ID
        '''

        if projectId is None and userId is None:
            return

        if projectId is not None and userId is not None:
            for connect_id in self.__connects_dict.keys():
                connect_info = self.__connects_dict[connect_id]
                if connect_info["project_id"] == projectId and connect_info['user_id'] == userId:
                    connect_info['connect'].write_message(message.to_json())
                    return

        if projectId is not None and userId is None:
            for connect_id in self.__connects_dict.keys():
                connect_info = self.__connects_dict[connect_id]
                if connect_info["project_id"] == projectId:
                    connect_info['connect'].write_message(message.to_json())

        if projectId is None and userId is not None:
            for connect_id in self.__connects_dict.keys():
                connect_info = self.__connects_dict[connect_id]
                if connect_info["user_id"] == userId:
                    connect_info['connect'].write_message(message.to_json())