# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-29 11:47:07
@LastEditTime: 2019-12-03 19:59:26
@Description:
'''

import time
import asyncio

from threading import Thread

class HeartCheck(Thread):

    def __init__(self, parameter1):
        Thread.__init__(self)
        self.parameter1 = parameter1
        self.__running = True

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        while self.__running:
            if self.parameter1 and self.parameter1.ws_connection:
                self.parameter1.heart_check()
            time.sleep(20)

    def close(self):
        self.__running = False