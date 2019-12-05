# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-05 21:06:00
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
from multiprocessing import Queue

from core import PreprocessingContext, Config
from handler import PreprocessingWorkProcess


class PreprocessingWorkThread(threading.Thread):

    def __init__(self, name, ws, image, thread_array, result_queue):
        super(PreprocessingWorkThread, self).__init__()

        self.name = name
        self.__ws = ws
        self.__image = image
        self.__thread_array = thread_array
        self.__result_queue = result_queue
        self.__config = Config()


    def run(self):
        logging.debug("preprocessing work thread start, name:'%s'." % self.name)

        lock = threading.Lock()

        # time.sleep(random.randint(1,9))

        image_real_path = self.__image['path']
        for conver in self.__config.path_conversion_list:
            if conver['source'] in image_real_path:
                image_real_path = image_real_path.replace(conver['source'], conver['target'])
                break

        if not os.path.exists(image_real_path):
            self.__result_queue.put({"message":"图片不存在，无法执行"})
            self.__delete_self_name_by_thread_list(lock)
            return

        work_process = PreprocessingWorkProcess(
            name="preprocessing-work-thread-" + self.__image['id'],
            image_id=self.__image['id'],
            image_path=image_real_path,
            save_root_path=self.__config.tiles_save_root_path,
            processes=self.__config.default_concurrent_processes_number,
            progress_queue=self.__result_queue
        )
        work_process.start()
        work_process.join()

        self.__result_queue.put({"message":"子进程干完了"})

        self.__delete_self_name_by_thread_list(lock)

    def __delete_self_name_by_thread_list(self, lock):
        lock.acquire()
        for i in range(len(self.__thread_array)):
            if self.__thread_array[i] == self.name:
                del self.__thread_array[i]
                break
        lock.release()