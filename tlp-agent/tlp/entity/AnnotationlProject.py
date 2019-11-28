# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-20 13:54:20
@LastEditTime: 2019-11-26 10:25:31
@Description:
'''

from tlp.entity import GenericEntity

class AnnotationlProject(GenericEntity):

    @classmethod
    def convert_database_result_2_dict(cls, data_result):
        data_dict = dict()

        data_dict['id']                     = data_result["id"].decode("utf-8") if data_result["id"] else ""
        data_dict['index']                  = data_result["index"] if data_result["index"] is not None else 0
        data_dict['name']                   = data_result["name"].decode("utf-8") if data_result["name"] else ""
        data_dict['resume']                 = data_result["resume"].decode("utf-8") if data_result["resume"] else ""
        data_dict['cover']                  = data_result["cover"].decode("utf-8") if data_result["cover"] else ""
        data_dict['coverBackground']        = data_result["coverBackground"].decode("utf-8") if data_result["coverBackground"] else ""
        data_dict['bannerBackground']       = data_result["bannerBackground"].decode("utf-8") if data_result["bannerBackground"] else ""
        data_dict['description']            = data_result["description"].decode("utf-8") if data_result["description"] else ""
        data_dict['firstCategoryId']        = data_result["firstCategoryId"].decode("utf-8") if data_result["firstCategoryId"] else ""
        data_dict['secondCategoryId']       = data_result["secondCategoryId"].decode("utf-8") if data_result["secondCategoryId"] else ""
        data_dict['locked']                 = (True if data_result["locked"] else False) if data_result["locked"] is not None else 0
        data_dict['creatorId']              = data_result["creatorId"].decode("utf-8") if data_result["creatorId"] else ""
        data_dict['createTime']             = data_result["createTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["createTime"] is not None else ""
        data_dict['updateTime']             = data_result["updateTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["updateTime"] is not None else ""

        return data_dict
