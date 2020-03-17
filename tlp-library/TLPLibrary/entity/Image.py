
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 17:39:06
@LastEditTime: 2020-03-16 14:51:39
@Description:
'''
import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import MetaLabel, ImageRegion
from TLPLibrary.error import ClassCastException

class Image(GenericEntity):

    def __init__(self, path):
        super(Image, self).__init__()

        self.path = path
        self.id = None
        self.meta_labels = []
        self.regions = []


    def addMetaLabel(self, meta_label):
        if not isinstance(meta_label, MetaLabel):
            raise ClassCastException("请添加MetaLabel类型的标签到Image")

        #TODO:是否要合并同名
        # for self_label in self.meta_labels:
        #     if self_label.name == meta_label.name:
        #         raise ClassCastException("图片已包含同名MetaLabe，请确认是否应该合并")

        # for self_label in self.meta_labels:
        #     if self_label.name == meta_label.name:
        #         self_label.name = meta_label.name
        #         self_label.background_color = meta_label.background_color

        #         self_label.attributes = {}

        self.meta_labels.append(meta_label)

    def addImageRegion(self, image_region):
        if not isinstance(image_region, ImageRegion):
            raise ClassCastException("请添加ImagePolygonRegion或ImageRectangleRegion类型的区域到Image")

        self.regions.append(image_region)
