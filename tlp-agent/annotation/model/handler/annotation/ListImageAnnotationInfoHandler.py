# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
LastEditTime: 2020-03-24 19:38:14
@Description:
'''

import sys
import json
import logging
import traceback
import datetime
import uuid

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid

from tlp.entity import AnnotationProjectImage, AnnotationProjectImageMetaLabel, AnnotationProjectImageRegion, AnnotationProjectImageRegionLabel
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
            image_table_name = '`AnnotationProjectImage' + project_index_str + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="要操作的图片没有找到")

            image = AnnotationProjectImage.create_by_database_result(target_image_result[1])

            # if image.annotationUserId != self.user.userId:
            #     # 当前用户没有锁定图片
            #     return self.replyMessage(message, state=False, msg="您并没有锁定要操作的图片，请确认信息")

            action = data['action']

            meta_label_table_name = '`AnnotationProjectImageMetaLabel' + project_index_str + '`'
            image_region_table_name = '`AnnotationProjectImageRegion' + project_index_str + '`'
            image_region_label_table_name = '`AnnotationProjectImageRegionLabel' + project_index_str + '`'

            if action == 'image-meta-label':
                # 查询图片得meta信息
                return self.replyMessage(message, state=True, msg="select meta lable success.", metaLabels=self.__select_meta_label(mysql, meta_label_table_name, image.id), action=action)
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
                if context.get_label_filter_condition(id(self.websocket)):
                    (meta_label_list, region_list) = self.__select_all_region_and_label_use_label_filter_condition(mysql, image.id, project_index_str, context.get_label_filter_condition(id(self.websocket)))
                    return self.replyMessage(message, state=True, msg="select all label success.", metaLabels= meta_label_list, regionLabels=region_list, action=action)
                else:
                    meta_label_list = self.__select_meta_label(mysql, meta_label_table_name, image.id)
                    region_label_list = self.__select_region_and_region_label(mysql, image_region_table_name, image_region_label_table_name, image.id)

                    return self.replyMessage(message, state=True, msg="select all label success.", metaLabels= meta_label_list, regionLabels=region_label_list, action=action)
            else:
                return self.replyMessage(message, state=False, msg="不明确得动作定义，请指定查询内容")

        except Exception as e:
            mysql.end(False)
            raise RunTimeException("get all regions code error.")
        finally:
            mysql.destory()


    def destroy(self):
        logging.info("ListImageAnnotationInfoHandler destroy.")
        return True


    def __select_meta_label(self, mysql, meta_label_table_name, imageId):
        '''
        @description:
        @param {type}
        @return:
        '''
        select_sql = """select * from """ + meta_label_table_name + """ where imageId = %s"""
        select_result = mysql.selectAll(select_sql, (imageId, ))
        meta_lable_list = []

        if select_result[0]:
            for meta in select_result[1]:
                meta_lable_list.append(AnnotationProjectImageMetaLabel.convert_database_result_2_dict(meta))

        return meta_lable_list


    def __select_region_and_region_label(self, mysql, image_region_table_name, image_region_label_table_name, imageId):
        '''
        @description:
        @param {type}
        @return:
        '''
        select_sql = """select * from """ + image_region_table_name + """ where imageId = %s order by `index` asc"""
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
                region_obj['labels'] = []

                for region_label_obj in region_label_list:
                    if region_obj['id'] == region_label_obj['regionId']:
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

    def __select_all_region_and_label_use_label_filter_condition(self, mysql, imageId, project_index_str, label_filter_condition):
        '''新版本的查询图片所属区域、meta label、和区域label的方法

        Args:
            mysql:查询用的mysql线程对象
            imageId:要查询的图片ID
            project_index_str:当前项目的表索引
            label_filter_condition:当前用户配置的过滤条件,
                {
                    "typeList":["MANUAL","IMPORT","DEPOSITORY","LOAD","OTHER"],
                    "inferencerIdList":["4bb77e60-a57b-4a65-b117-97aa1484bff8"],
                    "groupIdList":["4bb77e60-a57b-4a65-b117-97aa1484bff8"]
                    "confidence":[0,1]
                }
        '''

        meta_label_table_name = '`AnnotationProjectImageMetaLabel' + project_index_str + '`'
        image_region_table_name = '`AnnotationProjectImageRegion' + project_index_str + '`'
        image_region_label_table_name = '`AnnotationProjectImageRegionLabel' + project_index_str + '`'

        # label_filter_condition_json = json.loads(label_filter_condition)
        label_filter_condition_json = label_filter_condition

        label_type_list_str = None
        if 'typeList' in label_filter_condition_json:
            label_type_list_str = ''
            for type in label_filter_condition_json['typeList']:
                label_type_list_str += "'" + type + "',"
            label_type_list_str = label_type_list_str[:-1]

        inferencer_id_list_str = None
        if 'inferencerIdList' in label_filter_condition_json:
            inferencer_id_list_str = ''
            for inference_id in label_filter_condition_json['inferencerIdList']:
                inferencer_id_list_str += "'" + inference_id + "',"
            inferencer_id_list_str = inferencer_id_list_str[:-1]

        group_id_list_str = None
        if 'groupIdList' in label_filter_condition_json:
            group_id_list_str = ''
            for group_id in label_filter_condition_json['groupIdList']:
                group_id_list_str += "'" + group_id + "',"
            group_id_list_str = group_id_list_str[:-1]

        min_confidence_str = None
        max_confidence_str = None
        if 'confidence' in label_filter_condition_json:
            confidences = label_filter_condition_json['confidence']
            min_confidence = confidences[0]
            max_confidence = confidences[1]

            min_confidence_str = "attribute->'$.confidence' >= " + str(min_confidence)
            max_confidence_str = "attribute->'$.confidence' <= " + str(max_confidence)

        select_meta_label_sql = "select apiml.* from " + meta_label_table_name + " apiml left join AnnotationProjectLabelTemplate aplt on apiml.labelId = aplt.id where apiml.imageId = %s "

        if label_type_list_str is not None:
            select_meta_label_sql += " and apiml.`type` in (" + label_type_list_str + ") "

        if inferencer_id_list_str is not None:
            select_meta_label_sql += " and apiml.`inferencerId` in (" + inferencer_id_list_str + ") "

        if group_id_list_str is not None:
            select_meta_label_sql += " and aplt.labelGroupId in (" + group_id_list_str + ") "

        if min_confidence_str is not None and max_confidence_str is not None:
            select_meta_label_sql += " and apiml." + min_confidence_str + " and apiml." + max_confidence_str

        # logging.debug("select_meta_label_sql:%s" % select_meta_label_sql)

        select_meta_result = mysql.selectAll(select_meta_label_sql, (imageId, ))
        meta_lable_list = []

        if select_meta_result[0]:
            for meta in select_meta_result[1]:
                meta_lable_list.append(AnnotationProjectImageMetaLabel.convert_database_result_2_dict(meta))

        # 查标签带着区域的ID，吧区域的ID单独查出来整合
        select_region_label_sql = "select apirl.* from " + image_region_label_table_name + " apirl left join AnnotationProjectLabelTemplate aplt on apirl.labelId = aplt.id where apirl.imageId = %s "

        if label_type_list_str is not None:
            select_region_label_sql += " and apirl.`type` in (" + label_type_list_str + ") "

        if inferencer_id_list_str is not None:
            select_region_label_sql += " and apirl.`inferencerId` in (" + inferencer_id_list_str + ") "

        if group_id_list_str is not None:
            select_region_label_sql += " and aplt.labelGroupId in (" + group_id_list_str + ") "

        if min_confidence_str is not None and max_confidence_str is not None:
            select_region_label_sql += " and apirl." + min_confidence_str + " and apirl." + max_confidence_str

        # logging.debug("select_region_label_sql:%s" % select_region_label_sql)

        select_region_label_result = mysql.selectAll(select_region_label_sql, (imageId, ))
        region_label_list = []

        if select_region_label_result[0]:
            for label_result in select_region_label_result[1]:
                region_label_list.append(AnnotationProjectImageRegionLabel.convert_database_result_2_dict(label_result))

        region_ids = set()
        region_ids_str = ''
        for region_label in region_label_list:
            region_ids.add(region_label['regionId'])
        for region_id in region_ids:
            region_ids_str += "'" + region_id + "',"
        region_ids_str = region_ids_str[:-1]

        region_list = []
        if region_ids_str:
            select_region_sql = "select * from " + image_region_table_name + " where id in (" + region_ids_str + ") order by `index` asc"
            select_region_result = mysql.selectAll(select_region_sql)

            if select_region_result[0]:
                for region_result in select_region_result[1]:
                    region_list.append(AnnotationProjectImageRegion.convert_database_result_2_dict(region_result))

            for region in region_list:
                region['labels'] = []
                for region_label in region_label_list:
                    if region['id'] == region_label['regionId']:
                        region['labels'].append(region_label)

        return (meta_lable_list, region_list)



