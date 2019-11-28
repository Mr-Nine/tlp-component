# -- coding: utf-8 --
'''
@Project:dcp-tlp
@Team:DCP team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-13 14:34:13
@LastEditTime: 2019-11-20 14:19:28
@Description:TLP模块中使用的用户实体
'''

class User(object):

    def __init__(self, userId='', username='', projectId='', token='', chineseName='', linuxUid='', admin=False, review=False, label=False):
        self._userId = userId
        self._username = username
        self._projectId = projectId
        self._token = token
        self._chineseName = chineseName
        self._linuxUid = linuxUid
        self._admin = admin
        self._review = review
        self._label = label

    @property
    def userId(self):
        return self._userId

    @property
    def username(self):
        return self._username

    @property
    def projectId(self):
        return self._projectId

    @property
    def token(self):
        return self._token

    @property
    def chineseName(self):
        return self._chineseName

    @property
    def linuxUid(self):
        return self._linuxUid

    @property
    def admin(self):
        return self._admin

    @property
    def review(self):
        return self._review

    @property
    def label(self):
        return self._label


