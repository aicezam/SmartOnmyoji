# import time
# import win32gui
from HandleSet import HandleSet
from AutoClick import get_active_window


# def get_active_window(loop_times):
#     """点击鼠标获取目标窗口句柄"""
#     # loop_times = 10  # 倒计时10秒
#     # hand_win = ""
#     hand_win_title = ""
#     for t in range(loop_times):
#         print('请在倒计时%d秒结束前，点击目标窗口' % loop_times)
#         loop_times -= 1
#         hand_win = win32gui.GetForegroundWindow()
#         hand_win_title = win32gui.GetWindowText(hand_win)
#         print(f"目标窗口：[{hand_win_title}], [{hand_win}]")
#         # print("目标窗口：[", hand_win_title, hand_win, "]")
#         time.sleep(1)  # 每1s输出一次
#     # left, top, right, bottom = win32gui.GetWindowRect(hand_win)
#     # print("目标窗口: [", hand_win_title, "] ,窗口大小：[%d X" % (right - left), "%d]" % (bottom - top))
#     return hand_win_title


def main():
    priority = int(input("请输入优先级（0-5）："))
    handle_title = get_active_window(5)
    handle = HandleSet(handle_title)
    handle.set_priority(priority)


if __name__ == '__main__':
    main()
