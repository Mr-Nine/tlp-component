# -- coding: utf-8 --

class RegionType(object):
    '''描述一个图片标注区域类型的标签。
    RECTANGLE:一个矩形区域
    POLYGON:一个多边形区域
    '''
    RECTANGLE = "RECTANGLE"
    POLYGON = "POLYGON"