# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
LastEditors: jerome.du
@Date: 2019-11-25 11:21:03
LastEditTime: 2020-04-01 10:20:01
@Description:
'''

import json

from tlp.entity import GenericEntity

class AnnotationProjectImageRegion(GenericEntity):

    @classmethod
    def convert_database_result_2_dict(cls, data_result):
        data_dict = dict()

        data_dict['id']         = data_result['id'].decode("utf-8") if data_result["id"] else ""
        data_dict['imageId']    = data_result['imageId'].decode("utf-8") if data_result["imageId"] else ""
        data_dict['type']       = data_result['type'].decode("utf-8") if data_result['type'] else ""
        data_dict['index']      = data_result['index']
        data_dict['shape']      = data_result['shape'].decode("utf-8") if data_result["shape"] else ""
        data_dict['shapeData']  = data_result['shapeData'].decode("utf-8") if data_result["shapeData"] else ""
        data_dict['userId']     = data_result['userId'].decode("utf-8") if data_result["userId"] else ""
        data_dict['createTime'] = data_result["createTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["createTime"] else ""
        data_dict['updateTime'] = data_result["updateTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["updateTime"] else ""
        data_dict['version']  = data_result['version'] if data_result["version"] else None
        data_dict['inferencerId']  = data_result['inferencerId'].decode("utf-8") if data_result["inferencerId"] else None

        return data_dict