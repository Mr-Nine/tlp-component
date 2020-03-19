# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:14:30
@LastEditTime: 2020-03-19 18:03:20
@Description:
'''
import datetime
import json

from core.utils import get_current_datetime_string

class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        # elif isinstance(obj, date):
        #     return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)

class Message(object):

    def __init__(self, senderMid = None, messageType = None, targetMid = None, tnsNumber = None, data = None):
        self.senderMid = senderMid
        self.targetMid = targetMid
        self.messageType = messageType
        self.createTime = None # get_current_datetime_string()
        self.senderTime = None # self.createTime
        self.tnsNumber = tnsNumber
        self.data = data


    def to_json(self):
        # x = self.data
        # self.data = lambda x: x.encode('ascii') if isinstance(x, unicode) else x
        return json.dumps(self.__dict__, cls=DateEncoder)


    def fromJson(self, data=""):
        self.__dict__ = json.loads(data)


    def to_string(self):
        """
        简单地实现类似对象打印的方法
        :param cls: 对应的类(如果是继承的类也没有关系，比如A(object), cls参数传object一样适用，如果你不想这样，可以修改第一个if)
        :param obj: 对应类的实例
        :return: 实例对象的to_string
        """
        to_string = str(self.__name__) + "("
        items = self.__dict__
        n = 0
        for k in items:
            if k.startswith("_"):
                continue
            to_string = to_string + str(k) + "=" + str(items[k]) + ","
            n += 1
        if n == 0:
            to_string += str(self.__name__).lower() + ": 'Instantiated objects have no property values'"
        return to_string.rstrip(",") + ")"
