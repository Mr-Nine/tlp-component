# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2020-03-16 15:02:45
@Description:
'''

import sys
import logging
import traceback
import datetime

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid

from tlp.entity import AnnotationProjectImage

class UnlocakImageHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(UnlocakImageHandler, self).__init__("unlock-image", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'UnlocakImageHandler' receive message %s", message.to_json())

        if message.data is None:
            return self.replyMessage(message, state=False, msg='30201', data=None)

        data = message.data
        if 'projectId' not in data or 'imageId' not in data or 'action' not in data:
            return self.replyMessage(message, state=False, msg="30202", data=None)

        if data['projectId'] != self.user.projectId:
            return self.replyMessage(message, state=False, msg="30203", data=None)

        context = TLPContext()
        project =context.get_project(self.user.projectId)
        mysql = MysqlManager()

        try:
            image_table_name = '`AnnotationProjectImage' + str(project.index) + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="指定的图片不存在，请确认。", data=None)

            image = AnnotationProjectImage.create_by_database_result(target_image_result[1])

            if image.annotationUserId != self.user.userId and image.reviewUserId != self.user.userId and image.completedUserId != self.user.userId:
                # 当前用户没有锁定图片
                return self.replyMessage(message, state=False, msg="您还没有锁定这张图片，无权解锁。", data=None)

            action = data['action']

            if action == 'annotation' and image.annotationUserId != self.user.userId:
                return self.replyMessage(message, state=False, msg="30206", data=None)

            if action == 'review' and image.annotationUserId != self.user.userId:
                return self.replyMessage(message, state=False, msg="30206", data=None)

            if action == 'completed' and image.annotationUserId != self.user.userId:
                return self.replyMessage(message, state=False, msg="30206", data=None)

            sql_start = """update """ + image_table_name + """ set """
            sql_end = """ where `id` = %s and `updateVersion` = %s """

            result = 0
            if action == "annotation":
                result = mysql.update(sql_start + """`annotation` = 0, `annotationUserId` = null, `updateVersion` = `updateVersion` + 1 """ + sql_end, (image.id, image.updateVersion))
            elif action == "review":
                result = mysql.update(sql_start + """`review` = 0, `reviewUserId` = null, `updateVersion` = `updateVersion` + 1 """ + sql_end, (image.id, image.updateVersion))
            elif action == 'completed':
                result = mysql.update(sql_start + """`completed` = 0, `completedUserId` = null, `updateVersion` = `updateVersion` + 1 """ + sql_end, (image.id, image.updateVersion))

            if not result:
                # 更新行数小于1,数据异常(id, userId等), 乐观锁
                return self.replyMessage(message, state=False, msg="30206", data=None)

            notice_msg = self.replyMessage(message, state=True, msg="notice", type="unlock-image", action=action, userId=self.user.userId, projectId=project.id, imageId=image.id)

            notice_msg.senderMid = MessageMid.IMAGES()

            # 更新成功，要对多有当前已经连接到次项目的用户发出通知
            context.notice(notice_msg, project.id)

            return None

        finally:
            mysql.destory()


    def destroy(self):
        logging.info("UnlocakImageHandler destroy.")
        return True
