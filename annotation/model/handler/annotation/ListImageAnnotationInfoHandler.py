# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2019-11-28 15:29:22
@Description:
'''

import sys
import logging
import traceback
import datetime
import uuid

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid

from tlp.entity import AnnotationlProjectImage, AnnotationProjectImageMateLabel, AnnotationProjectImageRegion, AnnotationProjectImageRegionLabel
from tlp.error import RunTimeException

class ListImageAnnotationInfoHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(ListImageAnnotationInfoHandler, self).__init__("list-label", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'ListImageAnnotationInfoHandler' receive message %s", message.to_json())

        if message.data is None:
            return self.replyMessage(message, state=False, msg='请填写需要提交的数据')

        data = message.data
        if 'projectId' not in data or 'imageId' not in data or 'action' not in data:
            return self.replyMessage(message, state=False, msg="请填写关键的信息", data=None)

        if data['projectId'] != self.user.projectId:
            return self.replyMessage(message, state=False, msg="您不属于当前项目，无法进行操作，请检查权限")

        context = TLPContext()
        project =context.get_project(self.user.projectId)
        project_index_str = str(project.index)
        mysql = MysqlManager()

        try:
            image_table_name = '`AnnotationlProjectImage' + project_index_str + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="要操作的图片没有找到")

            image = AnnotationlProjectImage.create_by_database_result(target_image_result[1])

            if image.annotationUserId != self.user.userId:
                # 当前用户没有锁定图片
                return self.replyMessage(message, state=False, msg="您并没有锁定要操作的图片，请确认信息")

            action = data['action']

            mate_label_table_name = '`AnnotationProjectImageMateLabel' + project_index_str + '`'
            image_region_table_name = '`AnnotationProjectImageRegion' + project_index_str + '`'
            image_region_label_table_name = '`AnnotationProjectImageRegionLabel' + project_index_str + '`'

            if action == 'image-mate-label':
                # 查询图片得mate信息
                return self.replyMessage(message, state=True, msg="select mate lable success.", mateLabels=self.__select_meta_label(mysql, mate_label_table_name, image.id), action=action)
            elif action == 'image-region-label':
                # 查询图片得区域和区域得label信息
                return self.replyMessage(message, state=True, msg="select region lable success.", regions=self.__select_region_and_region_label(mysql, image_region_table_name, image_region_label_table_name, image.id), action=action)
            elif action == 'region-label':
                # 查询单个形状得label信息
                if 'regionId' not in data:
                    return self.replyMessage(message, state=False, msg="region id not found.", regionLabels=[], action=action)

                regionId = data['regionId']
                return self.replyMessage(message, state=True, msg="select region label success.", regionLabels=self.__select_one_region_label(mysql, image_region_label_table_name, regionId), action=action)
            elif action == 'all':
                # 查询所有信息
                mate_label_list = self.__select_meta_label(mysql, mate_label_table_name, image.id)
                region_label_list = self.__select_region_and_region_label(mysql, image_region_table_name, image_region_label_table_name, image.id)

                return self.replyMessage(message, state=False, msg="region id not found.", mateLabels= mate_label_list, regionLabels=region_label_list, action=action)
            else:
                return self.replyMessage(message, state=False, msg="不明确得动作定义，请指定查询内容")

        except Exception as e:
            mysql.end(False)
            raise RunTimeException("save all regions code error.")
        finally:
            mysql.destory()


    def destroy(self):
        logging.info("ListImageAnnotationInfoHandler destroy.")
        return True


    def __select_meta_label(self, mysql, mate_label_table_name, imageId):
        '''
        @description:
        @param {type}
        @return:
        '''
        select_sql = """select * from """ + mate_label_table_name + """ where imageId = %s"""
        select_result = mysql.selectAll(select_sql, (imageId, ))
        mate_lable_list = []

        if select_result[0]:
            for mate in select_result[1]:
                mate_lable_list.append(AnnotationProjectImageMateLabel.convert_database_result_2_dict(mate))

        return mate_lable_list


    def __select_region_and_region_label(self, mysql, image_region_table_name, image_region_label_table_name, imageId):
        '''
        @description:
        @param {type}
        @return:
        '''
        select_sql = """select * from """ + image_region_table_name + """ where imageId = %s"""
        select_result = mysql.selectAll(select_sql, (imageId, ))
        select_region_label_where_sql = ""
        region_list = []

        if select_result[0]:
            for region in select_result[1]:
                region_dict = AnnotationProjectImageRegion.convert_database_result_2_dict(region)
                select_region_label_where_sql += ("regionId = '" + region_dict['id'] + "' or ")
                region_list.append(region_dict)

            select_region_label_where_sql = select_region_label_where_sql[0:-3]

            select_region_label_sql = """select * from """ + image_region_label_table_name + """ where """ + select_region_label_where_sql
            select_label_result = mysql.selectAll(select_region_label_sql)
            region_label_list = []

            if select_label_result[0]:
                for region_label in select_label_result[1]:
                    region_label_list.append(AnnotationProjectImageRegionLabel.convert_database_result_2_dict(region_label))

                for region_obj in region_list:
                    for region_label_obj in region_label_list:
                        if region_obj['id'] == region_label_obj['regionId']:
                            if 'labels' not in region_obj:
                                region_obj['labels'] = []
                            region_obj['labels'].append(region_label_obj)

        return region_list


    def __select_one_region_label(self, mysql, image_region_label_table_name, regionId):
        select_region_label_sql = """select * from """ + image_region_label_table_name + """ where regionId = %s"""
        select_label_result = mysql.selectAll(select_region_label_sql, (regionId, ))

        region_label_list = []
        if select_label_result[0]:
            for region_label in select_label_result[1]:
                region_label_list.append(AnnotationProjectImageRegionLabel.convert_database_result_2_dict(region_label))

        return region_label_list