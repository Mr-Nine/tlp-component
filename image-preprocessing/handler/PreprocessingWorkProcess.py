# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
LastEditors: jerome.du
@Date: 2019-12-04 17:52:11
LastEditTime: 2020-03-30 20:25:59
@Description:
'''

import os
import math
import shutil
import logging
import subprocess

from PIL import Image
from multiprocessing import Process


Image.MAX_IMAGE_PIXELS = None

class PreprocessingWorkProcess(Process):
    def __init__(self, name, image_id, image_path, save_root_path, processes, progress_queue):
        super(PreprocessingWorkProcess, self).__init__()
        self.name = name
        self.pending_image_id = image_id
        self.pending_image_path = image_path
        self.save_root_path = save_root_path
        self.image_root_path = os.path.join(self.save_root_path, self.pending_image_id)
        self.processes = processes
        self.progress_queue = progress_queue


    def run(self):

        if not os.path.exists(self.image_root_path):
            os.makedirs(self.image_root_path)

        self.__generate_thumbnail()

        self.__generate_tile_file()

        # TODO:告诉父进程我切图做完了


    def __generate_thumbnail(self):
        try:
            Image.MAX_IMAGE_PIXELS = None

            image_obj = Image.open(self.pending_image_path)

            self.max_zoom = int(math.ceil(math.log(max(image_obj.width, image_obj.height)/256) / math.log(2)))

            size = image_obj.size
            if size[0] <= 200:
                self.__copy_image_to_target('thumbnail.png')
                self.progress_queue.put({"state":"true", "progress":"thumbnail", "imageId":self.pending_image_id, "imagePath":self.pending_image_path, "width":size[0], "height":size[1], "minZoom":0, "maxZoom":self.max_zoom})
                return

            rate = float(200) / float(size[1])
            new_size = (int(size[0] * rate), 200)

            image_obj.thumbnail(new_size, Image.BILINEAR)

            thumbnail_path = os.path.join(self.image_root_path, 'thumbnail.png')
            image_obj.save(thumbnail_path, 'PNG')

            self.progress_queue.put({"state":"true", "progress":"thumbnail", "imageId":self.pending_image_id, "imagePath":self.pending_image_path, "width":size[0], "height":size[1], "minZoom":0, "maxZoom":self.max_zoom})
        except Exception as e:
            logging.error("%s:generate thumbnail error, error msg:%s" % (self.name, str(e)))
            import traceback
            traceback.print_exc()
            self.progress_queue.put({"state":"ERROR", "progress":"thumbnail", "imageId":self.pending_image_id, "imagePath":self.pending_image_path, "width":size[0], "height":size[1], "minZoom":0, "maxZoom":self.max_zoom})


    def __generate_tile_file(self):

        try:
            if (self.max_zoom < 3):
                '''
                如果目标图片的不需要切图(图片可以切的层数小于等于3，则直接将图片复制到目标路径)
                '''
                file_path, file_name = os.path.split(self.pending_image_path)
                self.__copy_image_to_target(file_name)
                logging.info("not tile image, image path %s, send 'ORIGINAL' message."%self.pending_image_path)
                self.progress_queue.put({"state":"ORIGINAL", "progress":"tiles", "imageId":self.pending_image_id, "imagePath":self.pending_image_path})
            else:
                current_path = os.path.dirname(os.path.abspath(__file__))
                command = "python2 " + os.path.join(current_path, "gdal2tiles-multiprocess.py") + " -l -p raster -z 0-" + str(self.max_zoom) + " -w none --processes=" + str(self.processes) + " " + self.pending_image_path + " " + self.image_root_path
                logging.info(command)

                tile_process = subprocess.Popen(command, shell=True, cwd="/", stdout=subprocess.PIPE)

                out = tile_process.stdout.readlines()

                '''
                b'Generating Base Tiles:\n'
                b'0...10...20...30...40...50...60...70...80...90...100 - done.\n'
                b'Generating Overview Tiles:\n'
                b'0...10...20...30...40...50...60...70...80...90...100 - done.\n'
                '''
                for i in range(len(out)):
                    if i == 1 or i == 3:
                        line = out[i].decode("utf-8")
                        if "100 - done." not in line:
                            self.progress_queue.put({"state":"ERROR", "progress":"tiles", "imageId":self.pending_image_id, "imagePath":self.pending_image_path})
                            return
                            # TODO:清除垃圾文件

                self.progress_queue.put({"state":"TILE", "progress":"tiles", "imageId":self.pending_image_id, "imagePath":self.pending_image_path})
        except Exception as e:
            logging.error("%s:generate tile file error, error msg:%s" % (self.name, str(e)))
            import traceback
            traceback.print_exc()
            self.progress_queue.put({"state":"ERROR", "progress":"tiles", "imageId":self.pending_image_id, "imagePath":self.pending_image_path})


    def __copy_image_to_target(self, image_name):
        '''
        '''
        shutil.copyfile(self.pending_image_path, os.path.join(self.image_root_path, image_name))

