# -*- coding: utf-8 -*-
from os.path import abspath, dirname
from cv2 import cv2


class ImgProcess:
    """图像处理，传入的图片格式必须是cv2的格式"""

    def __init__(self):
        super(ImgProcess, self).__init__()

    @staticmethod
    def save_img(img, img_path_name=r'\screen_img\screen_pic.jpg'):
        """保存内存中cv2格式的图片为本地文件"""
        if img is None:
            print("未获取到需要保存的图片！")
        else:
            file_path = abspath(dirname(__file__)) + img_path_name  # 截图的存储位置，程序路径里面
            cv2.imwrite(file_path, img, [int(cv2.IMWRITE_JPEG_QUALITY), 20])  # 保存截图 质量（0-100）

    @staticmethod
    def show_img(img):
        """查看内存中cv2格式的图片"""
        if img is None:
            print("未获取到需要显示的图片！")
        else:
            cv2.namedWindow('scr_img')  # 命名窗口
            cv2.imshow("scr_img", img)  # 显示
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    @staticmethod
    def draw_pos_in_img(img, pos, height_width):
        """
        在图片中指定坐标点绘制边框
        :param img: 需要绘制边框的图片
        :param pos: 中心坐标点
        :param height_width: 要绘制的边框的高和宽
        :return: 返回坐标(x,y) 与opencv坐标系对应
        """
        if pos is None:
            print("未获取坐标点位置！")
        else:
            img = cv2.rectangle(img,
                                (pos[0] - int(height_width[1] * 0.5), pos[1] - int(height_width[0] * 0.5)),
                                (pos[0] + int(height_width[1] * 0.5), pos[1] + int(height_width[0] * 0.5)),
                                (0, 238, 118),
                                2)  # 参数解释：图片，左上角坐标，右下角坐标，颜色，线宽
            return img

    @staticmethod
    def img_compress(img, compress_val=0.5):
        """压缩图片，默认0.5倍"""
        height, width = img.shape[:2]  # 获取宽高
        # 压缩图片,压缩率compress_val
        size = (int(width * compress_val), int(height * compress_val))
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
        return img

    @staticmethod
    def get_sift(img):
        """
        :param img: 传入cv2格式的图片，获取特征点信息
        :return: 返回特征点信息
        """
        # 初始化SIFT探测器
        sift = cv2.SIFT_create()
        # cv.xfeatures2d.BEBLID_create(0.75)  # 已过时用法
        kp, des = sift.detectAndCompute(img, None)
        img_sift = [kp, des]
        return img_sift
