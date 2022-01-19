"""
点击目标窗口的指定位置，可设置随机范围
"""
import os
import time
import random
import win32api
import win32con
from Module_HandleSet import HandleSet


class DoClick:
    """
    对象：坐标点、范围、句柄
    方法：点击、拖拽
    """

    def __init__(self, pos, move_var, handle_num=0):
        super(DoClick, self).__init__()
        self.move_var = move_var
        self.handle_num = handle_num
        self.pos = pos

    def do_click(self):
        """点击目标位置,可后台点击（兼容部分窗口程序）"""
        if self.pos is not None:
            pos = self.pos
            handle_num = self.handle_num
            move_var = int(self.move_var)
            px = random.randint(-move_var, move_var)  # 设置随机偏移范围，避免封号
            py = random.randint(-move_var, move_var)
            cx = px + pos[0]
            cy = py + pos[1]

            long_position = win32api.MAKELONG(cx, cy)  # 模拟鼠标指针 传送到指定坐标
            win32api.SendMessage(handle_num, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, long_position)  # 模拟鼠标按下
            time.sleep(0.05)
            win32api.SendMessage(handle_num, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, long_position)  # 模拟鼠标弹起

            print("点击坐标：[", cx, cy, "]", "[", HandleSet.get_handle_title(handle_num), "]")

    def adb_click(self):
        """数据线连手机点击"""
        if self.pos is not None:
            # HandleSet.adb_test()
            pos = self.pos
            move_var = int(self.move_var)
            px = random.randint(-move_var, move_var)  # 设置随机偏移范围，避免封号
            py = random.randint(-move_var, move_var)
            cx = px + pos[0]
            cy = py + pos[1]
            a = "adb shell input tap {0} {1}".format(cx, cy)
            os.system(a)
            print("点击坐标：[", cx, cy, "]")
