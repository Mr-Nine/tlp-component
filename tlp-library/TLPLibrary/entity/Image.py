# -- coding: utf-8 --
import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import MetaLabel, ImageRegion
from TLPLibrary.error import ClassCastException

class Image(GenericEntity):
    '''描述一个
    '''
    def __init__(self, path):
        super(Image, self).__init__()

        self.path = path
        self.id = None
        self.meta_labels = []
        self.regions = []


    def addMetaLabel(self, meta_label):
        '''关联一个元数据标签到图片

        Args:
            meta_label (MetaLabel) :要和图片关联的meta label对象
        '''
        if not isinstance(meta_label, MetaLabel):
            raise ClassCastException("add mate label type error.")

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
        '''关联一个图片上的标注区域

        Args:
            image_region (ImageRegion): 要关联的区域对象，可以是ImagePolygonRegion或ImageRectangleRegion的对象。
        '''
        if not isinstance(image_region, ImageRegion):
            raise ClassCastException("add region type error.")

        self.regions.append(image_region)
