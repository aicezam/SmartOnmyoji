# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import numpy as np


class ClickModSet:
    def __init__(self):
        super(self).__init__()

    @staticmethod
    def create_click_mod(zoom, loc=0.0, scale=0.5, size=(1000, 2)):
        """
        生成正态分布的鼠标随机点击模型，zoom是缩放比例，约等于偏移像素点
        """
        # 随机生成呈正态分布的聚合坐标（坐标0,0 附近概率最高）
        x, y = zip(*np.random.normal(loc=loc, scale=scale, size=size))

        # 对原始数据进行处理，点击模型除正态分布外，参照人类的眼动模型行为，点击规律还应呈现一定的长尾效应，所以对第二象限进行放大，对第四象限缩小
        x_int = []
        y_int = []
        for i in range(len(x)):

            # 对第二象限的坐标放大
            if x[i] < 0 and y[i] > 0:
                x_int.append(int(x[i] * zoom * 1.57))
                y_int.append(int(y[i] * zoom * 1.57))

            # 对第四象限的坐标缩小
            elif x[i] > 0 and y[i] < 0:

                # 若第四象限全部缩小，会导致第四象限的密度偏大，所以把其中三分之一的坐标，转换为第二象限的坐标（第二象限放大后密度会变小）
                roll = np.random.randint(0, 8)
                if roll < 3:
                    x_int.append(int(x[i] * zoom * -1.57))
                    y_int.append(int(y[i] * zoom * -1.57))
                else:
                    x_int.append(int(x[i] * zoom * 0.74))
                    y_int.append(int(y[i] * zoom * 0.74))
            else:
                # 其他象限的坐标不变
                x_int.append(int(x[i] * zoom))
                y_int.append(int(y[i] * zoom))

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

        # 随机抽取（平均抽取，每个坐标抽取概率相同，多次抽取的样本约等于模型中的样本，结果数据也呈正态分布）
        roll = np.random.randint(0, len(data_list) - 1)
        x = data_list[roll][0] + xp
        y = data_list[roll][1] + yp

        return x, y


if __name__ == '__main__':
    data = ClickModSet.create_click_mod(50)
    print(data[:10])

    x, y = ClickModSet.choice_mod_pos(data)
    print(x, y)

    # 测试随机取值是否呈正态分布
    # for i in range(2000):
    #     # xy 写入txt
    #     xy = ClickModSet.choice_mod_pos(data)
    #     f = open(r"D:\click_mod\1.txt", "a")
    #     f.writelines(str(xy[0]) + ',' + str(xy[1]) + '\n')
