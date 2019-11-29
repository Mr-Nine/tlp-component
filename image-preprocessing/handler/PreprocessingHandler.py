# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-28 16:58:42
@LastEditTime: 2019-11-29 16:27:42
@Description:
'''

import sys
import json
import time
import logging
import asyncio
import traceback

import tornado.web
import tornado.websocket

from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from core import PreprocessingContext
from handler import HeartCheck

class PreprocessingHandler(tornado.websocket.WebSocketHandler):

    executor = ThreadPoolExecutor(2)
    __context = PreprocessingContext()

    def initialize(self, loop):
        self.loop = loop

    def _id(self):
        '''
        @description:获取连接对象的唯一标识
        @return:当前连接的唯一标识
        '''
        return id(self)


    # 连接权限检查
    def __check_connection_user(self, *args, **kwargs):
        '''
        @description:检查连接的用户是否符合连接要求
        @param {MysqlManager} mysql:mysql连接器
        @return:tuple
        '''
        logging.info("New websocket connection, check connecting authenticator.")

        # self.context = self.request.connection.context

        return True


    def _send_ws_message_and_close_connection(self, log, error_code, reason):
        '''
        @description:发送ws层的消息
        @param {string} log:错误日志
        @param {int} error_code:错误码
        @param {string} reason:错误消息
        '''
        logging.error(log)
        self.write_message(self._create_ws_base_message("error", {'message':error_code, 'reason':reason}))
        super(PreprocessingHandler, self).close()


    def open(self, *args, **kwargs):
        '''
        @description:
        @param {type}
        @return:
        '''
        """ws打开连接时执行的动作，加入一个新的客户端到管理字典
        """

        try:
            checkResult = self.__check_connection_user(args, kwargs)
            if not checkResult:
                self._send_ws_message_and_close_connection("Web socket not init, connection user check fail.")
                return

            connectionId = self._id()

            connectionInfo = {}
            connectionInfo["connect"] = self

            self.__context.set_connect(self._id(), connectionInfo)

            # 后端主动心跳机制
            if ('hc' not in dir()):
                self.hc = HeartCheck(self)
                self.hc.start()
            # self.loop.add_callback(self.heart_check)

            opened_result = {}
            opened_result["state"] = True
            opened_result["message"] = 'connection image preprocessing agent success.'

            self.write_message(self._create_ws_base_message(opened_result))

        except BaseException as e:
            if self.__context.get_connect(self._id()):
                del self.__context.get_connect_dict()[self._id()]
            traceback.print_exc(file=sys.stdout)


    def on_message(self, msg):
        """websocket接收到客户端发送的消息时的处理函数
        """
        logging.debug(u"Receive message: %s, self id: %s" % (msg, self._id()))

        # 检查接收到的消息是否是要处理图片的要求
        if 'action' not in msg or msg['action'] != 'preprocessing':
            self.write_message(self._create_ws_base_message({'state':False, 'message':'requests not accepted.'}))

        # 拆分要求处理的图片信息
        if 'data' not in msg or not msg['data']:
            self.write_message(self._create_ws_base_message({'state':False, 'message':'no picture information found to process.'}))

        images = msg['data']



        pass


    def on_ping(self, data):
        """心跳包响应, data是`.ping`发出的数据
        """
        logging.info('Into on_ping the data is |%s|' % data)


    def on_pong(self, data):
        """ 心跳包响应, data是`.ping`发出的数据
        """
        logging.info('Into on_pong the data is |%s|' % data)


    def on_close(self, transfer=True):
        connection_info = self.__context.get_connect(self._id())
        if connection_info is not None:
            connection_info["publisher"].destroy()
            del self.__context.get_connect_dict()[self._id()]
            logging.debug("client close the connection id:%s, current connection count:%s" % (self._id(), str(len(self.__context.get_connect_dict().keys()))))


    def check_origin(self, origin):
        """同源检查，当前默认返回TRUE，后面可能会有变化
        """
        logging.debug(u"New websocket connection, check origin.")
        return True


    def _create_ws_base_message(self, data):
        return json.dumps(data)


    # @run_on_executor
    def heart_check(self):
        while True:
            self.write_message(self._create_ws_base_message({'message':'heart check'}))
            time.sleep(20)

