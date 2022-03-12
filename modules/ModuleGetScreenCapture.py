# -*- coding: utf-8 -*-
from subprocess import Popen, PIPE
from numpy import frombuffer, uint8, array
from win32con import SRCCOPY
from win32gui import DeleteObject, SetForegroundWindow, GetWindowRect, GetWindowDC
from win32ui import CreateDCFromHandle, CreateBitmap
from cv2 import cv2
from PIL import ImageGrab


class GetScreenCapture:
    def __init__(self, handle_num=0, handle_width=0, handle_height=0):
        super(GetScreenCapture, self).__init__()
        self.hwd_num = handle_num
        self.screen_width = handle_width
        self.screen_height = handle_height

    def window_screen(self):
        """windows api 窗体截图方法，可后台截图，可被遮挡，不兼容部分窗口"""
        hwnd = self.hwd_num
        screen_width = self.screen_width
        screen_height = self.screen_height

        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        hwnd_dc = GetWindowDC(hwnd)
        # 创建设备描述表
        mfc_dc = CreateDCFromHandle(hwnd_dc)
        # 创建内存设备描述表
        save_dc = mfc_dc.CreateCompatibleDC()
        # 创建位图对象准备保存图片
        save_bit_map = CreateBitmap()
        # 为bitmap开辟存储空间
        save_bit_map.CreateCompatibleBitmap(mfc_dc, screen_width, screen_height)
        # 将截图保存到saveBitMap中
        save_dc.SelectObject(save_bit_map)
        # 保存bitmap到内存设备描述表
        save_dc.BitBlt((0, 0), (screen_width, screen_height), mfc_dc, (0, 0), SRCCOPY)

        # 保存图像
        signed_ints_array = save_bit_map.GetBitmapBits(True)
        im_opencv = frombuffer(signed_ints_array, dtype='uint8')
        im_opencv.shape = (screen_height, screen_width, 4)
        im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2GRAY)
        # im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2BGR)
        print("截图成功！")

        # 测试显示截图图片
        # cv2.namedWindow('scr_img')  # 命名窗口
        # cv2.imshow("scr_img", im_opencv)  # 显示
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # 内存释放
        DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        return im_opencv

    def window_screen_bk(self):
        """PIL截图方法，不能被遮挡"""
        SetForegroundWindow(self.hwd_num)  # 自动置顶
        x1, y1, x2, y2 = GetWindowRect(self.hwd_num)  # 获取窗口坐标
        grab_image = ImageGrab.grab((x1, y1, x2, y2))  # 用PIL方法截图
        im_cv2 = array(grab_image)  # 转换为cv2的矩阵格式
        im_opencv = cv2.cvtColor(im_cv2, cv2.COLOR_BGRA2GRAY)

        # 测试显示截图图片
        # cv2.namedWindow('scr_img')  # 命名窗口
        # cv2.imshow("scr_img", im_opencv)  # 显示
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        return im_opencv

    @staticmethod
    def adb_screen():
        """安卓手机adb截图"""
        commend = Popen("adb shell screencap -p",
                        stdin=PIPE,
                        stdout=PIPE,
                        shell=True)  # 截图
        img_bytes = commend.stdout.read().replace(b'\r\n', b'\n')  # 传输
        scr_img = cv2.imdecode(frombuffer(img_bytes, uint8), cv2.IMREAD_COLOR)  # 转格式
        scr_img = cv2.cvtColor(scr_img, cv2.COLOR_BGRA2GRAY)
        print("截图成功！")
        return scr_img
