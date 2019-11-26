# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 11:19:32
@LastEditTime: 2019-11-21 15:36:56
@Description:
'''

import sys
import logging

class AbstractModel(object):
    """处理模块的基类，保存关键的mid信息和定义了接收消息的函数
    """

    def __init__(self, mid, name, model_name, websocket, user):
        self._handlers = dict()
        self._mid = mid
        self._name = name
        self._model_name = model_name
        self.add_handler(websocket, user)

    @property
    def mid(self):
        return self._mid

    @property
    def name(self):
        return self._name

    @property
    def handler(self):
        return self._handlers

    def receive_message(self, message):
        if (message.messageType.lower() in self._handlers):
            replyMessage = self._handlers[message.messageType.lower()].handle(message)
            if replyMessage is not None:
                replyMessage.senderMid = self._mid
                return replyMessage.to_json()

            return None
        else:
            logging.warn("Undefined message type %s", message.messageType)

    def destroy(self):
        for key in list(self._handlers.keys()):
            self._handlers[key].destroy()
            del(self._handlers[key])

    def add_handler(self, websocket, authenticator):
        __import__(self._model_name)
        handlers = sys.modules[self._model_name]
        attributes = dir(handlers)

        from annotation.model.handler import AbstractHandler

        for attr in attributes:
            attribute = getattr(handlers, attr)
            if type(attribute) == type and AbstractHandler in attribute.__bases__:
                model = attribute(websocket, authenticator)
                self._handlers[model.messageType] = model

