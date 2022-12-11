# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from configparser import ConfigParser
from os.path import abspath, dirname, exists


class ReadConfigFile:
    def __init__(self):
        super(ReadConfigFile, self).__init__()
        self.file_path = abspath(dirname(dirname(__file__))) + r'/modules/config.ini'  # 获取配置文件的绝对路径

    def read_config_ui_info(self):
        config_ini = ConfigParser()

        # 校验文件是否存在
        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        config_ini.read(self.file_path, encoding="utf-8-sig")  # 读配置文件

        # 读取confing.ini的参数
        connect_mod = config_ini.get('ui_info', 'connect_mod')
        target_path_mode = config_ini.get('ui_info', 'target_path_mode')
        handle_title = config_ini.get('ui_info', 'handle_title')
        click_deviation = int(config_ini.get('ui_info', 'click_deviation'))
        interval_seconds = float(config_ini.get('ui_info', 'interval_seconds'))
        loop_min = float(config_ini.get('ui_info', 'loop_min'))
        img_compress_val = float(config_ini.get('ui_info', 'img_compress_val'))
        match_method = config_ini.get('ui_info', 'match_method')
        run_mode = config_ini.get('ui_info', 'run_mode')
        custom_target_path = config_ini.get('ui_info', 'custom_target_path')
        process_num = config_ini.get('ui_info', 'process_num')
        handle_num = config_ini.get('ui_info', 'handle_num')
        if_end = config_ini.get('ui_info', 'if_end')
        debug_status = self.str_to_bool(config_ini.get('ui_info', 'debug_status'))
        set_priority_status = self.str_to_bool(config_ini.get('ui_info', 'set_priority_status'))
        interval_seconds_max = float(config_ini.get('ui_info', 'interval_seconds_max'))
        screen_scale_rate = config_ini.get('other_setting', 'screen_scale_rate')
        times_mode = config_ini.get('ui_info', 'times_mode')

        return [connect_mod, target_path_mode, handle_title, click_deviation, interval_seconds, loop_min,
                img_compress_val, match_method, run_mode, custom_target_path, process_num, handle_num, if_end,
                debug_status, set_priority_status, interval_seconds_max, screen_scale_rate, times_mode]

    def read_config_target_path_files_name(self):
        config_ini = ConfigParser()

        # 校验文件是否存在
        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        config_ini.read(self.file_path, encoding="utf-8-sig")  # 读配置文件

        # 读取confing.ini的参数
        file_name_0 = config_ini.get('target_path_files_name', 'file_name_0')
        file_name_1 = config_ini.get('target_path_files_name', 'file_name_1')
        file_name_2 = config_ini.get('target_path_files_name', 'file_name_2')
        file_name_3 = config_ini.get('target_path_files_name', 'file_name_3')
        file_name_4 = config_ini.get('target_path_files_name', 'file_name_4')
        file_name_5 = config_ini.get('target_path_files_name', 'file_name_5')
        file_name_6 = config_ini.get('target_path_files_name', 'file_name_6')

        target_file_name_list = [file_name_0.split(","), file_name_1.split(","), file_name_2.split(","),
                                 file_name_3.split(","), file_name_4.split(","), file_name_5.split(","),
                                 file_name_6.split(","),
                                 ]

        return target_file_name_list

    def read_config_other_setting(self):
        config_ini = ConfigParser()

        # 校验文件是否存在
        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        config_ini.read(self.file_path, encoding="utf-8-sig")  # 读配置文件

        # 读取confing.ini的参数
        save_ui_info_in_config = self.str_to_bool(config_ini.get('other_setting', 'save_ui_info_in_config'))
        playtime_warming_status = self.str_to_bool(config_ini.get('other_setting', 'playtime_warming_status'))
        success_times_warming_status = self.str_to_bool(config_ini.get('other_setting', 'success_times_warming_status'))
        success_times_warming_times = config_ini.get('other_setting', 'success_times_warming_times')
        success_times_warming_waiting_seconds = config_ini.get('other_setting', 'success_times_warming_waiting_seconds')
        debug_status_show_pics = self.str_to_bool(config_ini.get('other_setting', 'debug_status_show_pics'))
        set_priority_num = config_ini.get('other_setting', 'set_priority_num')
        play_sound_status = self.str_to_bool(config_ini.get('other_setting', 'play_sound_status'))
        adb_wifi_status = self.str_to_bool(config_ini.get('other_setting', 'adb_wifi_status'))
        adb_wifi_ip = config_ini.get('other_setting', 'adb_wifi_ip')
        ex_click = config_ini.get('other_setting', 'ex_click')
        screen_scale_rate = config_ini.get('other_setting', 'screen_scale_rate')
        if_match_then_stop = self.str_to_bool(config_ini.get('other_setting', 'if_match_then_stop'))
        stop_target_img_name = config_ini.get('other_setting', 'stop_target_img_name')
        if_match_5times_stop = self.str_to_bool(config_ini.get('other_setting', 'if_match_5times_stop'))
        save_click_log = self.str_to_bool(config_ini.get('other_setting', 'save_click_log'))
        target_deviation = int(config_ini.get('other_setting', 'target_deviation'))
        success_match_then_wait = config_ini.get('other_setting', 'success_match_then_wait')

        other_setting = [save_ui_info_in_config, playtime_warming_status, success_times_warming_status,
                         success_times_warming_times, success_times_warming_waiting_seconds.split(","),
                         debug_status_show_pics, set_priority_num, play_sound_status, adb_wifi_status, adb_wifi_ip,
                         ex_click, screen_scale_rate, if_match_then_stop, stop_target_img_name.split(","),
                         if_match_5times_stop, save_click_log, target_deviation, success_match_then_wait.split(",")]

        return other_setting

    def writ_config_ui_info(self, info):
        config_ini = ConfigParser(comment_prefixes='/', allow_no_value=True)  # 保留注释

        # 校验文件是否存在
        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        # 先把所有参数转为str格式，否则写入会报错
        for i in range(len(info)):
            info[i] = str(info[i])

        config_ini.read(self.file_path, encoding="utf-8-sig")  # 读配置文件

        # 写入confing.ini的参数
        config_ini.set("ui_info", "connect_mod", info[0])
        config_ini.set("ui_info", "target_path_mode", info[1])
        config_ini.set("ui_info", "handle_title", info[2])
        config_ini.set("ui_info", "click_deviation", info[3])
        config_ini.set("ui_info", "interval_seconds", info[4])
        config_ini.set("ui_info", "loop_min", info[5])
        config_ini.set("ui_info", "img_compress_val", info[6])
        config_ini.set("ui_info", "match_method", info[7])
        config_ini.set("ui_info", "run_mode", info[8])
        config_ini.set("ui_info", "custom_target_path", info[9])
        config_ini.set("ui_info", "process_num", info[10])
        config_ini.set("ui_info", "handle_num", info[11])
        config_ini.set("ui_info", "if_end", info[12])
        config_ini.set("ui_info", "debug_status", info[13])
        config_ini.set("ui_info", "set_priority_status", info[14])
        config_ini.set("ui_info", "interval_seconds_max", info[15])
        config_ini.set("other_setting", "screen_scale_rate", info[16])
        config_ini.set("ui_info", "times_mode", info[17])

        # 写入文件
        config_ini.write(open(self.file_path, 'w', encoding="utf-8"))

    @staticmethod
    def str_to_bool(str_val):
        return True if str_val.lower() == 'true' else False

# rc = ReadConfigFile()  # 实例化
#
# info_r = rc.read_config_ui_info()  # 读参数
# print(info_r)
#
# # info_w = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14']
# info_w = ['Windows程序窗体', '御魂', '阴阳师-网易游戏', 35, 5.0, 90.0, 1.0, '模板匹配', '正常-可后台', None, '单开', 0, '不执行任何操作', False, True]
#
# rc.writ_config_ui_info(info_w)  # 写参数


# rc = ReadConfigFile()
# file_name = rc.read_config_target_path_files_name()
# print(file_name)
