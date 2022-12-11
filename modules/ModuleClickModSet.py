# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import math
import numpy as np


class ClickModSet:
    def __init__(self):
        super(self).__init__()

    @staticmethod
    def create_click_mod(zoom, loc=0.0, scale=0.45, size=(2000, 2)):
        """
        生成正态分布的鼠标随机点击模型，zoom是缩放比例，约等于偏移像素点，size是模型大小即模型中的坐标总量
        """

        # 随机生成呈正态分布的聚合坐标（坐标0,0 附近概率最高）
        mx, my = zip(*np.random.normal(loc=loc, scale=scale, size=size))

        # 对原始数据进行处理，点击模型除正态分布外，参照人类的眼动模型行为，点击规律还应呈现一定的长尾效应，所以对第二象限进行放大，对第四象限缩小
        x_int = []
        y_int = []
        for t in range(len(mx)):

            # 对第二象限的坐标放大
            if mx[t] < 0 and my[t] > 0:
                x_int.append(int(mx[t] * zoom * 1.373))
                y_int.append(int(my[t] * zoom * 1.303))

            # 对第四象限的坐标缩小
            elif mx[t] > 0 and my[t] < 0:

                # 若第四象限全部缩小，会导致第四象限的密度偏大，所以把其中三分之一的坐标，转换为第二象限的坐标（第二象限放大后密度会变小）
                roll = np.random.randint(0, 9)
                if roll < 5:  # 转换其中二分之一的坐标
                    # pos = ClickModSet.pos_rotate([int(mx[t]), int(my[t])], 180)
                    # x_int.append(int(pos[0]))
                    # y_int.append(int(pos[1]))

                    x_int.append(int(mx[t] * zoom * -1.350))
                    y_int.append(int(my[t] * zoom * -1.200))

                    # x_int.append(int(mx[i] * zoom * -1))
                    # y_int.append(int(my[i] * zoom * -1))
                elif roll >= 8:  # 十分之二的坐标不处理
                    x_int.append(int(mx[t] * zoom))
                    y_int.append(int(my[t] * zoom))
                else:  # 剩下的坐标正常缩小
                    x_int.append(int(mx[t] * zoom * 0.618))
                    y_int.append(int(my[t] * zoom * 0.618))
            else:
                # 其他象限的坐标不变
                x_int.append(int(mx[t] * zoom))
                y_int.append(int(my[t] * zoom))

        # 处理边界问题，如果坐标点超出偏移范围，则缩小
        for t in range(len(x_int)):

            # # 先缩小，原始数据稍微超出了zoom的范围
            x_int[t] = int(x_int[t] * 0.816)
            y_int[t] = int(y_int[t] * 0.712)

            # 再判断是否超出边界，超出则再缩小超出的部分
            if abs(x_int[t]) > zoom:
                x_int[t] = int(x_int[t] * 0.718)
            if abs(y_int[t]) > zoom*1.15:
                y_int[t] = int(y_int[t] * 0.618)

        # 合并数据
        mod_data = np.array(list(zip(x_int, y_int)))

        return mod_data

    @staticmethod
    def choice_mod_pos(data_list):
        """
        从模型中抽取一个坐标（x1,y1）
        """

        # 随机抽取（平均抽取，每个坐标抽取概率相同，多次抽取的样本约等于模型中的样本，结果数据也呈正态分布）
        roll = np.random.randint(0, len(data_list) - 1)
        x1 = data_list[roll][0]
        y1 = data_list[roll][1]

        # 在正态分布基础上，随机偏移，避免太过集中
        if abs(x1) <= 50 and abs(y1) <= 50:
            roll_seed = 5
        elif 50 < abs(x1) <= 100 and 50 < abs(y1) <= 100:
            roll_seed = 15
        elif abs(x1) <= 50 and 50 < abs(y1) <= 100:
            roll_seed = 10
        elif abs(y1) <= 50 and 50 < abs(x1) <= 100:
            roll_seed = 10
        else:
            roll_seed = 20

        # roll偏移量
        xp = np.random.randint(- roll_seed, roll_seed)
        yp = np.random.randint(- roll_seed, roll_seed)
        x1 = x1 + xp
        y1 = y1 + yp

        return x1, y1

    @staticmethod
    def pos_rotate(pos, r=90):
        """
        将一个坐标围绕原点（0，0）,进行顺时针旋转，默认90度
        """
        rx = pos[0]
        ry = pos[1]
        # 对每个坐标进行变换，参照数学公式变换，有一点点误差，但不影响
        ang = math.radians(r)  # 将角度转换成弧度
        new_x = int(rx * math.cos(ang) + ry * math.sin(ang))
        new_y = int(-rx * math.sin(ang) + ry * math.cos(ang))

        return new_x, new_y


if __name__ == '__main__':
    data = ClickModSet.create_click_mod(50)

    x, y = ClickModSet.choice_mod_pos(data)

    # 模型测试
    print("原始模型显示前5个坐标\n", data[:20])
    print("测试坐标旋转，对第一个点旋转180度", ClickModSet.pos_rotate([data[0][0], data[0][1]], 180))
    print(f"随机取值 ({x},{y})，并旋转90度 {ClickModSet.pos_rotate([x,y], 90)}")

    # 测试随机取值是否呈正态分布
    # os.remove(r"D:\click_mod\1.txt")
    # for i in range(500):
    #     # xy 写入txt
    #     xy = ClickModSet.choice_mod_pos(data)
    #     f = open(r"D:\click_mod\1.txt", "a")
    #     f.writelines(str(xy[0]) + ',' + str(xy[1]) + '\n')
