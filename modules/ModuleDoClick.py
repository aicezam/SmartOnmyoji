# -*- coding: utf-8 -*-
from os import system
from time import sleep
from random import randint
from win32gui import SetForegroundWindow, GetWindowRect
from win32api import MAKELONG, SendMessage
from win32con import WM_LBUTTONUP, MK_LBUTTON, WM_LBUTTONDOWN
from pymouse import PyMouse
from modules.ModuleHandleSet import HandleSet


class DoClick:
    def __init__(self, pos, move_var, handle_num=0):
        super(DoClick, self).__init__()
        self.move_var = move_var
        self.handle_num = handle_num
        self.pos = pos

    def windows_click(self):
        """点击目标位置,可后台点击（兼容部分窗口程序）"""
        if self.pos is not None:
            pos = self.pos
            handle_num = self.handle_num
            move_var = int(self.move_var)
            px = randint(-move_var, move_var)  # 设置随机偏移范围，避免封号
            py = randint(-move_var, move_var)
            cx = int(px + pos[0])
            cy = int(py + pos[1])

            long_position = MAKELONG(cx, cy)  # 模拟鼠标指针 传送到指定坐标
            SendMessage(handle_num, WM_LBUTTONDOWN, MK_LBUTTON, long_position)  # 模拟鼠标按下
            sleep(0.05)
            SendMessage(handle_num, WM_LBUTTONUP, MK_LBUTTON, long_position)  # 模拟鼠标弹起

            print(f"点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

    def adb_click(self):
        """数据线连手机点击"""
        if self.pos is not None:
            # HandleSet.adb_test()
            pos = self.pos
            move_var = int(self.move_var)
            px = randint(-move_var, move_var)  # 设置随机偏移范围，避免封号
            py = randint(-move_var, move_var)
            cx = int(px + pos[0])
            cy = int(py + pos[1])
            a = "adb shell input tap {0} {1}".format(cx, cy)
            system(a)
            print(f"点击坐标: [ {cx} , {cy} ]")

    def windows_click_bk(self):
        # 前台点击，窗口必须置顶，兼容所有窗口（模拟器、云游戏等）点击
        pos = self.pos
        handle_num = self.handle_num
        move_var = int(self.move_var)
        x1, y1, x2, y2 = GetWindowRect(handle_num)

        # 设置随机偏移范围，避免封号
        px = randint(-move_var, move_var)
        py = randint(-move_var, move_var)
        cx = int(px + pos[0])
        cy = int(py + pos[1])

        # 计算绝对坐标位置
        jx = cx + x1
        jy = cy + y1

        # 把窗口置顶，并进行点击
        SetForegroundWindow(handle_num)
        m = PyMouse()
        now_loc = PyMouse()
        now_pos = now_loc.position()  # 获取鼠标当前位置
        m.move(jx, jy)  # 鼠标移至目标
        m.press(jx, jy, button=1)  # 按下
        sleep(0.1)
        m.release(jx, jy, button=1)  # 松开
        sleep(0.05)

        m.move(now_pos[0], now_pos[1])  # 把鼠标移回之前的位置

        print(f"点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")
