import base64
import os
import shlex
import subprocess
import sys
from os.path import abspath, dirname

import numpy as np
from cv2 import cv2


# command = "adb shell \"screencap -p | busybox base64\""
# pcommand = os.popen(command)
# png_screenshot_data = pcommand.read()
# png_screenshot_data = base64.b64decode(png_screenshot_data)
# pcommand.close()
# images = cv2.imdecode(np.frombuffer(png_screenshot_data, np.uint8), cv2.IMREAD_COLOR)
# cv2.imshow("", images)
# cv2.waitKey(0)
# cv2.destroyWindow("")

# command = r"adb shell screencap -p"
# proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
# out = proc.stdout.read(30000000)
# img = cv2.imdecode(np.frombuffer(out, np.uint8), cv2.IMREAD_COLOR)
# if img is not None:
#     cv2.imshow("", img)
#     cv2.waitKey(0)
#     cv2.destroyWindow("")

def adb_touch():
    # x, y = pos
    x = 540
    y = 1104
    # if mode == 0:  #adb点击
    # a = "adb shell input touchscreen tap {0} {1}".format(x, y)
    a = "adb shell input tap {0} {1}".format(x, y)
    os.system(a)


def adb_test():
    # if mode == 1:
    #     return
    raw_content = os.popen('adb devices').read()
    row_list = raw_content.split('List of devices attached\n')[0].split('\n')  # 下标需要为0？
    devices_list = [i for i in row_list if len(i) > 1]
    print(raw_content)
    devices_count = len(devices_list)
    if devices_count >= 1:
        print('adb连接设备数量为 ', devices_count)
    else:
        print('无设备连接')
        sys.exit(0)  # 脚本结束


def adb_screen():
    commend = subprocess.Popen("adb shell screencap -p",
                               stdin=subprocess.PIPE,
                               stdout=subprocess.PIPE, shell=True)
    img_bytes = commend.stdout.read().replace(b'\r\n', b'\n')
    scr_img = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    scr_img = cv2.cvtColor(scr_img, cv2.COLOR_RGB2BGRA)
    return scr_img


def save_screen_capture(scr_img):
    """保存内存中cv2格式的图片为本地文件"""
    filename = abspath(dirname(__file__)) + r'\screen_img\%s' % 'screen_pic.jpg'  # 截图的存储位置，程序路径里面
    scr_img = cv2.cvtColor(scr_img, cv2.COLOR_RGB2BGRA)  # 要保存必须还原颜色空间，否则会变色
    cv2.imwrite(filename, scr_img, [int(cv2.IMWRITE_JPEG_QUALITY), 20])  # 保存截图 质量（0-100）


def show_screen_capture(scr_img):
    """查看内存中cv2格式的图片"""
    scr_img = cv2.cvtColor(scr_img, cv2.COLOR_RGB2BGRA)  # 要保存必须还原颜色空间，否则会变色
    cv2.namedWindow('scr_img')  # 命名窗口
    cv2.imshow("scr_img", scr_img)  # 显示
    cv2.waitKey(0)
    cv2.destroyAllWindows()


adb_test()
image = adb_screen()
show_screen_capture(image)
save_screen_capture(image)
adb_touch()

# cv2.imshow("", image)
# cv2.waitKey(0)
# cv2.destroyWindow("")
