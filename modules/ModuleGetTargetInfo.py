# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from os import path, walk
from re import search, compile
from numpy import uint8, fromfile
from cv2 import cv2
from modules.ModuleImgProcess import ImgProcess
from modules.ModuleGetConfig import ReadConfigFile


class GetTargetPicInfo:
    def __init__(self, target_modname, custom_target_path, compress_val=1):
        super(GetTargetPicInfo, self).__init__()
        self.modname = target_modname
        self.custom_target_path = custom_target_path
        self.target_folder_path = None
        self.compress_val = compress_val

    def get_target_folder_path(self):
        """
        不同的模式下，匹配对应文件夹的图片
        :returns: 需要匹配的目标图片地址，如果没有返回空值
        """
        rc = ReadConfigFile()
        file_name = rc.read_config_target_path_files_name()  # 读取配置文件中的待匹配目标的名字信息

        parent_path = path.abspath(path.dirname(path.dirname(__file__)))  # 父路径

        # 通过界面上的选择目标，定位待匹配的目标文件夹
        for i in range(7):
            if self.modname == file_name[i][0]:
                target_folder_path = parent_path + r"\img\\" + file_name[i][1]
                return target_folder_path

        if self.modname == "自定义":
            target_folder_path = self.custom_target_path
            return target_folder_path
        else:
            return None

    @property
    def get_target_info(self):
        """获取目标图片文件夹路径下的所有图片信息"""
        target_img_sift = {}
        img_hw = {}
        img_name = []
        folder_path = self.get_target_folder_path()
        img_file_path = []
        cv2_img = {}

        # 获取每张图片的路径地址
        if folder_path is None:
            print("<br>未找到目标文件夹或图片地址！即将退出！")
            return None  # 脚本结束
        else:
            for cur_dir, sub_dir, included_file in walk(folder_path):
                if included_file:
                    for file in included_file:
                        if search(r'.jpg', file):
                            img_file_path.append(cur_dir + "\\" + file)
                        elif search(r'.png', file):  # 兼容png格式
                            img_file_path.append(cur_dir + "\\" + file)
            if len(img_file_path) == 0:
                print("<br>未找到目标文件夹或图片地址！")
                return None  # 脚本结束

            # 通过图片地址获取每张图片的信息
            for i in range(len(img_file_path)):
                # img = cv2.imread(img_file_path[i])  # 读取图片地址的图片到内存中
                img = cv2.imdecode(fromfile(img_file_path[i], dtype=uint8), -1)  # 修复中文路径下opencv报错问题
                img_process = ImgProcess()
                img_hw[i] = img.shape[:2]  # 获取目标图片宽高
                img_name.append(self.trans_path_to_name(img_file_path[i]))  # 获取目标图片名称
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                # print(f"<br><img src='{img_file_path[i]}' />")
                # img_process.show_img(img)
                target_img_sift[i] = img_process.get_sift(img)  # 获取目标图片特征点信息
                cv2_img[i] = img  # 将图片信息读取到内存

            return target_img_sift, img_hw, img_name, img_file_path, cv2_img  # 返回图片特征点信息，图片宽高，图片名称，图片路径地址，图片

    @staticmethod
    def trans_path_to_name(path_string):
        """获取指定文件路径的文件名称"""
        pattern = compile(r'([^<>/\\|:"*?]+)\.\w+$')
        data = pattern.findall(path_string)
        if data:
            return data[0]
