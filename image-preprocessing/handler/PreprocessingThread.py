# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-02 18:39:36
@Description:
'''

import os
import time
import signal
import asyncio
import threading

import multiprocessing

from core import PreprocessingContext

class PreprocessingThread(threading.Thread):

    def __init__(self, ws):
        super(PreprocessingThread, self).__init__()

        self.__running = threading.Event()
        self.__ws = ws


    def run(self):

        try:
            print("我是处理程序的子进程，我启动了")
            # time.sleep(3)
            print("我去启动我的子进程去了。")

            self.__running.set()

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            process_count = multiprocessing.cpu_count() / 2
            if process_count - 1 == 0:
                process_count = 1
            else:
                process_count = process_count - 1

            count = 0
            while self.__running.isSet():
                time.sleep(3)
                count += 1
                # print("监控数据:%d"%count)
                if self.__ws:
                    if not self.__running.isSet():
                        # 如果当前线程已经不运行了，则让loop等到发送返回值的消息完成后才继续(阻塞解释，直到都发出去)
                        loop.run_until_complete(self.__ws.write_message("监控数据:%d"%count))
                    else:
                        self.__ws.write_message("监控数据:%d"%count)

                print("OK")

            print('%s has done' % self.name)
        finally:
            loop.close()


    def stop(self):
        self.__running.clear()

    def is_stoped(self):
        return self.__running.isSet()