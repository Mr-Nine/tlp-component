# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-25 15:34:29
@LastEditTime: 2019-11-25 21:01:17
@Description:
'''
from TLPLibrary.error import TLPError

class DataCastException(TLPError):
    """TLP 数据转换错误，用于抛出从数据库查询出来的数据转换位Entity时使用
    """