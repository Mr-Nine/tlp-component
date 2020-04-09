# -- coding: utf-8 --
'''
@Project:TLP-Agent
@Team:DCP
@Author: jerome.du
LastEditors: jerome.du
@Date: 2019-10-31 09:56:39
LastEditTime: 2020-04-09 21:04:59
@Description:程序启动入口,负责启动tornado服务，实例化模块管理器
'''
__author__ = 'dcp team dujiujun - tlp - agent'

import sys
import os.path

sys.path.append(os.path.dirname(__file__) + os.sep + '../')

import atfork
atfork.monkeypatch_os_fork_functions()

def fix_logging_module():
    logging = sys.modules.get('logging')
    # Prevent fixing multiple times as that would cause a deadlock.
    if logging and getattr(logging, 'fixed_for_atfork', None):
        return
    if logging:
        warnings.warn('logging module already imported before fixup.')
    import logging
    if logging.getLogger().handlers:
        # We could register each lock with atfork for these handlers but if
        # these exist, other loggers or not yet added handlers could as well.
        # Its safer to insist that this fix is applied before logging has been
        # configured.
        raise BaseException('logging handlers already registered.')

    logging._acquireLock()
    try:
        def fork_safe_createLock(self):
            self._orig_createLock()
            atfork.atfork(self.lock.acquire,
                          self.lock.release, self.lock.release)

        # Fix the logging.Handler lock (a major source of deadlocks).
        logging.Handler._orig_createLock = logging.Handler.createLock
        logging.Handler.createLock = fork_safe_createLock

        # Fix the module level lock.
        atfork.atfork(logging._acquireLock,
                      logging._releaseLock, logging._releaseLock)

        logging.fixed_for_atfork = True
    finally:
        logging._releaseLock()

fix_logging_module()

import time
import logging
import logging.config
import json
import signal
import warnings

import tornado.httpserver
import tornado.ioloop
import tornado.log
import tornado.options
import tornado.web

from datetime import datetime
from tornado.options import define, options, parse_config_file

from core import PreprocessingContext
from handler import MainHandler, PreprocessingHandler


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
            (r"/preprocessing", PreprocessingHandler) # , init_parameter
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

    # welcome info
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
