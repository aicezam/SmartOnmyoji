import heapq
import sys
from os.path import dirname, abspath
import numpy
import numpy as np
from PIL import ImageGrab
from cv2 import cv2
from cv2.cv2 import SIFT


class GetTargetPosSift:
    def __init__(self, handle_width, screen_height, target_pic, screen_capture):
        super(GetTargetPosSift, self).__init__()
        self.screen_width = handle_width
        self.screen_height = screen_height
        self.target_pic = target_pic
        self.screen_capture = screen_capture

    @staticmethod
    def draw_target_pos(pos, scr_img, move_var):
        if pos is not None:
            # 在截图上框住识别的位置（左上角、右下角、颜色、线宽），这里可以改成函数调用
            # scr_img = cv2.cvtColor(scr_img, cv2.COLOR_RGB2BGRA)
            scr_img_tag = abspath(dirname(__file__)) + r'\screen_img\%s' % 'screen_img_tag.jpg'  # 截图的存储位置，程序路径里面
            cv2.rectangle(scr_img, (int(pos[0] - move_var[1]), int(pos[1] - move_var[0])),
                          (int(pos[0] + move_var[1]), int(pos[1] + move_var[0])),
                          (0, 238, 118), 2)
            # cv2.imshow('s', scr_img)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
            cv2.imwrite(scr_img_tag, scr_img, [int(cv2.IMWRITE_JPEG_QUALITY), 20])  # 保存 质量（0-100）

    @staticmethod
    def get_sift(cv2_img):
        """
        由于屏幕分辨率高，计算耗时，这里优化一下
        :return:
        """
        # 初始化SIFT探测器
        sift = cv2.SIFT_create()
        kp, des = sift.detectAndCompute(cv2_img, None)
        img_sift_info = [kp, des]
        return img_sift_info

    @staticmethod
    def get_target_pos_sift(target_sift, screen_sift, target_hw):
        """
        获取目标图像在截图中的位置
        :param target: 检测目标
        :return: 返回坐标(x,y) 与opencv坐标系对应
        """

        kp1 = target_sift[0]
        des1 = target_sift[1]

        kp2 = screen_sift[0]
        des2 = screen_sift[1]

        min_match_count = 10
        flann_index_kdtree = 0
        index_params = dict(algorithm=flann_index_kdtree, trees=4)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)
        good = []
        for m, n in matches:
            if m.distance < 0.75 * n.distance:
                good.append(m)
        if len(good) > min_match_count:
            src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            m, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            h, w = target_hw
            pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            if m is not None:
                dst = cv2.perspectiveTransform(pts, m)
                arr = np.int32(dst)  #
                pos_arr = arr[0] + (arr[2] - arr[0]) // 2
                pos = (int(pos_arr[0][0]), int(pos_arr[0][1]))  # 图片被压缩，坐标需要还原
                return pos
            else:
                return None
        else:
            return None


# test
# def main():
#     img1 = cv2.imread('img/tupo/end_win_2.jpg')
#     img1_hw = img1.shape[:2]
#
#     img2 = cv2.imread('screen_img/screen_pic.jpg')
#
#     target_info = GetTargetPosSift.get_sift(img1)
#
#     screen_info = GetTargetPosSift.get_sift(img2)
#
#     pos = GetTargetPosSift.get_target_pos_sift(target_info, screen_info, img1_hw)
#     # print(pos)
#
#     move_var = [img1_hw[0], img1_hw[1]]
#     GetTargetPosSift.draw_target_pos(pos, img2, move_var)
#
#
# if __name__ == '__main__':
#     main()
