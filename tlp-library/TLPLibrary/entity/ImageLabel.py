# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 13:52:40
@LastEditTime: 2019-12-18 18:14:10
@Description:
'''

import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import ValueType, LabelType

class Label(GenericEntity):

    def __init__(self, name, backgroundColor=None):
        super(Label, self).__init__()
        self.name = name
        self.id = None
        self.backgroundColor = backgroundColor
        self.attributes = {}


    def addAttribute(self, key, valueType, value):
        if not ValueType.check_type(valueType):
            valueType = ValueType.TEXT
        self.attributes[key] = {"type":valueType, "value":value}


    def removeAttribute(self, key):
        del self.attributes[key]


    def hasAttribute(self):
        return True if self.attributes else False


    def generateAttributeData(self):
        attribute_data = []
        for key in self.attributes:
            attributeMap = {key:self.attributes[key]["value"]}
            attribute_data.append(attributeMap)

        return attribute_data


    def generateAttributeJson(self):
        return json.dumps(self.generateAttributeData())


    def generateLabelTemplateData(self):
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
        return json.dumps(self.generateLabelTemplateData())


class MateLabel(Label):

    def __init__(self, name):
        super(MateLabel, self).__init__(name)
        self.type = LabelType.MATE


class RegionLabel(Label):

    def __init__(self, name):
        super(RegionLabel, self).__init__(name)
        self.regionId = None
        self.type = LabelType.REGION
