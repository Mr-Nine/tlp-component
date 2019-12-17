
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 17:39:06
@LastEditTime: 2019-12-16 19:37:36
@Description:
'''
import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import MateLabel, ImageRegion
from TLPLibrary.error import ClassCastException

class Image(GenericEntity):

    def __init__(self, path):
        super(Image, self).__init__()

        self.path = path
        self.id = None
        self.mateLabels = []
        self.regions = []


    def addMateLabel(self, mateLabel):
        if not isinstance(mateLabel, MateLabel):
            raise ClassCastException("请添加MateLabel类型的标签到Image")

        for selfLabel in self.mateLabels:
            if selfLabel.name == mateLabel.name:
                raise ClassCastException("图片已包含同名MateLabe，请确认是否应该合并")

        self.mateLabels.append(mateLabel)

    def addImageRegion(self, imageRegion):
        if not isinstance(imageRegion, ImageRegion):
            raise ClassCastException("请添加ImagePolygonRegion或ImageRectangleRegion类型的区域到Image")

        self.regions.append(imageRegion)
