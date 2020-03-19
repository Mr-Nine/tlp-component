# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2020-03-19 20:17:20
@Description:
'''

import sys
import logging
import traceback
import datetime
import uuid

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid

from tlp.entity import AnnotationProjectImage

class AnnotationMetaLabelHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(AnnotationMetaLabelHandler, self).__init__("meta-label", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'AnnotationMetaLabelHandler' receive message %s", message.to_json())

        if message.data is None:
            return self.replyMessage(message, state=False, msg='50101')

        data = message.data
        if 'projectId' not in data or 'imageId' not in data or 'action' not in data:
            return self.replyMessage(message, state=False, msg="50102", data=None)

        if data['projectId'] != self.user.projectId:
            return self.replyMessage(message, state=False, msg="50103")

        context = TLPContext()
        project =context.get_project(self.user.projectId)
        mysql = MysqlManager()

        try:
            image_table_name = '`AnnotationProjectImage' + str(project.index) + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="50104")

            image = AnnotationProjectImage.create_by_database_result(target_image_result[1])

            if image.annotationUserId != self.user.userId:
                # 当前用户没有锁定图片
                return self.replyMessage(message, state=False, msg="50105")

            action = data['action']

            meta_label_table_name = '`AnnotationProjectImageMetaLabel' + str(project.index) + '`'

            if action == 'add':
                # 为图片增加新的meta标签

                if 'labelId' not in data:
                    # 要增加的label关联不存在
                    return self.replyMessage(message, state=False, msg="50106")

                labelId = data['labelId']
                attribute = data['attribute'] if ('attribute' in data and data['attribute'] is not None) else None

                # 增加默认的置信度的设置
                if attribute is not None:
                    self._merge_default_attribute(context.get_default_attribute(), attribute)

                sql = """insert into """ + meta_label_table_name + """ (`id`, `imageId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""

                now = datetime.datetime.today()
                newId = str(uuid.uuid4())

                count = mysql.insertOne(sql, (newId, image.id, labelId, 'MANUAL', '0', attribute, self.user.userId, now, now))
                if count:
                    return self.replyMessage(message, state=True, msg="add meta label success.", id=newId, imageId=image.id, labelId=labelId)
                else:
                    return self.replyMessage(message, state=False, msg="50107", imageId=image.id, labelId=labelId) # 插入为写入数据库

            elif action == 'delete':
                # 为图片取消一个meta标签

                if 'id' not in data:
                    # 要删除的ID不存在
                    return self.replyMessage(message, state=False, msg="50107")

                delete_id = data['id']

                sql = """delete from """ + meta_label_table_name + """ where id = %s"""

                count = mysql.delete(sql, (delete_id, ))
                if count:
                    return self.replyMessage(message, state=True, msg="delete meta label success.", id=delete_id, imageId=image.id)
                else:
                    return self.replyMessage(message, state=False, msg="50108", id=delete_id, imageId=image.id) # 删除未成功执行

            elif action == 'update':
                # 为图像的Meta修改属性
                if 'id' not in data:
                    # 要删除的ID不存在
                    return self.replyMessage(message, state=False, msg="50107")

                update_id = data['id']
                attribute = data['attribute'] if ('attribute' in data and data['attribute'] is not None) else None

                sql = """update """ + meta_label_table_name + """ set attribute = %s where id = %s"""
                count = mysql.update(sql, (attribute, update_id))

                if count:
                    return self.replyMessage(message, state=True, msg="update meta label attribute success.", id=update_id, imageId=image.id)
                else:
                    return self.replyMessage(message, state=False, msg="50108", id=update_id, imageId=image.id) # 删除未成功执行

            else:
                # 未知的meta操作
                return self.replyMessage(message, state=False, msg="50109", imageId=image.id) # 未知的Action操作目标

        finally:
            mysql.destory()


    def destroy(self):
        logging.info("AnnotationMetaLabelHandler destroy.")
        return True

    def _merge_default_attribute(self, default_attributes, target_attribute):
        for default in default_attributes:
            default_key = default['key']
            default_value = default['default']

            if default_key not in target_attribute:
                target_attribute[default_key] = default_value