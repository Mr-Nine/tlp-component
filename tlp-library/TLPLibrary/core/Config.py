# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-13 17:16:51
@LastEditTime: 2020-03-18 14:46:14
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
        tlp_config.read(filenames=os.path.join(os.path.dirname(__file__), "library.conf"), encoding="utf-8")

        self.mysql_host = tlp_config['tlp-library'].get('mysql_host', '127.0.0.1')
        self.mysql_port = tlp_config['tlp-library'].getint('mysql_port', '3306')
        self.mysql_user = tlp_config['tlp-library'].get('mysql_user', 'root')
        self.mysql_pwd = tlp_config['tlp-library'].get('mysql_pwd', 'root')
        self.database_name = tlp_config['tlp-library'].get('database_name', 'dcp')
        self.database_charset = tlp_config['tlp-library'].get('database_charset', 'utf8')
        self.database_mincached = tlp_config['tlp-library'].getint('database_mincached', 1)
        self.database_maxcached = tlp_config['tlp-library'].getint('database_maxcached', 20)
        self.database_maxshared = tlp_config['tlp-library'].getint('database_maxshared', 20)
        self.database_maxconnections = tlp_config['tlp-library'].getint('database_maxconnections', 20)

        self.image_depository_table_name=tlp_config['tlp-table'].get('image_depository_table_name', 'AnnotationImageDepository')
        self.project_table_name=tlp_config['tlp-table'].get('project_table_name', 'AnnotationProject')
        self.project_source_table_name=tlp_config['tlp-table'].get('project_source_table_name', 'AnnotationProjectSource')
        self.project_reasoning_machine_table_name=tlp_config['tlp-table'].get('project_reasoning_machine_table_name', 'AnnotationProjectInference')
        self.project_label_template_table_name=tlp_config['tlp-table'].get('project_label_template_table_name', 'AnnotationProjectLabelTemplate')
        self.project_image_table_name=tlp_config['tlp-table'].get('project_image_table_name', 'AnnotationProjectImage')
        self.project_meta_label_table_name=tlp_config['tlp-table'].get('project_meta_label_table_name', 'AnnotationProjectImageMetaLabel')
        self.project_image_region_table_name=tlp_config['tlp-table'].get('project_image_region_table_name', 'AnnotationProjectImageRegion')
        self.project_image_region_label_table_name=tlp_config['tlp-table'].get('project_image_region_label_table_name', 'AnnotationProjectImageRegionLabel')
