# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-25 15:34:29
@LastEditTime: 2019-11-25 21:05:10
@Description:
'''
from tlp.error import TLPError

class DataBaseException(TLPError):
    """TLP数据库异常，用于封装数据库错误位可读信息
    """