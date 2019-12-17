# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-02 11:10:52
@LastEditTime: 2019-12-17 18:19:28
@Description:
'''

import os
import json
import asyncio
import logging
import traceback
import threading
import subprocess

from core import Config

class AutoAnnotationLabelThread(threading.Thread):

    config = Config()

    def __init__(self, ws, message, image_path, script_path, project_id, user_id, inferencer_id):
        super(AutoAnnotationLabelThread, self).__init__()
        self.__ws = ws
        self.__image_path = image_path
        self.__script_path = script_path
        self.__message = message
        self.__project_id = project_id
        self.__user_id = user_id
        self.__inferencer_id = inferencer_id

    def run(self):

        try:
            logging.info("auto annotation label thread start, name:%s" % self.name)

            # 设置线程得独立loop
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # -pid 80882967-e342-4417-b002-8aeaf41cd6ea -uid 31602ab7-8527-4952-a252-639a9be22d64 -p 192.168.30.198:/export/dujiujun/tlp/gdal2tiles/source/8.jpg -t inferencer -iid 66655555-e342-4417-b002-111111111111
            work_dir = os.path.dirname(self.__script_path)
            # source /export/software/miniconda3/bin/activate &&
            command = "cd " + work_dir + " && python " + self.__script_path
            command = ""
            command = "python " + self.__script_path + " -t inferencer" + " -pid " + self.__project_id + " -uid " + self.__user_id + " -p " + self.__image_path + " -iid " + self.__inferencer_id
            logging.info(command)
            auto_label_process = subprocess.Popen(command, shell=True, cwd=work_dir, stdout=subprocess.PIPE)
            out = auto_label_process.stdout.readlines()
            for out_line in out:
                line = out_line.decode("utf-8")
                if "True" in line:
                    self.__message.data = {"state":True}
                    self.loop.run_until_complete(self.__ws.write_message(self.__message.to_json()))
                else:
                    self.__message.data = {"state":False}
                    self.loop.run_until_complete(self.__ws.write_message(self.__message.to_json()))
        except Exception as e:
            from io import StringIO
            fp = StringIO()
            traceback.print_exc(file=fp)
            exception_stack = fp.getvalue()
            fp.close()
            exception_stack = self.message + "\n-------------stack info start -----------------\n" + exception_stack + "\n-------------stack info end-----------------\n"
            logging.error(exception_stack)
        finally:
            if self.loop:
                self.loop.close() # 线程结束关闭loop
