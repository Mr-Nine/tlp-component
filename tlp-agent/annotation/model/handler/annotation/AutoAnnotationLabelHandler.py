# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2019-12-17 16:58:21
@Description:
'''

import sys
import uuid
import logging
import traceback
import datetime

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid
from core.utils import mysql_dict_2_dict

from tlp.entity import AnnotationlProjectImage

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
            image_table_name = '`AnnotationlProjectImage' + str(project.index) + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="指定的图片没有找到")

            image = AnnotationlProjectImage.create_by_database_result(target_image_result[1])

            if image.annotationUserId != self.user.userId:
                # 当前用户没有锁定图片
                return self.replyMessage(message, state=False, msg="请先标记此图片为要标注图片")

            inferencer_result = mysql.selectOne("""select * from AnnotationlProjectInferencer where id = %s""", (data['inferencerId'],))
            if inferencer_result[0]:
                return self.replyMessage(message, state=False, msg="指定的标注器找不到")

            inferencer = mysql_dict_2_dict(inferencer_result[1])



            autoAnnotationLabelThread = AutoAnnotationLabelThread(ws=self, pending_queue=self.pending_image_queue, state_queue=self.controller_thread_state_queue)

            action = data['action']

            mate_label_table_name = '`AnnotationProjectImageMateLabel' + str(project.index) + '`'

            if action == 'add':
                # 为图片增加新的mate标签

                if 'labelId' not in data:
                    # 要增加的label关联不存在
                    return self.replyMessage(message, state=False, msg="50106")

                labelId = data['labelId']
                attribute = data['attribute'] if ('attribute' in data and data['attribute'] is not None) else None

                sql = """insert into """ + mate_label_table_name + """ (`id`, `imageId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                now = datetime.datetime.today()
                newId = str(uuid.uuid4())

                count = mysql.insertOne(sql, (newId, image.id, labelId, 'MANUAL', '0', attribute, self.user.userId, now, now))
                if count:
                    return self.replyMessage(message, state=True, msg="add mate label success.", id=newId, imageId=image.id, labelId=labelId)
                else:
                    return self.replyMessage(message, state=False, msg="50107", imageId=image.id, labelId=labelId) # 插入为写入数据库

            elif action == 'delete':
                # 为图片取消一个mate标签

                if 'id' not in data:
                    # 要删除的ID不存在
                    return self.replyMessage(message, state=False, msg="50107")

                delete_id = data['id']

                sql = """delete from """ + mate_label_table_name + """ where id = %s"""

                count = mysql.delete(sql, (delete_id, ))
                if count:
                    return self.replyMessage(message, state=True, msg="delete mate label success.", id=delete_id, imageId=image.id)
                else:
                    return self.replyMessage(message, state=False, msg="50108", id=delete_id, imageId=image.id) # 删除未成功执行

            elif action == 'update':
                # 为图像的Mate修改属性
                if 'id' not in data:
                    # 要删除的ID不存在
                    return self.replyMessage(message, state=False, msg="50107")

                update_id = data['id']
                attribute = data['attribute'] if ('attribute' in data and data['attribute'] is not None) else None

                sql = """update """ + mate_label_table_name + """ set attribute = %s where id = %s"""
                count = mysql.update(sql, (attribute, update_id))

                if count:
                    return self.replyMessage(message, state=True, msg="update mate label attribute success.", id=update_id, imageId=image.id)
                else:
                    return self.replyMessage(message, state=False, msg="50108", id=update_id, imageId=image.id) # 删除未成功执行

            else:
                # 未知的mate操作
                return self.replyMessage(message, state=False, msg="50109", imageId=image.id) # 未知的Action操作目标

        finally:
            mysql.destory()


    def destroy(self):
        logging.info("AnnotationMateLabelHandler destroy.")
        return True
