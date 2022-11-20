# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE
import pathlib
import random
import sys
import time
from os import system
from os.path import abspath, dirname
from random import uniform
from time import sleep

from PyQt5 import QtCore
from win32con import WM_CLOSE
from win32gui import PostMessage

from modules.ModuleClickModSet import ClickModSet
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
    clean_run_log_signal = QtCore.pyqtSignal(str)
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
        interval_seconds = info[4]
        start_match = StartMatch(info[:12])
        loop_seconds = int(info[5] * 60)
        start_time = time.mktime(time.localtime())  # 开始时间的时间戳
        end_time = start_time + loop_seconds  # 结束时间的时间戳

        # 生成随机点击模型，其中info[3]是随机偏移像素值，这里作为点击模型的坐标范围，
        # 如：偏移50，则模型的坐标范围为[(-50,50),(-50,50)]的正态分布数组
        click_mod = ClickModSet.create_click_mod(info[3])

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
        success_target_list = [0, 1, 2, 3, 4, 5]  # 初始化匹配成功的图片数组，只记录5个
        warming_time = time.time()  # 记录当前时间(等待警告时间初始化，避免最开始的90秒内触发等待)

        print("<br>初始化中…")

        # 开始循环
        for i in range(20000):  # 最多20000次
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
            match_start_time = time.time()
            results = start_match.start_match_click(i, loop_times, target_info, debug_status, start_time, end_time,
                                                    now_time, loop_seconds, click_mod)
            match_end_time = time.time()
            run_status, match_status, stop_status, match_target_name, click_pos = results

            # 记录点击日志(如果匹配成功)
            if other_setting[15]:
                if click_pos:
                    today = time.strftime('%y%m%d', time.localtime(time.time()))
                    match_time = time.strftime('%y-%m-%d %H:%M:%S', time.localtime(match_end_time))
                    file_path = abspath(dirname(dirname(__file__))) + r'/modules/click_log/click_log_' + today + '.txt'
                    f = open(file_path, 'a+', encoding="utf-8")
                    for aa in range(len(click_pos)):
                        f.writelines(match_time + ',' + match_target_name + ',' + str(click_pos[aa][0]) + ',' + str(
                            click_pos[aa][1]) + '\n')

            # 当匹配到需要终止脚本运行的图片时
            if stop_status:
                if other_setting[7]:
                    HandleSet.play_sounds("warming")  # 播放提示音
                self.mutex.unlock()
                self.finished_signal.emit(True)
                break

            # 计算匹配成功的次数,每成功匹配x次，休息x秒，避免异常
            if match_status:
                success_times = success_times + 1
                print(f"<br>已成功匹配 [ {success_times} ] 次")

                # 以下是匹配成功后的随机等待算法

                # 如果上次警告提示到需要触发时不足90秒，不会触发等待
                if other_setting[2] is True and match_end_time - warming_time > 90:

                    # 根据配置文件中设置的概率来触发等待，随机性更强
                    roll_num = random.randint(0, 99)  # roll 0-99，触发几率在配置文件可设置
                    if roll_num < float(other_setting[3]) * 100:
                        print(f"<br>已成功匹配{success_times}次，为防止异常检测，在此期间请等待或手动操作！")
                        if other_setting[7]:
                            HandleSet.play_sounds("ding")  # 播放提示音
                        roll_wait_sec = random.randint(int(other_setting[4][0]), int(other_setting[4][1]))
                        for t in range(int(roll_wait_sec)):
                            print(f"<br>为防止异常，[ {int(roll_wait_sec) - t} ] 秒后继续……")
                            sleep(1)

                        # 记录警告提示的时间戳，避免出现1分钟内出现2次以上的等待
                        warming_time = time.time()  # 记录当前时间

                    # 匹配指定次数（100次）后，立即触发等待（写死每100次必须等待）
                    elif (success_times + 1) % 100 == 0:
                        print(f"<br>已成功匹配{success_times}次，为防止异常检测，在此期间请等待或手动操作！")
                        if other_setting[7]:
                            HandleSet.play_sounds("ding")  # 播放提示音
                        roll_wait_sec = random.randint(int(other_setting[4][0]), int(other_setting[4][1]))
                        for t in range(int(roll_wait_sec)):
                            print(f"<br>为防止异常，[ {int(roll_wait_sec) - t} ] 秒后继续……")
                            sleep(1)

                        # 记录警告提示的时间戳，避免出现1分钟内出现2次以上的等待
                        warming_time = time.time()  # 记录当前时间

            # 当连续匹配同一个图片超过5次，脚本终止（没体力时一直点击的情况、游戏卡住的情况）
            if match_status and other_setting[14]:  # 如果匹配成功且开启5次匹配停止脚本的配置
                success_target_list.insert(0, match_target_name)  # 插入最新的匹配成功的图片名称在数组头部
                success_target_list.pop()  # 移除数组尾部最老的匹配成功的图片名称
                if len(set(success_target_list)) == 1:  # 如果数组中所有元素都相同，则意味着连续5次匹配到了同一个目标，触发脚本终止
                    print(f"<br>--------------------------------------------"
                          f"<br>已连续5次匹配同一目标图片 [ {success_target_list[0]} ] ，触发终止条件，脚本停止运行！！！"
                          f"<br>--------------------------------------------"
                          )

                    if other_setting[7]:
                        HandleSet.play_sounds("warming")  # 播放提示音
                    self.mutex.unlock()
                    self.finished_signal.emit(True)
                    break

            # 检测是否正常运行，否则重试
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
                show_log_tool_url = pathlib.PureWindowsPath(
                    abspath(dirname(__file__)) + r'\manual\show_log_tool.html')
                print("<br>日志分析工具：<a href=" + show_log_tool_url.as_posix() + ">->点击使用</a>")
                if other_setting[7]:
                    HandleSet.play_sounds("end")  # 播放提示音
                self.end_do(info)
                self.mutex.unlock()
                self.finished_signal.emit(True)
                break
            else:
                # 倒推剩余时间（时分秒格式）
                # 设置随机延时，防检测
                ts = uniform(-0.6, 0.6)
                # 根据时间来计算剩余时间
                remaining_time = time_transform(end_time - now_time)
                # 执行一次匹配所需的时间
                match_once_time = match_end_time - match_start_time
                if match_once_time >= interval_seconds + ts:
                    sleep_time = 0
                else:
                    sleep_time = interval_seconds - match_once_time + ts
                print(
                    f"<br>匹配一次需 [ {round(match_once_time, 2)} ] 秒, [ {round(sleep_time, 2)} ] 秒后继续，[ {remaining_time} ] 后结束")
                print("<br>-------------------------------------------")
                # 匹配间隔 机器计算时间不计入
                sleep(sleep_time)
                sleep(random.uniform(0.05, 0.3))  # 再额外随机等待0.05-0.3秒

                # 通过线程信号清除日志，避免日志过多导致运行缓慢(10次匹配清除1次)
                if (i + 1) % 10 == 0:
                    self.clean_run_log_signal.emit('')

            # 上面是Qthread中的循环匹配代码--------------

            # 线程锁off
            self.mutex.unlock()

        # 运行结束重置按钮可用状态
        self.finished_signal.emit(True)
