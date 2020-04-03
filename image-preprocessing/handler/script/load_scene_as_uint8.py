#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from osgeo import gdal
import numpy as np
import cv2
import time


def load_PAN_as_uint8(tiffile, blocksize=None):
    ds = gdal.Open(tiffile)     # 导入tif文件
    bd = ds.GetRasterBand(1)
    img_scene = np.empty((bd.YSize, bd.XSize), dtype=np.uint8)  # 初始化整景图
    minval, maxval = bd.ComputeRasterMinMax(1)  # 整景图最大最小值
    if blocksize is not None:
        # 按块读取
        nx = np.ceil(np.float(bd.XSize) / np.float(blocksize)).astype(np.int)   # x向分块数量
        ny = np.ceil(np.float(bd.YSize) / np.float(blocksize)).astype(np.int)   # y向分块数量
        for idx in range(nx):
            x0 = idx * blocksize                              # 块x向起始索引
            x1 = min([(idx + 1) * blocksize, bd.XSize])       # 块x向结束索引
            for idy in range(ny):
                y0 = idy * blocksize                          # 块y向起始索引
                y1 = min([(idy + 1) * blocksize, bd.YSize])   # 块y向结束索引
                img_block = bd.ReadAsArray(x0, y0, x1 - x0, y1 - y0)        # 读取块
                img_scene[y0:y1, x0:x1] = np.uint8(255.0 * (img_block - minval) / (maxval - minval))    # 线性变换uint8
    else:
        # 整体读取
        img_scene = bd.ReadAsArray(0, 0, bd.XSize, bd.YSize)
        img_scene = np.uint8(255.0 * (img_scene - minval) / (maxval - minval))    # 线性变换uint8
    return img_scene


path_src = r"/export/tmp/adads/tran"
path_dst = r"/export/tmp/adads/16"
for tif in os.listdir(path_src):
    if tif.endswith('.tif'):
        print(tif)
        start = time.time()
        image = load_PAN_as_uint8(os.path.join(path_src, tif), blocksize=20000)
        end = time.time()
        print(end - start)
        cv2.imencode('.tif', image)[1].tofile(os.path.join(path_dst, tif))
        # cv2.imwrite(os.path.join(path_dst, tif), image)

