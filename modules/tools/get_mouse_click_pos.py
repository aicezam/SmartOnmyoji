# -*- coding:utf-8 -*-
import sys
import time
from ctypes import windll

from pynput.mouse import Listener
from win32gui import GetWindowText, GetForegroundWindow


def on_move(x, y):
    # 监听鼠标移动
    print('Pointer moved to {0}'.format((x, y)))


def on_click(x, y, button, pressed):
    # 监听鼠标点击
    log_now_time = time.strftime('%y-%m-%d %H:%M:%S', time.localtime(time.time()))
    log_name = "mouse_click"

    if pressed:
        active_win_title = GetWindowText(GetForegroundWindow())
        if active_win_title == "阴阳师-网易游戏" and x < 1200 and y < 750:
            print(log_now_time, "点击：", x, y)
            # elif not pressed:
            #     print("抬起：", x, y)

            # 点击位置写入txt文件
            x_str = str(x)
            y_str = str(y)

            f = open(r"\click_pos.log", "a+")
            if x < 1200 and y < 750:
                f.writelines(log_now_time + ',' + log_name + ',' + x_str + ',' + y_str + '\n')
        else:
            print("未激活阴阳师桌面版窗口！")


def on_scroll(x, y, dx, dy):
    # 监听鼠标滚轮
    print('Scrolled {0}'.format((x, y)))


# 连接事件以及释放
# with Listener(on_move=on_move, on_click=on_click, on_scroll=on_scroll) as listener:
#     listener.join()

# with Listener(on_click=on_click) as listener:
#     listener.join()

if __name__ == '__main__':
    if windll.shell32.IsUserAnAdmin():  # 是否以管理员身份运行
        print("请打开阴阳师桌面版并置于左上角！")
        with Listener(on_click=on_click) as listener:  # 监听点击事件
            listener.join()
    else:
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  # 调起UAC以管理员身份重新执行
        sys.exit(0)
