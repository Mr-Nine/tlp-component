
'''
@Project:
@Team:
@Author: jerome.du
@LastEditors: jerome.du
@Date: 2019-12-10 18:34:19
@LastEditTime: 2019-12-16 19:54:50
@Description:
'''
import datetime

from TLPLibrary.entity import *
from TLPLibrary.core import Mysql, RunParameter
from TLPLibrary.error import *
from TLPLibrary.service import ImportLabelService, InferencerLabelService

# projectId 80882967-e342-4417-b002-8aeaf41cd6ea
# userId 31602ab7-8527-4952-a252-639a9be22d64
# path 192.168.30.198:/export/dujiujun/tlp/gdal2tiles/source/
# type import
# inferencerId 66655555-e342-4417-b002-111111111111

def a(runParameter):
    print("===========================================")

    mate = MateLabel(name="01")
    mate.addAttribute(key="K1", valueType=ValueType.INT, value=0)
    mate.addAttribute(key="K2", valueType=ValueType.INT, value=1)
    mate.addAttribute(key="K3", valueType=ValueType.TEXT, value="aaaaaa")

    mate2 = MateLabel(name="04")
    mate2.addAttribute(key="K10", valueType=ValueType.INT, value=6)
    mate2.addAttribute(key="K11", valueType=ValueType.INT, value=7)
    mate2.addAttribute(key="K12", valueType=ValueType.TEXT, value="aaaaaa")

    mate3 = MateLabel(name="01")
    mate3.addAttribute(key="K13", valueType=ValueType.INT, value=6)
    mate3.addAttribute(key="K11", valueType=ValueType.FLOAT, value=7)
    mate3.addAttribute(key="K3", valueType=ValueType.FLOAT, value=0.7)

    # ======================================================================================

    regionLabel = RegionLabel(name="02")
    regionLabel.addAttribute(key="K4", valueType=ValueType.INT, value=2)
    regionLabel.addAttribute(key="K5", valueType=ValueType.INT, value=3)
    regionLabel.addAttribute(key="K6", valueType=ValueType.TEXT, value="bbbbbbb")

    regionLabel2 = RegionLabel(name="03")
    regionLabel2.addAttribute(key="K7", valueType=ValueType.INT, value=4)
    regionLabel2.addAttribute(key="K8", valueType=ValueType.INT, value=5)
    regionLabel2.addAttribute(key="K9", valueType=ValueType.TEXT, value="ccccccc")

    regionLabel3 = RegionLabel(name="04")
    regionLabel3.addAttribute(key="K7", valueType=ValueType.INT, value=4)
    regionLabel3.addAttribute(key="K8", valueType=ValueType.INT, value=5)
    regionLabel3.addAttribute(key="K9", valueType=ValueType.TEXT, value="ccccccc")

    regionLabel4 = RegionLabel(name="03")
    regionLabel4.addAttribute(key="K10", valueType=ValueType.INT, value=4)
    regionLabel4.addAttribute(key="K11", valueType=ValueType.INT, value=5)
    regionLabel4.addAttribute(key="K9", valueType=ValueType.FLOAT, value=0.07)

    regionLabel5 = RegionLabel(name="05")

    # ======================================================================================

    points = [(88,77), (66,55), (44,33), (22,11)]
    boundingBox = [(88,77), (66,55), (44,33), (22,11)]
    polygonRegion = ImagePolygonRegion(points, boundingBox)

    polygonRegion.addRegionLabel(regionLabel)
    polygonRegion.addRegionLabel(regionLabel2)

    points2 = [(88,77), (66,55), (44,33), (22,11)]
    boundingBox2 = [(88,77), (66,55), (44,33), (22,11)]
    polygonRegion2 = ImagePolygonRegion(points2, boundingBox2)

    polygonRegion2.addRegionLabel(regionLabel3)
    polygonRegion2.addRegionLabel(regionLabel4)
    polygonRegion2.addRegionLabel(regionLabel5)

    image = Image("192.168.30.198:/export/dujiujun/tlp/gdal2tiles/source/world.topo.bathy.200407.3x21600x21600.B2.png")
    image.addMateLabel(mate)
    image.addMateLabel(mate2)
    # image.addMateLabel(mate3)
    image.addImageRegion(polygonRegion)
    image.addImageRegion(polygonRegion2)

    try:
        inferencerLabelService = InferencerLabelService()
        inferencerLabelService.inferencerOneImageLabel(runParameter, image)

        # importLabelService = ImportLabelService()
        # importLabelService.importOneImageLabel(runParameter, image)
    except DataBaseException as dbe:
        dbe.print_exception_stack()

    print("===========================================")

def main():


    # print(image.to_json())

    runParameter = RunParameter.get_run_parameter()
    a(runParameter)

if __name__ == "__main__":
    main()

