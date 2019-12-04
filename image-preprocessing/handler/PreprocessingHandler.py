# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-28 16:58:42
@LastEditTime: 2019-12-04 17:21:58
@Description:
'''

import os
import sys
import json
import time
import types
import logging
import asyncio
import traceback
# import copyreg
import queue

import tornado.web
import tornado.websocket

from concurrent.futures import ThreadPoolExecutor
from tornado.concurrent import run_on_executor

from core import PreprocessingContext
from handler import HeartCheck, PreprocessingControllerThread


'''
# python的腌制问题还没弄好
def _pickle_method(m):
    if m.im_self is None:
        return getattr, (m.im_class, m.im_func.func_name)
    else:
        return getattr, (m.im_self, m.im_func.func_name)

copyreg.pickle(types.MethodType, _pickle_method)
'''

class PreprocessingHandler(tornado.websocket.WebSocketHandler):

    __context = PreprocessingContext()
    pending_image_queue = queue.Queue()
    controller_thread_state_queue = queue.Queue()

    def initialize(self):
        # , loop self.loop = loop
        self._controllerThread = None
        self.__working = True

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

            if self._controllerThread is None:
                # 如果控制进程没有启动，则启动预处理切图进程
                self._controllerThread = PreprocessingControllerThread(ws=self, pending_queue=self.pending_image_queue, state_queue=self.controller_thread_state_queue)
                self._controllerThread.name = "ImagePreprocessingThread"
                self._controllerThread.start()

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
        message = json.loads(msg)

        if 'senderMid' in message:
            return

        logging.debug(u"Receive message: %s, self id: %s" % (msg, self._id()))

        # 检查接收到的消息是否是要处理图片的要求
        if 'action' not in message:
            self.write_message(self._create_ws_base_message({'state':False, 'message':'requests not accepted.'}))

        action = message['action']

        if  action == 'preprocessing' and self.__working:
            # 拆分要求处理的图片信息
            if 'data' not in message or not message['data']:
                self.write_message(self._create_ws_base_message({'state':False, 'message':'no picture information found to process.'}))

            if self._controllerThread.isAlive():
                logging.debug("add pending pictrue 2 queue.")
                images = message['data']
                for image in images:
                    '''{
                        "id":"图片在仓库的ID",
                        "path":"图片的具体路径"
                    }
                    '''
                    self.pending_image_queue.put(image)
            else:
                # 错误了，线程没或者就没办法处理，应该告诉DCP那边
                self.write_message(self._create_ws_base_message({'state':False, 'message':'Preprocessor does not start.'}))
                return

        elif action == 'stop':
            self.__working = False # 关闭接受
            if self._controllerThread.isAlive():
                self._controllerThread.stop()


    def send_msg(self, msg):
        self.write_message(msg)


    def on_ping(self, data):
        """心跳包响应, data是`.ping`发出的数据
        """
        logging.info('Into on_ping the data is |%s|' % data)


    def on_pong(self, data):
        """ 心跳包响应, data是`.ping`发出的数据
        """
        logging.info('Into on_pong the data is |%s|' % data)


    def on_close(self, transfer=True):
        '''
        @description: 当本条ws被关闭的时候被调用，要处理工作的子线程回收
        '''
        connection = self.__context.get_connect(self._id())
        if connection is not None:
            del self.__context.get_connect_dict()[self._id()]
            self.hc.close()
            logging.debug("client close the connection id:%s, current connection count:%s" % (self._id(), str(len(self.__context.get_connect_dict().keys()))))

        if self._controllerThread.isAlive():
            self._controllerThread.stop() # 结束处理控制器线程
            close_result = self.controller_thread_state_queue.get() # 阻塞等待处理控制作为收尾工作

            if close_result[0]:
                logging.info("线程回收完毕")
            else:
                logging.error("线程回收失败，错误原因:%s" % close_result[1])


    def check_origin(self, origin):
        """同源检查，当前默认返回TRUE，后面可能会有变化
        """
        logging.debug(u"New websocket connection, check origin.")
        return True


    def _create_ws_base_message(self, data):
        return json.dumps(data)


    def heart_check(self):
        self.write_message(self._create_ws_base_message())
