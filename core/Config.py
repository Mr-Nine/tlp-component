# -- coding: utf-8 --
__author__ = 'dcp team dujiujun - dcp - agent'
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-13 17:16:51
@LastEditTime: 2019-11-22 17:16:58
@Description:
'''

import os
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
        tlp_config = configparser.ConfigParser()
        tlp_config.read(filenames=os.path.join(os.path.abspath('.'), "config/tlp.conf"), encoding="utf-8")

        self.db_host = tlp_config['db'].get('db_host', '127.0.0.1')
        self.db_port = tlp_config['db'].getint('db_port', '3306')
        self.db_user = tlp_config['db'].get('db_user', 'root')
        self.db_passwd = tlp_config['db'].get('db_passwd', 'root')
        self.db_name = tlp_config['db'].get('db_name', 'dcp')
        self.db_charset = tlp_config['db'].get('db_charset', 'utf8')
        self.db_mincached = tlp_config['db'].getint('db_mincached', 1)
        self.db_maxcached = tlp_config['db'].getint('db_maxcached', 300)
        self.db_maxshared = tlp_config['db'].getint('db_maxshared', 300)
        self.db_maxconnections = tlp_config['db'].getint('db_maxconnections', 300)

        self.page_size = tlp_config['web'].getint('page_size', 20)

