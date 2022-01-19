import subprocess
from os.path import abspath, dirname
import numpy
import numpy as np
import win32con
import win32gui
import win32ui
from cv2 import cv2


class GetScreenCapture:
    def __init__(self, handle_num=0, handle_width=0, handle_height=0, compress_val=0.5):
        super(GetScreenCapture, self).__init__()
        self.hwd_num = handle_num
        self.screen_width = handle_width
        self.screen_height = handle_height
        self.compress_val = compress_val

    def screen_capture(self):
        """截图函数"""
        hwnd = self.hwd_num
        screen_width = self.screen_width
        screen_height = self.screen_height
        compress_val = self.compress_val

        # 返回句柄窗口的设备环境，覆盖整个窗口，包括非客户区，标题栏，菜单，边框
        hwnd_dc = win32gui.GetWindowDC(hwnd)
        # 创建设备描述表
        mfc_dc = win32ui.CreateDCFromHandle(hwnd_dc)
        # 创建内存设备描述表
        save_dc = mfc_dc.CreateCompatibleDC()
        # 创建位图对象准备保存图片
        save_bit_map = win32ui.CreateBitmap()
        # 为bitmap开辟存储空间
        save_bit_map.CreateCompatibleBitmap(mfc_dc, screen_width, screen_height)
        # 将截图保存到saveBitMap中
        save_dc.SelectObject(save_bit_map)
        # 保存bitmap到内存设备描述表
        save_dc.BitBlt((0, 0), (screen_width, screen_height), mfc_dc, (0, 0), win32con.SRCCOPY)

        # 保存图像
        signed_ints_array = save_bit_map.GetBitmapBits(True)
        im_opencv = numpy.frombuffer(signed_ints_array, dtype='uint8')
        im_opencv.shape = (screen_height, screen_width, 4)
        im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGR2GRAY)  # 转灰度图片
        height, width = im_opencv.shape[:2]
        # 压缩图片,压缩率compress_val
        size = (int(width * compress_val), int(height * compress_val))
        im_opencv = cv2.resize(im_opencv, size, interpolation=cv2.INTER_AREA)
        print("截图成功！")
        # 内存释放
        win32gui.DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        return im_opencv

    @staticmethod
    def adb_screen(compress_val=0.5):
        commend = subprocess.Popen("adb shell screencap -p", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)  # 截图
        img_bytes = commend.stdout.read().replace(b'\r\n', b'\n')  # 传输
        scr_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)  # 转格式
        scr_img = cv2.cvtColor(scr_img, cv2.COLOR_BGR2GRAY)  # 转灰度
        height, width = scr_img.shape[:2]
        # 压缩图片,压缩率compress_val
        size = (int(width * compress_val), int(height * compress_val))
        scr_img = cv2.resize(scr_img, size, interpolation=cv2.INTER_AREA)
        print("截图成功！")
        return scr_img

    @staticmethod
    def save_screen_capture(scr_img):
        """保存内存中cv2格式的图片为本地文件"""
        filename = abspath(dirname(__file__)) + r'\screen_img\%s' % 'screen_pic.jpg'  # 截图的存储位置，程序路径里面
        # scr_img = cv2.cvtColor(scr_img, cv2.COLOR_RGB2BGRA)  # 要保存必须还原颜色空间，否则会变色
        cv2.imwrite(filename, scr_img, [int(cv2.IMWRITE_JPEG_QUALITY), 20])  # 保存截图 质量（0-100）

    @staticmethod
    def show_screen_capture(scr_img):
        """查看内存中cv2格式的图片"""
        # scr_img = cv2.cvtColor(scr_img, cv2.COLOR_RGB2BGRA)  # 要保存必须还原颜色空间，否则会变色
        cv2.namedWindow('scr_img')  # 命名窗口
        cv2.imshow("scr_img", scr_img)  # 显示
        cv2.waitKey(0)
        cv2.destroyAllWindows()
