
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 15:28:16
@LastEditTime: 2019-12-14 00:20:14
@Description:
'''
import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import RegionType, RegionLabel
from TLPLibrary.error import ClassCastException

class ImageRegion(GenericEntity):

    def __init__(self, points, boundingBox):

        super(ImageRegion, self).__init__()

        if not isinstance(points, list):
            raise ClassCastException()
        if not isinstance(boundingBox, list) or len(boundingBox) != 4:
            raise ClassCastException()

        self.shapeData = points
        self.boundingBox = boundingBox
        self.labels = []


    def addRegionLabel(self, label):
        if not isinstance(label, RegionLabel):
            raise ClassCastException("只能为ImageRegion添加RegionLabel类型的Label")

        # if label.name in self.labels:
        #     # 整合名称相同的Label
        #     self.labels[label.name].append()

        self.labels.append(label)

    def getShapeDataJson(self):
        if self.shapeData:
            return json.dumps(self.shapeData)

        return "[]"


class ImagePolygonRegion(ImageRegion):

    def __init__(self, points, boundingBox):
        super(ImagePolygonRegion, self).__init__(points, boundingBox)
        self.shape = RegionType.POLYGON


class ImageRectangleRegion(ImageRegion):

    def __init__(self, points, boundingBox):
        super(ImageRectangleRegion, self).__init__(points, boundingBox)
        self.shape = RegionType.RECTANGLE