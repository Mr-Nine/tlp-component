# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2019-12-17 17:27:03
@Description:负责处理获取图片列表的请求数据，会根据当前用户和所标注的项目去获取对应的图片信息,
消息格式：
send-message:{
    senderMid:'images',
    targetMid:'images',
    messageType:'image-list',
    createTime:'2019-11-19 00:00:00'
    senderTime:'2019-11-19 00:00:00'
    tnsNumber:'回溯用，给什么发回去什么'
    data: {
        'projectId':'str',
        'page':int,
        'action':'last|next'
    }
}
reply-message:{
    senderMid:'images',
    targetMid:'images',
    messageType:'image-list',
    createTime:'2019-11-19 00:00:00'
    senderTime:'2019-11-19 00:00:00'
    tnsNumber:'回溯用，给什么发回去什么'
    data: {
        'projectId':'str',
        'totalRow':int,
        'totalPage':int,
        'page':int,
        'pageSize':int,
        'currentImageId':'str',
        'imageDatas':({},{},{},{})
    }
}
'''

import sys
import logging
import traceback
import math

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext

from tlp.entity import AnnotationlProjectImage

class ImagesListHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(ImagesListHandler, self).__init__("image-list", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'ImagesListHandler' receive message %s", message.to_json())

        if not hasattr(message, 'data') or message.data is None:
            return self.replyMessage(message, state=False, msg='30001')

        data = message.data
        if 'projectId' not in data:
            return self.replyMessage(message, state=False, msg="30002")

        if self.user.projectId != data['projectId']:
            return self.replyMessage(message, state=False, msg="30003")

        project_id = self.user.projectId

        mysql = MysqlManager()

        tlpConfig = Config()
        page_size = tlpConfig.page_size
        current_image_id = None

        try:

            current_user_id = self.user.userId
            context = TLPContext()
            current_project = context.get_project(self.user.projectId)
            project_index = current_project.index

            image_table_name = '`AnnotationlProjectImage' + str(project_index) + '`'

            sql = """SELECT COUNT(1) total FROM """ + image_table_name
            total_rows = mysql.selectOne(sql)[1]['total']
            total_page = math.ceil(total_rows / page_size)

            current_page = 0
            page = 0
            if 'page' not in data:
                # 没有指定当前浏览的数据
                current_image_result = mysql.selectAll("""SELECT * FROM """ + image_table_name + """ WHERE `annotationUserId` = %s or `reviewUserId` = %s or `browseUserId` = %s""", (current_user_id, current_user_id, current_user_id))
                if (current_image_result[0] > 0):
                    # 已经有在处理的数据，需要知道是第几页的数据，从而继续从那边继续
                    current_images = current_image_result[1]
                    for image in current_images:
                        # 除了是正在标注的，其他的位置随便
                        if current_image_id is None:
                            current_image_id = image["id"]

                        if image["annotationUserId"] is not None:
                            current_image_id = image["id"]

                    sql = """
                    SELECT
                        rowNum FROM (
                            SELECT id, @ROWNUM := @ROWNUM + 1 AS rowNum FROM """ + image_table_name + """, (SELECT @ROWNUM := 0) r ORDER BY `name` ASC, `id` DESC
                        ) t
                    WHERE
                    id = %s
                    """
                    result = mysql.selectOne(sql, (current_image_id, ))
                    current_image_number = result[1]['rowNum']

                    current_page = int(current_image_number / page_size)
                    current_row = current_image_number % page_size

                    if current_page == 0:
                        # TODO:随机一个page数据
                        pass
                    else:
                        page = current_page

                else:
                    # 没有在处理的数据，并且没有指定页数，也就是刚开始标注
                    current_page = 0
                    # TODO:随机一个page数据
            else:
                # 已指定浏览信息，直接获取对应的要求数据
                current_page = data['page']
                action = data['action']

                if action == 'next':
                    page = current_page
                elif action == 'last':
                    page = current_page - 2

            # 是否要配置页面list的分页数量>分页量小访问频繁，分页量大数据获取慢
            # 使用有优化效果的Join子句
            sql = """SELECT i1.* FROM """ + image_table_name + """ AS i1 INNER JOIN (SELECT id FROM """ + image_table_name + """ ORDER BY `name` ASC, `id` DESC LIMIT %s, %s) i2 ON i1.id = i2.id"""
            page_result = mysql.selectAll(sql, ((page * page_size), page_size))

            if not page_result[0]:
                return self.replyMessage(message, state=False, msg='当前项目还没有可标注的图片')

            # 组织返回的数据
            # return_data = dict()
            # return_data['projectId'] = project_id
            # return_data['totalRow'] = total_rows
            # return_data['totalPage'] = total_page
            # return_data['page'] = page + 1
            # return_data['pageSize'] = page_size
            # return_data['currentImageId'] = current_image_id

            image_list = []
            for i in range(len(page_result[1])):
                image_list.append(AnnotationlProjectImage.convert_database_result_2_dict(page_result[1][i]))

            return self.replyMessage(message,
                state=True,
                msg='',
                projectId=project_id,
                totalRow=total_rows,
                totalPage=total_page,
                page=(page + 1),
                pageSize=page_size,
                currentImageId=current_image_id.decode('utf-8') if current_image_id is not None else '',
                images=image_list
            )

        finally:
            mysql.destory()


    def destroy(self):
        logging.info("ImagesListHandler destroy.")
        return True
