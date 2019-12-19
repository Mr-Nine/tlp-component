# -- coding: utf-8 --
'''
@Project:TLP
@Team:dcp team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 14:04:52
@LastEditTime: 2019-12-19 14:36:18
@Description:
'''

import sys
import logging
import traceback
import datetime
import uuid

from annotation.model.handler import AbstractHandler
from core import Config, MysqlManager, TLPContext, MessageMid

from tlp.entity import AnnotationlProjectImage, AnnotationProjectImageRegion, AnnotationProjectImageRegionLabel
from tlp.error import RunTimeException

class AnnotationRegionLabelHandler(AbstractHandler):

    def __init__(self, websocket, user):
        super(AnnotationRegionLabelHandler, self).__init__("region-label", websocket, user)


    def handle(self, message):
        '''
        @description:
        @param {type}
        @return:
        '''
        logging.debug("'AnnotationRegionLabelHandler' receive message %s", message.to_json())

        if message.data is None:
            return self.replyMessage(message, state=False, msg='40101')

        data = message.data
        if 'projectId' not in data or 'imageId' not in data or 'action' not in data:
            return self.replyMessage(message, state=False, msg="40102", data=None)

        if data['projectId'] != self.user.projectId:
            return self.replyMessage(message, state=False, msg="40103")

        if 'regions' not in data:
            return self.replyMessage(message, state=False, msg="40109")

        regions = data['regions']

        context = TLPContext()
        project =context.get_project(self.user.projectId)
        mysql = MysqlManager()

        try:
            image_table_name = '`AnnotationlProjectImage' + str(project.index) + '`'
            region_table_name = '`AnnotationProjectImageRegion' + str(project.index) + '`'
            region_label_table_name = '`AnnotationProjectImageRegionLabel' + str(project.index) + '`'

            target_image_result = mysql.selectOne("""select * from """ + image_table_name + """ where id = %s""", (data['imageId'], ))
            if target_image_result[0] == 0:
                # 目标图片不存在
                return self.replyMessage(message, state=False, msg="40104")

            image = AnnotationlProjectImage.create_by_database_result(target_image_result[1])

            if image.annotationUserId != self.user.userId:
                # 当前用户没有锁定图片
                return self.replyMessage(message, state=False, msg="40105")

            action = data['action']

            if action == 'save-all':
                # 更新全部的页面Region标签

                userId = self.user.userId
                now = datetime.datetime.today()

                (insert_region_list, insert_region_lable_list, update_region_list, update_region_label_list) = self.__create_region_and_region_label_data(regions, image.id, userId, now)

                # if not insert_region_list and not update_region_list and not update_region_label_list:
                #     return self.replyMessage(message, state=False, msg="40110") # 没有可以写入的数据

                if insert_region_list:
                    insert_region_sql = """insert into """ + region_table_name + """ (`id`, `imageId`, `index`, `shape`, `shapeData`, `userId`, `createTime`, `updateTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                    insert_region_data = []

                    for region_obj in insert_region_list:
                        insert_region_data.append(region_obj.to_value_list(('id', 'imageId', 'index', 'shape', 'shapeData', 'userId', 'createTime', 'updateTime')))

                    # 新的标注形状写入
                    mysql.close_transaction_insert_many(insert_region_sql, insert_region_data)

                if insert_region_lable_list:
                    # 继续写入需要新的label数据
                    insert_region_label_sql = """insert into """ + region_label_table_name + """(`id`, `imageId`, `regionId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    insert_region_label_data = []

                    for label_object in insert_region_lable_list:
                        insert_region_label_data.append(label_object.to_value_list(('id', 'imageId', 'regionId', 'labelId', 'type', 'version', 'attribute', 'userId', 'createTime', 'updateTime')))

                    # 新的标注属性
                    mysql.close_transaction_insert_many(insert_region_label_sql, insert_region_label_data)


                if update_region_list:
                    # 如果有需要更新的矩形数据--更新
                    update_region_sql = """update """ + region_table_name + """ set shapeData = %s, updateTime = %s where id = %s"""

                    for region_obj in update_region_list:
                        mysql.update(update_region_sql, parameter=(region_obj.shapeData, region_obj.updateTime, region_obj.id), auto_commit=False)

                if update_region_label_list:
                    # 如果有需要更新的矩形标签--更新
                    update_region_label_sql = """update """ + region_label_table_name + """ set attribute = %s, updateTime = %s where id = %s"""

                    for label_object in update_region_label_list:
                        mysql.update(update_region_label_sql, parameter=(label_object.attribute, label_object.updateTime, label_object.id), auto_commit=False)

                if 'deleteRegions' in data:
                    # 删除对应的区域和属性
                    delete_region_sql = """delete from """ + region_table_name + """ where id = %s"""
                    deleteRegions = data['deleteRegions']
                    for region_id in deleteRegions:
                        mysql.delete(sql=delete_region_sql, parameter=(region_id,), auto_commit=False)

                if 'deleteRegionLabels' in data:
                    # 删除对应的属性
                    delete_region_label_sql = """delete from """ + region_label_table_name + """ where id = %s"""
                    deleteRegionLabels = data['deleteRegionLabels']
                    for region_label_id in deleteRegionLabels:
                        mysql.delete(sql=delete_region_label_sql, parameter=(region_label_id,), auto_commit=False)

                # 都执行成功了，commit一次到数据库
                mysql.end()

                get_all_region_sql = """select * from """ + region_table_name + """ where imageId = %s"""
                image_all_region_result = mysql.selectAll(get_all_region_sql, (image.id,))
                image_all_region_label_result = []
                result_data = []

                if image_all_region_result[0]:
                    # 有相关的数据，返回的时候返回当前数据的所有结构
                    get_all_region_label_where_sql = ""
                    for region in image_all_region_result[1]:
                        get_all_region_label_where_sql += "regionId = '" + region["id"].decode("utf-8") + "' or "

                    get_all_region_label_where_sql = get_all_region_label_where_sql[0:-3]
                    get_all_region_label_sql = """select * from """ + region_label_table_name + """ where """ + get_all_region_label_where_sql

                    image_all_region_label_result = mysql.selectAll(get_all_region_label_sql)

                    for region in image_all_region_result[1]:
                        region_dict = AnnotationProjectImageRegion.convert_database_result_2_dict(region)
                        region_dict["labels"] = []

                        if image_all_region_label_result[0]:
                            for region_label in image_all_region_label_result[1]:
                                if region_label["regionId"].decode("utf-8") == region_dict['id']:
                                    region_dict["labels"].append(AnnotationProjectImageRegionLabel.convert_database_result_2_dict(region_label))

                        result_data.append(region_dict)


                    return self.replyMessage(message, state=True, msg="save all region lable success.", imageId=image.id, regions=result_data, action="save-all")
                else:
                    # 没有形状信息就直接返回一个图片的ID
                    return self.replyMessage(message, state=True, msg="save all region lable success.", imageId=image.id, action="save-all")

        except Exception as e:
            mysql.end(False)
            raise RunTimeException("save all regions code error.")
        finally:
            mysql.destory()


    def destroy(self):
        logging.info("AnnotationRegionLabelHandler destroy.")
        return True

    def __create_region_and_region_label_data(self, regions, imageId, userId, now):
        insert_region_list = []
        insert_region_label_list = []
        update_region_list = []
        update_region_label_list = []

        for region in regions:
            index = region['index']
            shape = region['shape']
            shapeData = region['shapeData']
            if not shapeData:
                continue

            if 'id' in region:
                # update
                region_id = region['id']
                # create_time = region['createTime']
                # if create_time:
                #     create_time = datetime.datetime.strptime(create_time, '%Y-%m-%d %H:%M:%S')
                region_obj = AnnotationProjectImageRegion(id=region_id, imageId=imageId, type='MANUAL', index=index, shape=shape, shapeData=shapeData, userId=userId, updateTime=now)
                update_region_list.append(region_obj)

                if 'labels' in region and region['labels']:
                    labels = region['labels']

                    for label in labels:
                        if 'labelId' not in label:
                            continue

                        labelId = label['labelId']
                        attribute = label['attribute']

                        if 'id' in label:
                            # 已经存在的图形也可能有2种情况，就是update-label和insert-label
                            region_label_id = label['id']
                            label_obj = AnnotationProjectImageRegionLabel(id=region_label_id, imageId=imageId, regionId=region_id, labelId=labelId, type="", version="0", attribute=attribute, userId=userId, createTime=now, updateTime=now)
                            update_region_label_list.append(label_obj)
                        else:
                            region_label_id = str(uuid.uuid4())

                            label_obj = AnnotationProjectImageRegionLabel(id=region_label_id, imageId=imageId, regionId=region_id, labelId=labelId, type="", version="0", attribute=attribute, userId=userId, createTime=now, updateTime=now)
                            insert_region_label_list.append(label_obj)
            else:
                # insert 如果矩形没有ID，那就说明他是新得，那它的label也都按新得处理
                region_id = str(uuid.uuid4())
                region_obj = AnnotationProjectImageRegion(id=region_id, imageId=imageId, type='MANUAL', index=index, shape=shape, shapeData=shapeData, userId=userId, createTime=now, updateTime=now)
                insert_region_list.append(region_obj)

                if 'labels' in region and region['labels']:
                    labels = region['labels']

                    for label in labels:
                        if 'labelId' not in label:
                            continue

                        labelId = label['labelId']
                        attribute = label['attribute']
                        region_label_id = str(uuid.uuid4())

                        label_obj = AnnotationProjectImageRegionLabel(id=region_label_id, imageId=imageId, regionId=region_id, labelId=labelId, type="", version="0", attribute=attribute, userId=userId, createTime=now, updateTime=now)
                        insert_region_label_list.append(label_obj)

        return (insert_region_list, insert_region_label_list, update_region_list, update_region_label_list)
