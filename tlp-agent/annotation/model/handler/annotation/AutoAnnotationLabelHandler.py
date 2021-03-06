# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2020-03-18 17:55:35
@Description:
'''

import os
import sys
import uuid
import logging
import traceback
import datetime

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid
from core.utils import mysql_dict_2_dict
from annotation.model.handler.annotation import AutoAnnotationLabelThread

from tlp.entity import AnnotationProjectImage

class AutoAnnotationLabelHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(AutoAnnotationLabelHandler, self).__init__("auto-label", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'AutoAnnotationLabelHandler' receive message %s", message.to_json())

        if message.data is None:
            return self.replyMessage(message, state=False, msg='请指定消息的内容')

        data = message.data
        if 'projectId' not in data or 'imageId' not in data or 'inferencerId' not in data:
            return self.replyMessage(message, state=False, msg="请指定要处理的数据", data=None)

        if data['projectId'] != self.user.projectId:
            return self.replyMessage(message, state=False, msg="您没有权限操作此项目")

        context = TLPContext()
        project = context.get_project(self.user.projectId)
        mysql = MysqlManager()

        try:
            image_table_name = '`AnnotationProjectImage' + str(project.index) + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="指定的图片没有找到")

            image = AnnotationProjectImage.create_by_database_result(target_image_result[1])

            if image.annotationUserId != self.user.userId:
                # 当前用户没有锁定图片
                return self.replyMessage(message, state=False, msg="请先标记此图片为要标注图片")

            inference_result = mysql.selectOne("""select * from AnnotationProjectInferencer where id = %s""", (data['inferencerId'],))
            if not inference_result[0]:
                return self.replyMessage(message, state=False, msg="指定的标注器没有找到")

            inference_dict = mysql_dict_2_dict(inference_result[1])

            if inference_dict["state"] != 'GENERAL':
                return self.replyMessage(message, state=False, msg="推理器正在工作，请等待推理完成后重试")

            script_path = inference_dict['script']
            if not os.path.exists(script_path):
                return self.replyMessage(message, state=False, msg="指定的自动标注脚本没有找到")

            autoAnnotationLabelThread = AutoAnnotationLabelThread(ws=self.websocket, message=message, image_path=image.path, script_path=script_path, project_id=project.id, user_id=self.user.userId, inferencer_id=inference_dict["id"])
            autoAnnotationLabelThread.start()

        finally:
            mysql.destory()


    def destroy(self):
        logging.info("AutoAnnotationLabelHandler destroy.")
        return True
