# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-29 11:47:07
@LastEditTime: 2019-12-04 16:56:58
@Description:
'''

import time
import json
import asyncio

from threading import Thread

class HeartCheck(Thread):

    def __init__(self, ws):
        Thread.__init__(self)
        self.__ws = ws
        self.__running = True

    def run(self):

        try:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            while self.__running:
                if self.__ws and self.__ws.ws_connection:
                    self.loop.run_until_complete(self.__ws.write_message(json.dumps({'message':'heart check'})))
                time.sleep(20)
        finally:
            if self.loop:
                self.loop.close()


    def close(self):
        self.__running = False