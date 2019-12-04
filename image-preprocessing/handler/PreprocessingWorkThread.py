# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-04 17:39:09
@Description:要做的事情：
1)检查和生成存储目录
2)生成缩略图
3)启动切图的进程，切图
'''


import os
import sys
import time
import signal
import random
import logging
import asyncio
import threading
import traceback

import multiprocessing

from multiprocessing import Pool

from core import PreprocessingContext


class PreprocessingWorkThread(threading.Thread):

    def __init__(self, name, ws, image, thread_array, result_queue):
        super(PreprocessingWorkThread, self).__init__()

        self.name = name
        self.__ws = ws
        self.__image = image
        self.__thread_array = thread_array
        self.__result_queue = result_queue


    def run(self):
        logging.debug("preprocessing work thread start, name:'%s'." % self.name)

        lock = threading.Lock()

        time.sleep(random.randint(1,9))
        # TODO:改为管道发送
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.__ws.write_message({"message":"子进程干完了"}))
        self.__result_queue.put({"message":"子进程干完了"})

        self.__delete_self_name_by_thread_list(lock)

    def __delete_self_name_by_thread_list(self, lock):
        lock.acquire()
        for i in range(len(self.__thread_array)):
            if self.__thread_array[i] == self.name:
                del self.__thread_array[i]
                break
        lock.release()