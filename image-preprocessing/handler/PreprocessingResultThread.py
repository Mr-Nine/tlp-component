# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2020-03-06 18:52:13
@Description:要做的事情：
等待图片处理work线程的运行，知道队列中有了返回值，就组织返回值发送给前端
'''


import os
import sys
import time
import json
import queue
import signal
import pickle
import asyncio
import logging
import threading
import traceback

import multiprocessing

from core import PreprocessingContext

class PreprocessingResultThread(threading.Thread):

    def __init__(self, name, ws, result_queue, over_queue):
        super(PreprocessingResultThread, self).__init__()

        self.name = name
        self.__ws = ws

        self.__result_queue = result_queue
        self.__over_queue = over_queue

        self.__running = threading.Event()
        self.__waiting = threading.Event()

        self.__running.set()
        self.__waiting.set()

        self.__save_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pending_message_list.data")


    def run(self):
        '''
        @description: 获取返回结果并发送给DCP,有三个阻塞点，是否运行，是否暂停，是否有需要发送的结果
        @param {type}
        @return:
        '''
        logging.info("preprocessing result thread start, name:%s" % self.name)

        try:
            try:
                pending_message_list = []
                if os.path.exists(self.__save_file_path):
                    with open(self.__save_file_path, 'rb+') as load_file:
                        pending_message_list = pickle.load(load_file)
                        load_file.truncate()

                    if pending_message_list:
                        for message in pending_message_list:
                            self.__result_queue.put(message)
                logging.info("%s:recover unsent messages to a thread." % self.name)
            except Exception as e:
                logging.error("%s:recovery of unsent messages failed, error:%s" % (self.name, str(e)))

            # time.sleep(3) # TODO:为了两次连接等待ws的正式建立，具体sleep的时间应该看

            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            if self.__running.isSet() and self.__ws.ws_connection:
                # 在运行，有ws连接，有需要发送的返回值
                opened_result = {}
                opened_result["type"] = 'system'
                opened_result["state"] = True
                opened_result["message"] = 'connection image preprocessing agent success.'
                self.loop.run_until_complete(self.__ws.write_message(json.dumps(opened_result)))

            while self.__running.isSet():
                self.__waiting.wait()

                next_result_wati_count = 1
                result = None
                while True:
                    try:
                        result = self.__result_queue.get_nowait()
                        break
                    except queue.Empty as e:
                        if self.__running.isSet():
                            time.sleep(next_result_wati_count)
                            if next_result_wati_count < 30:
                                next_result_wati_count += 1
                        else:
                            break

                if self.__running.isSet() and self.__ws.ws_connection and result:
                    # 在运行，有ws连接，有需要发送的返回值
                    reply_message = json.dumps(result)
                    logging.debug("--- reply client:%s"%reply_message)
                    self.loop.run_until_complete(self.__ws.write_message(reply_message))
                else:
                    pending_message_list = []
                    if result:
                        pending_message_list.append(result)

                    while not self.__result_queue.empty():
                        pending_message_list.append(self.__result_queue.get())

                    # 将未处理的数据保存到本地文件，等待再启动的时候恢复回来
                    with open(self.__save_file_path, 'wb') as save_file:
                        pickle.dump(pending_message_list, save_file)

                    self.__over_queue.put({"state":True})
        except Exception as e2:
            logging.error("%s:preprocessing result thread error:%s" % (self.name, str(e2)))
        finally:
            if self.loop:
                self.loop.close()


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


    '''
    if not self.__running.isSet():
        # 如果当前线程已经不运行了，则让loop等到发送返回值的消息完成后才继续(阻塞解释，直到都发出去)
        loop.run_until_complete(self.__ws.write_message("监控数据:%d"%count))
    else:
        self.__ws.write_message("监控数据:%d"%count)
    '''