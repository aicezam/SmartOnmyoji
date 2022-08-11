# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import sys
import time
from os import system
from random import uniform
from time import sleep

from PyQt5 import QtCore
from win32con import WM_CLOSE
from win32gui import PostMessage

from modules.ModuleGetConfig import ReadConfigFile
from modules.ModuleHandleSet import HandleSet
from modules.ModuleStartMatching import StartMatch, time_transform


class GetActiveWindowThread(QtCore.QThread):
    """
    继承QThread，启用多线程，用于点击获取目标窗体的标题名称
    """
    active_window_signal = QtCore.pyqtSignal(str)

    def __init__(self, main_window_ui):
        super(GetActiveWindowThread, self).__init__()
        self.ui_info = main_window_ui

    def run(self):
        hand_title, hand_num = HandleSet.get_active_window()  # 鼠标点击获取句柄编号和标题
        if self.ui_info.process_num_one.isChecked():
            self.active_window_signal.emit(hand_title)  # 单开获取标题
        else:
            if self.ui_info.show_handle_num.text() == '0' or self.ui_info.show_handle_num.text() == '' or self.ui_info.show_handle_num.text() is None:
                hand_num = str(hand_num)  # 获取的句柄编号拼接到UI中
            else:
                hand_num = self.ui_info.show_handle_num.text() + ',' + str(hand_num)  # 新获取的编号拼接到UI中
            self.active_window_signal.emit(str(hand_num))  # 多开获取多个编号


class MatchingThread(QtCore.QThread):
    """
    为线程方法增加暂停、恢复、取消方法，并可以传递信号给UI控件
    """
    # 线程值信号
    progress_val_signal = QtCore.pyqtSignal(int)
    finished_signal = QtCore.pyqtSignal(bool)

    # 构造函数，thread初始化创建时，传入UI窗体类，可以在run中直接获取GUI中的参数
    def __init__(self, main_window_ui):
        super(MatchingThread, self).__init__()
        self.isPause = False
        self.isCancel = False
        self.cond = QtCore.QWaitCondition()
        self.mutex = QtCore.QMutex()
        self.ui_info = main_window_ui

    # 暂停
    def pause(self):
        # print("线程暂停")
        self.isPause = True

    # 恢复
    def resume(self):
        # print("线程恢复")
        self.isPause = False
        self.cond.wakeAll()

    # 取消
    def cancel(self):
        # print("线程取消")
        self.isCancel = True
        self.terminate()
        # 线程终止方法，terminate()据说是不安全的用法，但实际使用可以解决多线程结束后依然继续运行的问题，
        # 以及控制台的警告：QMutex: destroying locked mutex

    # 正常结束后执行
    @staticmethod
    def end_do(info):
        """
        :param info:界面配置参数
        :return: 无
        """
        if_end = info[12]
        handle_title = info[2]
        handle_num_list = info[11]
        process_num = info[10]
        connect_mod = info[0]

        if if_end == '电脑关机':
            print("<br>已完成，60秒后自动关机！")
            system('shutdown /s /t 60')
        elif if_end == '不执行任何操作':
            print("<br>已完成！")
        elif if_end == '关闭匹配目标窗体':
            print("<br>已完成，正在退出程序！")
            if process_num == '多开' and connect_mod == 'Windows程序窗体':
                handle_num_list = str(handle_num_list).split(",")
                for handle_num_loop in range(len(handle_num_list)):
                    PostMessage(handle_num_list[handle_num_loop], WM_CLOSE, 0, 0)  # 关闭程序
            else:
                handle_set = HandleSet(handle_title, 0)
                handle_num = handle_set.get_handle_num
                PostMessage(handle_num, WM_CLOSE, 0, 0)  # 关闭程序
        elif if_end == '关闭脚本':
            print("<br>已完成，%s即将退出！" % '护肝小能手')
            sys.exit(0)

    # 获取GUI界面参数
    def get_ui_info(self):
        """
        :return: GUI界面的参数
        """
        loop_min = float(self.ui_info.loop_min.value())  # 运行时长
        interval_seconds = float(self.ui_info.interval_seconds.value())  # 间隔时间
        click_deviation = int(self.ui_info.click_deviation.value())  # 点击偏移范围
        connect_mod = None  # 连接方式，电脑还是安卓手机
        if self.ui_info.rd_btn_windows_mod.isChecked():
            connect_mod = self.ui_info.rd_btn_windows_mod.text()
        elif self.ui_info.rd_btn_android_adb.isChecked():
            connect_mod = self.ui_info.rd_btn_android_adb.text()
        target_path_mode = str(self.ui_info.select_target_path_mode_combobox.currentText())  # 待匹配模板图片所在文件夹
        process_num = None  # 游戏单开还是多开
        handle_title = str(self.ui_info.show_handle_title.text())  # 待匹配窗体标题名称
        handle_num = self.ui_info.show_handle_num.text()
        if self.ui_info.process_num_one.isChecked():
            process_num = self.ui_info.process_num_one.text()
            handle_title = str(self.ui_info.show_handle_title.text())  # 待匹配窗体标题名称
        elif self.ui_info.process_num_more.isChecked():
            process_num = self.ui_info.process_num_more.text()
            handle_num = self.ui_info.show_handle_num.text()  # 待匹配窗体句柄编号
        img_compress_val = int(self.ui_info.image_compression.value()) / 100  # 图片压缩率
        match_method = None  # 匹配方法，模板匹配或特征点匹配
        if self.ui_info.template_matching.isChecked():
            match_method = self.ui_info.template_matching.text()
        elif self.ui_info.sift_matching.isChecked():
            match_method = self.ui_info.sift_matching.text()
        run_mode = None  # 运行模式，后台执行或兼容模式（兼容模式只能前台）
        if self.ui_info.runmod_nomal.isChecked():
            run_mode = self.ui_info.runmod_nomal.text()
        elif self.ui_info.runmod_compatibility.isChecked():
            run_mode = self.ui_info.runmod_compatibility.text()
        if_end = str(self.ui_info.if_end_do.currentText())  # 脚本运行正常结束后，执行的操作，未生效
        debug_status = self.ui_info.debug.isChecked()  # 是否启用调试
        custom_target_path = ''
        if self.ui_info.select_target_path_mode_combobox.currentText() == '自定义':
            custom_target_path = self.ui_info.show_target_path.text()
        set_priority_status = self.ui_info.set_priority.isChecked()  # 是否启用调试

        info = [connect_mod, target_path_mode, handle_title, click_deviation, interval_seconds, loop_min,
                img_compress_val, match_method, run_mode, custom_target_path, process_num, handle_num, if_end,
                debug_status, set_priority_status]

        # 界面设置的参数写入配置文件
        set_config = ReadConfigFile()
        other_setting = set_config.read_config_other_setting()
        if other_setting[0] is True:
            set_config.writ_config_ui_info(info)

        return connect_mod, target_path_mode, handle_title, click_deviation, interval_seconds, loop_min, img_compress_val, match_method, run_mode, custom_target_path, process_num, handle_num, if_end, debug_status, set_priority_status

    # 运行(入口)
    def run(self):
        """
        多线程执行，避免界面卡顿，通过线程锁实现暂停、终止的操作，通过信号实现传参到界面
        """
        # 加载配置参数设置
        set_config = ReadConfigFile()
        other_setting = set_config.read_config_other_setting()

        # print("线程开始")
        info = self.get_ui_info()

        if info[0] == "Windows程序窗体" and info[10] == "多开" and info[11] == '0':  # 检测如果选择多开，是否已经获取句柄编号
            # 多开使用循环，每个循环针对一个窗口
            print("<br>请点击【选择窗体】获取目标窗体的句柄编号，支持选择多个游戏窗口！")
            self.finished_signal.emit(True)
            return

        debug_status = info[13]
        set_priority_status = info[14]
        interval_seconds = int(info[4])
        start_match = StartMatch(info[:12])
        loop_seconds = int(info[5] * 60)
        start_time = time.mktime(time.localtime())  # 开始时间的时间戳
        end_time = start_time + loop_seconds  # 结束时间的时间戳
        str_start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))  # 开始时间
        str_end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))  # 结束时间
        print("<br>初始化中…")

        # 对UI参数初始化，计算匹配的次数、导入需要检测的目标图片
        init_value = start_match.set_init(set_priority_status)
        if init_value is None:
            self.finished_signal.emit(True)
            return
        else:
            loop_times, target_info, t1 = init_value

        # 检测游戏时间是否太晚，进行提示
        if other_setting[1] is True:
            start_match.time_warming()

        success_times = 0

        # 开始循环
        for i in range(int(loop_times)):
            # 线程锁on
            self.mutex.lock()
            if self.isPause:
                self.cond.wait(self.mutex)
            if self.isCancel:
                self.progress_val_signal.emit(0)
                break

            # 进度条，进度数值传递给UI界面的进度条，实时更新
            # progress = int((i + 1) / loop_times * 100)  # 根据次数计算进度

            now_time = time.mktime(time.localtime())  # 当前时间的时间戳
            progress = int((now_time - start_time) / loop_seconds * 100)  # 根据时间戳计算进度[（当前时间-开始时间）/总时间]
            if now_time >= end_time:
                progress = 100
            self.progress_val_signal.emit(progress)

            # 下面是Qthread中的循环匹配代码--------------

            # 开始匹配
            run_status, match_status = start_match.start_match_click(i, loop_times, target_info, debug_status, start_time, end_time, now_time, loop_seconds)

            # 计算匹配成功的次数,每成功匹配x次，休息x秒，避免异常
            if match_status:
                success_times = success_times + 1
                print(f"<br>已成功匹配 [ {success_times} ] 次")
                if other_setting[2] is True:
                    if success_times % int(other_setting[3]) == 0:
                        print(f"<br>已成功匹配{success_times}次，为防止异常检测，在此期间请等待或手动操作！")
                        if other_setting[7]:
                            HandleSet.play_sounds("warming")  # 播放提示音
                        for t in range(int(other_setting[4])):
                            print(f"<br>为防止异常，[ {int(other_setting[4]) - t} ] 秒后继续……")
                            sleep(1)

            # 检测是否正常运行，否则终止
            if not run_status:
                if other_setting[7]:
                    HandleSet.play_sounds("warming")  # 播放提示音
                    # 如果运行异常重新尝试继续执行
                print(f"<br>运行异常，请检查待匹配目标程序是否启动！")
                for t in range(10):
                    print(f"<br>{10 - t}秒后重试！")
                    sleep(1)
                pass

                # 如果运行异常直接终止
                # self.mutex.unlock()
                # self.finished_signal.emit(True)
                # break

            # 判断是否结束
            # if i == loop_times - 1:  # 根据执行次数判断结束时间
            if now_time >= end_time:  # 根据时间判断结束时间
                print("<br>---已执行完成!---")
                if other_setting[7]:
                    HandleSet.play_sounds("end")  # 播放提示音
                self.end_do(info)
                self.mutex.unlock()
                self.finished_signal.emit(True)
                break
            else:
                # 倒推剩余时间（时分秒格式）
                ts = uniform(0.2, 1.5)  # 设置随机延时，防检测
                # remaining_time = time_transform(int(((loop_times - i - 1) / (60 / (interval_seconds + t1))) * 60 - ts))  # 根据次数推算剩余时间
                remaining_time = time_transform(end_time-now_time)  # 根据时间来计算剩余时间
                print(f"<br>--- [ {round(interval_seconds + ts, 2)} ] 秒后继续，[ {remaining_time} ] 后结束---")
                print("<br>----------------------------------------------------------")
                sleep(interval_seconds + ts)

            # 上面是Qthread中的循环匹配代码--------------

            # 线程锁off
            self.mutex.unlock()

        # 运行结束重置按钮可用状态
        self.finished_signal.emit(True)
