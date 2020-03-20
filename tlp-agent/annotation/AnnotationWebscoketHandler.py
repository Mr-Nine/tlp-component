# -- coding: utf-8 --
'''
@Project:TLP
@Team:DCP-Team
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-10-31 11:57:58
@LastEditTime: 2020-03-20 12:11:16
@Description:负责标注页面的websocket连接的handler,在收到连接请求后，会先进行连接验证,如果验证通过，
    则创建连接并把连接管理交给模块控制器, 如果验证不通过，则会拒绝创建连接请求。
    在收到任何的消息后，都不会进行处理，而是直接发送给模块控制器。
'''

import re
import sys
import time
import json
import logging
import traceback
import math

import tornado.web
import tornado.gen
import tornado.websocket

from core.utils import *
from core import *
from tlp.entity import User, AnnotationProject, AnnotationProjectLabelTemplate

from annotation import Publisher

class AnnotationWebscoketHandler(tornado.websocket.WebSocketHandler):

    __context = TLPContext()
    # __heart_checker = None

    def _id(self):
        '''
        @description:获取连接对象的唯一标识
        @return:当前连接的唯一标识
        '''
        return id(self)


    # 连接权限检查
    def __check_connection_user(self, mysql, *args, **kwargs):
        '''
        @description:检查连接的用户是否符合连接要求
        @param {MysqlManager} mysql:mysql连接器
        @return:tuple
        '''
        logging.info("New websocket connection, check connecting authenticator.")

        # self.context = self.request.connection.context

        token = None
        if ((kwargs is not None) and ('token' in kwargs)):
            token = kwargs['token']
        elif self.get_argument('token', False):
            token =  self.get_argument('token')

        if (token is None):
            logging.error('Websocket connection close, not get token.')
            return False, 10201, 'websocket connection close, not get token.'

        logging.debug('Get connection token: %s' % token)

        selectResult = mysql.selectOne("select * from AnnotationProjectUser where token = %s", (token,))

        if selectResult[0] == 0 or not selectResult[1]:
            return False, 10202, 'websocket connection close, user not find.'

        user = User(
            userId=selectResult[1]["userId"].decode("utf-8"),
            projectId=selectResult[1]["projectId"].decode("utf-8"),
            token=selectResult[1]["token"].decode("utf-8"),
            admin=(True if selectResult[1]["admin"] else False),
            review=(True if selectResult[1]["review"] else False),
            label=(True if selectResult[1]["label"] else False)
        )

        for key in self.__context.get_connect_dict():
            connectInfo = self.__context.get_connect(key)
            if connectInfo is not None and connectInfo["user_id"] == user.userId:
                return False, 10203, 'websocket connection close, connection max.'

        return (True, user)


    def _send_ws_message_and_close_connection(self, log, error_code, reason):
        '''
        @description:发送ws层的消息
        @param {string} log:错误日志
        @param {int} error_code:错误码
        @param {string} reason:错误消息
        '''
        logging.error(log)
        self.write_message(self._create_ws_base_message("error", {'message':error_code, 'reason':reason}))
        super(AnnotationWebscoketHandler, self).close()


    def _load_and_check_project(self, mysql, project_id):
        '''
        @description:加载并检查项目是否存在
        @param {MysqlManager} mysql:mysql管理对象
        @param {string} project_id:要load的项目ID
        @return:
        '''
        project = self.__context.get_project(project_id)

        if project is None:
            selectResult = mysql.selectOne("""select * from AnnotationProject where id = %s""", (project_id, ))
            if selectResult[0]:
                project = AnnotationProject.create_by_database_result(selectResult[1])
                self.__context.set_project(project)
                return project
            else:
                return None

        return project

    def _load_default_label_attribute(self, mysql):
        '''
        '''
        default_atrribute = self.__context.get_default_attribute()
        if default_atrribute is None:
            default_attribute = mysql.selectOne("""select `value` from Config where `targetId` = -1 and `key` = 'ANNOTATION_LABEL_TEMPLATE_DEFAULT_ATTRIBUTE'""")
            if default_attribute[0]:
                default_attribute_json = json.loads(default_attribute[1]['value'].decode("utf-8"))
                self.__context.set_default_attribute(default_attribute_json)

    def open(self, *args, **kwargs):
        '''
        @description:
        @param {type}
        @return:
        '''
        """ws打开连接时执行的动作，加入一个新的客户端到管理字典
        """

        mysql = MysqlManager()

        try:
            checkResult = self.__check_connection_user(mysql, args, kwargs)
            if not checkResult[0]:
                self._send_ws_message_and_close_connection("Web socket not init, connection user check fail.", checkResult[1], checkResult[2])
                return

            self._load_default_label_attribute(mysql)

            connectionId = self._id()
            user = checkResult[1]

            connectionInfo = {}
            connectionInfo["user_id"] = user.userId
            connectionInfo["user"] = user
            connectionInfo["project_id"] = user.projectId
            connectionInfo["connect"] = self

            if self._load_and_check_project(mysql, user.projectId) is None:
                self._send_ws_message_and_close_connection("Web socket not init, connection project is not find.", 201110, '???')
                return


            project = self.__context.get_project(user.projectId)

            publisher = Publisher(self, user)
            connectionInfo["publisher"] = publisher

            self.__context.set_connect(self._id(), connectionInfo)

            # TODO:后端主动心跳机制
            # if ('hc' not in dir()):
            #     self.hc = HeartCheck(self.__connects)
            #     self.hc.start()

            opened_result = {}
            opened_result["state"] = True
            opened_result["message"] = 'user connection tlp agent success.'
            opened_result["projectId"] = user.projectId
            opened_result["projectId"] = user.projectId
            opened_result["projectName"] = project.name
            opened_result["projectLock"] = project.locked

            select_inference_sql = """select * from AnnotationProjectInferencer where projectId = %s"""
            select_inference_result = mysql.selectAll(select_inference_sql, (user.projectId, ))
            project_inference_list = []

            if select_inference_result[0]:
                for inference_result in select_inference_result[1]:
                    project_inference_list.append(mysql_dict_2_dict(inference_result))

            opened_result["inferencerInfo"] = project_inference_list

            sql_start = """select * from `AnnotationProjectLabelTemplate` where projectId = %s order by name asc"""
            sql_end = """ limit %s, %s"""

            meta_label_list = []
            region_label_list = []

            lable_result = mysql.selectAll(sql_start,(project.id, ))

            if lable_result[0]:
                for result in lable_result[1]:
                    if result["type"].decode("utf-8") == 'META':
                        meta_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))
                    else:
                        region_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))

            opened_result["metaLabels"] = meta_label_list
            opened_result["regionLabels"] = region_label_list
            self.write_message(self._create_ws_base_message("opened", opened_result))

            '''
            # 废弃掉的分页逻辑

            count_sql = """select count(1) as total from `AnnotationProjectLabelTemplate` where projectId = %s"""
            total_lable_number = mysql.selectOne(count_sql, (project.id, ))[1]['total']

            # 数据量较小，部分也直接发送全部到前端
            if total_lable_number > 0 and total_lable_number < 500:
                pass
            elif total_lable_number > 500:
                # 数据量不可控，分页查询多此返回
                total_page = math.ceil(total_lable_number / 500)

                for i in range(total_page):
                    meta_label_list = []
                    region_label_list = []
                    offset = i * 500

                    lable_result = mysql.selectAll((sql_start + sql_end),(project.id, offset, 500))

                    for result in lable_result[1]:
                        if result["type"].decode("utf-8") == 'META':
                            meta_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))
                        else:
                            region_label_list.append(AnnotationProjectLabelTemplate.convert_database_result_2_dict(result))

                    opened_result["projectLabel"]["metaLabel"] = meta_label_list
                    opened_result["projectLabel"]["regionLabel"] = region_label_list
                    opened_result["labelMessageCount"] = total_page

                    self.write_message(self._create_ws_base_message("opened", opened_result))
            else:
                opened_result["projectLabel"]["metaLabel"] = []
                opened_result["projectLabel"]["regionLabel"] = []
                opened_result["labelMessageCount"] = 0
                self.write_message(self._create_ws_base_message("opened", opened_result))
            '''
        except BaseException as e:
            if self._id() in self.__context.get_connect_dict():
                connection_info = self.__context.get_connect(self._id())
                if 'publisher' in connection_info:
                    connection_info["publisher"].destroy()
                del self.__context.get_connect_dict()[self._id()]
            logging.error(e)
            traceback.print_exc(file=sys.stdout)
        finally:
            mysql.destory()


    # @tornado.gen.coroutine
    def on_message(self, msg):
        """websocket接收到客户端发送的消息时的处理函数
        """
        # logging.debug(u"Receive message: %s" % msg)
        try:
            message = Message()
            message.fromJson(msg)

            if message.senderMid == "heartbeat":
                # 忽略心跳
                return

        except BaseException:
            logging.error(u"Error message: %s, message is discarded" % msg)
            self.write_message(self._create_ws_base_message("error", {'message':10301, 'reason':"error message"}))
            return

        # logging.debug("Dispatcher_model:%s" % self._id())
        publisher = self.__context.get_publisher(self._id())
        if publisher is not None:
            response_message = publisher.dispatcher_message(message)
            if response_message is not None:
                self.write_message(response_message)
            # else:
            #     self.write_message(self._create_ws_base_message("error", {'message':10303, 'reason':"error message"}))
        else:
            logging.error(message.to_json())
            self.write_message(self._create_ws_base_message("error", {'message':10304, 'reason':"error message"}))


    def on_ping(self, data):
        """心跳包响应, data是`.ping`发出的数据
        """
        logging.info('Into on_ping the data is |%s|' % data)


    def on_pong(self, data):
        """ 心跳包响应, data是`.ping`发出的数据
        """
        logging.info('Into on_pong the data is |%s|' % data)


    def on_close(self, transfer=True):
        connection_info = self.__context.get_connect(self._id())
        if connection_info is not None:
            connection_info["publisher"].destroy()
            del self.__context.get_connect_dict()[self._id()]
            logging.debug("client close the connection id:%s, current connection count:%s" % (self._id(), str(len(self.__context.get_connect_dict().keys()))))


    def check_origin(self, origin):
        """同源检查，当前默认返回TRUE，后面可能会有变化
        """
        logging.debug(u"New websocket connection, check origin.")
        return True


    def _create_ws_base_message(self, messageType, data):
        return Message("ws", messageType, "ws", 0, data).to_json()
