# -- coding: utf-8 --
'''
@Project:TLP-Agent
@Team:DCP
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-10-31 09:56:39
@LastEditTime: 2019-11-29 14:53:07
@Description:程序启动入口,负责启动tornado服务，实例化模块管理器
'''
__author__ = 'dcp team dujiujun - tlp - agent'

import sys
import time
import logging
import logging.config
import os.path
import json
import signal

import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.options
import tornado.web

from datetime import datetime
from tornado.options import define, options, parse_config_file

from core import PreprocessingContext
from handler import MainHandler, PreprocessingHandler


sys.path.append(os.path.dirname(__file__) + os.sep + '../')

define('port', default=7979)

settings = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static-file"),
    static_url_prefix="/public/"
)

def welcome():
    logging.info(u"welcome tlp agent :)")


def init_agent_logging():
    """Init python env `logging` setting.
    """
    filepath = os.path.join(os.path.dirname(__file__), './config/logging.conf')
    logging.config.fileConfig(filepath)
    logger = logging.getLogger()
    tornado.log.enable_pretty_logging(logger=logger)

max_body_size = 1 * 1024 * 1024 * 1024


def get_server_settings(options=None):
    service_settings = dict(
        xheaders= True, # options.xheaders,
        max_body_size = max_body_size,
        # trusted_downstream=get_trusted_downstream(options.tdstream)
    )
    return service_settings


class Application(tornado.web.Application):
    """Configure the service started by agent.
    """

    def __init__(self, loop):

        init_parameter = {"loop":loop}

        handlers = [
            (r"/", MainHandler),
            (r"/index.html", MainHandler),
            (r"/index", MainHandler),
            (r"/preprocessing", PreprocessingHandler, init_parameter)
            # (r"/annotation", AnnotationWebscoketHandler, init_parameter)
        ]

        tornado.web.Application.__init__(self, handlers, **settings)

def sig_exit(signum, frame):
    tornado.ioloop.IOLoop.instance().add_callback_from_signal(do_stop)

def do_stop(signum, frame):
    tornado.ioloop.IOLoop.instance().stop()

def main():

    # set tornado confing
    options.parse_config_file("./config/webserver.conf")

    # start tornado listen
    web_loop = tornado.ioloop.IOLoop.instance()

    # create handler
    app = Application(loop=web_loop)

    # get server custom settings
    server_settings = get_server_settings()
    app.listen(options.port, '0.0.0.0', **server_settings)
    # http_server = tornado.httpserver.HTTPServer(app)
    # http_server.listen(options.port)

    # print welcome info
    welcome()

    context = PreprocessingContext()

    try:
        # start tornado ioloop
        logging.info("tornado ioloop start")
        signal.signal(signal.SIGINT, sig_exit)
        web_loop.start()
    except BaseException as e:
        logging.error(e)
    finally:
        web_loop.stop()       # might be redundant, the loop has already stopped
        web_loop.close(True)  # needed to close all open sockets

if __name__ == "__main__":
    main()
