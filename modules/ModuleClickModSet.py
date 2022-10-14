# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import numpy as np
from numpy.random import normal


class ClickModSet:
    def __init__(self):
        super(self).__init__()

    @staticmethod
    def create_click_mod(zoom, loc=0.0, scale=0.8, size=(500, 2)):
        """
        生成正态分布的鼠标随机点击模型
        """
        # 随机生成呈正态分布的聚合坐标（坐标0,0 附近概率最高）
        x, y = zip(*normal(loc=loc, scale=scale, size=size))
        # y = normal(loc=loc, scale=scale, size=size)

        # 缩放数据，将原始数据进行缩放，等同于之前的坐标偏移量/2
        x_int = []
        y_int = []
        for i in range(len(x)):
            x_int.append(int(x[i] * (zoom/2)))
            y_int.append(int(y[i] * (zoom/2)))

        # 合并数据
        mod_data = np.array(list(zip(x_int, y_int)))

        return mod_data

    @staticmethod
    def choice_mod_pos(data_list):
        """
        从模型中抽取一个坐标（x,y）
        """
        # 在正态分布基础上，随机偏移，避免太过集中
        xp = np.random.randint(-5, 5)
        yp = np.random.randint(-5, 5)

        # 随机抽取（平均分布，每个坐标抽取概率相同）
        roll = np.random.randint(0, len(data_list) - 1)
        x = data_list[roll][0] + xp
        y = data_list[roll][1] + yp

        return x, y


if __name__ == '__main__':
    data = ClickModSet.create_click_mod(50)
    print(data)

    xy = ClickModSet.choice_mod_pos(data)
    print(xy[0], xy[1])

    # 测试随机取值是否呈正态分布
    # for i in range(1000):
    #     # xy 写入txt
    #     xy = ClickModSet.choice_mod_pos(data)
    #     f = open(r"D:\SmartOnmyoji_V8.0\modules\click_mod\1.txt", "a")
    #     f.writelines(str(xy[0]) + ',' + str(xy[1]) + '\n')
