# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2019-12-19 19:41:41
@Description:
'''

import sys
import logging
import traceback
import datetime

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid

class LockImageHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(LockImageHandler, self).__init__("lock-image", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'LockImageHandler' receive message %s", message.to_json())

        if message.data is None:
            return self.replyMessage(message, state=False, msg='30101')

        data = message.data
        if 'projectId' not in data or 'imageId' not in data or 'action' not in data:
            return self.replyMessage(message, state=False, msg="30102")

        if data['projectId'] != self.user.projectId:
            return self.replyMessage(message, state=False, msg="30103")

        context = TLPContext()
        project =context.get_project(self.user.projectId)
        mysql = MysqlManager()

        try:
            image_table_name = '`AnnotationlProjectImage' + str(project.index) + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="30104")

            target_image = target_image_result[1]
            if target_image['annotation'] or target_image['review'] or target_image['completed']:
                # 已经被锁住的图片，不管是否是自己锁得都不予继续处理
                return self.replyMessage(message, state=False, msg="30105")

            action = data['action']

            sql_start = """update """ + image_table_name + """ set """
            sql_end = """ where `id` = %s and `updateVersion` = %s """

            result = 0
            if action == "annotation":
                select_result = mysql.selectOne("""select `id`, `updateVersion` from """ + image_table_name + """ where annotation = 1 and annotationUserId = %s""", (self.user.userId, ))
                if select_result[0]:
                    unlock_image_id = select_result[1]['id'].decode("utf-8")
                    update_version= select_result[1]['updateVersion']
                    result = mysql.update(sql_start + """ `annotation` = 0, `annotationUserId` = null, `updateVersion` = `updateVersion` + 1 """ + sql_end, (unlock_image_id, update_version))
                    if result > 0:
                        notice_msg = self.replyMessage(message, state=True, msg="notice", type="unlock-image", action=action, userId=self.user.userId, projectId=project.id, imageId=unlock_image_id)
                        notice_msg.senderMid = MessageMid.IMAGES()
                        notice_msg.messageType = 'unlock-image'
                        context.notice(notice_msg, project.id) # 发送自动解锁的通知
                        result = mysql.update(sql_start + """`annotation` = 1, `annotationUserId` = %s, `updateVersion` = `updateVersion` + 1 """ + sql_end, (self.user.userId, data['imageId'], target_image['updateVersion']))
                else:
                    result = mysql.update(sql_start + """`annotation` = 1, `annotationUserId` = %s, `updateVersion` = `updateVersion` + 1 """ + sql_end, (self.user.userId, data['imageId'], target_image['updateVersion']))
            elif action == "review":
                select_result = mysql.selectOne("""select `id`, `updateVersion` from """ + image_table_name + """ where `review` = 1 and `reviewUserId` = %s""", (self.user.userId, ))
                if select_result[0]:
                    unlock_image_id = select_result[1]['id'].decode("utf-8")
                    update_version= select_result[1]['updateVersion']
                    result = mysql.update(sql_start + """ `review` = 0, `reviewUserId` = null, `updateVersion` = `updateVersion` + 1 """ + sql_end, (unlock_image_id, update_version))
                    if result > 0:
                        notice_msg = self.replyMessage(message, state=True, msg="notice", type="unlock-image", action=action, userId=self.user.userId, projectId=project.id, imageId=unlock_image_id)
                        notice_msg.senderMid = MessageMid.IMAGES()
                        notice_msg.messageType = 'unlock-image'
                        context.notice(notice_msg, project.id) # 发送自动解锁的通知
                        result = mysql.update(sql_start + """`review` = 1, `reviewUserId` = %s, `updateVersion` = `updateVersion` + 1 """ + sql_end, (self.user.userId, data['imageId'], target_image['updateVersion']))
                else:
                    result = mysql.update(sql_start + """`review` = 1, `reviewUserId` = %s, `updateVersion` = `updateVersion` + 1 """ + sql_end, (self.user.userId, data['imageId'], target_image['updateVersion']))
            elif action == 'completed':
                result = mysql.update(sql_start + """`completed` = 1, `completedUserId` = %s, `completedTime` = %s, `updateVersion` = `updateVersion` + 1 """ + sql_end, (self.user.userId, datetime.datetime.today(), data['imageId'], target_image['updateVersion']))

            if not result:
                # 更新行数小于1,数据异常(id, userId等), 乐观锁
                return self.replyMessage(message, state=False, msg="操作出现冲突，请重试")

            notice_msg = self.replyMessage(message, state=True, msg="notice", type="lock-image", action=action, userId=self.user.userId, projectId=project.id, imageId=data["imageId"])

            notice_msg.senderMid = MessageMid.IMAGES()

            # 更新成功，要对多有当前已经连接到次项目的用户发出通知
            context.notice(notice_msg, project.id)

            return None

        finally:
            mysql.destory()


    def destroy(self):
        logging.info("LockImageHandler destroy.")
        return True
