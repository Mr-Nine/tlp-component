# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-05 16:33:35
@Description:
'''

import os
import sys
import time
import queue
import signal
import pickle
import asyncio
import logging
import threading
import traceback

import multiprocessing
from multiprocessing import Queue

from core import PreprocessingContext, Config
from handler import PreprocessingResultThread, PreprocessingWorkThread

class PreprocessingControllerThread(threading.Thread):

    work_result_queue = queue.Queue()
    send_thread_over_queue = queue.Queue()
    config = Config()

    def __init__(self, ws, pending_queue, state_queue):
        super(PreprocessingControllerThread, self).__init__()

        self.__ws = ws
        self.__pending_queue = pending_queue
        self.__state_queue = state_queue

        self.__running = threading.Event()
        self.__waiting = threading.Event()

        self.__sub_thread_array = []

        self.__result_thread = None
        self.__save_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending_image_list.data")

        self.__work_thread_count = self.config.default_max_processing_thread_number
        if self.__work_thread_count:
            self.__work_thread_count = int(multiprocessing.cpu_count() / self.config.default_concurrent_processes_number)

    def run(self):

        try:
            logging.info("preprocessing controller thread start, name:%s" % self.name)

            self.__running.set()
            self.__waiting.set()

            self.__result_thread = PreprocessingResultThread('preprocessing-result-thread', self.__ws, self.work_result_queue, self.send_thread_over_queue)
            self.__result_thread.start() # 启动监听结果的线程

            pending_image_list = []
            try:
                if os.path.exists(self.__save_file_path):
                    with open(self.__save_file_path, 'rb+') as load_file:
                        pending_image_list = pickle.load(load_file)
                        load_file.truncate()

                    if pending_image_list:
                        for image in pending_image_list:
                            self.__pending_queue.put(image)
                logging.info("%s:restore unprocessed pictures to the queue." % self.name)
            except Exception as e:
                logging.error("%s:failed to restore unprocessed pictures to the queue, error:"%(self.name, str(e)))


            # 设置线程得独立loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)


            sub_thread_wati_count = 1
            while self.__running.isSet():

                if len(self.__sub_thread_array) == self.__work_thread_count:
                    logging.debug("%s:waiting for the work thread queue to be free." % self.name)

                    time.sleep(sub_thread_wati_count)
                    if sub_thread_wati_count < self.config.default_max_sleep_time:
                        sub_thread_wati_count += 1

                    continue
                else:
                    sub_thread_wati_count = 1

                logging.debug("%s:check pause status." % self.name)
                self.__waiting.wait() # 如果线程没有暂停就继续

                '''
                从队列里获取新得图片，如果队列为空，
                则抛出异常捕获并休眠等待，
                为的是不阻塞回收线程的处理。
                '''
                image = None
                next_image_wati_count = 1
                while True:
                    try:
                        image = self.__pending_queue.get_nowait()
                        break
                    except queue.Empty as e:
                        if self.__running.isSet():
                            time.sleep(next_image_wati_count)
                            if next_image_wati_count < self.config.default_max_sleep_time:
                                next_image_wati_count += 1
                        else:
                            break

                if image:
                    thread_name = 'preprocessing-work-thread-' + image["id"]
                    work = PreprocessingWorkThread(thread_name, self.__ws, image, self.__sub_thread_array, self.work_result_queue)
                    work.start()
                    self.__sub_thread_array.append(work.name)

            logging.debug("%s:start processing thread recycling." % self.name)

            while self.__sub_thread_array:
                # 如果还有没有完成的线程，就等着
                logging.debug("%s:wait for the work thread to end." % self.name)
                time.sleep(3)

            logging.debug("%s:notify the send thread to end." % self.name)
            self.__result_thread.stop()
            send_thread_over_result = self.send_thread_over_queue.get() # 阻塞等待消息发送线程结束

            # 都结束了，开始处理未完成的数据
            logging.debug("%s:start processing incomplete data." % self.name)
            pending_image_list = []
            while not self.__pending_queue.empty():
                pending_image_list.append(self.__pending_queue.get())

            # 将未处理的数据保存到本地文件，等待再启动的时候恢复回来
            with open(self.__save_file_path, 'wb') as save_file:
                pickle.dump(pending_image_list, save_file)

            logging.debug("%s:incomplete data saved." % self.name)

            # for task in asyncio.Task.all_tasks():
            #     #task.cancel()
            #     print(task)

            # 保存完成，告诉父进程可以完了，我都弄好了
            self.__state_queue.put((True, "save pending success."))

            logging.info('%s:end of processing thread recycling.' % self.name)

        finally:
            if self.loop:
                self.loop.close() # 线程结束关闭loop


    def stop(self):
        self.__running.clear()


    def is_stoped(self):
        return self.__running.isSet()


    def pause(self):
        self.__waiting.clear()
        if self.__result_thread.isAlive():
            self.__result_thread.pause()


    def resume(self):
        self.__waiting.set()
        if self.__result_thread.isAlive():
            self.__result_thread.resume()

    def is_pause(self):
        return self.__waiting.isSet()
