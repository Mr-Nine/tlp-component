# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-11-28 16:58:42
@LastEditTime: 2019-11-29 11:10:41
@Description:
'''

import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')