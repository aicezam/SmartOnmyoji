# -*- coding: utf-8 -*-
import os
import time
import random
import win32api
import win32con
# import win32gui
# import pyautogui
# from pymouse import PyMouse
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
            px = random.randint(-move_var, move_var)  # 设置随机偏移范围，避免封号
            py = random.randint(-move_var, move_var)
            cx = int(px + pos[0])
            cy = int(py + pos[1])

            long_position = win32api.MAKELONG(cx, cy)  # 模拟鼠标指针 传送到指定坐标
            win32api.SendMessage(handle_num, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)  # 模拟鼠标按下
            time.sleep(0.05)
            win32api.SendMessage(handle_num, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)  # 模拟鼠标弹起

            print(f"点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

    def adb_click(self):
        """数据线连手机点击"""
        if self.pos is not None:
            # HandleSet.adb_test()
            pos = self.pos
            move_var = int(self.move_var)
            px = random.randint(-move_var, move_var)  # 设置随机偏移范围，避免封号
            py = random.randint(-move_var, move_var)
            cx = int(px + pos[0])
            cy = int(py + pos[1])
            a = "adb shell input tap {0} {1}".format(cx, cy)
            os.system(a)
            print(f"点击坐标: [ {cx} , {cy} ]")

    # def do_click_foreground(self):
    #     # 前台点击，窗口必须置顶，必须放左上角，兼容所有窗口（模拟器、手机同步等）点击
    #     pos = self.pos
    #     move_var = int(self.move_var)
    #     handle_num = self.handle_num
    #     px = random.randint(-move_var, move_var)  # 设置随机偏移范围，避免封号
    #     py = random.randint(-move_var, move_var)
    #     cx = int(px + pos[0])
    #     cy = int(py + pos[1])
    #     win32gui.SetForegroundWindow(handle_num)
    #     m = PyMouse()
    #     now_loc = PyMouse()
    #     now_pos = now_loc.position()  # 获取鼠标当前位置
    #     m.move(cx, cy)  # 鼠标移至目标
    #     m.click(cx, cy)  # 鼠标点击目标
    #     m.move(now_pos[0], now_pos[1])  # 移回上个位置
    #
    #     print(f"点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")
    #
    # def do_drag(self):
    #     # 拖拽目标 横向拖动
    #     pos = self.pos
    #     move_var = int(self.move_var)
    #     handle_num = self.handle_num
    #     t = 0.5
    #     win32gui.SetForegroundWindow(handle_num)
    #     pyautogui.dragRel(pos[0], pos[0] + 20, duration=t)
