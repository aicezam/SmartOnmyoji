# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

"""
基于脚本的防检测算法，模拟N连续次点击的窗口的关键位置
生成的txt文件可用excel或其他工具生成热力图分析
"""

import random
from modules.ModuleClickModSet import ClickModSet


def get_p_pos(pos, py_pos, scr_size):
    width1, height1 = scr_size
    if pos[0] < width1 * 0.618 and pos[1] < height1 * 0.618:
        # 如果需要点击的位置位于窗口左上，则坐标顺时针旋转180度
        p_x, p_y = ClickModSet.pos_rotate(py_pos, 180)
    elif pos[0] < width1 * 0.618 and pos[1] > height1 * 0.618:
        # 如果需要点击的位置位于窗口左下，则坐标顺时针旋转90度
        p_x, p_y = ClickModSet.pos_rotate(py_pos, 90)
    elif pos[0] > width1 * 0.618 and pos[1] < height1 * 0.618:
        # 如果需要点击的位置位于窗口右上，则坐标顺时针旋转270度
        p_x, p_y = ClickModSet.pos_rotate(py_pos, 270)
    else:
        # 如果需要点击的位置位于窗口右上或其他情况，则坐标不变
        p_x, p_y = py_pos
    return p_x, p_y


screen_size = [1152, 680]  # 窗口大小
target_pos1 = [1032, 576]  # 开始位置（开始、准备、挑战）
target_pos2 = [560, 200]  # 结束位置（胜利、失败）
target_pos3 = [620, 565]  # 奖励位置（达摩）
click_deviation = 50  # 偏移范围
ex_click_probability = 0.15  # 额外点击的概率

click_times = 1000  # 每个点的点击次数

click_mod = ClickModSet.create_click_mod(50)
target_pos_list = []
for i in range(click_times):
    p_pos = ClickModSet.choice_mod_pos(click_mod)

    px, py = get_p_pos(target_pos1, p_pos, screen_size)
    cx1 = int(px + target_pos1[0])
    cy1 = int(py + target_pos1[1])
    target_pos_list.append([cx1, cy1])

    px, py = get_p_pos(target_pos2, p_pos, screen_size)
    cx2 = int(px + target_pos2[0])
    cy2 = int(py + target_pos2[1])
    target_pos_list.append([cx2, cy2])

    px, py = get_p_pos(target_pos3, p_pos, screen_size)
    cx3 = int(px + target_pos3[0])
    cy3 = int(py + target_pos3[1])
    target_pos_list.append([cx3, cy3])

    roll_num = random.randint(0, 999)  # roll 0-999，触发几率在配置文件可设置

    if roll_num < ex_click_probability * 0.1 * 1000:
        if roll_num < 333:
            target_pos_list.append([cx1, cy1])
        elif 333 <= roll_num < 666:
            target_pos_list.append([cx2, cy2])
        elif 666 <= roll_num < 999:
            target_pos_list.append([cx3, cy3])

    elif ex_click_probability * 0.3 * 1000 < roll_num < ex_click_probability * 0.6 * 1000:
        width, height = screen_size
        mx = int(width * 0.618 + px)
        my = int(height * 0.618 + py)
        target_pos_list.append([mx, my])

    elif ex_click_probability * 0.6 * 1000 < roll_num < ex_click_probability * 0.9 * 1000:
        width, height = screen_size
        mx = int(random.randint(100, width))
        my = int(random.randint(100, height))
        target_pos_list.append([mx, my])

for i in range(len(target_pos_list)):
    xy = target_pos_list[i]
    f = open(r"D:\click_mod\1.txt", "a")
    f.writelines(str(xy[0]) + ',' + str(xy[1]) + '\n')
