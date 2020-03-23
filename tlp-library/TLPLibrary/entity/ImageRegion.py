# -- coding: utf-8 --

import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import RegionType, RegionLabel
from TLPLibrary.error import ClassCastException

class ImageRegion(GenericEntity):
    '''
    标识图片上一个标注区域的对象描述
    '''
    def __init__(self, points, bounding_box):
        '''初始化一个区域对象

        Args:
            points (list): ((point1, point2), (point3, point4)...(pointN, pointN+1))
            bounding_box (list): ((point1, point2), (point3, point4), (point5, point6), (point7, point8))
        '''
        super(ImageRegion, self).__init__()

        if not isinstance(points, list):
            raise ClassCastException()
        if not isinstance(bounding_box, list) or len(bounding_box) != 4:
            raise ClassCastException()
        if len(points) < 3:
            raise ClassCastException()

        self.shape_data = points
        self.bounding_box = bounding_box
        self.labels = []


    def addRegionLabel(self, label):
        '''关联一个区域的标签对象

        Args:
            label (RegionLabel): 关联
        '''
        if not isinstance(label, RegionLabel):
            raise ClassCastException("add region label type error.")

        # if label.name in self.labels:
        #     # 整合名称相同的Label
        #     self.labels[label.name].append()

        self.labels.append(label)

    def getShapeDataJson(self):
        '''获取描述区域形状的坐标数据的JSON结构。

        Returns (json):
            JSON结构的数据结构[[point, point], [point, point], [point, point], [point, point]]
        '''
        if self.shape_data:
            return json.dumps(self.shape_data)

        return "[]"


class ImagePolygonRegion(ImageRegion):
    '''描述一个多边形区域的对象
    '''
    def __init__(self, points, bounding_box):
        super(ImagePolygonRegion, self).__init__(points, bounding_box)
        self.shape = RegionType.POLYGON
        self.shape_data.append(points[0])


class ImageRectangleRegion(ImageRegion):
    '''描述一个举行区域的对象
    '''
    def __init__(self, points, bounding_box):
        super(ImageRectangleRegion, self).__init__(points, bounding_box)
        self.shape = RegionType.RECTANGLE

        if len(points) == 4:
            self.shape_data.append(points[0])