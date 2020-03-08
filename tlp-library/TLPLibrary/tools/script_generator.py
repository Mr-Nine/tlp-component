
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors  : jerome.du
@Date: 2019-12-11 14:17:40
@LastEditTime : 2020-01-17 14:48:01
@Description:
'''

import os
import tempfile
import argparse

def get_run_parameter():
    description= """
    欢迎使用TLP脚本生成器.\n
    """
    parse = argparse.ArgumentParser(description=description)
    parse.add_argument("-t", "--type", help="脚本类型, 可选参数为'import'或'inferencer'，默认为'import'。", type=str, metavar="", choices=('import', 'inferencer'))
    parse.add_argument("-o", "--output", help="生成脚本输出的路径，默认存储在系统的临时文件夹下，当输入路径时，请使用正确的路径分隔符'\\\\'(windows)或'/'(unix)。", type=str, metavar="")
    parse.add_argument("-n", "--name", help="生成脚本的名字，脚本类型默认生成为'import_region_and_label.py'或'inferencer_region_and_label.py'。", type=str, metavar="")

    args = parse.parse_args()

    type = args.type if args.type else 'import'
    output = args.output if args.output else tempfile.gettempdir()
    name = args.name if args.name else 'import_region_and_label.py' if not args.type or args.type == 'import' else 'inferencer_region_and_label.py'

    return (type, output, name)

def copy_template_file(source, target):
    with open(source, mode='r', encoding="utf-8") as template_file:
        templates = template_file.readlines()

    with open(target, mode='w', encoding="utf-8") as target_file:
        target_file.writelines(templates)

def main():
    print("""welcome use tlp script generator. entry '-h' show this help message.""")

    (type, output, name) = get_run_parameter()

    print("""generator template script...""")

    target = os.path.join(output, name)

    if type == 'import':
        copy_template_file(os.path.join(os.path.dirname(__file__), 'import_script_template'), target)
    elif type == 'inferencer':
        copy_template_file(os.path.join(os.path.dirname(__file__), 'inferencer_script_template'), target)
    else:
        pass

    print("""generator success, save path %s"""% target)

if __name__ == "__main__":
    main()