# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-13 17:16:51
@LastEditTime: 2019-12-05 16:54:49
@Description:
'''

import os
import json
import configparser

class Config(object):

    __instance=None

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = object.__new__(cls)
            cls.__instance.initConfig()

        return cls.__instance

    def __init__(self):
        pass

    def initConfig(self):
        config_context = configparser.ConfigParser()
        config_context.read(filenames=os.path.join(os.path.abspath('.'), "config/preprocessing.conf"), encoding="utf-8")

        self.default_max_sleep_time = config_context['preprocessing'].getint('default_max_sleep_time', 30)
        self.default_max_processing_thread_number = config_context['preprocessing'].getint('default_max_processing_thread_number', 0)
        self.default_concurrent_processes_number = config_context['preprocessing'].getint('default_concurrent_processes_number', 2)
        self.tiles_save_root_path = config_context['preprocessing'].get('tiles_save_root_path', '/tmp/tile/')
        conversions = config_context['preprocessing'].get('path_conversion_list', '[]')
        print(conversions)
        self.path_conversion_list = json.loads(conversions)



