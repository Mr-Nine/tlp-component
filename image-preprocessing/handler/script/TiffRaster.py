#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from osgeo import gdal
import numpy as np
import cv2

OVR_LIST = [2, 4, 8, 16, 32]     # 金字塔各层下采样倍数
# 备注：1. list长度即金字塔层数，数值表示每层下采样倍数，从小到大排列，2的指数增长为常见取值，也可以尝试其他倍数
#       2. 此处示例分为5层，具体分几层、每层倍数取值，最好设计函数算一下，既可保证显示快、又可使金字塔制作又快又小


class TiffRaster:
    def __init__(self, path_tiff):
        """初始化类，获取栅格数据基本信息，生成金字塔ovr文件
        Args:
            path_tiff: tiff文件完整路径
        """
        self.dataset = gdal.Open(path_tiff)
        self.xsize = self.dataset.RasterXSize       # 栅格数据的x向尺寸
        self.ysize = self.dataset.RasterYSize       # 栅格数据的y向尺寸
        self.nchannel = self.dataset.RasterCount    # 栅格数据的通道数
        assert self.nchannel == 1 or self.nchannel == 3, '通道数量异常，只支持1或3通道'
        self.band = self.dataset.GetRasterBand(1)
        self.minval, self.maxval = self.band.ComputeRasterMinMax(1)        # 栅格数据的最小值、最大值
        assert self.minval < self.maxval, 'DN值异常，minval=maxval'
        if not os.path.exists(path_tif + '.ovr'):
            self.dataset.BuildOverviews(resampling='NEAREST', overviewlist=OVR_LIST)     # 制作金字塔
            # 备注：ovr会自动保存至tiff相同路径，可试验不同尺寸tiff的ovr制作时间，以设计进度条

    def get_data_to_show(self, xoff, yoff, xsize, ysize, win_xsize, win_ysize):
        """从Tiff文件中获取要显示的区域数据, 并转换为uint8
        Args:
            xoff: 要读取的栅格数据x向起点像素, int型
            yoff: 要读取的栅格数据y向起点像素, int型
            xsize: 要读取的栅格数据x向长度, int型
            ysize: 要读取的栅格数据y向长度, int型
            win_xsize: 要显示的窗口x向长度, int型
            win_ysize: 要显示的窗口y向长度，int型
                       注意: 窗口尺寸的长宽尽量与读取范围的长宽比一致, 否则图像将被拉伸显示
        Returns:
            data: 按窗口尺寸缩放的指定区域数据, uint8型
        """
        data = self.dataset.ReadAsArray(xoff=xoff, yoff=yoff, xsize=xsize, ysize=ysize,
                                        buf_xsize=win_xsize, buf_ysize=win_ysize)
        # 备注：ReadAsArray会自动将数据缩放至buf尺寸，并根据tiff同路径下的ovr加速读取速度
        data = data.astype(np.float)
        data = np.uint8(255.0 * (data - self.minval) / (self.maxval - self.minval))
        return data


# 使用样例，需根据实际情况获取xoff, yoff, xsize, ysize, win_xsize, win_ysize与显示脚本
path_tif = r"E:\dataset\test\美国_梅波特海军基地2-20181218_L20_10w.tif"
image = TiffRaster(path_tif)
imdata = image.get_data_to_show(xoff=0, yoff=0, xsize=image.xsize, ysize=image.ysize, win_xsize=905, win_ysize=905)
cv2.imshow('test_show', imdata)
cv2.waitKey(0)
