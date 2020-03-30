# -- coding: utf-8 --

import os

# import you library

import json
import xml.sax
import chardet
from xml.dom import minidom
from xml.dom.minidom import parse

# import TLPLibrary
from TLPLibrary.core import *
from TLPLibrary.error import *
from TLPLibrary.entity import *
from TLPLibrary.service import ImportLabelService



def input_data(run_parameter):
    '''导入数据的逻辑实现

    Args:
        run_parameter (RunParameter): RunParameter类的对象，封装了调用脚本时传入的参数

    Returns:
        boolean: 如果正确导入完成返回True,否则返回False
    '''
    image_path = run_parameter.path
    with open("D:\\ProgramFiles\\User\\Desktop\\标注导出.txt", mode="r", encoding="utf-8") as json_file:
        json_data = json.load(json_file)
    import_image_label_data(run_parameter, json_data, image_path)


    # if os.path.isdir(image_path):
    #     # 批量导入操作，获取的是一个存放图片的目录
    #     import_images_label_data(run_parameter, image_path)
    # elif os.path.isfile(image_path):
    #     # 运行参数传递的单张图片的路径，导入程序针对这一张图片进行处理
    #     import_image_label_data(run_parameter, image_path)


def import_image_label_data(run_parameter, json_data, image_path):
    (image_path_dir, image_file_name) = os.path.split(image_path)
    (file_name, exte_name) = os.path.splitext(image_file_name)

    # find image by json
    image_data = None
    for image_json in json_data:
        if 'path' in image_json and image_json['path'] == image_path:
            image_data = image_json
            break

    if image_data is None:
        print("not find image data in json file.")
        return

    # create image object
    image = Image(image_json['path'])

    regions_data = image_json['regions']
    if not regions_data:
        print("image not found region data.")

    for region_data in regions_data:
        shape = region_data['shape']
        region = None
        if shape == 'RECTANGLE':
            region = ImageRectangleRegion(json.loads(region_data['shapeData']), bounding_box=None)
        else:
            region = ImagePolygonRegion(json.loads(region_data['shapeData']), bounding_box=None)

        if not region:
            print("region data error.")
            continue

        regionLabels = region_data["regionLabels"]
        for region_label in regionLabels:
            label = RegionLabel(name=region_label["name"])
            attributes = region_label['attribute']
            for key,value in attributes.items():
                label.addAttribute(key, 'NUMBER', value)
            region.addRegionLabel(label)

        image.addImageRegion(region)

    try:
        importLabelService = ImportLabelService()
        importLabelService.importOneImageLabel(run_parameter, image)
        print(True)
    except DataBaseException as dbe:
        dbe.print_exception_stack()
        print(False)


def import_images_label_data(run_parameter, image_dir):
    '''
    '''
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            print(os.path.join(root, file))
            import_image_label_data(run_parameter, os.path.join(root, file))


def __demo_method(run_parameter, image_dir):
    '''
    @description: 示例代码，展示如何构建并写入导入的图片标注数据
    @param {TLPLibrary.core.RunParameter} run_parameter: 脚本调用时传入的参数对象
    @param {str} image_dir: 要导入的图片的路径
    '''
    images = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            image_path = os.path.join(root, file)

            # 使用图片的路径创建图片对象，所有图片相关的数据都以图片为基础单位进行处理
            image = Image(image_path)

            # with open('读取的存储数据的源文件', 'r') as source_file:
            #     # 处理文件，找到当前图片的数据
            #     # 解析数据

            # 根据解析的数据构建图片的标签数据,找到当前图片的信息

            # 图片的meta标签创建
            image_meta_label = MetaLabel(name="dog")
            # 增加meta标签的属性
            image_meta_label.addAttribute(key="type", value_type=ValueType.TEXT, value="hound")
            image_meta_label.addAttribute(key="age", value_type=ValueType.NUMBER, value=4)
            # 将meta标签关联图片
            image.addMateLabel(image_meta_label)

            # 图片的区域标签创建
            # 构建区域的范围，4个坐标点，左上，右上，左下，右下
            points = [(837.1087959345828,-257.7348285803571), (1058.9210291123998,-452.5918634450022), (1197.9418369768098,-294.3398615503354), (976.1296037989925,-99.48282668569021)]
            # 区域的顶点坐标
            bounding_box = [(88,77), (66,55), (44,33), (22,11)]
            # 创建一个矩形区域对象
            rectangle_region = ImageRectangleRegion(points, bounding_box)

            # 区域的标签属性
            region_label = RegionLabel(name="eye")
            region_label.addAttribute(key="color", value_type=ValueType.TEXT, value="black")

            # 关联区域和标签
            rectangle_region.addRegionLabel(region_label)

            # 将区域对象标签关联图片
            image.addImageRegion(rectangle_region)

            images.append(image)

    try:
        importLabelService = ImportLabelService()
        importLabelService.importManyImageLabel(run_parameter, images)
        print(True)
    except DataBaseException as dbe:
        dbe.print_exception_stack()
        print(False)


def main():
    run_parameter = RunParameter.get_run_parameter()
    input_data(run_parameter)

if __name__ == "__main__":
    main()