# -- coding: utf-8 --
__author__ = 'dcp team dujiujun - tlp-agent'
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 11:19:43
@LastEditTime: 2019-11-21 14:40:18
@Description:
'''

import logging.config

from core import MessageMid, Message

class AbstractHandler(object):
    """所有Handler的基类，定义类基础的类结构和关键属性
    """

    def __init__(self, messageType, websocket, user):
        self.__messageType = messageType
        self.__websocket = websocket
        self.__user = user

    @property
    def messageType(self):
        return self.__messageType

    @property
    def user(self):
        return self.__user

    @property
    def websocket(self):
        return self.__websocket

    def handle(self, message):
        """所有子类必须实现的方法，负责处理请求的消息
        """
        raise ReferenceError("the message_receiver method should be implemented")

    def destroy(self):
        """所有子类的必须实现的方法，负责在整体连接销毁时提供回收占用资源的方法
        """
        raise ReferenceError("the destroy method should be implemented")

    def replyMessage(self, receivedMessage, state = False, msg = 'error info.', **kwargs):
        """
        """
        kwargs["state"] = state
        kwargs["message"] = msg

        return Message(messageType = self.messageType, targetMid = receivedMessage.senderMid, tnsNumber = receivedMessage.tnsNumber, data = kwargs)