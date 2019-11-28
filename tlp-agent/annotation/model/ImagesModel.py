# -- coding: utf-8 --
__author__ = 'dcp team dujiujun - dcp - agent'

'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 11:30:29
@LastEditTime: 2019-11-15 17:19:46
@Description:
'''

import logging

from annotation.model import AbstractModel
from core import MessageMid

class ImagesModel(AbstractModel):
    """
    """

    def __init__(self, websocket, authenticator):
        super(ImagesModel, self).__init__(MessageMid.IMAGES(), "images heandler", "annotation.model.handler.images", websocket, authenticator)
