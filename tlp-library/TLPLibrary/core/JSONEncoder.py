# -- coding: utf-8 --

import json

from TLPLibrary.core import GenericEntity

class JSONEncoder(json.JSONEncoder):
    '''JSON编码对象时的转化对象，用来兼容GenericEntity对象
    '''
    def default(self, obj):
        if isinstance(obj, GenericEntity):
            return obj.to_dict()
        else:
            return json.JSONEncoder.default(self, obj)