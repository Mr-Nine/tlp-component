# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 20:44:56
@LastEditTime: 2020-03-17 17:43:14
@Description:
'''

import uuid
import json
import datetime

from TLPLibrary.core import *
from TLPLibrary.error import *
from TLPLibrary.entity import *

from TLPLibrary.service import BusinessService

class ImportLabelService(BusinessService):

    def __init__(self):
        super(ImportLabelService, self).__init__()

    def importManyImageLabel(self, run_parameter, images):
        '''
        @description:批量导入
        @param {run_parameter}:程序运行的入口参数对象
        @para {images}:
        @return:
        '''

        try:
            self._checkRunParameter(run_parameter)
            self._checkImagesParameter(run_parameter, images)

            project_info = self._findProjectInfo(run_parameter)
            project_id = project_info["id"]
            table_index = str(project_info['index'])

            now = datetime.datetime.today()
            image_table_name = self._config.project_image_table_name + table_index

            # 导入的批次版本号，先通过时间做一个标识
            version = self._getImportBatchVersion()

            for image in images:
                # TODO: 有什么办法可以不是每次都查一次呢？
                # TODO: 如果给定的图片并不存在于项目中，是否应该不抛出异常而是跳过，那是不是应该有写日志的办法？
                imageInfo = self._findProjectImageInfo(image_table_name, image.path)
                image.id = imageInfo['id']

                # 数据库中已存在的元数据模板信息
                database_meta_label_template_map = self._buildLabelTemplateDatabaseMap(project_id, LabelType.META)
                # 数据库中已存在的区域模板信息
                database_region_label_template_map = self._buildLabelTemplateDatabaseMap(project_id, LabelType.REGION)

                # 数据组织变量声明
                merged_meta_label_template_list = []
                merged_region_label_template_list = []
                insert_meta_label_template_values = []
                update_meta_label_template_values = []
                insert_region_label_template_values = []
                update_region_label_template_values = []
                meta_label_values = []
                region_values = []
                region_label_values = []

                # 提取这张图片的元数据标签模板信息
                self._mergeLabelTemplate(image.meta_labels, database_meta_label_template_map, merged_meta_label_template_list)

                # 提取需要创建或更新的元数据标签模板信息
                print("A")
                print(merged_meta_label_template_list)
                print("B")
                for meta_label_template in merged_meta_label_template_list:
                    template_label_attribute = json.dumps(meta_label_template["attribute"])
                    if "id" in meta_label_template and meta_label_template["id"]:
                        # 处理要更新的元数据标签模板数据
                        update_meta_label_template_values.append((template_label_attribute, now, meta_label_template['id']))
                    else:
                        # 处理要新增的元数据标签模板数据
                        background_color = meta_label_template["backgroundColor"]
                        if not background_color:
                            background_color = self._generateRandomColors()
                        meta_label_template['id'] = str(uuid.uuid4())
                        insert_meta_label_template_values.append((meta_label_template['id'], run_parameter.project_id, meta_label_template['name'], LabelType.META, TaggingType.IMPORT, 1, background_color, 0, 0, 0, 0, template_label_attribute, run_parameter.user_id, now, now))

                # 提取并组织图片要写入的元数据标签
                for meta_label in image.meta_labels:
                    label_template_id = self._getLabelTemplateIdByTemplateName(meta_label.name, merged_meta_label_template_list, database_meta_label_template_map)
                    if label_template_id is None:
                        raise NotFoundException("运行异常，没有找到标签所属的模板信息")
                    meta_label_id = str(uuid.uuid4())
                    meta_label_attribute = meta_label.generateAttributeJson()
                    meta_label_values.append((meta_label_id, image.id, label_template_id, TaggingType.IMPORT, version, meta_label_attribute, run_parameter.user_id, now, now))

                # 提取这张图片的区域标签模板信息
                for region in image.regions:
                    self._mergeLabelTemplate(region.labels, database_region_label_template_map, merged_region_label_template_list)

                # 提取需要创建或更新的区域标签模板信息
                for region_label_template in merged_region_label_template_list:
                    template_label_attribute = json.dumps(region_label_template["attribute"])
                    if "id" in region_label_template and region_label_template["id"]:
                        # 处理要更新的区域数据标签模板数据
                        update_region_label_template_values.append((template_label_attribute, now, region_label_template["id"]))
                    else:
                        # 处理要新增的区域数据标签模板数据
                        background_color = region_label_template["backgroundColor"]
                        if not background_color:
                            background_color = self._generateRandomColors()
                        region_label_template['id'] = str(uuid.uuid4())
                        insert_region_label_template_values.append((region_label_template['id'], run_parameter.project_id, region_label_template['name'], LabelType.REGION, TaggingType.IMPORT, 1, background_color, 0, 0, 0, 0, template_label_attribute, run_parameter.user_id, now, now))


                # 处理Region、RegionLabel和他的模板信息
                index = 0
                for region in image.regions:
                    region_id = str(uuid.uuid4())
                    # 提取需要写入的区域信息
                    region_values.append((region_id, image.id, index, region.shape, region.getShapeDataJson(), run_parameter.user_id, now, now, version))
                    index += 1

                    for region_label in region.labels:
                        background_color = self._getLabelBackgroundColor(region_label)
                        region_label_attribute = region_label.generateAttributeJson()
                        label_template_id = self._getLabelTemplateIdByTemplateName(region_label.name, merged_region_label_template_list, database_region_label_template_map) #self._findLabelTemplateId(region_label_template_map, region_label.name)
                        if label_template_id is None:
                            raise NotFoundException("运行异常，没有找到标签所属的模板信息")
                        region_label_id = str(uuid.uuid4())
                        region_label_values.append((region_label_id, image.id, region_id, label_template_id, TaggingType.IMPORT, version, region_label_attribute, run_parameter.user_id, now, now))

                # 写入新增的标签模板
                if insert_meta_label_template_values or insert_region_label_template_values:
                    print("insert new meta and region label template...")
                    print(insert_meta_label_template_values)
                    print(insert_region_label_template_values)
                    insert_label_template_sql = """insert into """ + self._config.project_label_template_table_name + """ (`id`, `projectId`, `name`, `type`, `source`, `heat`, `backgroundColor`, `enabled`, `required`, `defaulted`, `reviewed`, `attribute`, `creatorId`, `createTime`, `updateTime`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
                    insert_result = self._mysql.close_transaction_insert_many(insert_label_template_sql, insert_meta_label_template_values + insert_region_label_template_values)
                    print("insert " + str(insert_result) + " entries.")

                # 更新已经存在的有变更的标签模板
                if update_meta_label_template_values or update_region_label_template_values:
                    print("update meta and region label template.")
                    print(update_meta_label_template_values)
                    update_result = 0
                    update_label_template_sql = """update """ + self._config.project_label_template_table_name + """ set `attribute` = %s, `updateTime` = %s where `id` = %s"""
                    if update_meta_label_template_values:
                        for u_m_l_t_v in update_meta_label_template_values:
                            update_result += self._mysql.update(sql=update_label_template_sql, parameter=u_m_l_t_v, auto_commit=False)

                    print(update_region_label_template_values)
                    if update_region_label_template_values:
                        for u_r_l_t_v in update_region_label_template_values:
                            update_result += self._mysql.update(sql=update_label_template_sql, parameter=u_r_l_t_v, auto_commit=False)

                    # update_result = self._mysql.update(sql=update_label_template_sql, parameter=update_meta_label_template_values + update_region_label_template_values, auto_commit=False)
                    print("update " + str(update_result) + " entries.")

                # 处理并写入METALabel信息，关联LabelTemplate和图片
                if meta_label_values:
                    print("insert new image meta label info.")
                    print(meta_label_values)
                    insert_meta_label_sql = """insert into """ + self._config.project_meta_label_table_name + table_index + """ (`id`, `imageId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """
                    insert_result = self._mysql.close_transaction_insert_many(insert_meta_label_sql, meta_label_values)
                    print("insert " + str(insert_result) + " entries.")

                # 写入新增的region信息并关联图片
                if region_values:
                    print("insert new image region info.")
                    print(region_values)
                    insert_region_sql = """insert into """ + self._config.project_image_region_table_name + table_index + """ (`id`, `imageId`, `index`, `shape`, `shapeData`, `userId`, `createTime`, `updateTime`, `version`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    insert_result = self._mysql.close_transaction_insert_many(insert_region_sql, region_values)
                    print("insert " + str(insert_result) + " entries.")

                # 写入region的label信息，关联模板和图片
                if region_label_values:
                    print("insert new image region lable info.")
                    print(region_label_values)
                    insert_region_lable_sql = """insert into """ + self._config.project_image_region_label_table_name + table_index + """ (`id`, `imageId`, `regionId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                    insert_result = self._mysql.close_transaction_insert_many(insert_region_lable_sql, region_label_values)
                    print("insert " + str(insert_result) + " entries.")

                self._mysql.end()

                print("import image lable info success.")
        finally:
            self._mysql.destory(is_end=False)


    def importOneImageLabel(self, run_parameter, image):
        '''
        @description: 导入单张图片的标签信息的方法
        @param {type}
        @return:
        '''
        if not isinstance(image, Image):
            raise ClassCastException("请指定要导入标签的图片对象")

        self.importManyImageLabel(run_parameter=run_parameter, images=(image))

