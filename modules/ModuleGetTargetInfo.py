# -*- coding: utf-8 -*-
from os import path, walk
from os.path import abspath, dirname
from re import search, compile
from numpy import uint8, fromfile
from cv2 import cv2
from modules.ModuleImgProcess import ImgProcess


class GetTargetPicInfo:
    def __init__(self, modname, compress_val=1):
        super(GetTargetPicInfo, self).__init__()
        self.modname = modname
        self.target_folder_path = None
        self.compress_val = compress_val

    def get_target_folder_path(self):
        """
        不同的模式下，匹配对应文件夹的图片
        :returns: 需要匹配的目标图片地址，如果没有返回空值
        """
        parent_path = path.abspath(path.dirname(path.dirname(__file__)))  # 父路径
        current_path = abspath(dirname(__file__))  # 当前路径
        if self.modname == "御魂":
            target_folder_path = parent_path + r'\img\yuhun'
            # target_folder_path = current_path + r'\img\yuhun'
            # print(target_folder_path)
        elif self.modname == "探索":
            target_folder_path = parent_path + r'\img\tansuo'
        elif self.modname == "突破":
            target_folder_path = parent_path + r'\img\tupo'
        elif self.modname == "活动":
            target_folder_path = parent_path + r'\img\huodong'
        elif self.modname == "觉醒":
            target_folder_path = parent_path + r'\img\juexing'
        elif self.modname == "百鬼夜行":
            target_folder_path = parent_path + r'\img\baigui'
        elif self.modname == "微信红包":
            target_folder_path = parent_path + r'\img\wxhongbao'
        else:
            target_folder_path = None
        return target_folder_path

    @property
    def get_target_info(self, img_type='.jpg'):
        """获取目标图片文件夹路径下的所有图片信息"""
        target_img_sift = {}
        img_hw = {}
        img_name = []
        folder_path = self.get_target_folder_path()
        img_file_path = []
        cv2_img = {}

        # 获取每张图片的路径地址
        if folder_path is None:
            print("未找到目标文件夹或图片地址！即将退出！")
            return None  # 脚本结束
        else:
            # print("------------------------------------------------------------")
            # print("正在读取目标图片(仅限.jpg格式)……")
            for cur_dir, sub_dir, included_file in walk(folder_path):
                if included_file:
                    for file in included_file:
                        if search(img_type, file):
                            # print(cur_dir + "\\" + file)
                            # print(file)
                            img_file_path.append(cur_dir + "\\" + file)
            if len(img_file_path) == 0:
                print("未找到目标文件夹或图片地址！")
                return None # 脚本结束
            # print("图片路径读取完成!共[%d]张图片" % len(target_file_path))
            # print("------------------------------------------------------------")

            # 通过图片地址获取每张图片的信息
            for i in range(len(img_file_path)):
                # img = cv2.imread(img_file_path[i])  # 读取图片地址的图片到内存中
                img = cv2.imdecode(fromfile(img_file_path[i], dtype=uint8), -1)  # 修复中文路径下opencv报错问题
                img_process = ImgProcess()
                img_hw[i] = img.shape[:2]  # 获取目标图片宽高
                img_name.append(self.trans_path_to_name(img_file_path[i]) + '.jpg')  # 获取目标图片名称
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
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
