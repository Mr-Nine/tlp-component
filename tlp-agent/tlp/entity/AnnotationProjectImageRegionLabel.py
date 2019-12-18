# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-25 11:21:03
@LastEditTime: 2019-12-18 17:12:36
@Description:
'''

import json

from tlp.entity import GenericEntity

class AnnotationProjectImageRegionLabel(GenericEntity):

    @classmethod
    def convert_database_result_2_dict(cls, data_result):
        data_dict = dict()

        data_dict['id']         = data_result['id'].decode("utf-8") if data_result["id"] else ""
        data_dict['imageId']   = data_result['imageId'].decode("utf-8") if data_result["imageId"] else ""
        data_dict['regionId']   = data_result['regionId'].decode("utf-8") if data_result["regionId"] else ""
        data_dict['labelId']    = data_result['labelId'].decode("utf-8") if data_result["labelId"] else ""
        data_dict['type']       = data_result['type'].decode("utf-8") if data_result["type"] else ""
        data_dict['version']    = data_result['version'].decode("utf-8") if data_result["version"] else ""
        data_dict['attribute']  = data_result['attribute'].decode("utf-8") if data_result["attribute"] else ""
        data_dict['userId']     = data_result['userId'].decode("utf-8") if data_result["userId"] else ""
        data_dict['createTime'] = data_result["createTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["createTime"] else ""
        data_dict['updateTime'] = data_result["updateTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["updateTime"] else ""

        return data_dict