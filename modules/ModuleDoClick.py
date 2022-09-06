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
from modules.ModuleHandleSet import HandleSet
from modules.ModuleGetConfig import ReadConfigFile

rc = ReadConfigFile()
other_setting = rc.read_config_other_setting()


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
            px = random.randint(-click_deviation - 5, click_deviation + 5)  # 设置随机偏移范围，避免封号
            py = random.randint(-click_deviation - 5, click_deviation + 5)
            cx = int(px + pos[0])
            cy = int(py + pos[1])

            # 模拟鼠标指针 点击指定位置
            # 减去40是因为window这个框占用40单位的高度
            long_position = MAKELONG(cx, cy-40)
            SendMessage(handle_num, WM_ACTIVATE, WA_ACTIVE, 0)
            # SendMessage(handle_num, WM_LBUTTONDOWN, MK_LBUTTON, long_position)  # 模拟鼠标按下
            # sleep(0.05)
            # SendMessage(handle_num, WM_LBUTTONUP, MK_LBUTTON, long_position)  # 模拟鼠标弹起
            SendMessage(handle_num, WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
            sleep(0.05)
            SendMessage(handle_num, WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起

            print(f"<br>点击坐标: [ {cx} , {cy} ] <br>窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

            if other_setting[10]:  # 如果配置文件设置了额外随机点击
                # 以下代码模拟真实点击，怀疑痒痒鼠会记录点击坐标数据，然后AI判断是否规律（比如一段时间内，每次都总点某个按钮附近，不超过100像素，就有风险），
                # 如果只是随机延迟+坐标偏移，可能骗不过后台
                # 这里模拟正常点击偶尔会多点一次的情况，另外再增加混淆点击，使整体点击看起来不那么规律
                roll_num = random.randint(0, 99)  # roll 0-99，15%的几率触发混淆点击
                if roll_num < 10:  # 匹配坐标附近的，不偏移太远
                    sleep((random.randint(5, 15)) / 100)  # 随机延迟0.05-0.15秒
                    mx = random.randint(-50, 300) + cx
                    my = random.randint(-50, 300) + cy
                    SendMessage(handle_num, WM_LBUTTONDOWN, 0, MAKELONG(mx, my))  # 模拟鼠标按下
                    sleep(0.05)
                    SendMessage(handle_num, WM_LBUTTONUP, 0, MAKELONG(mx, my))  # 模拟鼠标弹起
                    print(f"<br>点击偏移坐标: [ {mx}, {my} ]")
                elif 47 < roll_num < 50 or roll_num > 97:  # 随机点击其他地方
                    sleep((random.randint(5, 15)) / 100)
                    mx = random.randint(200, 1000)
                    my = random.randint(200, 1000)
                    SendMessage(handle_num, WM_LBUTTONDOWN, 0, MAKELONG(mx, my))  # 模拟鼠标按下
                    sleep(0.05)
                    SendMessage(handle_num, WM_LBUTTONUP, 0, MAKELONG(mx, my))  # 模拟鼠标弹起
                    print(f"<br>点击偏移坐标: [ {mx}, {my} ]")

            return True

    def adb_click(self, device_id):
        """数据线连手机点击"""
        if self.pos is not None:
            pos = self.pos
            click_deviation = int(self.click_deviation)
            px = random.randint(-click_deviation - 5, click_deviation + 5)  # 设置随机偏移范围，避免封号
            py = random.randint(-click_deviation - 5, click_deviation + 5)
            cx = int(px + pos[0])
            cy = int(py + pos[1])
            # 使用modules下的adb工具执行adb命令
            command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {cx} {cy}'
            HandleSet.deal_cmd(command)
            # system(command)
            print(f"<br>点击设备 [ {device_id} ] 坐标: [ {cx} , {cy} ]")

            if other_setting[10]:  # 如果配置文件设置了额外随机点击
                roll_num = random.randint(0, 99)
                if roll_num < 10:
                    mx = random.randint(-50, 300) + cx
                    my = random.randint(-50, 300) + cy
                    sleep((random.randint(5, 15)) / 100)
                    command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {mx} {my}'
                    HandleSet.deal_cmd(command)
                    print(f"<br>点击设备 [ {device_id} ] 坐标: [ {mx} , {my} ]")
                elif 47 < roll_num < 50 or roll_num > 97:
                    mx = random.randint(200, 1000)
                    my = random.randint(200, 1000)
                    sleep((random.randint(5, 15)) / 100)
                    command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {mx} {my}'
                    HandleSet.deal_cmd(command)
                    print(f"<br>点击设备 [ {device_id} ] 坐标: [ {mx} , {my} ]")

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
        px = random.randint(-click_deviation - 5, click_deviation + 5)
        py = random.randint(-click_deviation - 5, click_deviation + 5)
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
        if other_setting[10]:  # 如果配置文件设置了额外随机点击
            roll_num = random.randint(0, 99)
            if roll_num < 10:
                sleep((random.randint(5, 15)) / 100)
                click(random.randint(-50, 300) + cx, random.randint(-50, 300) + cy)
            elif 47 < roll_num < 50 or roll_num > 97:
                sleep((random.randint(5, 15)) / 100)
                click(random.randint(200, 1000), random.randint(200, 1000))
        moveTo(now_pos[0], now_pos[1])

        print(f"<br>点击坐标: [ {cx} , {cy} ] 窗口名称: [ {HandleSet.get_handle_title(handle_num)} ]")

        return True
