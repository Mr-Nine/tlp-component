# -- coding: utf-8 --

import sys
import json
import logging
import traceback
import datetime
import uuid

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid

from tlp.entity import AnnotationProjectImage

class LabelFilterConditionHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(LabelFilterConditionHandler, self).__init__("filter-label", websocket, user)


    def handle(self, message):
        logging.debug("'LabelFilterConditionHandler' receive message %s", message.to_json())

        if message.data is None:
            return self.replyMessage(message, state=False, msg='请指定要设置的标签筛选条件')

        data = message.data
        if 'projectId' not in data or 'action' not in data:
            return self.replyMessage(message, state=False, msg="请指定要设置的标签筛选条件")

        if data['projectId'] != self.user.projectId:
            return self.replyMessage(message, state=False, msg="您不属于当前项目的用户，无法进行操作")

        context = TLPContext()
        project =context.get_project(self.user.projectId)
        # mysql = MysqlManager()

        try:
            action = data['action']
            connect_id = id(self.websocket)

            if action == 'set-condition' and "condition" in data and data["condition"]:
                context.set_label_filter_condition(connect_id=connect_id, condition=data["condition"])
                return self.replyMessage(message, state=True, msg="设置成功")
            elif action == 'clean-condition':
                context.set_label_filter_condition(connect_id=connect_id, condition=None)
                return self.replyMessage(message, state=True, msg="清除成功")

        finally:
            pass
            # mysql.destory()


    def destroy(self):
        logging.info("LabelFilterConditionHandler destroy.")
        return True
