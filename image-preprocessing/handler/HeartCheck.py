# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-29 11:47:07
@LastEditTime: 2019-11-29 14:58:56
@Description:
'''

import time
import asyncio

from threading import Thread

class HeartCheck(Thread):

    def __init__(self, parameter1):
        Thread.__init__(self)
        self.parameter1 = parameter1

    def run(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        while True:
            if self.parameter1:
                self.parameter1.heart_check()
            time.sleep(20)