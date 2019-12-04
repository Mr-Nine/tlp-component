# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-03 17:56:08
@Description:要做的事情：
1)检查和生成存储目录
2)生成缩略图
3)启动切图的进程，切图
'''


import os
import sys
import time
import signal
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
        time1 = time.time()
        lock = threading.Lock()
        print("------------------------------------------")
        print(self.getName())
        print(self.__thread_array)
        print("我在生成缩略图")
        time.sleep(5)
        print("我启动了子进程并等着它干活")
        time.sleep(5)
        # TODO:改为管道发送
        # loop = asyncio.get_event_loop()
        # loop.run_until_complete(self.__ws.write_message({"message":"子进程干完了"}))
        self.__result_queue.put({"message":"子进程干完了"})
        lock.acquire()
        for i in range(len(self.__thread_array)):
            if self.__thread_array[i] == self.name:
                del self.__thread_array[i]
                break
        lock.release()
        time2 = time.time()
        print(time2-time1)
        print("------------------------------------------")
