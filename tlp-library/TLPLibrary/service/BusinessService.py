
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-13 11:48:14
@LastEditTime: 2020-03-16 18:08:13
@Description:
'''
import os
import uuid
import time
import json
import random

from TLPLibrary.core import *
from TLPLibrary.error import *
from TLPLibrary.entity import *

class BusinessService(object):

    def __init__(self):
        self._mysql = Mysql()
        self._config = Config()

    def _generateRandomColors(self):
        return '#' + ("".join([random.choice("0123456789ABCDEF") for i in range(6)]))


    def _getLabelBackgroundColor(self, label):
        '''
        @description:检查并获取一个label的背景色
        '''
        if label.background_color:
            return label.background_color
        else:
            return self._generateRandomColors()


    def _checkRunParameter(self, run_parameter):
        '''
        @description: 检查运行参数的类型是否正确
        @param {RunParameter} runParameter: 运行参数对象
        '''
        if not isinstance(run_parameter, RunParameter):
            raise DataTypeException("请指定运行参数")


    def _checkImageParameter(self, run_parameter, image):
        '''
        @description:检查图片参数对象类型是否正确，是否包含必要的参数
        @param {Image} image: 图片对象
        '''
        if not isinstance(image, Image):
            raise DataTypeException("请指定要导入的图片信息")

        if not image.path:
            raise ParameterNotFoundException("请指定图存储的路径")

        # if not image.metaLabels and not image.regions:
        #     raise ParameterNotFoundException("请指定图片的标注信息")

        # if not os.path.exists(image.path):
        #     full_path = os.path.join(run_parameter.path, image.path)
        #     if os.path.exists(full_path):
        #         image.path = full_path
        #     else:
        #         raise ParameterNotFoundException("图片不能访问，请检查路径是否正确")


    def _checkImagesParameter(self, run_parameter, images):
        '''
        @description:检查图片列表参数对象类型是否正确，是否包含必要的参数
        @param {list} images: 图片对象的列表
        '''
        for image in images:
            self._checkImageParameter(run_parameter, image)


    def _findProjectInfo(self, run_parameter):
        '''
        @description:查找运行参数中指定的项目Id
        @param {RunParameter} run_parameter:启动的运行参数
        @return:如果查找到则返回项目信息的dict，否则抛出异常
        '''
        find_project_sql = """select * from """ + self._config.project_table_name + """ where id = %s"""
        find_project_result = self._mysql.selectOne(find_project_sql, (run_parameter.project_id, ))
        if not find_project_result[0]:
            raise NotFoundException("指定的项目不存在")

        return Utils.transform_database_result_2_dict(find_project_result[1])


    def _findProjectImageInfo(self, table_name, image_path):
        '''
        @description:
        @param {type}
        @return:
        '''
        find_project_image_sql = """select * from """ + table_name + """ where path = %s"""
        find_image_result = self._mysql.selectOne(find_project_image_sql, (image_path, ))
        if not find_image_result[0]:
            raise NotFoundException("指定的图片并不存在于项目中")

        return Utils.transform_database_result_2_dict(find_image_result[1])


    def _groupLabel(self, label_template_list):
        '''
        @description:将name相同的label分组
        '''
        label_name_map = {}
        for label in label_template_list:
            label_name = label.name
            if label_name not in label_name_map:
                label_name_map[label_name] = []

            label_name_map[label_name].append(label)

        return label_name_map


    def _findLabelTemplateId(self, label_template_map, find_name):
        '''
        @description: 在数据库的dict中查找默认的ID信息
        '''
        if find_name in label_template_map:
            return label_template_map[find_name]['id']

        return None


    def _getLabelTemplateIdByTemplateName(self, find_name, merge_result_list, database_template_map):
        '''
        @description: 在merge后的列表和数据库的dict中查找template的Id信息
        '''
        if find_name in database_template_map:
            return database_template_map[find_name]['id']

        for merge_template in merge_result_list:
            if merge_template['name'] == find_name:
                return merge_template['id']

        return None


    def _loadProjectLabelsByDatabase(self, project_id, label_type, names = None):
        '''
        @description:
        '''
        select_sql = "select * from AnnotationProjectLabelTemplate where `projectId` = %s and `type` = %s"
        if names:
            names_str = ""
            for name in names:
                names_str += "'" + name + "',"
            select_sql += " and name in (" + names_str[:-1] + ")"
        labels = self._mysql.selectAll(select_sql, (project_id, label_type, ))

        if labels[0]:
            return labels[1]
        return None


    def _getImportBatchVersion(self, project_id=None, label_type=None):
        '''
        @description: 返回当前时间戳作为导入或推理的写入版本号
        @project_id {}:
        @label_type {}:
        '''
        return time.time()


    def _getInferencerBatchVersion(self, inferencer_id):
        '''
        @description:获取推理器的版本信息
        @param {type}
        @return:
        '''
        current_version_result = self._mysql.selectOne("""select version from """ + self._config.project_reasoning_machine_table_name + """ where id = %s""", (inferencer_id, ))
        if current_version_result[0]:
            return current_version_result[1]['version']

        return None


    def _getInferencerInfo(self, inferencer_id):
        '''
        @description:
        @param {type}
        @return:
        '''
        inferencer_result = self._mytsql.selectOne("""select * from """ + self._config.project_reasoning_machine_table_name + """ where id = %s""", (inferencer_id, ))
        if inferencer_result[0]:
            return Utils.transform_database_result_2_dict(inferencer_result[1])

        return None


    def _getRegionAndLabelInferencerLastVersionFromImage(self, image_id, table_index):
        '''
        @description:
        @param {type}
        @return:
        '''
        str_index = str(table_index)
        region_table_name = self._config.project_image_region_table_name + str_index
        meta_label_table_name = self._config.project_meta_label_table_name + str_index
        region_label_table_name = self._config.project_image_region_label_table_name + str_index

        last_version_result = self._mysql.selectOne("select (select IFNULL(MAX(version), -1) from " + region_table_name + ") as region_last_version, (select IFNULL(MAX(version), -1) from " + meta_label_table_name + " where type ) as meta_label_last_version")
        if last_version_result[0]:
            max_version = int(last_version_result[1]["region_last_version"])
            if max_version < int(last_version_result[1]["meta_label_last_version"]):
                max_version = int(last_version_result[1]["meta_label_last_version"])
            if max_version < int(last_version_result[1]["region_label_last_version"]):
                max_version = int(last_version_result[1]["region_label_last_version"])

            return max_version

        return -1


    def _isNewLabel(self, label_name, merge_template_list, database_label_template_map):
        '''
        @description:
        '''
        return (not self._isExistedLable(label_name, database_label_template_map) and not self._isIncludeLable(label_name, merge_template_list))

    def _isExistedLable(self, label_name, database_label_template_map):
        '''
        @description:
        '''
        return label_name in database_label_template_map


    def _isIncludeLable(self, label_name, merge_template_list):
        '''
        @description:
        '''
        for tamplate_label in merge_template_list:
            if tamplate_label['name'] == label_name:
                return True
        return False


    def _attributeIsUpdate(self, attribute, attribute2):
        '''
        @description:
        '''
        print(attribute["type"] + " === " + attribute2["type"])
        return attribute["type"] != attribute2["type"]


    def _buildLabelTemplateDatabaseMap(self, project_id, leabel_type):
        '''
        @description:
        @param {type}
        @return:
        '''
        meta_label_template_map = {}
        database_result = self._loadProjectLabelsByDatabase(project_id, leabel_type)

        if database_result is None:
            return meta_label_template_map

        for database_label in database_result:
            label_dict = Utils.transform_database_result_2_dict(database_label)
            if 'attribute' in label_dict and label_dict['attribute'] is not None and len(label_dict['attribute']) > 1:
                label_dict['attribute'] = json.loads(label_dict['attribute'])
            meta_label_template_map[label_dict['name']] = label_dict

        return meta_label_template_map


    def _mergeLabelTemplateAttribute(self, source_attribute_list, target_attribute_list):
        '''
        @description:
        '''
        update = False
        for source_attribute in source_attribute_list:
            find = False
            for target_attribute in target_attribute_list:
                if source_attribute['key'] == target_attribute['key']:
                    find = True
                    if self._attributeIsUpdate(source_attribute, target_attribute):
                        target_attribute['type'] = source_attribute['type'] # TODO覆盖
                        target_attribute['default'] = source_attribute['default'] # TODO覆盖
                        target_attribute['name'] = source_attribute['name'] # TODO覆盖
                        update = True

            if not find:
                target_attribute_list.append(source_attribute)
                update = True

        return update


    def _mergeLabelTemplate(self, ready_label_list, database_label_template_map, merge_result_list):
        '''
        @description: 整合模板数据的方法
            找到已经存在的name相同的模板，检查是否要更新(属性模板有变化)，把需要更新的处理出来(带模板ID);
            找到当前不存在的模板，name没有，把需要新建的处理出来(不带模板ID);
        @param {list} ready_label_template_list:写入前未整合的label模板信息
        @param {dict} database_label_template_map:数据库中已经存在的模板信息
        @param {list} merge_result_list:返回整理后的结果
        '''
        print("*****************************************merge开始******************************************")
        print('')
        # 整合名称相同的KEY，将返回的数据结构调整为map
        ready_label_map = self._groupLabel(ready_label_list)
        for ready_label_name in ready_label_map:
            ready_lables = ready_label_map[ready_label_name]
            print(ready_label_name)

            # 数据库中和merge内存中都没有这个label模板
            if self._isNewLabel(ready_label_name, merge_result_list, database_label_template_map):
                print("新的模板")
                new_template = {}
                new_template["id"] = None
                new_template["name"] = ready_label_name
                new_template["type"] = ready_lables[0].type
                new_template["backgroundColor"] = ready_lables[0].background_color
                new_template["attribute"] = []

                # 整理属性, 因为一个标签下会有多个属性，so需要做2层的整理
                for ready_label in ready_lables:
                    ready_label_templates = ready_label.generateLabelTemplateData()
                    self._mergeLabelTemplateAttribute(ready_label_templates, new_template["attribute"])

                merge_result_list.append(new_template)

            # 内存中已经存在merge过
            elif self._isIncludeLable(ready_label_name, merge_result_list):
                print("内存中已存在")
                include_template = None
                for include in merge_result_list:
                    if include['name'] == ready_label_name:
                        include_template = include

                for ready_label in ready_lables:
                    ready_label_template_attributes = ready_label.generateLabelTemplateData()
                    self._mergeLabelTemplateAttribute(ready_label_template_attributes, include_template["attribute"])

            # 数据库中这个模板存在属性信息
            else:
                print("数据库中已存在")
                label_template = database_label_template_map[ready_label_name]
                template_attributes = label_template["attribute"]

                if template_attributes:
                    for ready_label in ready_lables:
                        ready_label_template_attributes = ready_label.generateLabelTemplateData()
                        update = self._mergeLabelTemplateAttribute(ready_label_template_attributes, template_attributes)
                        # label_template['attribute'] = template_attributes
                        if update:
                            print("待更新模板：" + json.dumps(label_template))
                            merge_result_list.append(label_template)

        print("*****************************************merge结束******************************************")
        print('')
        #     # 为当前导入批次初始化一个新的name集合
        #     if loaded_label_template_name not in database_label_template_map:
        #         # 定义的基础数据结构必须和数据相同，要不就挂了
        #         database_label_template_map[loaded_label_template_name] = {}
        #         database_label_template_map[loaded_label_template_name]["id"] = str(uuid.uuid4())
        #         database_label_template_map[loaded_label_template_name]["name"] = loaded_label_template_name
        #         database_label_template_map[loaded_label_template_name]["attribute"] = []
        #         database_label_template_map[loaded_label_template_name]["backgroundColor"] = None

        #     # 整合template的属性模板
        #     for label in loaded_lable_templates:
        #         # 从all模板集合中获取当前
        #         label_template = database_label_template_map[loaded_label_template_name]
        #         #
        #         template_attributes = label_template["attribute"] # json.loads()
        #         loaded_template_attributes = label.generateLabelTemplateData()
        #         for attribute in loaded_template_attributes:
        #             # attribute={'default': '', 'name': 'K6', 'key': 'K6', 'type': 'TEXT'}
        #             if template_attributes and attribute['key'] in template_attributes:
        #                 template_attribute['type'] = attribute['type'] # TODO覆盖
        #                 template_attribute['default'] = attribute['default'] # TODO覆盖
        #                 template_attribute['name'] = attribute['name'] # TODO覆盖
        #             else:
        #                 template_attributes.append(attribute)
        #                 label_template["backgroundColor"] = label.background_color # TODO:应该没用

        #         # 更新模板的attribute
        #         label_template['attribute'] = template_attributes


        # return database_label_template_map
