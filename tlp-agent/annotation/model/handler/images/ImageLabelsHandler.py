# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2020-03-16 15:02:16
@Description:
'''

import sys
import logging
import traceback
import math

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext
from tlp.entity import AnnotationProjectLabelTemplate

class ImageLabelsHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(ImageLabelsHandler, self).__init__("list-label-template", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'ImageLabelsHandler' receive message %s", message.to_json())

        if not hasattr(message, 'data') or message.data is None:
            return self.replyMessage(message, state=False, msg='请指定消息体')

        data = message.data
        if 'projectId' not in data:
            return self.replyMessage(message, state=False, msg="请指定要处理的项目")

        if self.user.projectId != data['projectId']:
            return self.replyMessage(message, state=False, msg="您无权处理此项目的数据")

        project_id = self.user.projectId

        if 'action' not in data:
            return self.replyMessage(message, state=False, msg="请指定操作类型")

        action = data['action']
        mysql = MysqlManager()
        tlpConfig = Config()
        page_size = tlpConfig.page_size
        current_image_id = None

        try:

            current_user_id = self.user.userId
            context = TLPContext()
            current_project = context.get_project(self.user.projectId)
            project_index = current_project.index

            sql_start = """select * from `AnnotationProjectLabelTemplate` where projectId = %s """
            sql_end = """ order by name asc"""

            if action == 'meta':
                meta_label_list = []

                lable_result = mysql.selectAll(sql_start + """ and `type` = 'Meta' """ + sql_end, (project_id, ))

                if lable_result[0]:
                    for result in lable_result[1]:
                        meta_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))

                return self.replyMessage(message,
                    state=True,
                    msg='',
                    projectId=project_id,
                    metaLabes=meta_label_list
                )
            elif action == 'region':
                region_label_list = []

                lable_result = mysql.selectAll(sql_start + """ and `type` = 'REGION' """ + sql_end, (project_id, ))

                if lable_result[0]:
                    for result in lable_result[1]:
                        region_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))

                return self.replyMessage(message,
                    state=True,
                    msg='',
                    projectId=project_id,
                    metaLabels=meta_label_list,
                    regionLabels=region_label_list
                )
            else:
                meta_label_list = []
                region_label_list = []

                lable_result = mysql.selectAll(sql_start + sql_end,(project_id, ))

                if lable_result[0]:
                    for result in lable_result[1]:
                        if result["type"].decode("utf-8").lower() == 'meta':
                            meta_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))
                        else:
                            region_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))

                return self.replyMessage(message,
                    state=True,
                    msg='',
                    projectId=project_id,
                    metaLabels=meta_label_list,
                    regionLabels=region_label_list
                )
        finally:
            mysql.destory()


    def destroy(self):
        logging.info("ImagesListHandler destroy.")
        return True
