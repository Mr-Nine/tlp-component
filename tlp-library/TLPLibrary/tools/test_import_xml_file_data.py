# -- coding: utf-8 --

import os

# import you library

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
    import_image_label_data(run_parameter, image_path)


    # if os.path.isdir(image_path):
    #     # 批量导入操作，获取的是一个存放图片的目录
    #     import_images_label_data(run_parameter, image_path)
    # elif os.path.isfile(image_path):
    #     # 运行参数传递的单张图片的路径，导入程序针对这一张图片进行处理
    #     import_image_label_data(run_parameter, image_path)


def import_image_label_data(run_parameter, image_path):
    (image_path_dir, image_file_name) = os.path.split(image_path)
    (file_name, exte_name) = os.path.splitext(image_file_name)

    # find data xml file
    target_file_name = file_name + '.xml'
    xml_file_path = _find_xml_file(image_path_dir, target_file_name)

    if xml_file_path is None:
        print("image not found.")

    data_xml = minidom.parse(xml_file_path)
    # get annotation element
    annotation = data_xml.documentElement

    meta_data = annotation.getElementsByTagName("Metadata")[0]

    # get element and element text
    meta_data_file_name = meta_data.getElementsByTagName("ImageFilename")[0].childNodes[0].data
    if meta_data_file_name != image_file_name:
        print("the data file error.")
        return

    # create image object
    image = Image(image_path)

    width_size = int(meta_data.getElementsByTagName("WidthInPixels")[0].childNodes[0].data)
    height_size = int(meta_data.getElementsByTagName("HeightInPixels")[0].childNodes[0].data)

    # add image meta label -- ROIClass
    image_meta_label = MetaLabel(name=meta_data.getElementsByTagName("ROIClass")[0].childNodes[0].data)
    image.addMetaLabel(image_meta_label)

    # add other...

    # add image region and region label
    objects = annotation.getElementsByTagName("Object")
    for obj in objects:

        # get positions info
        positions = obj.getElementsByTagName("Position")[0].childNodes
        image_regions = []
        for position in positions:
            if isinstance(position, xml.dom.minidom.Element):
                image_regions.append(eval(position.childNodes[0].data))

        # 同步坐标系
        region_images2 = []
        for region in image_regions:
            region_images2.append((region[0], height_size - region[1]))

        if len(region_images2) == 4:
            region = ImageRectangleRegion(region_images2, bounding_box=None)
        else:
            region = ImagePolygonRegion(region_images2, bounding_box=None)

        # get class info
        classes = obj.getElementsByTagName("Class")[0].childNodes
        classes_value = []
        for cls in classes:
            if isinstance(cls, xml.dom.minidom.Element):
                classes_value.append(cls.childNodes[0].data)

        # create region label
        label = RegionLabel(name="ship-class")
        # 没有什么好办法对多级标签进行初始化，可能需要先手动弄到DCP里面
        label.addAttribute(key="ship-class", value_type=ValueType.CASCADER, value=classes_value)
        # add label 2 region
        region.addRegionLabel(label)

        # add region 2 image
        image.addImageRegion(region)

    try:
        importLabelService = ImportLabelService()
        importLabelService.importOneImageLabel(run_parameter, image)
        print(True)
    except DataBaseException as dbe:
        dbe.print_exception_stack()
        print(False)

def _find_xml_file(image_path, target_file_name):

    for root, dirs, files in os.walk(image_path):
        for file in files:
            if file == target_file_name:
                return os.path.join(root, file)

    return None


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
            # 创建一个举行区域对象
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