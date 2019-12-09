# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-29 11:47:07
@LastEditTime: 2019-12-06 15:41:27
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
        time.sleep(10) # TODO:BufferError: Existing exports of data: object cannot be re-sized
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