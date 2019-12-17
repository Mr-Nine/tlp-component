
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-12 18:45:05
@LastEditTime: 2019-12-12 19:04:28
@Description:
'''

import json

from TLPLibrary.core import GenericEntity

class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, GenericEntity):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)