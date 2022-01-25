# -*- coding: utf-8 -*-
import gc
import random
import sys
import time
import win32gui
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


def get_active_window(loop_times=10):
    """点击鼠标获取目标窗口句柄"""
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
    return hand_win_title


def start_click(connect_mod='windows-程序', modname='御魂', hwd_title='阴阳师-网易游戏', click_deviation=20,
                interval_seconds=1,
                loop_min=120, compress_val=1, match_method='模板匹配'):
    """
    在图片中指定坐标点绘制边框
    :param connect_mod: 需点击的端，windows-程序 or Android-Adb
    :param modname: 需要使用的功能，即对应的文件夹
    :param hwd_title: windows程序窗口标题名称
    :param click_deviation: 鼠标点击偏移范围值，从中心点往周围随机偏移
    :param interval_seconds: 每次循环间隔的时间
    :param loop_min: 一共要循环的分钟数，受脚本执行时间的影响，实际执行时间大概会略小于这个时间
    :param compress_val: 对图片进行压缩的压缩率（1为不压缩），压缩程度越高，匹配速度越快，匹配精度越低，ADB模式下，0.8比较合适
    :param match_method: 匹配方法
    :return: 无
    """

    # 参数初始化
    modname = modname
    hwd_title = hwd_title  # 句柄名称
    # hwd_title = get_active_window()  # 点击窗口获取窗体名称
    click_deviation = int(click_deviation)  # 随机偏移量
    compress_val = float(compress_val)
    match_method = match_method

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
    if connect_mod == 'windows-程序':
        handle_set = HandleSet(hwd_title)
        handle_num = handle_set.get_handle_num
        handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
        handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
        handle_set.set_priority(random.randint(3, 5))  # 设置目标程序优先级，避免程序闪退
        screen_method = GetScreenCapture(handle_num, handle_width, handle_height)
    elif connect_mod == 'Android-Adb':
        adb_device_connect_status, device_id = HandleSet.adb_device_status()
        if adb_device_connect_status:
            print(f'已连接设备[ {device_id} ]')
        else:
            print(device_id)
            sys.exit(0)  # 脚本结束

    # 开始循环（截图->匹配->点击）
    for i in range(loop_times):
        now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        progress = format((i + 1) / loop_times, '.2%')
        print(f"第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次, 当前进度 [ {progress} ], 当前时间 [ {now_time} ]")

        # 获取截图
        print('正在截图…')
        screen_img = None
        if connect_mod == 'windows-程序':
            handle_set = HandleSet(hwd_title)
            handle_set.handle_is_active()
            screen_img = screen_method.window_screen()

        elif connect_mod == 'Android-Adb':
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                screen_img = screen_method.adb_screen()
            else:
                print(device_id)
                sys.exit(0)  # 脚本结束
        # ImgProcess.show_img(screen_img)  # test显示截图

        # 开始匹配
        print("正在匹配…")
        pos = None
        target_num = None
        target_img_m = target_img
        # 模板匹配方法
        if match_method == '模板匹配':
            if compress_val != 1:  # 压缩图片，模板匹配：模板和截图必须一起压缩
                screen_img = ImgProcess.img_compress(screen_img, compress_val)
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
                                                      target_img, screen_img)

        if pos and target_num is not None:
            # test,查看匹配情况，在获取的截图上画边框
            # target_img_hw_m = [target_img_hw[target_num][0] * compress_val,
            #                    target_img_hw[target_num][1] * compress_val]
            # draw_img = ImgProcess.draw_pos_in_img(screen_img, pos, target_img_hw_m)
            # ImgProcess.show_img(draw_img)

            # 如果图片有压缩，需对坐标还原
            if compress_val != 1:
                pos = [pos[0] / compress_val, pos[1] / compress_val]

            # 打印匹配到的实际坐标点和匹配到的图片信息
            print(f"匹配成功! 匹配到第 [ {target_num} ] 张图片: [ {target_img_name[target_num]} ]\n"
                  f"坐标位置: [ {int(pos[0])} , {int(pos[1])} ] ")

            # 开始点击
            if connect_mod == 'windows-程序':
                handle_set = HandleSet(hwd_title)
                handle_set.handle_is_active()
                handle_num = handle_set.get_handle_num
                click = DoClick(pos, click_deviation, handle_num)
                click.windows_click()
            elif connect_mod == 'Android-Adb':
                click = DoClick(pos, click_deviation)
                click.adb_click()
        else:
            print("匹配失败！")

        # ImgProcess.show_img(screen_img)  # test显示截图

        # 判断是否结束
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

            # 内存清理
            del screen_img, pos, now_time  # 删除变量
            if match_method == '特征点匹配':
                del screen_sift  # 删除变量
            else:
                del target_img_m
            gc.collect()  # 清理内存


def main():
    start_click()


if __name__ == '__main__':
    main()
