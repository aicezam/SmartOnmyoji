import random
import time
import win32gui
# import gc
from cv2 import cv2

from Module_DoClick import DoClick
from Module_GetScreenCapture import GetScreenCapture
from Module_GetTargetPic import GetTargetPic
from Module_GetTargetPos import GetTargetPos
from Module_GetTargetPosSift import GetTargetPosSift
from Module_HandleSet import HandleSet


def time_transform(seconds):
    """转换时间格式 秒—>时分秒"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    run_time = "%02d时%02d分%02d秒" % (h, m, s)
    return run_time


def get_active_window(loop_times):
    """点击鼠标获取目标窗口句柄"""
    # loop_times = 10  # 倒计时10秒
    hand_win = ""
    hand_win_title = ""
    for t in range(loop_times):
        print('请在倒计时%d秒结束前，点击目标窗口' % loop_times)
        loop_times -= 1
        hand_win = win32gui.GetForegroundWindow()
        hand_win_title = win32gui.GetWindowText(hand_win)
        print("目标窗口：[", hand_win_title, hand_win, "]")
        time.sleep(1)  # 每1s输出一次
    left, top, right, bottom = win32gui.GetWindowRect(hand_win)
    print("目标窗口: [", hand_win_title, "] ,窗口大小：[%d X" % (right - left), "%d]" % (bottom - top))
    # return hand_win
    return hand_win_title


def auto_click(connect_mod, modname, hwd_title, move_var, interval_seconds, loop_min):
    modname = modname
    hwd_title = hwd_title  # 句柄名称
    # hwd_title = get_active_window()
    move_var = int(move_var)  # 随机偏移量
    interval_seconds = int(interval_seconds)  # 每次执行间隔秒数
    loop_min = int(loop_min)  # 执行分钟数

    # 获取目标图片路径
    print('目标图片读取中……')
    target_pic = GetTargetPic(connect_mod, modname)
    target_pic_sift = target_pic.get_target_sift
    print('目标图片特征点提取成功！')
    target_pic_path = target_pic.get_target_file_path
    # print(target_pic_info)
    print('目标图片读取完成！')

    if connect_mod == '电脑端':
        # 句柄信息获取
        handle_set = HandleSet(hwd_title)
        handle_num = handle_set.get_handle_num
        handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
        handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
        handle_set.set_priority(random.randint(3, 5))  # 设置目标程序优先级，避免程序闪退

        get_screen_capture = GetScreenCapture(handle_num, handle_width, handle_height)  # 截图方法实例化

        t1 = len(target_pic_path) / 12  # 每次循环匹配找图需要消耗的时间, 脚本每次匹配一般平均需要2.5秒（30个匹配目标）
        loop_min = int(loop_min)  # 初始化执行时间，因为不能使用字符串，所以要转一下
        interval_seconds = int(interval_seconds)  # 初始化间隔秒数
        loop_times = int(loop_min * (60 / (interval_seconds + t1)))  # 计算要一共要执行的次数

        for i in range(loop_times):
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            progress = format((i + 1) / loop_times, '.2%')
            # print(f"当前进度：{progress}")
            print(f"第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次, 当前进度 [ {progress} ], 当前时间 [ {now_time} ]")
            handle_set.handle_is_active()  # 检测句柄是否存在，不存在会退出
            screen_capture = get_screen_capture.screen_capture()  # 获取截图，保存到内存
            # get_screen_capture.show_screen_capture(screen_capture)  # 显示截图
            # get_screen_capture.save_screen_capture(screen_capture)  # 保存截图
            get_pos = GetTargetPos(handle_width, handle_height, target_pic_path, screen_capture)  # 获取目标坐标方法实例化
            pos = get_pos.get_target_pos()  # 获取目标图片的坐标
            # get_pos.draw_target_pos(pos ,screen_capture, move_var)  # 绘制目标坐标范围在截图上的位置
            click = DoClick(pos, move_var, handle_num)
            click.do_click()  # 随机范围内点击坐标

            if i == loop_times - 1:
                print("---------------------已执行完成!---------------------")
                break
            else:
                # 倒推剩余时间（时分秒格式）
                remaining_time = time_transform(int(((loop_times - i - 1) / (60 / (interval_seconds + t1))) * 60))
                print("-----------------------%.2f秒后继续" % interval_seconds,
                      "%s后结束-----------------------" % remaining_time)
                ts = random.uniform(0.1, 1.5)  # 设置随机延时
                time.sleep(interval_seconds + ts)
                # del progress, screen_capture, pos, now_time, click, remaining_time  # 删除变量
                # gc.collect()  # 清理内存

    # elif connect_mod == '手机端-ADB':
    #     handle_set = HandleSet()
    #     handle_set.adb_test()  # 检测手机是否连接
    #
    #     screen_capture = GetScreenCapture.adb_screen()  # 截图手机端
    #     # GetScreenCapture.show_screen_capture(screen_capture)
    #     GetScreenCapture.save_screen_capture(screen_capture)
    #
    #     imginfo = screen_capture.shape
    #     height = imginfo[0]
    #     width = imginfo[1]
    #     get_pos = GetTargetPos(width, height, target_pic_path, screen_capture)  # 获取目标坐标方法实例化
    #     pos = get_pos.get_target_pos()  # 获取目标图片的坐标
    #     # print(pos)
    #     click = DoClick(pos, move_var)
    #     click.adb_click()
    #     # get_pos.draw_target_pos(pos, screen_capture, move_var)
    #     # handle_set.adb_kill()

    elif connect_mod == '手机端-ADB':
        pos = None
        target_pic_hw = []
        # handle_set = HandleSet()
        # handle_set.adb_test()  # 检测手机是否连接

        screen_capture = GetScreenCapture.adb_screen()  # 通过adb，保存手机截图到内存中
        # GetScreenCapture.show_screen_capture(screen_capture)  # 显示截图
        GetScreenCapture.save_screen_capture(screen_capture)  # 保存截图
        screen_capture_sift = GetTargetPosSift.get_sift(screen_capture)  # 提取特征点
        for i in range(len(target_pic_path)):
            target_pic_path_info = cv2.imread(target_pic_path[i])  # 转换目标图片为cv2格式
            target_pic_hw = target_pic_path_info.shape[:2]  # 获取目标图片的高度和宽度信息
            pos = GetTargetPosSift.get_target_pos_sift(target_pic_sift[i], screen_capture_sift,
                                                       target_pic_hw)  # 获取目标图片的坐标
            if pos is not None:
                break
        if pos is not None:
            print(pos)
        else:
            print('匹配失败！')
        GetTargetPosSift.draw_target_pos(pos, screen_capture, target_pic_hw)
        # click = DoClick(pos, move_var)
        # click.adb_click()
        # get_pos.draw_target_pos(pos, screen_capture, move_var)
        # handle_set.adb_kill()


def main():
    modname = "御魂"
    hwd_title = "阴阳师-网易游戏"  # 句柄名称
    move_var = 60  # 随机偏移量
    interval_seconds = 5  # 每次执行间隔秒数
    loop_min = 20  # 执行分钟数
    connect_mod = '电脑端'

    select_modname = int(input("----------------------------------------------"
                               "\n【御魂】按1\n【探索】按2\n【突破】按3\n【活动】按4\n【觉醒】按5\n【百鬼夜行】按6\n【微信红包】按7\n请输入对应的数字："))  # 选择模式
    if select_modname == 1:
        modname = "御魂"
    elif select_modname == 2:
        modname = "探索"
    elif select_modname == 3:
        modname = "突破"
    elif select_modname == 4:
        modname = "活动"
    elif select_modname == 5:
        modname = "觉醒"
    elif select_modname == 6:
        modname = "百鬼夜行"
    elif select_modname == 7:
        modname = "微信红包"

    select_connect_mod = int(input("----------------------------------------------"
                                   "\n【电脑端使用】按1\n【手机端-ADB模式】按2\n请输入对应的数字："))  # 选择模式
    if select_connect_mod == 1:
        connect_mod = '电脑端'
    elif select_connect_mod == 2:
        connect_mod = '手机端-ADB'

    loop_min = int(input("时间（分）："))  # 设置循环次数
    interval_seconds = int(input("延迟（秒）："))  # 设置每次循环等待时间
    move_var = int(input("偏移范围："))  # 设置每次循环等待时间
    hwd_title = get_active_window(5)

    auto_click(connect_mod, modname, hwd_title, move_var, interval_seconds, loop_min)


if __name__ == '__main__':
    main()
