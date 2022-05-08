# -*- coding: utf-8 -*-
from os import system
from os.path import abspath, dirname
from time import sleep
from random import randint
import win32com.client
from win32gui import SetForegroundWindow, GetWindowRect
from win32api import MAKELONG, SendMessage, mouse_event, SetCursorPos
from win32con import WM_LBUTTONUP, MK_LBUTTON, WM_LBUTTONDOWN, WM_ACTIVATE, WA_ACTIVE, MOUSEEVENTF_LEFTUP, \
    MOUSEEVENTF_LEFTDOWN
from pyautogui import position, click, moveTo
from modules.ModuleHandleSet import HandleSet


class DoClick:
    def __init__(self, pos, click_deviation, handle_num=0):
        super(DoClick, self).__init__()
        self.click_deviation = click_deviation
        self.handle_num = handle_num
        self.pos = pos

    def windows_click(self):
        """
        点击目标位置,可后台点击（仅兼容部分窗体程序）
        """
        if self.pos is not None:
            pos = self.pos
            handle_num = self.handle_num
            click_deviation = int(self.click_deviation)
            px = randint(-click_deviation - 5, click_deviation + 5)  # 设置随机偏移范围，避免封号
            py = randint(-click_deviation - 5, click_deviation + 5)
            cx = int(px + pos[0])
            cy = int(py + pos[1])

            # 模拟鼠标指针 点击指定位置
            long_position = MAKELONG(cx, cy)
            SendMessage(handle_num, WM_ACTIVATE, WA_ACTIVE, 0)
            # SendMessage(handle_num, WM_LBUTTONDOWN, MK_LBUTTON, long_position)  # 模拟鼠标按下
            # sleep(0.05)
            # SendMessage(handle_num, WM_LBUTTONUP, MK_LBUTTON, long_position)  # 模拟鼠标弹起
            SendMessage(handle_num, WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
            sleep(0.05)
            SendMessage(handle_num, WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起

            print(f"<br>点击坐标: [ {cx} , {cy} ] <br>窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

            return True

    def adb_click(self):
        """数据线连手机点击"""
        if self.pos is not None:
            pos = self.pos
            click_deviation = int(self.click_deviation)
            px = randint(-click_deviation - 5, click_deviation + 5)  # 设置随机偏移范围，避免封号
            py = randint(-click_deviation - 5, click_deviation + 5)
            cx = int(px + pos[0])
            cy = int(py + pos[1])
            # 使用modules下的adb工具执行adb命令
            command = abspath(dirname(__file__)) + r'\adb.exe shell input tap {0} {1}'.format(cx, cy)
            # command = "adb shell input tap {0} {1}".format(cx, cy)
            system(command)
            print(f"<br>点击坐标: [ {cx} , {cy} ]")

            return True

    def windows_click_bk(self):
        """
        点击目标位置,只能前台点击（兼容所有窗体程序）
        """
        # 前台点击，窗口必须置顶，兼容所有窗口（模拟器、云游戏等）点击
        pos = self.pos
        handle_num = self.handle_num
        click_deviation = int(self.click_deviation)
        x1, y1, x2, y2 = GetWindowRect(handle_num)

        # 设置随机偏移范围，避免封号
        px = randint(-click_deviation - 5, click_deviation + 5)
        py = randint(-click_deviation - 5, click_deviation + 5)
        cx = int(px + pos[0])
        cy = int(py + pos[1])

        # 计算绝对坐标位置
        jx = cx + x1
        jy = cy + y1

        # 把窗口置顶，并进行点击
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        SetForegroundWindow(handle_num)
        sleep(0.2)  # 置顶后等0.2秒再点击
        now_pos = position()
        moveTo(jx, jy)  # 鼠标移至目标
        click(jx, jy)
        moveTo(now_pos[0], now_pos[1])

        print(f"<br>点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

        return True
