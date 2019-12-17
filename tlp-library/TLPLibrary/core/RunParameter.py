# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-11 20:54:31
@LastEditTime: 2019-12-13 17:48:39
@Description:
'''

import argparse

class RunParameter(object):

    @staticmethod
    def get_run_parameter(): # , choices=('import', 'inferencer')
        parse = argparse.ArgumentParser(description="run customer script")
        parse.add_argument("-pid", "--projectId", help="当前脚本要处理的数据所属的项目ID", type=str, metavar="", required=True)
        parse.add_argument("-p", "--path", help="图片全路径(自动推理)或要处理的图片所在的根目录(导入原有标注信息)", type=str, metavar="", required=True)
        parse.add_argument("-t", "--type", help="脚本类型, 可选参数为'import'或'inferencer'，默认为'import'。", type=str, metavar="", choices=('import', 'inferencer'), required=True)
        parse.add_argument("-uid", "--userId", help="当前用户启动脚本的用户Id", type=str, metavar="", required=True)
        parse.add_argument("-iid", "--inferencerId", help="推理程序的系统ID", type=str, metavar="")

        args = parse.parse_args()

        runParameter = RunParameter()

        runParameter.projectId = args.projectId
        runParameter.path = args.path
        runParameter.type = args.type
        runParameter.userId = args.userId
        runParameter.inferencerId = args.inferencerId

        return runParameter

