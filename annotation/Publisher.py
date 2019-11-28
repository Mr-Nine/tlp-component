# -- coding: utf-8 --
__author__ = 'dcp team dujiujun - tlp-agent'

'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 10:58:00
@LastEditTime: 2019-11-27 13:50:25
@Description:
'''

import sys
import datetime
import traceback
import logging

from core import TLPDBException, Message
from annotation.model import AbstractModel
from tlp.error import *


class Publisher(object):

    __instance = None

    def __init__(self, websocket, user, *args, **kwargs):
        """
        """
        self.__models = dict()

        __import__("annotation.model") # 动态导入模块
        handlers = sys.modules["annotation.model"] # 获取模块的对象
        attributes = dir(handlers) # 获取模块内的所有属性

        # 遍历这个模块下的所有对象属性
        for attr in attributes:
            attribute = getattr(handlers, attr) # 获得属性对象
            if type(attribute) == type and AbstractModel in attribute.__bases__:
                model = attribute(websocket, user) # 获得类的实例
                self.__models[model.mid] = model # 注册这个类
                logging.debug("model %s regist", model.mid)


    def dispatcher_message(self, message):
        if ((self.check_message(message)) and (message.targetMid.lower() in self.__models)):

            logging.debug("Dispactcher message by target mid: %s." % message.targetMid)

            response_message = None

            try:
                module = self.__models[message.targetMid.lower()]
                response_message = module.receive_message(message)
            except DataBaseException as e1:
                # 数据库操作异常
                e1.print_exception_stack()
                return self.create_global_message(message.senderMid, "10001").to_json()
            except DataCastException as e2:
                # 数据转换错误
                e2.print_exception_stack()
                return self.create_global_message(message.senderMid, "10002").to_json()
            except RunTimeException as e3:
                e3.print_exception_stack()
                return self.create_global_message(message.senderMid, "10003").to_json()
            except BaseException as e4:
                # 运行时异常
                logging.error("Error info {}".format(e4))
                traceback.print_exc(file=sys.stdout)
                return self.create_global_message(message.senderMid, "10004").to_json()

            return response_message
        else:
            logging.debug("Disable message: %s" % message.senderMid)
            return None


    def destroy(self):
        logging.debug("Message publisher destory!")
        for key in list(self.__models.keys()):
            self.__models[key].destroy()
            del(self.__models[key])


    def check_message(self, message):
        if (not hasattr(message, 'targetMid') or message.targetMid.strip() == ""):
            return False

        if (not hasattr(message, 'messageType') or message.messageType.strip() == ""):
            return False

        if (not hasattr(message, 'senderMid') or message.senderMid.strip() == ""):
            return False

        return True

    def create_global_message(self, targetMid, exception):
        message = Message()
        message.senderMid = 'global'
        message.targetMid = targetMid
        message.messageType = 'error'
        message.createTime = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
        message.senderTime = message.createTime
        message.tnsNumber = 0
        message.data = {"exception":exception}

        return message

    @property
    def models(self):
        return self.__models
