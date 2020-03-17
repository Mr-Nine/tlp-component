# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 13:52:40
@LastEditTime: 2020-03-16 14:51:46
@Description:
'''

import json

from TLPLibrary.core import GenericEntity
from TLPLibrary.entity import ValueType, LabelType

class Label(GenericEntity):

    def __init__(self, name, background_color=None):
        super(Label, self).__init__()
        self.name = name
        self.id = None
        self.background_color = background_color
        self.attributes = {}


    def addAttribute(self, key, value_type, value):
        if not ValueType.check_type(value_type):
            value_type = ValueType.TEXT
        self.attributes[key] = {"type":value_type, "value":value}


    def removeAttribute(self, key):
        del self.attributes[key]


    def hasAttribute(self):
        return True if self.attributes else False


    def generateAttributeData(self):
        attribute_data = {}
        for key in self.attributes:
            attribute_data[key] = self.attributes[key]["value"]
            # attributeMap = {key:self.attributes[key]["value"]}
            # attribute_data.append(attributeMap)

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


class MetaLabel(Label):

    def __init__(self, name):
        super(MetaLabel, self).__init__(name)
        self.type = LabelType.META


class RegionLabel(Label):

    def __init__(self, name):
        super(RegionLabel, self).__init__(name)
        self.region_id = None
        self.type = LabelType.REGION
