# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-20 16:53:11
@LastEditTime: 2019-12-10 19:26:54
@Description:
'''

from TLPLibrary.entity import GenericEntity

class ProjectImage(GenericEntity):

    @classmethod
    def convert_database_result_2_dict(cls, data_result):
        data_dict = dict()

        data_dict["id"]                 = data_result["id"].decode("utf-8")
        data_dict["projectId"]          = data_result["projectId"].decode("utf-8")
        data_dict["imageId"]            = data_result["imageId"].decode("utf-8")
        data_dict["tableName"]          = data_result["tableName"].decode("utf-8")
        data_dict["path"]               = data_result["path"].decode("utf-8")
        data_dict["name"]               = data_result["name"].decode("utf-8")
        data_dict["type"]               = data_result["type"].decode("utf-8")
        data_dict["size"]               = data_result["size"]
        data_dict["width"]              = data_result["width"]
        data_dict["height"]             = data_result["height"]
        data_dict["thumbnail"]          = True if data_result["thumbnail"] else False
        data_dict["tile"]               = True if data_result["tile"] else False
        data_dict["minZoom"]            = data_result["minZoom"]
        data_dict["maxZoom"]            = data_result["maxZoom"]
        data_dict["sourceId"]           = data_result["sourceId"].decode("utf-8")
        data_dict["state"]              = data_result["state"].decode("utf-8")
        data_dict["synchronizedTime"]   = data_result["synchronizedTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["synchronizedTime"] is not None else ""
        data_dict["autoLable"]          = True if data_result["autoLable"] else False
        data_dict["importLable"]        = True if data_result["importLable"] else False
        data_dict["annotation"]         = True if data_result["annotation"] else False
        data_dict["annotationUserId"]   = data_result["annotationUserId"].decode("utf-8") if data_result["annotationUserId"] is not None else ""
        data_dict["review"]             = True if data_result["review"] else False
        data_dict["reviewUserId"]       = data_result["reviewUserId"].decode("utf-8") if data_result["reviewUserId"] is not None else ""
        data_dict["browse"]             = True if data_result["browse"] else False
        data_dict["browseUserId"]       = data_result["browseUserId"].decode("utf-8") if data_result["browseUserId"] is not None else ""
        data_dict["completed"]          = True if data_result["completed"] else False
        data_dict["completedUserId"]    = data_result["completedUserId"].decode("utf-8") if data_result["completedUserId"] is not None else ""
        data_dict["completedTime"]      = data_result["completedTime"].strftime("%Y-%m-%d %H:%M:%S") if data_result["completedTime"] is not None else ""
        data_dict["updateVersion"]      = data_result["updateVersion"]

        return data_dict
