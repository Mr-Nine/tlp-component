
'''
@Project:
@Team:
@Author: jerome.du
LastEditors: jerome.du
@Date: 2019-11-22 21:06:12
LastEditTime: 2020-04-01 10:02:06
@Description:
'''

from tlp.entity import GenericEntity

class AnnotationProjectImageMetaLabel(GenericEntity):

    @classmethod
    def convert_database_result_2_dict(cls, data_result):
        data_dict = dict()

        data_dict['id']         = data_result['id'].decode("utf-8")
        data_dict['imageId']    = data_result['imageId'].decode("utf-8")
        data_dict['labelId']    = data_result['labelId'].decode("utf-8")
        data_dict['type']       = data_result['type'].decode("utf-8")
        data_dict['version']    = data_result['version']
        data_dict['attribute']  = data_result['attribute'].decode("utf-8") if data_result["attribute"] else ""
        data_dict['userId']     = data_result['userId'].decode("utf-8")
        data_dict['createTime'] = data_result["createTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["createTime"] is not None else ""
        data_dict['updateTime'] = data_result["updateTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["updateTime"] is not None else ""
        data_dict['inferencerId']  = data_result['inferencerId'].decode("utf-8") if data_result["inferencerId"] else None

        return data_dict
