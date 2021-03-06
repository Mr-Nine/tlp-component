# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
LastEditTime: 2020-04-02 17:12:16
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

    def __init__(self, name, image, thread_array, result_queue, threading_lock):
        super(PreprocessingWorkThread, self).__init__()

        # 线程名称
        self.name = name
        # 要处理的目标图片
        self.__image = image
        # 父线程存放所有工作中线程的列表
        self.__thread_array = thread_array
        # 消息通信的队列
        self.__result_queue = result_queue
        # 程序配置对象
        self.__config = Config()
        # 锁
        self.__threading_lock = threading_lock


    def run(self):
        logging.debug("preprocessing work thread start, name:'%s'." % self.name)

        # time.sleep(random.randint(1,9))

        # 固定目录转换，比如mgt上的路径是/a/b/c/image，到了切图服务器上需要转换位/d/e/f/image
        image_real_path = self.__image['path']
        for conver in self.__config.path_conversion_list:
            if conver['source'] in image_real_path:
                image_real_path = image_real_path.replace(conver['source'], conver['target'])
                break

        if not os.path.exists(image_real_path):
            logging.warn("image not fond, image id: %s, path: %s." % (self.__image['id'], self.__image['path']))
            self.__result_queue.put({'state':False, "message":"图片不存在，无法执行", 'imageId':self.__image['id'], 'path':self.__image['path']})
            self.__delete_self_name_by_thread_list()
            return

        work_process = PreprocessingWorkProcess(
            name="preprocessing-work-process-" + self.__image['id'],
            image_id=self.__image['id'],
            image_path=image_real_path,
            save_root_path=self.__config.tiles_save_root_path,
            processes=self.__config.default_concurrent_processes_number,
            progress_queue=self.__result_queue
        )
        work_process.start()
        work_process.join()

        self.__result_queue.put({"message":"子进程干完了", 'imageId':self.__image['id'], 'path':self.__image['path']})

        self.__delete_self_name_by_thread_list()

    def __delete_self_name_by_thread_list(self):
        self.__threading_lock.acquire()
        logging.info("%s lock thread array."%self.name)
        for i in range(len(self.__thread_array)):
            if self.__thread_array[i] == self.name:
                del self.__thread_array[i]
                break
        self.__threading_lock.release()
        logging.info("%s release thread array."%self.name)