
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-10 12:52:24
@LastEditTime: 2019-12-10 13:54:30
@Description:
'''


from TLPLibrary.entity import GenericEntity

class ImageDepository(GenericEntity):

    @classmethod
    def convert_database_result_2_dict(cls, data_result):
        data_dict = dict()

        date_dict['id']                     = data_result['id'].decode("utf-8")
        date_dict['path']                   = data_result['path'].decode("utf-8")
        date_dict['name']                   = data_result['name'].decode("utf-8")
        date_dict['type']                   = data_result['type'].decode("utf-8")
        date_dict['thumbnail']              = data_result['thumbnail'] if data_result["index"] is not None else 0
        date_dict['tile']                   = data_result['tile'].decode("utf-8") if data_result["tile"] else ""
        date_dict['size']                   = data_result['size'] if data_result["size"] is not None else 0.0
        date_dict['width']                  = data_result['width'] if data_result["width"] is not None else 0
        date_dict['height']                 = data_result['height'] if data_result["height"] is not None else 0
        date_dict['minZoom']                = data_result['minZoom'] if data_result["minZoom"] is not None else 0
        date_dict['maxZoom']                = data_result['maxZoom'] if data_result["maxZoom"] is not None else 0
        date_dict['hashCode']               = data_result['hashCode'] if data_result["hashCode"] is not None else 0
        date_dict['referenceCounting']      = data_result['referenceCounting'] if data_result["referenceCounting"] is not None else 0

        return data_dict