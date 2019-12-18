
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-13 11:48:14
@LastEditTime: 2019-12-18 18:16:34
@Description:
'''
import os
import uuid
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


    def _get_label_background_color(self, label):
        '''
        @description:检查并获取一个label的背景色
        '''
        if label.backgroundColor:
            return label.backgroundColor
        else:
            return self._generateRandomColors()


    def _checkRunParameter(self, runParameter):
        '''
        @description: 检查运行参数的类型是否正确
        @param {RunParameter} runParameter: 运行参数对象
        '''
        if not isinstance(runParameter, RunParameter):
            raise DataTypeException("请指定运行参数")


    def _checkImageParameter(self, runParameter, image):
        '''
        @description:检查图片参数对象类型是否正确，是否包含必要的参数
        @param {Image} image: 图片对象
        '''
        if not isinstance(image, Image):
            raise DataTypeException("请指定要导入的图片信息")

        if not image.path:
            raise ParameterNotFoundException("请指定图存储的路径")

        # if not image.mateLabels and not image.regions:
        #     raise ParameterNotFoundException("请指定图片的标注信息")

        # if not os.path.exists(image.path):
        #     full_path = os.path.join(runParameter.path, image.path)
        #     if os.path.exists(full_path):
        #         image.path = full_path
        #     else:
        #         raise ParameterNotFoundException("图片不能访问，请检查路径是否正确")


    def _checkImagesParameter(self, images):
        '''
        @description:检查图片列表参数对象类型是否正确，是否包含必要的参数
        @param {list} images: 图片对象的列表
        '''
        for image in images:
            checkImageParameter(image)


    def _findProjectInfo(self, runParameter):
        '''
        @description:查找运行参数中指定的项目Id
        @param {RunParameter} runParameter:启动的运行参数
        @return:如果查找到则返回项目信息的dict，否则抛出异常
        '''
        find_project_sql = """select * from """ + self._config.project_table_name + """ where id = %s"""
        find_project_result = self._mysql.selectOne(find_project_sql, (runParameter.projectId, ))
        if not find_project_result[0]:
            raise NotFoundException("指定的项目不存在")

        return Utils.transform_database_result_2_dict(find_project_result[1])


    def _findProjectImageInfo(self, tableName, imagePath):
        '''
        @description:
        @param {type}
        @return:
        '''
        find_project_image_sql = """select * from """ + tableName + """ where path = %s"""
        find_image_result = self._mysql.selectOne(find_project_image_sql, (imagePath, ))
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
        {'01': {'template_id': '094f8034-1bf5-40f4-87be-34ac9f8b93a9', 'template_attributes': [{'key': 'K1', 'valueType': 'INT'}, {'key': 'K2', 'valueType': 'INT'}, {'key': 'K3', 'valueType': 'FLOAT'}, {'key': 'K13', 'valueType': 'INT'}, {'key': 'K11', 'valueType': 'FLOAT'}]}, '04': {'template_id': '5e2f96af-234c-4259-a08f-33f3e00f8dde', 'template_attributes': [{'key': 'K10', 'valueType': 'INT'}, {'key': 'K11', 'valueType': 'INT'}, {'key': 'K12', 'valueType': 'TEXT'}]}}
        {'02': {'template_id': '54f5ed48-9bec-4602-8b6a-a1478003dada', 'template_attributes': [{'key': 'K4', 'valueType': 'INT'}, {'key': 'K5', 'valueType': 'INT'}, {'key': 'K6', 'valueType': 'TEXT'}]}, '03': {'template_id': 'b2b679a1-d173-40e2-8a7e-6b30a9ef2ee7', 'template_attributes': [{'key': 'K10', 'valueType': 'INT'}, {'key': 'K11', 'valueType': 'INT'}, {'key': 'K9', 'valueType': 'FLOAT'}]}}
        '''
        if find_name in label_template_map:
            return label_template_map[find_name]['template_id']

        return None


    def _mergeLabelTemplate(self, label_template_list, label_template_map):
        '''
        @description: 整合模板数据的方法，会在写入前先将模板的数据进行整合，
        将重复的name和类型作为唯一值，追加不重复Key的attribute,最后在分配ID。
        @param {list} label_template_list:写入前未整合的label模板信息
        '''
        label_name_map = self._groupLabel(label_template_list)

        # 整合名称相同的KEY，将返回的数据结构调整为:
        for label_name in label_name_map:
            labels = label_name_map[label_name]

            # 为当前导入批次初始化一个新的name集合
            if label_name not in label_template_map:
                label_template_map[label_name] = {}
                label_template_map[label_name]["template_id"] = str(uuid.uuid4())
                label_template_map[label_name]["template_attributes"] = []
                label_template_map[label_name]["backgroundColor"] = None

            # label=[{'key':'', 'valueType':''}, {'key':'', 'valueType':''}, {'key':'', 'valueType':''}], [{'key':'', 'valueType':''}, {'key':'', 'valueType':''}, {'key':'', 'valueType':''}]
            for label in labels:
                label_template = label_template_map[label_name]
                # template_attributes=[{'key':'', 'valueType:''}, {'key':'', 'valueType:''}]
                template_attributes = label_template["template_attributes"]
                # label.generateLabelTemplateData=[{'key':'', 'valueType':''}, {'key':'', 'valueType':''}]
                for attribute in label.generateLabelTemplateData():
                    # attribute={'key':'', 'valueType:''}
                    find = False

                    if template_attributes:
                        for template_attribute in template_attributes:
                            if attribute['key'] == template_attribute['key']:
                                find = True
                                template_attribute['type'] = attribute['type'] # 覆盖

                    if not find:
                        label_template["backgroundColor"] = label.backgroundColor
                        template_attributes.append(attribute)


        return label_template_map
