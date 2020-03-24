# -- coding: utf-8 --
import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.error import *
from TLPLibrary.entity import ValueType, LabelType

class Label(GenericEntity):
    '''图像meta标签和一个区域的标签对象的基类
    '''

    def __init__(self, name, background_color=None):
        '''构造一个新的标签对象

        Args:
            name (str): 标签的名称，在项目的标签模板中唯一.
            background_color (str): 标签的背景色，如果不给系统将随机分配一个颜色
        '''
        super(Label, self).__init__()
        self.name = name
        self.id = None
        self.background_color = background_color
        self.attributes = {}
        self.__confidence = None


    def addAttribute(self, key, value_type, value):
        ''' 添加一个标签的属性到标签

        一个标签不应该包含多个重复key的值，所以重复添加key将会覆盖之前的以经添加的属性。

        Args:
            key (str): 标签属性的key，会对应模板属性中的key.
            value_type (ValyeType): 标签属性值的类型.
            value : 标签属性具体的值.
        '''
        if not ValueType.check_type(value_type):
            value_type = ValueType.TEXT
        self.attributes[key] = {"type":value_type, "value":value}


    def removeAttribute(self, key):
        '''删除一个以经存在的标签属性

        如果key不存在则不会发生任何变化

        Args:
            key (str): 标签属性的key值
        '''
        del self.attributes[key]


    def hasAttribute(self):
        '''
        判断当前Label中是否包含属性
        Returns:
        '''
        return True if self.attributes else False


    def generateAttributeData(self):
        '''获取当前标签的属性数据.

        Returns:
            返回当前标签key和value的属性字典，不包含属性的value_type.
        '''
        attribute_data = {}
        for key in self.attributes:
            attribute_data[key] = self.attributes[key]["value"]

        return attribute_data


    def generateAttributeJson(self):
        '''
        获取当前标签的属性数据的JSON格式结果.

        Returns:
            返回当前标签key和value的属性字典JSON字符串.
        '''
        print("!")
        print(self.generateAttributeData())
        return json.dumps(self.generateAttributeData())


    def generateLabelTemplateData(self):
        '''获取当前标签的属性处理成数据模板需要的格式.

        Returns:
            返回结构为list包含多个字典，每个字典代表一个模板的信息，包括key\\name\\type\\default的信息.
        '''
        template_data = []
        for key in self.attributes:
            template = {}
            template['key'] = key
            template['name'] = key
            template['type'] = self.attributes[key]["type"]
            template['default'] = ''
            template_data.append(template)

        return template_data


    def generateLabelTemplateJson(self):
        '''获取当前标签的属性处理成数据模板的JSON结构.

        Args:
            None
        Returns:
            返回JSON结构的数据
        '''
        return json.dumps(self.generateLabelTemplateData())


    def setLabelConfidence(self, confidence):
        '''设置标签的置信度

        Args:
            param (float): confidence 标签的置信度是多少
        '''
        if not isinstance(confidence, float):
            raise DataCastException("confidence cast error.")

        self.__confidence = confidence


    def getLabelConfidence(self):
        '''获取当前标签的置信度
        Args:
            None
        Returns (float):
            如果没有设置标签的置信度，则返回None
        '''
        return self.__confidence


class MetaLabel(Label):
    '''图像meta标签的描述类
    '''
    def __init__(self, name):
        super(MetaLabel, self).__init__(name)
        self.type = LabelType.META


class RegionLabel(Label):
    '''图像区域标签的描述类
    '''
    def __init__(self, name):
        super(RegionLabel, self).__init__(name)
        self.region_id = None
        self.type = LabelType.REGION
