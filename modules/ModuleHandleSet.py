# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import winsound
from os import system
from re import search
from os.path import abspath, dirname
from subprocess import Popen, PIPE
from time import sleep

from win32api import OpenProcess
from win32con import PROCESS_ALL_ACCESS
from win32gui import GetWindowText, FindWindow, FindWindowEx, GetWindowRect, GetForegroundWindow
from win32process import NORMAL_PRIORITY_CLASS, REALTIME_PRIORITY_CLASS, SetPriorityClass, IDLE_PRIORITY_CLASS, \
    HIGH_PRIORITY_CLASS, GetWindowThreadProcessId, BELOW_NORMAL_PRIORITY_CLASS, ABOVE_NORMAL_PRIORITY_CLASS

from modules.ModuleGetConfig import ReadConfigFile


class HandleSet:
    def __init__(self, handle_title, handle_num):
        super(HandleSet, self).__init__()
        self.handle_pos = None
        self.handle_title = handle_title
        self.handle_num = int(handle_num)
        self.handle_pid = None
        set_config = ReadConfigFile()  # 读取配置文件
        self.other_setting = set_config.read_config_other_setting()

    @property
    def get_handle_num(self):
        """通过句柄标题获取句柄编号"""
        # 如果编号不为0或者标题为空，说明是设置的多开，此时直接校验编号即可
        if self.handle_num != 0 or self.handle_title == '':
            if search("雷电模拟器", self.get_handle_title(self.handle_num)):
                self.handle_num = FindWindowEx(self.handle_num, None, None, "TheRender")  # 兼容雷电模拟器后台点击
                return None if self.handle_num == 0 else self.handle_num
            else:
                return self.handle_num
        else:
            # 其他情况，说明设置的单开，此时需要通过标题名称来获取编号，再对编号进行校验
            self.handle_num = FindWindow(None, self.handle_title)  # 搜索句柄标题，获取句柄编号
            if search("雷电模拟器", self.handle_title):
                self.handle_num = FindWindowEx(self.handle_num, None, None, "TheRender")  # 兼容雷电模拟器后台点击
                return None if self.handle_num == 0 else self.handle_num
            else:
                return None if self.handle_num == 0 else self.handle_num

    @staticmethod
    def get_handle_title(handle_num=None):
        """
        通过句柄编号获取句柄标题
        :param handle_num: 句柄编号
        :returns: 句柄标题
        """
        return None if handle_num is None or handle_num == 0 or handle_num == '' else GetWindowText(handle_num)
        # if handle_num is None or handle_num == 0 or handle_num == '':
        #     return None
        # else:
        #     handle_title = GetWindowText(handle_num)  # 获取句柄标题
        #     return handle_title

    @property
    def get_handle_pid(self):
        """通过句柄标题获取句柄进程id"""
        self.handle_pid = GetWindowThreadProcessId(self.get_handle_num)  # 获取进程Pid
        return self.handle_pid[1]

    @property
    def get_handle_pos(self):
        """
        获取句柄的坐标
        :returns: 坐标，左上角（x1，y1），右下角（x2，y2）
        """
        return None if self.get_handle_num is None else GetWindowRect(self.get_handle_num)
        # if self.get_handle_num is None:
        #     return None
        # else:
        #     self.handle_pos = GetWindowRect(self.get_handle_num)
        #     return self.handle_pos

    def handle_is_active(self, process_num):
        """检测句柄是否停止"""
        if self.handle_num != 0 and process_num == '多开':  # 多开时，通过编号找标题是否存在
            if self.get_handle_title(self.handle_num) == '':
                if self.other_setting[7]:
                    self.play_sounds("warming")  # 播放提示音
                return False
            else:
                return True
        elif self.handle_title != '' and process_num == '单开':  # 单开时，通过标题找编号是否存在
            if self.get_handle_num is None:
                if self.other_setting[7]:
                    self.play_sounds("warming")  # 播放提示音
                return False
            else:
                return True

    def set_priority_bk(self):
        """尝试用自带的wmic设置优先级，但，已被弃用"""
        system("wmic process where name=\"onmyoji.exe\" CALL setpriority 128")

    def set_priority(self, priority=4):
        """
        设置程序的优先级,需要管理员模式运行
        :param priority: 0-5,(0-最低，5-最高)
        """
        pid = self.get_handle_pid
        priority_classes = [IDLE_PRIORITY_CLASS,
                            BELOW_NORMAL_PRIORITY_CLASS,
                            NORMAL_PRIORITY_CLASS,
                            ABOVE_NORMAL_PRIORITY_CLASS,
                            HIGH_PRIORITY_CLASS,
                            REALTIME_PRIORITY_CLASS]

        # print(pid)
        handle = OpenProcess(PROCESS_ALL_ACCESS, True, pid)
        SetPriorityClass(handle, priority_classes[priority])

        handle_title = self.get_handle_title(self.get_handle_num)
        priority_name = None
        if priority == 0:
            priority_name = "最低"
        if priority == 1:
            priority_name = "低于正常"
        if priority == 2:
            priority_name = "正常"
        if priority == 3:
            priority_name = "高于正常"
        if priority == 4:
            priority_name = "高"
        if priority == 5:
            priority_name = "最高"
        print(f"<br>已设置进程 [{handle_title} {self.handle_num}] 的优先级为 [{priority_name}] ")
        print("<br>-----------------------------")

    @staticmethod
    def deal_cmd(cmd):
        """执行cmd命令"""
        pi = Popen(cmd, shell=True, stdout=PIPE)
        return pi.stdout.read()

    @staticmethod
    def adb_device_status():
        """检测设备是否在线，如果在线返回True和在线设备列表，不在线则返回False和异常信息"""
        try:
            # HandleSet.deal_cmd(abspath(dirname(__file__)) + r'\adb.exe kill-server')
            command = abspath(dirname(__file__)) + r'\adb.exe devices'  # adb放在modules目录下，不用那么麻烦安装adb命令了
            # result = HandleSet.deal_cmd('adb devices')
            # command = abspath(dirname(__file__)) + r'\adb.exe connect 127.0.0.1:7555'
            result = HandleSet.deal_cmd(command)
            result = result.decode("utf-8")
            if result.startswith('List of devices attached'):
                # 查看连接设备
                result = result.strip().splitlines()
                # 查看连接设备数量
                device_size = len(result)
                if device_size > 1:
                    device_list = []
                    for i in range(1, device_size):
                        device_detail = result[1].split('\t')
                        if device_detail[1] == 'device':
                            device_list.append(device_detail[0])
                        elif device_detail[1] == 'offline':
                            print(device_detail[0])
                            return False, '<br>连接出现异常，设备无响应'
                        elif device_detail[1] == 'unknown':
                            print(device_detail[0])
                            return False, '<br>设备不在线，请重新连接，或打开安卓调试模式'
                    return True, device_list
                else:
                    return False, "<br>设备不在线，请重新连接，或打开安卓调试模式"
        except:
            return False, '<br>连接出现异常，或设备无响应'

    @staticmethod
    def get_active_window(loop_times=5):
        """
        点击鼠标获取目标窗口句柄
        :param loop_times: 倒计时/循环次数
        :return: 窗体标题名称
        """
        hand_num = ""
        hand_win_title = ""
        for t in range(loop_times):
            print(f'<br>请在倒计时 [ {loop_times} ] 秒结束前，点击目标窗口')
            loop_times -= 1
            hand_num = GetForegroundWindow()
            hand_win_title = GetWindowText(hand_num)
            print(f"<br>目标窗口： [ {hand_win_title} ] [ {hand_num} ] ")
            sleep(1)  # 每1s输出一次
        left, top, right, bottom = GetWindowRect(hand_num)
        print("<br>-----------------------------------------------------------")
        print(f"<br>目标窗口: [ {hand_win_title} ] 窗口大小：[ {right - left} X {bottom - top} ]")
        print("<br>-----------------------------------------------------------")
        return hand_win_title, hand_num

    @staticmethod
    def play_sounds(flag):
        """播放声音"""
        if flag == "warming":
            sound = abspath(dirname(__file__)) + r'\sounds\\warming.wav'
            winsound.PlaySound(sound, winsound.SND_ALIAS)
        elif flag == "end":
            sound = abspath(dirname(__file__)) + r'\sounds\\end.wav'
            winsound.PlaySound(sound, winsound.SND_ALIAS)
