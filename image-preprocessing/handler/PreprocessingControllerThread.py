# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-04 10:33:56
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

from core import PreprocessingContext
from handler import PreprocessingResultThread, PreprocessingWorkThread


class PreprocessingControllerThread(threading.Thread):

    work_result_queue = queue.Queue()

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


    def run(self):

        try:
            logging.info("我是处理程序的子进程，我启动了")

            self.__running.set()
            self.__waiting.set()

            self.__result_thread = PreprocessingResultThread('preprocessing-result-thread', self.__ws, self.work_result_queue)
            self.__result_thread.start() # 启动监听结果的线程
            logging.info("我启动了监听结果的进程")

            pending_image_list = []
            try:
                if os.path.exists(self.__save_file_path):
                    with open(self.__save_file_path, 'rb') as load_file:
                        pending_image_list = pickle.load(load_file)
                    # print(pending_image_list)

                    if pending_image_list:
                        for image in pending_image_list:
                            self.__pending_queue.put(image)
                logging.info("我恢复了未处理完成的图片列表")
            except Exception as e:
                logging.error("恢复未处理的数据失败:{}".format(e))


            # 设置线程得独立loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            logging.info("我创建了我的event loop")

            process_count = int(multiprocessing.cpu_count() / 2)
            if process_count - 1 == 0:
                process_count = 1
            else:
                process_count = process_count - 1

            count = 0
            image = self.__pending_queue.get()
            while self.__running.isSet():
                # 如果线程没有结束
                print("开始处理图片")
                if len(self.__sub_thread_array) == 3:
                    logging.info("wait work run over.")
                    # 这个不能删，测试完了也不能删，因为没有队列空间时间会比较长，所以一定要等
                    time.sleep(3)
                    continue

                self.__waiting.wait() # 如果线程没有暂停

                thread_name = 'preprocessing-work-thread-' + image["id"]
                work = PreprocessingWorkThread(thread_name, self.__ws, image, self.__sub_thread_array, self.work_result_queue)
                work.start()
                self.__sub_thread_array.append(work.name)

                time.sleep(2)
                count += 1
                logging.info("我创建了我的新的work thread:%s"%thread_name)
                print(image)

                '''
                if not self.__running.isSet():
                    # 如果当前线程已经不运行了，则让loop等到发送返回值的消息完成后才继续(阻塞解释，直到都发出去)
                    loop.run_until_complete(self.__ws.write_message("监控数据:%d"%count))
                else:
                    self.__ws.write_message("监控数据:%d"%count)
                '''
                print("获取下一张图片")
                # 从队列里获取新得图片，如果队列为空，则阻塞等待
                # 但是为了不阻塞结束的进程，所以增加了一层循环，控制退出
                while True:
                    try:
                        image = self.__pending_queue.get_nowait()
                        break
                    except queue.Empty as e:
                        if self.__running.isSet():
                            time.sleep(1)
                        else:
                            break


            # 如果线程不玩了，处理收尾工作
            while self.__sub_thread_array:
                # 如果还有没有完成的线程，就等着
                time.sleep(3)

            print("1")

            # 都结束了，开始处理未完成的数据
            pending_image_list = []
            while not self.__pending_queue.empty():
                pending_image_list.append(self.__pending_queue.get())

            print("2")

            # 将未处理的数据保存到本地文件，等待再启动的时候恢复回来
            with open(self.__save_file_path, 'wb') as save_file:
                pickle.dump(pending_image_list, save_file)
                # save_file.write(d)
                # save_file.flush()

            print("3")

            # 保存完成，告诉父进程可以完了，我都弄好了
            self.__state_queue.put((True, "save pending success."))
            print('%s has done' % self.name)

        finally:
            if self.loop:
                self.loop.close() # 线程结束关闭loop


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



    # if self.__ws:
    #     if not self.__running.isSet():
    #         # 如果当前线程已经不运行了，则让loop等到发送返回值的消息完成后才继续(阻塞解释，直到都发出去)
    #         self.loop.run_until_complete(self.__ws.write_message("监控数据:%d"%result))
    #     else:
    #         self.__ws.write_message("监控数据:%d"%result)
