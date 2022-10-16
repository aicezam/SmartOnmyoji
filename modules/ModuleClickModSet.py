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
        生成正态分布的鼠标随机点击模型，zoom是缩放比例，约等于偏移像素点
        """

        # 随机生成呈正态分布的聚合坐标（坐标0,0 附近概率最高）
        mx, my = zip(*np.random.normal(loc=loc, scale=scale, size=size))

        # 对原始数据进行处理，点击模型除正态分布外，参照人类的眼动模型行为，点击规律还应呈现一定的长尾效应，所以对第二象限进行放大，对第四象限缩小
        x_int = []
        y_int = []
        for i in range(len(mx)):

            # 对第二象限的坐标放大
            if mx[i] < 0 and my[i] > 0:
                x_int.append(int(mx[i] * zoom * 1.373))
                y_int.append(int(my[i] * zoom * 1.373))

            # 对第四象限的坐标缩小
            elif mx[i] > 0 and my[i] < 0:

                # 若第四象限全部缩小，会导致第四象限的密度偏大，所以把其中三分之一的坐标，转换为第二象限的坐标（第二象限放大后密度会变小）
                roll = np.random.randint(0, 8)
                if roll < 3:  # 转换其中三分之一的坐标
                    x_int.append(int(mx[i] * zoom * -1.373))
                    y_int.append(int(my[i] * zoom * -1.373))
                elif roll >= 7:  # 九分之二的坐标不处理
                    x_int.append(int(mx[i] * zoom))
                    y_int.append(int(my[i] * zoom))
                else:  # 剩下的坐标正常缩小
                    x_int.append(int(mx[i] * zoom * 0.752))
                    y_int.append(int(my[i] * zoom * 0.752))
            else:
                # 其他象限的坐标不变
                x_int.append(int(mx[i] * zoom))
                y_int.append(int(my[i] * zoom))

        # 处理边界问题，如果坐标点超出偏移范围，则缩小
        for i in range(len(x_int)):

            # 先缩小，原始数据稍微超出了zoom的范围
            x_int[i] = int(x_int[i] * 0.618)
            y_int[i] = int(y_int[i] * 0.618)

            # 再判断是否超出边界，超出则再缩小超出的部分
            if abs(x_int[i]) > zoom:
                x_int[i] = int(x_int[i] * 0.618)
            if abs(y_int[i]) > zoom:
                y_int[i] = int(y_int[i] * 0.618)

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
        围绕原点（0，0）,进行顺时针旋转，默认90度，十分之一的概率不旋转
        """
        roll = np.random.randint(0, 99)
        if roll > 5:
            rx = pos[0]
            ry = pos[1]
            # 对每个坐标进行变换，参照数学公式变换，有一点点误差，但不影响
            ang = math.radians(r)  # 将角度转换成弧度
            new_x = int(rx * math.cos(ang) + ry * math.sin(ang))
            new_y = int(-rx * math.sin(ang) + ry * math.cos(ang))
        else:
            new_x = pos[0]
            new_y = pos[1]
        return new_x, new_y


if __name__ == '__main__':
    data = ClickModSet.create_click_mod(50)
    print(data[:5])

    x, y = ClickModSet.choice_mod_pos(data)
    print(x, y)

    # 坐标旋转测试
    print("原始数组", data[:5])
    print("坐标旋转", ClickModSet.pos_rotate([data[0][0], data[0][1]], 270))

    x, y = ClickModSet.choice_mod_pos(data)
    print("随机取值", x, y)

    # 测试随机取值是否呈正态分布
    # for i in range(5000):
    #     # xy 写入txt
    #     xy = ClickModSet.choice_mod_pos(data_r)
    #     f = open(r"D:\click_mod\1.txt", "a")
    #     f.writelines(str(xy[0]) + ',' + str(xy[1]) + '\n')
