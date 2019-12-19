
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 20:45:34
@LastEditTime: 2019-12-19 14:55:44
@Description:
'''

import uuid
import json
import datetime

from TLPLibrary.core import *
from TLPLibrary.error import *
from TLPLibrary.entity import *
from TLPLibrary.service import BusinessService

class InferencerLabelService(BusinessService):

    def __init__(self):
        super(InferencerLabelService, self).__init__()


    def inferencerOneImageLabel(self, runParameter, image):
        try:
            if not runParameter.inferencerId:
                raise NotFoundException("请指定标注器的ID")

            self._checkRunParameter(runParameter)
            self._checkImageParameter(runParameter, image)

            projectInfo = self._findProjectInfo(runParameter)
            tableIndex = str(projectInfo['index'])
            inferencerId = runParameter.inferencerId

            imageInfo = self._findProjectImageInfo(self._config.project_image_table_name + tableIndex, image.path)
            image.id = imageInfo['id']

            now = datetime.datetime.today()
            version = 1

            # 提取MateLabel的Template
            mateLabelTemplateMap = self._mergeLabelTemplate(image.mateLabels, {})

            # 提取regionLabel的Template
            regionLabelTemplateMap = {}
            for region in image.regions:
                regionLabelTemplateMap = self._mergeLabelTemplate(region.labels, regionLabelTemplateMap)

            # 处理图片的MateLabelTemplate信息
            mateLabelTemplateValues = []
            for label_name in mateLabelTemplateMap:
                mateLabelTemplate = mateLabelTemplateMap[label_name]
                backgroundColor = mateLabelTemplate["backgroundColor"]
                if not backgroundColor:
                    backgroundColor = self._generateRandomColors()
                templateLabelAttribute = json.dumps(mateLabelTemplate["template_attributes"])
                mateLabelTemplateValues.append((mateLabelTemplate['template_id'], runParameter.projectId, label_name, LabelType.MATE, TaggingType.AUTO, 1, inferencerId, backgroundColor, 0, 0, 0, 0, templateLabelAttribute, runParameter.userId, now, now))

            # 处理图片的MateLabel信息
            mateLabelValues = []
            for mateLabel in image.mateLabels:
                labelTemplateId = self._findLabelTemplateId(mateLabelTemplateMap, mateLabel.name)
                mateLabelId = str(uuid.uuid4())
                mateLabelAttribute = mateLabel.generateAttributeJson()
                mateLabelValues.append((mateLabelId, image.id, labelTemplateId, TaggingType.AUTO, '1', mateLabelAttribute, runParameter.userId, now, now))

            # 处理图片的RegionLabelTemplate信息
            regionLabelTemplateValues = []
            for label_name in regionLabelTemplateMap:
                regionLabelTemplate = regionLabelTemplateMap[label_name]
                backgroundColor = regionLabelTemplate["backgroundColor"]
                if not backgroundColor:
                    backgroundColor = self._generateRandomColors()
                templateLabelAttribute = json.dumps(regionLabelTemplate["template_attributes"])
                regionLabelTemplateValues.append((regionLabelTemplate['template_id'], runParameter.projectId, label_name, LabelType.REGION, TaggingType.AUTO, 1, inferencerId, backgroundColor, 0, 0, 0, 0, templateLabelAttribute, runParameter.userId, now, now))

            # 处理Region、RegionLabel和他的模板信息
            regionValues = []
            regionLabelValues = []
            index = 0
            for region in image.regions:
                regionId = str(uuid.uuid4())
                regionValues.append((regionId, image.id, 'AUTO', index, region.shape, region.getShapeDataJson(), runParameter.userId, now, now))
                index += 1

                for regionLabel in region.labels:
                    backgroundColor = self._get_label_background_color(regionLabel)
                    templateLabelAttribute = regionLabel.generateLabelTemplateJson()
                    regionLabelAttribute = regionLabel.generateAttributeJson()
                    labelTemplateId =  self._findLabelTemplateId(regionLabelTemplateMap, regionLabel.name)
                    regionLabelId = str(uuid.uuid4())
                    regionLabelValues.append((regionLabelId, image.id, regionId, labelTemplateId, TaggingType.AUTO, '1.0', regionLabelAttribute, runParameter.userId, now, now))

            insert_label_template_sql = """insert into """ + self._config.project_label_template_table_name + """ (`id`, `projectId`, `name`, `type`, `source`, `heat`, `inferencerId`, `backgroundColor`, `enabled`, `required`, `defaulted`, `reviewed`, `attribute`, `creatorId`, `createTime`, `updateTime`) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) """
            insert_result = self._mysql.close_transaction_insert_many(insert_label_template_sql, (mateLabelTemplateValues + regionLabelTemplateValues))

            if not insert_result:
                raise DataBaseException("写入标签模板信息失败")

            # 处理并写入MateLabel信息，关联LabelTemplate和图片
            insert_mate_label_sql = """insert into """ + self._config.project_mate_label_table_name + tableIndex + """ (`id`, `imageId`, `labelId`, `type`, `version`, `attribute`, `userId`, `createTime`, `updateTime`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) """
            insert_result = self._mysql.close_transaction_insert_many(insert_mate_label_sql, mateLabelValues)

            if not insert_result:
                raise DataBaseException("写入图片的Mate标签信息失败")

            # 处理并写入Region信息,关联图片
            insert_region_sql = """insert into """ + self._config.project_image_region_table_name + tableIndex + """ (`id`, `imageId`, `type`, `index`, `shape`, `shapeData`, `userId`, `createTime`, `updateTime`) values (%s, %s, %s, %s, %s, %s, %s, %s)"""
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