# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from os.path import abspath, dirname
from time import sleep
import random
import win32com.client
from win32gui import SetForegroundWindow, GetWindowRect
from win32api import MAKELONG, SendMessage
from win32con import WM_LBUTTONUP, WM_LBUTTONDOWN, WM_ACTIVATE, WA_ACTIVE
from pyautogui import position, click, moveTo

from modules.ModuleClickModSet import ClickModSet
from modules.ModuleHandleSet import HandleSet
from modules.ModuleGetConfig import ReadConfigFile


class DoClick:
    def __init__(self, pos, click_mod, handle_num=0):
        super(DoClick, self).__init__()
        self.click_mod = click_mod
        self.handle_num = handle_num
        self.pos = pos
        rc = ReadConfigFile()
        other_setting = rc.read_config_other_setting()
        self.ex_click_probability = float(other_setting[10])  # 从配置文件读取是否有设置额外偏移点击概率

    def windows_click(self):
        """
        点击目标位置,可后台点击（仅兼容部分窗体程序）
        """
        if self.pos is not None:
            pos = self.pos
            click_pos_list = []
            x1, y1, x2, y2 = GetWindowRect(self.handle_num)
            width = int(x2 - x1)
            height = int(y2 - y1)

            px, py = self.get_p_pos(self.click_mod, width, height, pos)

            cx = int(px + pos[0])
            cy = int(py + pos[1]) - 40  # 减去40是因为window这个框占用40单位的高度

            # 模拟鼠标指针 点击指定位置
            long_position = MAKELONG(cx, cy)
            SendMessage(self.handle_num, WM_ACTIVATE, WA_ACTIVE, 0)
            SendMessage(self.handle_num, WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
            sleep((random.randint(5, 15)) / 100)  # 点击弹起改为随机
            SendMessage(self.handle_num, WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起

            print(f"<br>点击坐标: [ {cx} , {cy} ] <br>窗口名称: [ {HandleSet.get_handle_title(self.handle_num)} ]")

            click_pos_list.append([cx, cy])

            # 模拟真实点击、混淆点击热区
            if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
                ex_pos = self.get_ex_click_pos(self.ex_click_probability, width, height, [cx, cy], px, py)
                if ex_pos is not None:
                    sleep((random.randint(5, 15)) / 100)  # 点击弹起改为随机
                    long_position = MAKELONG(ex_pos[0], ex_pos[1])
                    SendMessage(self.handle_num, WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
                    sleep((random.randint(5, 15)) / 100)  # 点击弹起改为随机
                    SendMessage(self.handle_num, WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起
                    print(f"<br>点击偏移坐标: [ {ex_pos[0]}, {ex_pos[1]} ]")
                    click_pos_list.append([ex_pos[0], ex_pos[1]])

            return True, click_pos_list

    def adb_click(self, device_id):
        """数据线连手机点击"""
        if self.pos is not None:
            click_pos_list = []
            pos = self.pos
            screen_size = HandleSet.get_screen_size(device_id)
            height = int(screen_size[0])
            width = int(screen_size[1])

            px, py = self.get_p_pos(self.click_mod, width, height, pos)

            cx = int(px + pos[0])
            cy = int(py + pos[1])

            # 使用modules下的adb工具执行adb命令
            command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {cx} {cy}'
            HandleSet.deal_cmd(command)
            # system(command)
            print(f"<br>点击设备 [ {device_id} ] 坐标: [ {cx} , {cy} ]")
            click_pos_list.append([cx, cy])

            # 模拟真实点击、混淆点击热区
            if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
                ex_pos = self.get_ex_click_pos(self.ex_click_probability, width, height, [cx, cy], px, py)
                if ex_pos is not None:
                    sleep((random.randint(5, 15)) / 100)  # 点击弹起改为随机
                    command = abspath(
                        dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {ex_pos[0]} {ex_pos[1]}'
                    HandleSet.deal_cmd(command)
                    print(f"<br>点击设备 [ {device_id} ] 额外偏移坐标: [ {ex_pos[0]} {ex_pos[1]} ]")
                    click_pos_list.append([ex_pos[0], ex_pos[1]])

            return True, click_pos_list

    def windows_click_bk(self):
        """
        点击目标位置,只能前台点击（兼容所有窗体程序）
        """
        # 前台点击，窗口必须置顶，兼容所有窗口（模拟器、云游戏等）点击
        click_pos_list = []
        pos = self.pos
        x1, y1, x2, y2 = GetWindowRect(self.handle_num)

        width = int(x2 - x1)
        height = int(y2 - y1)

        px, py = self.get_p_pos(self.click_mod, width, height, pos)

        # 设置随机偏移范围，避免封号
        cx = int(px + pos[0])
        cy = int(py + pos[1]) - 40  # 减去40是因为window这个框占用40单位的高度

        # 计算绝对坐标位置
        jx = cx + x1
        jy = cy + y1

        # 把窗口置顶，并进行点击
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        SetForegroundWindow(self.handle_num)
        sleep(0.2)  # 置顶后等0.2秒再点击
        now_pos = position()
        moveTo(jx, jy)  # 鼠标移至目标
        click(jx, jy)
        print(f"<br>点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(self.handle_num)} ]")
        click_pos_list.append([cx, cy])

        # 模拟真实点击、混淆点击热区
        if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
            ex_pos = self.get_ex_click_pos(self.ex_click_probability, width, height, [jx, jy], px, py)
            if ex_pos is not None:
                sleep((random.randint(5, 15)) / 100)  # 点击弹起改为随机
                click(ex_pos[0], ex_pos[1])
                print(f"<br>点击偏移坐标: [ {ex_pos[0]}, {ex_pos[1]} ]")
                click_pos_list.append([ex_pos[0], ex_pos[1]])

        moveTo(now_pos[0], now_pos[1])

        return True, click_pos_list

    @staticmethod
    def get_ex_click_pos(ex_click_probability, width, height, old_pos, px, py):
        """获取额外点击的偏移坐标"""
        roll_num = random.randint(0, 999)
        if roll_num < ex_click_probability * 0.1 * 1000:
            x = old_pos[0]
            y = old_pos[1]
            return x, y
        elif ex_click_probability * 0.3 * 1000 < roll_num < ex_click_probability * 0.6 * 1000:
            x = int(width * 0.618 + px)
            y = int(height * 0.618 + py)
            return x, y
        elif ex_click_probability * 0.6 * 1000 < roll_num < ex_click_probability * 0.9 * 1000:
            x = int(random.randint(100, width))
            y = int(random.randint(100, height))
            return x, y
        else:
            return None

    @staticmethod
    def get_p_pos_4grid(click_mod, width, height, pos):
        """获取模型中的偏移坐标（4宫格）"""
        # 从原始模型中抽取一个坐标，根据在窗口中的相对位置，进行旋转
        p_pos = ClickModSet.choice_mod_pos(click_mod)
        if pos[0] < width * 0.618 and pos[1] < height * 0.618:
            # 如果需要点击的位置位于窗口左上，则坐标顺时针旋转180度
            px, py = ClickModSet.pos_rotate(p_pos, 180)
        elif pos[0] < width * 0.618 and pos[1] > height * 0.618:
            # 如果需要点击的位置位于窗口左下，则坐标顺时针旋转90度
            px, py = ClickModSet.pos_rotate(p_pos, 90)
        elif pos[0] > width * 0.618 and pos[1] < height * 0.618:
            # 如果需要点击的位置位于窗口右上，则坐标顺时针旋转270度
            px, py = ClickModSet.pos_rotate(p_pos, 270)
        else:
            # 如果需要点击的位置位于窗口右上或其他情况，则坐标不变
            px, py = p_pos

        return px, py
    
    @staticmethod
    def get_p_pos(click_mod, width, height, pos):
        """获取模型中的偏移坐标（九宫格）"""

        # 以窗口中偏下（0.618）的位置为中心，旋转得到的坐标，抽取模型中的一个点并进行旋转
        # 得到的结果会根据原始坐标在窗口中的相对位置，形成一个与点击模型点击分布类似，但缩放方向不同的集合
        x1 = 0.382 * width
        x2 = 0.618 * width
        x3 = width
        y1 = 0.382 * height
        y2 = 0.618 * height
        y3 = height
        x = pos[0]
        y = pos[1]

        p_pos = ClickModSet.choice_mod_pos(click_mod)

        if x <= x1 and y <= y1:
            # 左上
            px, py = ClickModSet.pos_rotate(p_pos, 180)
        elif x <= x1 and y1 < y <= y2:
            # 左中
            px, py = ClickModSet.pos_rotate(p_pos, 135)
        elif x <= x1 and y2 < y <= y3:
            # 左下
            px, py = ClickModSet.pos_rotate(p_pos, 90)
        elif x1 < x <= x2 and y <= y1:
            # 中上
            px, py = ClickModSet.pos_rotate(p_pos, 225)
        elif x1 < x <= x2 and y1 < y <= y2:
            # 中中，这个位置与左上一样处理
            px, py = ClickModSet.pos_rotate(p_pos, 180)
        elif x1 < x <= x2 and y2 < y <= y3:
            # 中下
            px, py = ClickModSet.pos_rotate(p_pos, 45)
        elif x2 < x <= x3 and y <= y1:
            # 右上
            px, py = ClickModSet.pos_rotate(p_pos, 270)
        elif x2 < x <= x3 and y1 < y <= y2:
            # 右中
            px, py = ClickModSet.pos_rotate(p_pos, 315)
        else:
            # 右下或其他情况
            px = p_pos[0]
            py = p_pos[1]

        py = int(py * 0.888)  # 让偏移结果再扁平一点

        return px, py
