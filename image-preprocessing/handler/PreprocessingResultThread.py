# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-03 17:43:07
@Description:要做的事情：
等待图片处理work线程的运行，知道队列中有了返回值，就组织返回值发送给前端
'''


import os
import sys
import time
import signal
import asyncio
import threading
import traceback

import multiprocessing

from core import PreprocessingContext


class PreprocessingResultThread(threading.Thread):

    def __init__(self, name, ws, result_queue):
        super(PreprocessingResultThread, self).__init__()

        self.name = name
        self.__ws = ws
        self.__result_queue = result_queue
        self.__running = threading.Event()
        self.__waiting = threading.Event()


    def run(self):
        '''
        @description: 获取返回结果并发送给DCP,有三个阻塞点，是否运行，是否暂停，是否有需要发送的结果
        @param {type}
        @return:
        '''
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        self.__running.set()
        self.__waiting.set()

        while self.__running.isSet():

            self.__waiting.wait() # 检查是否暂停(前端断开)

            result = self.__result_queue.get()

            print(result)
            # TODO:发送返回结果到前端


    def stop(self):
        self.__running.clear()


    def is_stoped(self):
        return self.__running.isSet()


    def pause(self):
        self.__waiting.clear()


    def resume(self):
        self.__waiting.set()


    def is_pause(self):
        return self.__waiting.isSet()