# -*- coding: utf-8 -*-
from gc import collect
from sys import exit
from time import sleep, localtime, strftime
from pyautogui import click
from win32gui import GetWindowText, GetWindowRect, GetForegroundWindow, SetForegroundWindow
from modules.ModuleGetTargetInfo import GetTargetPicInfo
from modules.ModuleGetScreenCapture import GetScreenCapture
from modules.ModuleHandleSet import HandleSet
from modules.ModuleImgProcess import ImgProcess
from modules.ModuleGetPos import GetPosByTemplateMatch, GetPosBySiftMatch
from modules.ModuleDoClick import DoClick


def time_transform(seconds):
    """转换时间格式 秒—>时分秒"""
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    run_time = "%02d时%02d分%02d秒" % (h, m, s)
    return run_time


def get_active_window(loop_times=5):
    """点击鼠标获取目标窗口句柄"""
    hand_win = ""
    hand_win_title = ""
    for t in range(loop_times):
        print(f'请在倒计时 [ {loop_times} ] 秒结束前，点击目标窗口')
        loop_times -= 1
        hand_win = GetForegroundWindow()
        hand_win_title = GetWindowText(hand_win)
        print(f"目标窗口： [ {hand_win_title} ] [ {hand_win} ] ")
        sleep(1)  # 每1s输出一次
    left, top, right, bottom = GetWindowRect(hand_win)
    print("-----------------------------------------------------------")
    print(f"目标窗口: [ {hand_win_title} ] 窗口大小：[ {right - left} X {bottom - top} ]")
    print("-----------------------------------------------------------")
    return hand_win_title


class StartMatch:
    def __init__(self, gui_info):
        super(StartMatch, self).__init__()
        self.connect_mod, self.modname, self.hwd_title, self.click_deviation, self.interval_seconds, self.loop_min, self.compress_val, self.match_method, self.scr_and_click_method = gui_info

    def set_init(self):

        # 参数初始化
        modname = self.modname
        connect_mod = self.connect_mod
        hwd_title = self.hwd_title
        interval_seconds = self.interval_seconds
        loop_min = self.loop_min
        scr_and_click_method = self.scr_and_click_method
        # 获取窗体标题
        if hwd_title == '开始后鼠标点击选择窗体':
            hwd_title = get_active_window()  # 点击窗口获取窗体名称
        else:
            hwd_title = hwd_title  # 句柄名称

        # 获取待检测目标图片信息
        print('目标图片读取中……')
        target_info = GetTargetPicInfo(modname, compress_val=1).get_target_info  # 目标图片不压缩（本身就小）
        target_img_sift, target_img_hw, target_img_name, target_img_file_path, target_img = target_info
        print(f'读取完成！共[ {len(target_img)} ]张图片\n{target_img_name}')

        # 计算循环次数、时间
        t1 = len(target_img) / 30  # 每次循环匹配找图需要消耗的时间, 脚本每次匹配一般平均需要2.5秒（30个匹配目标）
        loop_min = int(loop_min)  # 初始化执行时间，因为不能使用字符串，所以要转一下
        interval_seconds = int(interval_seconds)  # 初始化间隔秒数
        loop_times = int(loop_min * (60 / (interval_seconds + t1)))  # 计算要一共要执行的次数

        # 句柄操作（获取句柄编号、设置优先级、检测程序是否运行）
        screen_method = GetScreenCapture()
        if connect_mod == 'Windows程序窗体':
            handle_set = HandleSet(hwd_title)
            handle_num = handle_set.get_handle_num
            handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
            handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
            # handle_set.set_priority(randint(3, 5))  # 设置目标程序优先级，避免程序闪退，若需要避免可以打开
            screen_method = GetScreenCapture(handle_num, handle_width, handle_height)

            # 通过pywin32模块下的SetForegroundWindow函数调用时，会出现
            # error: (0, 'SetForegroundWindow', 'No error message is available')报错，为pywin32模块下的一个小bug，
            # 在该函数调用前，需要先发送一个其他键给屏幕，这里先用鼠标点一次就不会报错了
            if scr_and_click_method == '兼容模式':
                x1, y1, x2, y2 = GetWindowRect(handle_num)
                click(x1 + 10, y1 + 10)
                SetForegroundWindow(handle_num)  # 窗口置顶

        # 检测安卓设备是否正常连接
        elif connect_mod == 'Android-Adb':
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                print(f'已连接设备[ {device_id} ]')
            else:
                print(device_id)
                exit(0)  # 脚本结束
        return loop_times, screen_method, target_info, t1

    def start_match_click(self, i, loop_times, screen_method, target_info, debug_status):
        connect_mod = self.connect_mod
        hwd_title = self.hwd_title
        scr_and_click_method = self.scr_and_click_method
        match_method = self.match_method
        compress_val = float(self.compress_val)
        click_deviation = int(self.click_deviation)
        target_img_sift, target_img_hw, target_img_name, target_img_file_path, target_img = target_info

        if debug_status:
            now_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            progress = format((i + 1) / loop_times, '.2%')
            print(f"第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次 \n当前进度 [ {progress} ] \n当前时间 [ {now_time} ]")
        else:
            print(f"第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次")

        # 获取截图
        print('正在截图…')
        screen_img = None
        if connect_mod == 'Windows程序窗体':
            handle_set = HandleSet(hwd_title)
            handle_is_active = handle_set.handle_is_active()
            if handle_is_active is None:
                exit(0)

            # 如果部分窗口不能点击、截图出来是黑屏，可以使用兼容模式
            if scr_and_click_method == '正常-可后台':
                screen_img = screen_method.window_screen()
            elif scr_and_click_method == '兼容-不可后台':
                screen_img = screen_method.window_screen_bk()

        # 支持安卓adb连接
        elif connect_mod == 'Android-手机':
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                screen_img = screen_method.adb_screen()
            else:
                print(device_id)
                exit(0)  # 脚本结束

        if debug_status:
            ImgProcess.show_img(screen_img)  # test显示截图

        # 开始匹配
        print("正在匹配…")
        pos = None
        target_num = None
        target_img_m = target_img
        # 模板匹配方法
        if match_method == '模板匹配':
            if compress_val != 1:  # 压缩图片，模板匹配：模板和截图必须一起压缩
                screen_img = ImgProcess.img_compress(screen_img, compress_val)
                if debug_status:
                    ImgProcess.show_img(screen_img)  # test显示截图
                target_img_m = []
                for k in range(len(target_img)):
                    target_img_m.append(ImgProcess.img_compress(target_img[k], compress_val))
            # 开始匹配
            get_pos = GetPosByTemplateMatch()
            pos, target_num = get_pos.get_pos_by_template(screen_img, target_img_m)

        # 特征点匹配方法，准确度不能保证，但是不用适配不同设备
        elif match_method == '特征点匹配':
            if compress_val != 1:  # 压缩图片，特征点匹配方法，可以只压缩截图图片
                screen_img = ImgProcess.img_compress(screen_img, compress_val)
            screen_sift = ImgProcess.get_sift(screen_img)  # 获取截图的特征点
            # 开始匹配
            get_pos = GetPosBySiftMatch()
            pos, target_num = get_pos.get_pos_by_sift(target_img_sift, screen_sift,
                                                      target_img_hw,
                                                      target_img, screen_img, debug_status)

        if pos and target_num is not None:

            # 查看匹配情况，在获取的截图上画边框
            if debug_status:
                target_img_hw_m = [target_img_hw[target_num][0] * compress_val,
                                   target_img_hw[target_num][1] * compress_val]
                draw_img = ImgProcess.draw_pos_in_img(screen_img, pos, target_img_hw_m)
                ImgProcess.show_img(draw_img)

            # 如果图片有压缩，需对坐标还原
            if compress_val != 1:
                pos = [pos[0] / compress_val, pos[1] / compress_val]

            # 打印匹配到的实际坐标点和匹配到的图片信息
            print(f"匹配成功! 匹配到第 [ {target_num} ] 张图片: [ {target_img_name[target_num]} ]\n"
                  f"坐标位置: [ {int(pos[0])} , {int(pos[1])} ] ")

            # 开始点击
            if connect_mod == 'Windows程序窗体':
                handle_set = HandleSet(hwd_title)
                handle_is_active = handle_set.handle_is_active()
                if handle_is_active is None:
                    exit(0)
                handle_num = handle_set.get_handle_num
                doclick = DoClick(pos, click_deviation, handle_num)

                # 如果部分窗口不能点击、截图出来是黑屏，可以使用兼容模式
                if scr_and_click_method == '正常-可后台':
                    doclick.windows_click()
                elif scr_and_click_method == '兼容-不可后台':
                    doclick.windows_click_bk()

            # 支持安卓adb连接
            elif connect_mod == 'Android-手机':
                doclick = DoClick(pos, click_deviation)
                doclick.adb_click()
        else:
            print("匹配失败！")

        # 内存清理
        del screen_img, pos  # , now_time  # 删除变量
        if match_method == '特征点匹配':
            del screen_sift  # 删除变量
        else:
            del target_img_m
        collect()  # 清理内存
