# -- coding: utf-8 --

'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-21 21:07:14
@LastEditTime: 2019-12-17 15:07:12
@Description:
'''

from tlp.entity import GenericEntity

class AnnotationlProjectLabelTemplate(GenericEntity):

    @classmethod
    def convert_database_result_2_dict(cls, data_dict):
        data_dict2 = dict()

        data_dict2["id"]                 = data_dict["id"].decode("utf-8")
        data_dict2["projectId"]          = data_dict["projectId"].decode("utf-8")
        data_dict2["name"]               = data_dict["name"].decode("utf-8")
        data_dict2["labelGroupId"]       = data_dict["labelGroupId"].decode("utf-8") if data_dict["labelGroupId"] is not None else ""
        data_dict2["type"]               = data_dict["type"].decode("utf-8")
        data_dict2["source"]             = data_dict["source"].decode("utf-8")
        data_dict2["heat"]               = data_dict["heat"]
        data_dict2["inferencerId"]       = data_dict["inferencerId"].decode("utf-8") if data_dict["inferencerId"] is not None else ""
        data_dict2["icon"]               = data_dict["icon"].decode("utf-8") if data_dict["icon"] is not None else ""
        data_dict2["backgroundColor"]    = data_dict["backgroundColor"].decode("utf-8") if data_dict["backgroundColor"] is not None else ""
        data_dict2["shortcutKey"]        = data_dict["shortcutKey"].decode("utf-8") if data_dict["shortcutKey"] is not None else ""
        data_dict2["enabled"]            = True if data_dict["enabled"] else False
        data_dict2["required"]           = True if data_dict["required"] else False
        data_dict2["defaulted"]          = True if data_dict["defaulted"] else False
        data_dict2["reviewed"]           = True if data_dict["reviewed"] else False
        data_dict2["attribute"]          = data_dict["attribute"].decode("utf-8") if data_dict["attribute"] is not None else ""
        data_dict2["creatorId"]          = data_dict["creatorId"].decode("utf-8") if data_dict["creatorId"] is not None else ""
        data_dict2["createTime"]         = data_dict["createTime"].strftime("%Y-%m-%d %H:%M:%S") if data_dict["createTime"] is not None else ""
        data_dict2["updateTime"]         = data_dict["updateTime"].strftime("%Y-%m-%d %H:%M:%S") if data_dict["updateTime"] is not None else ""

        return data_dict2
