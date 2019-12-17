# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-17 17:15:44
@Description:
'''

import os
import json
import asyncio
import logging
import threading
import subprocess

from core import Config

class AutoAnnotationLabelThread(threading.Thread):

    config = Config()

    def __init__(self, ws, message, image_path, script_path):
        super(AutoAnnotationLabelThread, self).__init__()
        self.__ws = ws
        self.__image_path = image_path
        self.__script_path = script_path
        self.__message = message

    def run(self):

        try:
            logging.info("auto annotation label thread start, name:%s" % self.name)

            # 设置线程得独立loop
            # self.loop = asyncio.new_event_loop()
            # asyncio.set_event_loop(self.loop)

            work_dir = os.path.dirname(self.__script_path)
            command = "source /export/software/miniconda3/bin/activate && cd " + work_dir + " && python " + self.__script_path
            logging.info(command)
            auto_label_process = subprocess.Popen(command, shell=True, cwd=work_dir, stdout=subprocess.PIPE)
            out = auto_label_process.stdout.readlines()
            for out_line in out:
                if "True" in out_line:
                    self.__message.data = {"state":True}
                    self.__ws.write_message(json.dumps(self.__message))
                else:
                    self.__message.data = {"state":False}
                    self.__ws.write_message(json.dumps(self.__message))

        finally:
            # if self.loop:
            #     self.loop.close() # 线程结束关闭loop
            pass
