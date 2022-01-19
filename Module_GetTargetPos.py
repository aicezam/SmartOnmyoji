import heapq
import sys
from os.path import dirname, abspath
import numpy as np
from cv2 import cv2
from Module_GetTargetPic import GetTargetPic


class GetTargetPos:
    def __init__(self, handle_width, screen_height, target_pic, screen_capture):
        super(GetTargetPos, self).__init__()
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
            cv2.rectangle(scr_img, (pos[0] - move_var, pos[1] - move_var), (pos[0] + move_var, pos[1] + move_var),
                          (0, 238, 118), 2)
            cv2.imwrite(scr_img_tag, scr_img, [int(cv2.IMWRITE_JPEG_QUALITY), 20])  # 保存 质量（0-100）

    def get_target_pos(self):
        target_pic_path = self.target_pic
        # scr_img = self.screen_img
        scr_img = self.screen_capture
        screen_width = self.screen_width
        screen_height = self.screen_height
        max_val = []
        pos = None
        val = 0.85  # 初始化最低相似度
        print("正在匹配…")
        # for i in tqdm(range(0, len(find_pic)), colour='red'):  # 加进度条
        # for i in tqdm(range(0, len(find_pic))):  # 加进度条

        # 全部循环一遍之后，取最相似的图片的坐标
        # for i in range(len(target_pic_path)):  # 匹配所有目标图片，并记录最大匹配相似度数值，记录入数组
        #     max_val.append(self.get_all_target_max_val(scr_img, target_pic_path[i]))
        # max_val = self.get_target_best_match_val(max_val, target_pic_path)  # 取最大的匹配值及索引
        # target_pic_number = max_val[0]
        # # 获取最匹配的图片的相对坐标点
        # pos = self.get_target_pic_pos(scr_img, target_pic_path[target_pic_number], screen_width, screen_height, val)

        # 全部循环一遍，如果取到相似度达到val的图片就停止，不再继续匹配
        for i in range(len(target_pic_path)):
            pos = self.get_target_pic_pos(scr_img, target_pic_path[i], screen_width, screen_height, val)
            if pos is not None:
                pic_name = GetTargetPic.trans_path_to_name(target_pic_path[i]) + ".jpg"
                print(f"匹配到第：[ {i + 1} ] 张图片！图片名称：[ {pic_name} ]")
                break
        if pos is None:
            print("匹配失败！")
        return pos

    @staticmethod
    def get_all_target_max_val(img_path, target):
        """将目标突破与截图进行匹配，获取最大匹配值"""
        # img_src = cv2.imread(img_path)  # 转换截图为cv2格式
        img_src = img_path
        img_src = cv2.cvtColor(img_src, cv2.COLOR_BGRA2RGB)  # 去掉会导致不准确
        template = cv2.imread(target)  # 转换目标图片为cv2格式
        if (img_src is not None) and (template is not None):
            if (template.shape[1] > img_src.shape[1]) or (template.shape[0] > img_src.shape[0]):
                print("目标图片尺寸超过截图，或截图太小！")
                sys.exit(0)  # 脚本结束
            res = cv2.matchTemplate(img_src, template, cv2.TM_CCOEFF_NORMED)  # 最小匹配度，最大匹配度，最小匹配度的坐标，最大匹配度的坐标
            val = cv2.minMaxLoc(res)
            if val is None:
                val = 0
            else:
                val = round(val[1], 2)  # 数组中第2个数才是最大相似度，如果为None，返回0，并保留2位小数
            return val

    @staticmethod
    def get_target_pic_pos(img_path, target, screen_width, screen_height, val):
        """获取目标图片在截图中的中心点坐标"""
        # print("识别匹配中……")
        # start = time.time()
        img_src = img_path  # 如果时从内存中读取图片，就使用这句，要注释上面那个转换，因为内存中已经时cv2格式的图片了
        img_src = cv2.cvtColor(img_src, cv2.COLOR_BGRA2RGB)  # 去掉会导致不准确
        template = cv2.imread(target)
        if (img_src is not None) and (template is not None):  # 获取小图片的高和宽
            img_tmp_height = template.shape[0]
            img_tmp_width = template.shape[1]  # 获取大图片的高和宽
            img_src_height = img_src.shape[0]
            img_src_width = img_src.shape[1]  # 匹配图片的宽高
            res = cv2.matchTemplate(img_src, template, cv2.TM_CCOEFF_NORMED)  # 最小匹配度，最大匹配度，最小匹配度的坐标，最大匹配度的坐标
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            # print(number, "匹配度：", max_val)
            if max_val is None:
                max_val = 0
            else:
                max_val = round(max_val, 2)  # 取最大相似度，如果为None，返回0，并保留2位小数
            if max_val >= val:  # 计算相对坐标
                position = [int(screen_width / img_src_width * (max_loc[0] + img_tmp_width / 2)),
                            int(screen_height / img_src_height * (max_loc[1] + img_tmp_height / 2))]
                print(f"匹配成功！\n坐标位置：[ {position[0]} {position[1]} ]\n相似分数：[ {max_val} ]")
                return position

    @staticmethod
    def get_target_best_match_val(val_list, target_pic):
        """
        获取数组内最大值及索引
        bug:文件名有中文会报错（匹配失败返回相似度应该是0，或者直接报错），相似度返回时，应该只保留两位小数
        """
        if (val_list is not None) and (target_pic is not None):
            tmp = zip(range(len(val_list)), val_list)
            large = heapq.nlargest(1, tmp, key=lambda x: x[1])  # 求最大的值及索引
            # print(val_list)
            large_num = large[0]  # 从元组取值
            pic_name = GetTargetPic.trans_path_to_name(target_pic[large_num[0]]) + ".jpg"
            print("匹配到第：[%d]张图片！" % (large_num[0] + 1), "\n图片名称：[", pic_name, "]", "\n相似分数：[%.2f]" % large_num[1])
            return large_num  # 返回最大值索引
        else:
            return None
