
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 20:44:56
@LastEditTime: 2019-12-16 21:43:26
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


    def importManyImageLabel(self, runParameter, images):
        '''
        @description:批量导入
        @param {type}
        @return:
        '''

        try:
            self._checkRunParameter(runParameter)
            self._checkImagesParameter(runParameter, images)

            projectInfo = self._findProjectInfo(runParameter)
            tableIndex = str(projectInfo['index'])

            now = datetime.datetime.today()
            version = 1 # TODO:获取并生成本地导入的version

            mateLabelTemplateMap = {}
            regionLabelTemplateMap = {}
            mateLabelTemplateValues = []
            mateLabelValues = []
            regionLabelTemplateValues = []
            regionValues = []
            regionLabelValues = []

            for image in images:
                imageInfo = self._findProjectImageInfo(self._config.project_image_table_name + tableIndex, image.path)
                image.id = imageInfo['id']

                # 提取MateLabel的Template
                mateLabelTemplateMap = self._mergeLabelTemplate(image.mateLabels, mateLabelTemplateMap)

                # 提取regionLabel的Template
                for region in image.regions:
                    regionLabelTemplateMap = self._mergeLabelTemplate(region.labels, regionLabelTemplateMap)

                # 处理图片的MateLabelTemplate信息
                for label_name in mateLabelTemplateMap:
                    mateLabelTemplate = mateLabelTemplateMap[label_name]
                    backgroundColor = mateLabelTemplate["backgroundColor"]
                    if not backgroundColor:
                        backgroundColor = self._generateRandomColors()
                    templateLabelAttribute = json.dumps(mateLabelTemplate["template_attributes"])
                    mateLabelTemplateValues.append((mateLabelTemplate['template_id'], runParameter.projectId, label_name, LabelType.MATE, TaggingType.AUTO, 1, reasoningMachineId, backgroundColor, 0, 0, 0, 0, templateLabelAttribute, runParameter.userId, now, now))

                # 处理图片的MateLabel信息
                for mateLabel in image.mateLabels:
                    labelTemplateId = self._findLabelTemplateId(mateLabelTemplateMap, mateLabel.name)
                    mateLabelId = str(uuid.uuid4())
                    mateLabelAttribute = mateLabel.generateAttributeJson()
                    mateLabelValues.append((mateLabelId, image.id, labelTemplateId, TaggingType.AUTO, '1', mateLabelAttribute, runParameter.userId, now, now))

                # 处理图片的RegionLabelTemplate信息
                for label_name in regionLabelTemplateMap:
                    regionLabelTemplate = regionLabelTemplateMap[label_name]
                    backgroundColor = regionLabelTemplate["backgroundColor"]
                    if not backgroundColor:
                        backgroundColor = self._generateRandomColors()
                    templateLabelAttribute = json.dumps(regionLabelTemplate["template_attributes"])
                    regionLabelTemplateValues.append((regionLabelTemplate['template_id'], runParameter.projectId, label_name, LabelType.REGION, TaggingType.AUTO, 1, reasoningMachineId, backgroundColor, 0, 0, 0, 0, templateLabelAttribute, runParameter.userId, now, now))

                # 处理Region、RegionLabel和他的模板信息

                index = 0
                for region in image.regions:
                    regionId = str(uuid.uuid4())
                    regionValues.append((regionId, image.id, index, region.shape, region.getShapeDataJson(), runParameter.userId, now, now))
                    index += 1

                    for regionLabel in region.labels:
                        backgroundColor = self._get_label_background_color(regionLabel)
                        templateLabelAttribute = regionLabel.generateLabelTemplateJson()
                        regionLabelAttribute = regionLabel.generateAttributeJson()
                        labelTemplateId =  self._findLabelTemplateId(regionLabelTemplateMap, regionLabel.name)
                        regionLabelId = str(uuid.uuid4())
                        regionLabelValues.append((regionLabelId, image.id, regionId, labelTemplateId, TaggingType.AUTO, '1.0', regionLabelAttribute, runParameter.userId, now, now))

                insert_label_template_sql = """insert into """ + self._config.project_label_template_table_name + """ (`id`, `projectId`, `name`, `type`, `source`, `heat`, `reasoningMachineId`, `backgroundColor`, `enabled`, `required`, `defaulted`, `reviewed`, `attribute`, `creatorId`, `createTime`, `updateTime`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
                insert_result = self._mysql.close_transaction_insert_many(insert_label_template_sql, (mateLabelTemplateValues + regionLabelTemplateValues))

                if not insert_result:
                    raise DataBaseException("写入标签模板信息失败")

                # 处理并写入MateLabel信息，关联LabelTemplate和图片
                insert_mate_label_sql = """insert into """ + self._config.project_mate_label_table_name + tableIndex + """ (`id`, `imageId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """
                insert_result = self._mysql.close_transaction_insert_many(insert_mate_label_sql, mateLabelValues)

                if not insert_result:
                    raise DataBaseException("写入图片的Mate标签信息失败")

                # 处理并写入Region信息,关联图片
                insert_region_sql = """insert into """ + self._config.project_image_region_table_name + tableIndex + """ (`id`, `imageId`, `index`, `shape`, `shapeData`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s)"""
                insert_result = self._mysql.close_transaction_insert_many(insert_region_sql, regionValues)

                if not insert_result:
                    raise DataBaseException("写入图片的Region信息失败")

                # 处理并写入RegionLabel信息，关联图片和LabelTemplate
                insert_region_lable_sql = """insert into """ + self._config.project_image_region_label_table_name + tableIndex + """ (`id`, `imageId`, `regionId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
                insert_result = self._mysql.close_transaction_insert_many(insert_region_lable_sql, regionLabelValues)

                if not insert_result:
                    raise DataBaseException("写入图片的RegionLabel信息失败")

                self._mysql.end()

                return True




            # 处理MateLabel的模板信息和图片的MateLabel信息
            mateLabelTemplateValues = []
            mateLabelValues = []
            for mateLabel in image.mateLabels:
                backgroundColor = self._get_label_background_color(mateLabel)
                labelTemplateId = str(uuid.uuid4())
                mateLabelId = str(uuid.uuid4())
                templateLabelAttribute = mateLabel.generateLabelTemplateJson()
                mateLabelAttribute = mateLabel.generateAttributeJson()

                mateLabelTemplateValues.append((labelTemplateId, runParameter.projectId, mateLabel.name, mateLabel.type, TaggingType.IMPORT, 1, backgroundColor, 0, 0, 0, 0, templateLabelAttribute, runParameter.userId, now, now))
                mateLabelValues.append((mateLabelId, image.id, labelTemplateId, TaggingType.IMPORT, '1', mateLabelAttribute, runParameter.userId, now, now))

            # 处理Region、RegionLabel和他的模板信息
            regionLabelTemplateValues = []
            regionValues = []
            regionLabelValues = []
            index = 0
            for region in image.regions:
                regionId = str(uuid.uuid4())
                regionValues.append((regionId, image.id, index, region.shape, region.getShapeDataJson(), runParameter.userId, now, now))
                index += 1

                for regionLabel in region.labels:
                    backgroundColor = self._get_label_background_color(regionLabel)
                    templateLabelAttribute = regionLabel.generateLabelTemplateJson()
                    regionLabelAttribute = regionLabel.generateAttributeJson()
                    labelTemplateId =  str(uuid.uuid4())
                    regionLabelId = str(uuid.uuid4())

                    regionLabelTemplateValues.append((labelTemplateId, runParameter.projectId, regionLabel.name, regionLabel.type, TaggingType.IMPORT, 1, backgroundColor, 0, 0, 0, 0, templateLabelAttribute, runParameter.userId, now, now))
                    regionLabelValues.append((regionLabelId, image.id, regionId, labelTemplateId, TaggingType.IMPORT, '1.0', regionLabelAttribute, runParameter.userId, now, now))

            insert_label_template_sql = """insert into """ + self._config.project_label_template_table_name + """ (`id`, `projectId`, `name`, `type`, `source`, `heat`, `backgroundColor`, `enabled`, `required`, `defaulted`, `reviewed`, `attribute`, `creatorId`, `createTime`, `updateTime`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
            insert_result = self._mysql.close_transaction_insert_many(insert_label_template_sql, (mateLabelTemplateValues + regionLabelTemplateValues))
            if not insert_result:
                raise DataBaseException("写入标签模板信息失败")

            # 处理并写入MateLabel信息，关联LabelTemplate和图片
            insert_mate_label_sql = """insert into """ + self._config.project_mate_label_table_name + tableIndex + """ (`id`, `imageId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """
            insert_result = self._mysql.close_transaction_insert_many(insert_mate_label_sql, mateLabelValues)

            if not insert_result:
                raise DataBaseException("写入图片的Mate标签信息失败")

            # 处理并写入Region信息,关联图片
            insert_region_sql = """insert into """ + self._config.project_image_region_table_name + tableIndex + """ (`id`, `imageId`, `index`, `shape`, `shapeData`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s)"""
            insert_result = self._mysql.close_transaction_insert_many(insert_region_sql, regionValues)

            if not insert_result:
                raise DataBaseException("写入图片的Region信息失败")

            # 处理并写入RegionLabel信息，关联图片和LabelTemplate
            insert_region_lable_sql = """insert into """ + self._config.project_image_region_label_table_name + tableIndex + """ (`id`, `imageId`, `regionId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            insert_result = self._mysql.close_transaction_insert_many(insert_region_lable_sql, regionLabelValues)

            if not insert_result:
                raise DataBaseException("写入图片的RegionLabel信息失败")

            self._mysql.end()

            return True

        finally:
            self._mysql.destory(is_end=False)

    def importMaryImageLabels(self, runParameter, images):
        self._checkRunParameter(runParameter)
        self._checkImagesParameter(images)

        pass

