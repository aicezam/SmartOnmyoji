# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

"""
基于脚本的防检测算法，模拟N连续次点击的窗口的关键位置
生成的txt文件可用excel或其他工具生成热力图分析
"""

import random
from ModuleClickModSet import ClickModSet
from ModuleDoClick import DoClick

screen_size = [1152, 680]  # 窗口大小

target_pos1 = [1032, 576]  # 开始位置（开始、准备、挑战）
pos1_name = "start"
target_pos2 = [560, 200]  # 结束位置（胜利、失败）
pos2_name = "end"
target_pos3 = [620, 565]  # 奖励位置（达摩）
pos3_name = "win"
pos_ex = "ex_click"
click_deviation = 50  # 偏移范围
ex_click_probability = 0.15  # 额外点击的概率
click_times = 300  # 每个点的点击次数
time = "22-11-20 10:00:00"

click_mod = ClickModSet.create_click_mod(click_deviation)
click_mod2 = ClickModSet.create_click_mod(120)
target_pos_list = []

for i in range(click_times):
    p_pos = ClickModSet.choice_mod_pos(click_mod)

    px, py = DoClick.get_p_pos(click_mod2, screen_size[0], screen_size[1], target_pos1)
    # cx1 = int(target_pos1[0]) + random.randint(-100, 100)
    # cy1 = int(target_pos1[1]) + random.randint(-100, 100)
    # cx1 = int(target_pos1[0]) + random.normalvariate(20, 60)
    # cy1 = int(target_pos1[1]) + random.normalvariate(20, 60)
    cx1 = int(px + target_pos1[0])
    cy1 = int(py + target_pos1[1])
    target_pos_list.append([time, pos1_name, cx1, cy1])

    px, py = DoClick.get_p_pos(click_mod, screen_size[0], screen_size[1], target_pos2)
    cx2 = int(px + target_pos2[0])
    cy2 = int(py + target_pos2[1])
    target_pos_list.append([time, pos2_name, cx2, cy2])

    px, py = DoClick.get_p_pos(click_mod, screen_size[0], screen_size[1], target_pos3)
    cx3 = int(px + target_pos3[0])
    cy3 = int(py + target_pos3[1])
    target_pos_list.append([time, pos3_name, cx3, cy3])

    roll_num = random.randint(0, 999)  # 平均分配三个位置的点击次数，并追加额外点击模拟

    if roll_num < ex_click_probability * 0.1 * 1000:
        if roll_num < 333:
            target_pos_list.append([time, pos1_name, cx1, cy1])
        elif 333 <= roll_num < 666:
            target_pos_list.append([time, pos2_name, cx2, cy2])
        elif 666 <= roll_num < 999:
            target_pos_list.append([time, pos3_name, cx3, cy3])

    elif ex_click_probability * 0.3 * 1000 < roll_num < ex_click_probability * 0.6 * 1000:
        width, height = screen_size
        mx = int(width * 0.618 + px)
        my = int(height * 0.618 + py)
        target_pos_list.append([time, pos_ex, mx, my])

    elif ex_click_probability * 0.6 * 1000 < roll_num < ex_click_probability * 0.9 * 1000:
        width, height = screen_size
        mx = int(random.randint(100, width))
        my = int(random.randint(100, height))
        target_pos_list.append([time, pos_ex, mx, my])

for i in range(len(target_pos_list)):
    pos_log = target_pos_list[i]
    f = open(r"D:\click_mod\1.txt", "a")
    f.writelines(str(pos_log[0]) + ',' + str(pos_log[1]) + ',' + str(pos_log[2]) + ',' + str(pos_log[3]) + '\n')
