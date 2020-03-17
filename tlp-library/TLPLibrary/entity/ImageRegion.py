
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 15:28:16
@LastEditTime: 2020-03-12 11:02:24
@Description:
'''
import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import RegionType, RegionLabel
from TLPLibrary.error import ClassCastException

class ImageRegion(GenericEntity):

    def __init__(self, points, bounding_box):

        super(ImageRegion, self).__init__()

        if not isinstance(points, list):
            raise ClassCastException()
        if not isinstance(bounding_box, list) or len(bounding_box) != 4:
            raise ClassCastException()

        self.shape_data = points
        self.bounding_box = bounding_box
        self.labels = []


    def addRegionLabel(self, label):
        if not isinstance(label, RegionLabel):
            raise ClassCastException("只能为ImageRegion添加RegionLabel类型的Label")

        # if label.name in self.labels:
        #     # 整合名称相同的Label
        #     self.labels[label.name].append()

        self.labels.append(label)

    def getShapeDataJson(self):
        if self.shape_data:
            return json.dumps(self.shape_data)

        return "[]"


class ImagePolygonRegion(ImageRegion):

    def __init__(self, points, bounding_box):
        super(ImagePolygonRegion, self).__init__(points, bounding_box)
        self.shape = RegionType.POLYGON


class ImageRectangleRegion(ImageRegion):

    def __init__(self, points, bounding_box):
        super(ImageRectangleRegion, self).__init__(points, bounding_box)
        self.shape = RegionType.RECTANGLE