# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-11 20:54:31
@LastEditTime: 2020-03-18 14:46:32
@Description:
'''

import argparse

class RunParameter(object):

    @staticmethod
    def get_run_parameter(): # , choices=('import', 'inference')
        parse = argparse.ArgumentParser(description="run customer script")
        parse.add_argument("-pid", "--projectId", help="当前脚本要处理的数据所属的项目ID", type=str, metavar="", required=True)
        parse.add_argument("-p", "--path", help="图片全路径(自动推理)或要处理的图片所在的根目录(导入原有标注信息)", type=str, metavar="", required=True)
        parse.add_argument("-t", "--type", help="脚本类型, 可选参数为'import'或'inference'，默认为'import'。", type=str, metavar="", choices=('import', 'inference'), required=True)
        parse.add_argument("-uid", "--userId", help="当前用户启动脚本的用户Id", type=str, metavar="", required=True)
        parse.add_argument("-iid", "--inferenceId", help="推理程序的系统ID", type=str, metavar="")

        args = parse.parse_args()

        run_parameter = RunParameter()

        run_parameter.project_id = args.projectId
        run_parameter.path = args.path
        run_parameter.type = args.type
        run_parameter.user_id = args.userId
        run_parameter.inference_id = args.inferenceId

        return run_parameter

