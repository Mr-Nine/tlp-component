# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-04 11:30:46
@LastEditTime: 2019-11-15 17:19:53
@Description:
'''
__author__ = 'dcp team dujiujun - dcp - agent'

import logging

from core import MessageMid
from annotation.model import AbstractModel

class AnnotationModel(AbstractModel):
    """
    """

    def __init__(self, websocket, authenticator):
        super(AnnotationModel, self).__init__(MessageMid.ANNOTATION(), "Annotation Model", "annotation.model.handler.annotation", websocket, authenticator)