# -- coding: utf-8 --
'''
@Project:
@Team:
@Author: jerome.du
LastEditors: jerome.du
@Date: 2019-12-04 17:52:11
LastEditTime: 2020-04-09 20:14:40
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

        # 进程名称
        self.name = name
        # 需要处理的图片的编号（非项目）
        self.pending_image_id = image_id
        # 原图像的存放路径（转义后）
        self.pending_image_path = image_path
        # 处理后的图片的跟路径
        self.save_root_path = save_root_path
        # 处理后图片内容存放的路径
        self.image_root_path = os.path.join(self.save_root_path, self.pending_image_id)
        # 每张图的可以使用的进程数
        self.processes = processes
        # 发送处理结果的消息队列
        self.progress_queue = progress_queue


    def run(self):

        if not os.path.exists(self.image_root_path):
            os.makedirs(self.image_root_path)

        thumbnail_result = self.__generate_thumbnail()

        if thumbnail_result:
            self.__generate_tile_file()


    def __generate_thumbnail(self):
        try:
            logging.info("%s: generate thumbnail imageID----- %s, ." % (self.name, self.pending_image_id))
            Image.MAX_IMAGE_PIXELS = None

            fsize = os.path.getsize(self.pending_image_path) / float(1024 * 1024)
            (fname, suffix) = os.path.splitext(self.pending_image_path)

            # 如果超大文件或tif格式的文件，就换库处理缩略图的问题
            if suffix.lower() == '.tif':
                logging.info("thumbnail tif file.")
                pass
            elif fsize >= 2048:
                logging.info("thumbnail big file.")
                pass
            else:
                pass

            image_obj = None

            try:
                image_obj = Image.open(self.pending_image_path)
            except BaseException as identifier:
                logging.error("%s:open image file error, error msg:%s" % (self.name, str(e)))
                import traceback
                traceback.print_exc()
                self.progress_queue.put({"state":"ERROR", "progress":"thumbnail", "imageId":self.pending_image_id, "imagePath":self.pending_image_path, "width":-1, "height":-1, "minZoom":0, "maxZoom":0})
                return False

            self.max_zoom = int(math.ceil(math.log(max(image_obj.width, image_obj.height)/256) / math.log(2)))

            size = image_obj.size
            if size[0] <= 200:
                self.__copy_image_to_target('thumbnail.png')
                self.progress_queue.put({"state":"true", "progress":"thumbnail", "imageId":self.pending_image_id, "imagePath":self.pending_image_path, "width":size[0], "height":size[1], "minZoom":0, "maxZoom":self.max_zoom})
                return True

            rate = float(200) / float(size[1])
            new_size = (int(size[0] * rate), 200)

            image_obj.thumbnail(new_size)

            thumbnail_path = os.path.join(self.image_root_path, 'thumbnail.png')
            image_obj.save(thumbnail_path, 'PNG')

            self.progress_queue.put({"state":"true", "progress":"thumbnail", "imageId":self.pending_image_id, "imagePath":self.pending_image_path, "width":size[0], "height":size[1], "minZoom":0, "maxZoom":self.max_zoom})

            return True
        except Exception as e:
            logging.error("%s:generate thumbnail error, error msg:%s" % (self.name, str(e)))
            import traceback
            traceback.print_exc()
            self.progress_queue.put({"state":"ERROR", "progress":"thumbnail", "imageId":self.pending_image_id, "imagePath":self.pending_image_path, "width":size[0], "height":size[1], "minZoom":0, "maxZoom":self.max_zoom})
            return False


    def __generate_tile_file(self):
        logging.info("%s: generate tile imageID----- %s, ." % (self.name, self.pending_image_id))
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
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "script")
                command = "python " + os.path.join(script_path, "gdal2tiles_3.1_update_leaflet.py") + " -l -p raster -z 0-" + str(self.max_zoom) + " -w none --processes=" + str(self.processes) + " " + self.pending_image_path + " " + self.image_root_path
                logging.info(command)

                tile_process = subprocess.Popen(command, shell=True, cwd="/", stdout=subprocess.PIPE)

                (std_out, std_err) = tile_process.communicate()

                return_code = tile_process.poll()
                # out = tile_process.stdout.readlines()

                # '''
                # b'Generating Base Tiles:\n'
                # b'0...10...20...30...40...50...60...70...80...90...100 - done.\n'
                # b'Generating Overview Tiles:\n'
                # b'0...10...20...30...40...50...60...70...80...90...100 - done.\n'
                # '''
                # out_put_info = ""
                # for i in range(len(out)):
                #     if i == 1 or i == 3:
                #         line = out[i].decode("utf-8")
                #         out_put_info += line
                #         if "100 - done." not in line:
                #             logging.error(" generate tile file error, return message: %s." % out_put_info)
                #             self.progress_queue.put({"state":"ERROR", "progress":"tiles", "imageId":self.pending_image_id, "imagePath":self.pending_image_path})
                #             return

                if return_code:
                    outs = std_out.readlines()
                    out_put_info = ""
                    for i in range(len(outs)):
                        line = outs[i].decode("utf-8")
                        out_put_info += line
                    logging.error(" generate tile file error, return message: %s." % out_put_info)
                    self.progress_queue.put({"state":"ERROR", "progress":"tiles", "imageId":self.pending_image_id, "imagePath":self.pending_image_path})
                else:
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

