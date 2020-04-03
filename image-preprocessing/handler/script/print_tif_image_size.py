# -*- coding: utf-8 -*-

import math
from osgeo import gdal

# ds = gdal.Open("/export/tmp/adads/2-20181218_L20_1w_8bit.tif")
ds = gdal.Open("/export/tlp/source/PIA12348_orig.jpg")
bd = ds.GetRasterBand(1)
# ds = gdal.Open("/exprt/tmp/adads/2-20181218_L20_9w.tif")     # 导入tif文件
# bd = ds.GetRasterBand(1)
print(bd.XSize)
print(bd.YSize)
print(int(math.ceil(math.log(max(bd.XSize, bd.YSize)/256) / math.log(2))))
ds = None
