# -*- coding: utf-8 -*-
from gc import collect
from time import sleep, localtime, strftime
from os.path import abspath, dirname
from re import search

from win32gui import GetWindowText

from modules.ModuleDoClick import DoClick
from modules.ModuleGetPos import GetPosByTemplateMatch, GetPosBySiftMatch
from modules.ModuleGetScreenCapture import GetScreenCapture
from modules.ModuleGetTargetInfo import GetTargetPicInfo
from modules.ModuleHandleSet import HandleSet
from modules.ModuleImgProcess import ImgProcess
from modules.ModuleGetConfig import ReadConfigFile


def time_transform(seconds):
    """
    转换时间格式 秒—>时分秒
    :param seconds: 秒数
    :return: 时分秒格式
    """
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    run_time = "%02d时%02d分%02d秒" % (h, m, s)
    return run_time


class StartMatch:

    def __init__(self, gui_info):
        super(StartMatch, self).__init__()
        self.connect_mod, self.target_modname, self.hwd_title, self.click_deviation, self.interval_seconds, self.loop_min, self.compress_val, self.match_method, self.scr_and_click_method, self.custom_target_path, self.process_num, self.handle_num = gui_info
        rc = ReadConfigFile()
        self.other_setting = rc.read_config_other_setting()

    def set_init(self, set_priority_status):
        """
        获取待匹配的目标图片信息、计算循环次数、时间、截图方法
        :return: 循环次数、截图方法、图片信息、每次循环大约需要执行的时间
        """
        # 参数初始化
        target_modname = self.target_modname
        custom_target_path = self.custom_target_path
        interval_seconds = self.interval_seconds
        loop_min = self.loop_min
        # 获取待检测目标图片信息
        print('<br>目标图片读取中……')
        target_info = GetTargetPicInfo(target_modname, custom_target_path,
                                       compress_val=1).get_target_info  # 目标图片不压缩（本身就小）
        if target_info is None:
            return None

        target_img_sift, target_img_hw, target_img_name, target_img_file_path, target_img = target_info

        print(f'<br>读取完成！共[ {len(target_img)} ]张图片\n{target_img_name}')
        print("<br>--------------------------------------------")

        # 计算循环次数、时间
        t1 = len(target_img) / 30  # 每次循环匹配找图需要消耗的时间, 脚本每次匹配一般平均需要2.5秒（30个匹配目标）
        loop_min = int(loop_min)  # 初始化执行时间，因为不能使用字符串，所以要转一下
        interval_seconds = int(interval_seconds)  # 初始化间隔秒数
        loop_times = int(loop_min * (60 / (interval_seconds + t1)))  # 计算要一共要执行的次数

        # 程序初始化时，如果设置的wifi或远程连接，先使用adb connect 连接设备
        if self.connect_mod != 'Windows程序窗体':
            HandleSet.deal_cmd(abspath(dirname(__file__)) + r'\adb.exe kill-server')
            print("<br>正在尝试连接！如果失败请使用以下cmd命令重置adb，或使用USB连接手机")
            print("<br>--------------------------------------------")
            print(rf"<br>{abspath(dirname(__file__))}\adb.exe kill-server")
            print(rf"<br>{abspath(dirname(__file__))}\adb.exe devices")
            print("<br>--------------------------------------------")
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                print(rf"<br>已连接至：[ {device_id[0]} ]")
            # print("<br>连接中……")
            if self.other_setting[8]:
                try:
                    print(f"<br>正在尝试连接 [ {self.other_setting[9]} ] ……")
                    command = abspath(dirname(__file__)) + rf'\adb.exe connect {self.other_setting[9]}'
                    HandleSet.deal_cmd(command)
                except:
                    print("<br>连接出现异常，或设备无响应！")
                    return None

        elif self.connect_mod == 'Windows程序窗体':
            if search("模拟器", self.hwd_title):
                HandleSet.deal_cmd(abspath(dirname(__file__)) + r'\adb.exe kill-server')
                print("<br>正在尝试连接模拟器！如果失败请使用以下cmd命令重置adb")
                print(rf"<br>{abspath(dirname(__file__))}\adb.exe kill-server")
                print(rf"<br>{abspath(dirname(__file__))}\adb.exe devices")
                sleep(2)
                if search("MuMu模拟器", self.hwd_title):
                    HandleSet.deal_cmd(abspath(dirname(__file__)) + rf'\adb.exe connect 127.0.0.1:7555')
                elif search("夜神模拟器", self.hwd_title):
                    HandleSet.deal_cmd(abspath(dirname(__file__)) + rf'\adb.exe connect 127.0.0.1:62001')
                elif search("逍遥模拟器", self.hwd_title):
                    HandleSet.deal_cmd(abspath(dirname(__file__)) + rf'\adb.exe connect 127.0.0.1:21503')
                elif search("腾讯手游助手", self.hwd_title):
                    HandleSet.deal_cmd(abspath(dirname(__file__)) + rf'\adb.exe connect 127.0.0.1:6555')

                adb_device_connect_status, device_id = HandleSet.adb_device_status()
                if adb_device_connect_status:
                    print(rf"<br>已连接至：[ {device_id[0]} ]")
                    print("<br>--------------------------------------------")

        # 设置游戏进程优先级，避免闪退（部分电脑可能有bug，会报错）
        if set_priority_status:
            if self.process_num == '多开' and self.connect_mod == 'Windows程序窗体':
                handle_num_list = str(self.handle_num).split(",")
                if handle_num_list[0] == '' or handle_num_list[0] == '0' or handle_num_list[0] is None:
                    print("<br>【运行异常：请选择待匹配目标窗口！】")
                    return None
                for handle_num_loop in range(len(handle_num_list)):
                    handle_num = int(handle_num_list[handle_num_loop])
                    handle_set = HandleSet('', handle_num)
                    if not handle_set.handle_is_active(self.process_num):
                        print("<br>【运行异常：未选择待匹配目标程序，或程序异常终止！】")
                        return None
                    handle_set.set_priority(int(self.other_setting[6]))
            elif self.process_num == '单开' and self.connect_mod == 'Windows程序窗体':
                if self.hwd_title == '' or self.hwd_title is None:
                    print("<br>【运行异常：请选择待匹配目标窗口！】")
                    return None
                handle_set = HandleSet(self.hwd_title, 0)
                if not handle_set.handle_is_active(self.process_num):
                    print("<br>【运行异常：未选择待匹配目标程序，或程序异常终止！】")
                    return None
                handle_set.set_priority(int(self.other_setting[6]))

        return loop_times, target_info, t1

    def matching(self, connect_mod, handle_num, scr_and_click_method, screen_method, debug_status, match_method,
                 compress_val, target_info, click_deviation, run_status, match_status):
        """
        核心代码~
        :param connect_mod: 运行方式，windows或安卓
        :param handle_num: windows句柄编号
        :param scr_and_click_method: 是否兼容模式运行，两种方法不同
        :param screen_method: 截图方法
        :param debug_status: 是否启用调试模式
        :param match_method: 匹配方法、模板匹配、特征点匹配
        :param compress_val: 压缩参数，越高越不压缩
        :param target_info: 匹配目标图片
        :param click_deviation: 点击偏移量
        :param run_status: 运行状态
        :param match_status: 匹配状态
        :return: 运行状态、匹配状态
        """

        target_img_sift, target_img_hw, target_img_name, target_img_file_path, target_img = target_info

        # 获取截图
        print('<br>正在截图…')
        screen_img = None
        if connect_mod == 'Windows程序窗体':
            # 如果部分窗口不能点击、截图出来是黑屏，可以使用兼容模式
            if scr_and_click_method == '正常-可后台':
                screen_img = screen_method.window_screen()
            elif scr_and_click_method == '兼容-不可后台':
                screen_img = screen_method.window_screen_bk()

        # 支持安卓adb连接
        elif connect_mod == 'Android-手机':
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                screen_img = screen_method.adb_screen(device_id[0])  # 暂仅支持找到的第一个设备
            else:
                print(device_id)
                run_status = False
                return run_status, match_status

        if debug_status:
            if self.other_setting[5]:
                ImgProcess.show_img(screen_img)  # test显示压缩后截图

        # 开始匹配
        print("<br>正在匹配…")
        pos = None
        target_num = None
        target_img_tm = target_img

        # 模板匹配方法
        if match_method == '模板匹配':
            if compress_val != 1:  # 压缩图片，模板和截图必须一起压缩
                screen_img = ImgProcess.img_compress(screen_img, compress_val)
                if debug_status and compress_val != 1:
                    if self.other_setting[5]:
                        ImgProcess.show_img(screen_img)  # test显示压缩后截图
                target_img_tm = []
                for k in range(len(target_img)):
                    target_img_tm.append(ImgProcess.img_compress(target_img[k], compress_val))

            # 开始匹配
            get_pos = GetPosByTemplateMatch()
            pos, target_num = get_pos.get_pos_by_template(screen_img, target_img_tm, debug_status)

        # 特征点匹配方法，准确度不能保证，但是不用适配不同设备
        elif match_method == '特征点匹配':
            if compress_val != 1:  # 压缩图片，特征点匹配方法，只压缩截图
                screen_img = ImgProcess.img_compress(screen_img, compress_val)
                if debug_status and compress_val != 1:
                    if self.other_setting[5]:
                        ImgProcess.show_img(screen_img)  # test显示压缩后截图
            screen_sift = ImgProcess.get_sift(screen_img)  # 获取截图的特征点

            # 开始匹配
            get_pos = GetPosBySiftMatch()
            pos, target_num = get_pos.get_pos_by_sift(target_img_sift, screen_sift,
                                                      target_img_hw,
                                                      target_img, screen_img, debug_status)
            del screen_sift  # 删除截图的特征点信息

        if pos and target_num is not None:
            match_status = True

            # 如果图片有压缩，需对坐标还原
            if compress_val != 1:
                pos = [pos[0] / compress_val, pos[1] / compress_val]

            # 打印匹配到的实际坐标点和匹配到的图片信息
            print(f"<br>匹配成功! ")
            # if debug_status:
            # if self.other_setting[5]:  # 显示匹配成功的图片
            print(f"<br><img height=\"30\" src='{target_img_file_path[target_num]}'>")
            print(f"<br>匹配到第 [ {target_num + 1} ] 张图片: [ {target_img_name[target_num]} ]"
                  f"<br>坐标位置: [ {int(pos[0])} , {int(pos[1])} ] ")

            # 开始点击
            if connect_mod == 'Windows程序窗体':
                if search("模拟器", self.hwd_title) or search("手游助手", self.hwd_title):
                    # 针对 安卓模拟器 的兼容（使用ADB连接）
                    adb_device_connect_status, device_id = HandleSet.adb_device_status()
                    doclick = DoClick(pos, click_deviation)
                    doclick.adb_click(device_id[0])
                else:
                    # 针对 windows 程序
                    handle_set = HandleSet(self.hwd_title, handle_num)
                    handle_num = handle_set.get_handle_num
                    doclick = DoClick(pos, click_deviation, handle_num)

                    # 如果部分窗口不能点击、截图出来是黑屏，可以使用兼容模式
                    if scr_and_click_method == '正常-可后台':
                        doclick.windows_click()
                    elif scr_and_click_method == '兼容-不可后台':
                        doclick.windows_click_bk()

            # 支持安卓adb连接
            elif connect_mod == 'Android-手机':
                adb_device_connect_status, device_id = HandleSet.adb_device_status()
                doclick = DoClick(pos, click_deviation)
                doclick.adb_click(device_id[0])
        else:
            print("<br>匹配失败！")
            match_status = False

        # 内存清理
        del screen_img, pos, target_info, target_img, target_img_sift, screen_method  # 删除变量
        collect()  # 清理内存
        return run_status, match_status

    def start_match_click(self, i, loop_times, target_info, debug_status):
        """不同场景下的匹配方式"""
        match_status = False
        run_status = True
        connect_mod = self.connect_mod
        scr_and_click_method = self.scr_and_click_method
        match_method = self.match_method
        compress_val = float(self.compress_val)
        click_deviation = int(self.click_deviation)
        handle_num_list = str(self.handle_num).split(",")

        # 计算进度
        now_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
        progress = format((i + 1) / loop_times, '.2%')
        print(f"<br>第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次 当前进度 [ {progress} ] "
              f"<br>当前时间 [ {now_time} ]")

        # 多开场景下，针对每个窗口遍历：截图、匹配、点击
        if self.process_num == '多开' and connect_mod == 'Windows程序窗体':
            if handle_num_list[0] == '' or handle_num_list[0] == '0' or handle_num_list[0] is None:
                print("<br>【运行异常：请选择待匹配目标窗口！】")
                run_status = False
                return run_status, match_status
            for handle_num_loop in range(len(handle_num_list)):
                handle_num = int(handle_num_list[handle_num_loop])
                print("<br>--------------------------------------------")
                print(f"<br>正在匹配 [{GetWindowText(handle_num)}] [{handle_num}]")
                handle_set = HandleSet('', handle_num)
                if not handle_set.handle_is_active(self.process_num):
                    print("<br>【运行异常：未选择待匹配目标程序，或程序异常终止！】")
                    run_status = False
                    return run_status, match_status
                handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
                handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
                screen_method = GetScreenCapture(handle_num, handle_width, handle_height)
                run_status, match_status = self.matching(connect_mod, handle_num, scr_and_click_method,
                                                         screen_method,
                                                         debug_status, match_method,
                                                         compress_val, target_info, click_deviation, run_status,
                                                         match_status)

        # 单开场景下，通过标题找到窗口句柄
        elif self.process_num == '单开' and connect_mod == 'Windows程序窗体':
            if self.hwd_title == '' or self.hwd_title is None:
                print("<br>【运行异常：请选择待匹配目标窗口！】")
                run_status = False
                return run_status, match_status
            handle_set = HandleSet(self.hwd_title, 0)
            if not handle_set.handle_is_active(self.process_num):
                print("<br>【运行异常：未选择待匹配目标程序，或程序异常终止！】")
                run_status = False
                return run_status, match_status
            handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
            handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
            handle_num = handle_set.get_handle_num
            screen_method = GetScreenCapture(handle_num, handle_width, handle_height)
            run_status, match_status = self.matching(connect_mod, handle_num, scr_and_click_method, screen_method,
                                                     debug_status, match_method,
                                                     compress_val, target_info, click_deviation, run_status,
                                                     match_status)

        # adb模式下，暂仅支持单开
        # elif connect_mod == 'Android-Adb':
        else:
            adb_device_connect_status, device_id = HandleSet.adb_device_status()
            if adb_device_connect_status:
                print(f'<br>已连接设备[ {device_id} ]')
                screen_method = GetScreenCapture()
                run_status, match_status = self.matching(connect_mod, 0, scr_and_click_method, screen_method,
                                                         debug_status,
                                                         match_method,
                                                         compress_val, target_info, click_deviation, run_status,
                                                         match_status)
            else:
                print(device_id)
                run_status = False
                return run_status, match_status

        del target_info, screen_method, connect_mod, scr_and_click_method, match_method, compress_val, click_deviation, handle_num_list  # 删除变量
        collect()  # 清理内存

        return run_status, match_status

    @staticmethod
    def time_warming():
        """检测时间是否晚12-早8点之间，这个时间可能因为异常导致封号"""

        if localtime().tm_hour < 8:
            now_time = strftime("%H:%M:%S", localtime())
            print("<br>----------------------------------------------------------")
            print(f"<br>警告：现在 [ {now_time} ]【非正常游戏时间，请谨慎使用】")
            print("<br>----------------------------------------------------------")
            for t in range(8):
                print(f"<br>[ {8 - t} ] 秒后开始……")
                sleep(1)
            print("<br>----------------------------------------------------------")
