# -*- coding: utf-8 -*-
import sys
from ctypes import windll
from os.path import abspath, dirname
from time import sleep
from os import system
from random import uniform
import PyQt5.QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog
from win32con import WM_CLOSE
from win32gui import FindWindow, PostMessage
from modules.ModuleStart import StartMatch, time_transform, get_active_window
from modules.ui import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        super(MainWindow).__init__()
        self.setupUi(self)  # 继承UI类，下面进行信号与槽的绑定和修改

        # 控制台消息输出到窗口上
        sys.stdout = EmitStr(text_writ=self.output_write)  # 输出结果重定向
        sys.stderr = EmitStr(text_writ=self.output_write)  # 错误输出重定向

        # 继承重新设置GUI初始状态
        self.btn_pause.setEnabled(False)
        self.btn_pause.hide()
        self.btn_resume.setEnabled(False)
        self.btn_resume.hide()
        self.btn_stop.setEnabled(False)
        self.btn_stop.hide()
        self.btn_exit.show()
        self.loop_progress.setValue(0)
        self.run_log.setReadOnly(True)
        self.click_deviation.setValue(35)  # 设置默认偏移量
        self.select_targetpic_path_btn.hide()
        self.setWindowIcon(QIcon('img/logo.ico'))

        # 绑定信号
        self.btn_start.clicked.connect(self.__on_clicked_btn_begin)
        self.btn_pause.clicked.connect(self.__on_clicked_btn_pause)
        self.btn_resume.clicked.connect(self.__on_clicked_btn_resume)
        self.btn_stop.clicked.connect(self.__on_clicked_btn_cancel)
        self.btn_exit.clicked.connect(self.__on_clicked_exit)
        self.select_target_path_mode_combobox.currentIndexChanged.connect(
            lambda: self.select_target_path_mode_btn_enable(self.select_target_path_mode_combobox.currentIndex()))
        self.btn_select_handle.clicked.connect(self.__on_click_btn_select_handle)
        self.select_targetpic_path_btn.clicked.connect(self.__on_click_btn_select_custom_path)

    # 控制台消息重定向槽函数，字符追加到 run_log 中
    def output_write(self, text):
        # self.run_log.insertPlainText(text)
        # self.run_log.append(text)
        cursor = self.run_log.textCursor()
        cursor.insertText(text)
        self.run_log.setTextCursor(cursor)
        self.run_log.ensureCursorVisible()

    # 根据下拉框内容，设置按钮是否可点击
    def select_target_path_mode_btn_enable(self, tag):
        if tag == 7:
            self.select_targetpic_path_btn.show()
        else:
            self.select_targetpic_path_btn.hide()
            self.show_target_path.setText('')

    # 开始按钮被点击的槽函数
    def __on_clicked_btn_begin(self):
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_start.hide()
        self.btn_pause.show()
        self.btn_resume.hide()
        self.btn_stop.show()
        self.set_edit_enabled(False)
        self.run_log.setText('')
        self.thread = MatchingThread(self)  # 创建线程
        self.thread.finished_signal.connect(self.thread_finished)  # 线程信号和槽连接，任务正常结束重置按钮状态
        self.thread.progress_val_signal.connect(self.loop_progress.setValue)  # 线程信号和槽连接，设置进度条
        sleep(0.1)
        self.thread.start()

    # 暂停按钮被点击的槽函数
    def __on_clicked_btn_pause(self):
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(True)
        self.btn_stop.setEnabled(True)
        self.btn_resume.show()
        self.btn_pause.hide()
        sleep(0.1)
        self.thread.pause()

    # 恢复按钮被点击的槽函数
    def __on_clicked_btn_resume(self):
        self.btn_start.setEnabled(False)
        self.btn_pause.setEnabled(True)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.btn_resume.hide()
        self.btn_pause.show()
        sleep(0.1)
        self.thread.resume()

    # 取消按钮被点击的槽函数
    def __on_clicked_btn_cancel(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.set_edit_enabled(True)
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_resume.hide()
        self.btn_stop.hide()
        sleep(0.1)
        self.thread.cancel()

    # 正常完成后的槽函数
    def thread_finished(self):
        self.btn_start.setEnabled(True)
        self.btn_pause.setEnabled(False)
        self.btn_resume.setEnabled(False)
        self.btn_stop.setEnabled(False)
        self.set_edit_enabled(True)
        self.btn_start.show()
        self.btn_pause.hide()
        self.btn_resume.hide()
        self.btn_stop.hide()

    # 获取目标窗体的槽函数
    def __on_click_btn_select_handle(self):
        self.run_log.setText('')  # 清空运行日志
        self.thread_1 = GetActiveWindowThread(self)
        if self.process_num_one.isChecked():  # 如果单开
            self.thread_1.active_window_signal.connect(self.show_handle_title.setText)
        else:  # 如果多开
            self.thread_1.active_window_signal.connect(self.show_handle_num.setText)
        self.thread_1.start()

    def __on_click_btn_select_custom_path(self):
        current_path = abspath(dirname(__file__))  # 当前路径
        custom_path = QFileDialog.getExistingDirectory(None, "选择文件夹", current_path + r'\img')  # 起始路径
        self.show_target_path.setText(custom_path)  # 显示路径

    # 退出程序的槽函数
    def __on_clicked_exit(self):
        if self.btn_start.isHidden():
            self.thread.cancel()
        sys.exit(0)

    # 脚本开始运行后，禁用编辑参数
    def set_edit_enabled(self, bool_val=False):
        self.if_end_do.setEnabled(bool_val)
        self.template_matching.setEnabled(bool_val)
        self.sift_matching.setEnabled(bool_val)
        self.runmod_nomal.setEnabled(bool_val)
        self.runmod_compatibility.setEnabled(bool_val)
        self.debug.setEnabled(bool_val)
        self.select_target_path_mode_combobox.setEnabled(bool_val)
        self.show_handle_title.setEnabled(bool_val)
        self.show_handle_title.setEnabled(bool_val)
        self.btn_select_handle.setEnabled(bool_val)
        self.rd_btn_windows_mod.setEnabled(bool_val)
        self.rd_btn_android_adb.setEnabled(bool_val)
        self.show_target_path.setEnabled(bool_val)
        self.select_targetpic_path_btn.setEnabled(bool_val)
        self.interval_seconds.setEnabled(bool_val)
        self.loop_min.setEnabled(bool_val)
        self.click_deviation.setEnabled(bool_val)
        self.image_compression.setEnabled(bool_val)
        self.process_num_one.setEnabled(bool_val)
        self.process_num_more.setEnabled(bool_val)
        self.show_handle_num.setEnabled(bool_val)


class EmitStr(PyQt5.QtCore.QObject):
    """
    定义一个信号类，sys.stdout有个write方法，通过重定向，
    每当有新字符串输出时就会触发下面定义的write函数，进而发出信号
    """
    text_writ = PyQt5.QtCore.pyqtSignal(str)

    def write(self, text):
        self.text_writ.emit(str(text))


class GetActiveWindowThread(PyQt5.QtCore.QThread):
    """
    继承QThread，启用多线程，用于点击获取目标窗体的标题名称
    """
    active_window_signal = PyQt5.QtCore.pyqtSignal(str)

    def __init__(self, main_window_ui):
        super(GetActiveWindowThread, self).__init__()
        self.ui_info = main_window_ui

    def run(self):
        hand_title, hand_num = get_active_window()
        if self.ui_info.process_num_one.isChecked():
            self.active_window_signal.emit(hand_title)
        else:
            self.active_window_signal.emit(str(hand_num))


class MatchingThread(PyQt5.QtCore.QThread):
    """
    为线程方法增加暂停、恢复、取消方法，并可以传递信号给UI控件
    """
    # 线程值信号
    progress_val_signal = PyQt5.QtCore.pyqtSignal(int)
    finished_signal = PyQt5.QtCore.pyqtSignal(bool)

    # 构造函数，thread初始化创建时，传入UI窗体类，可以在run中直接获取GUI中的参数
    def __init__(self, main_window_ui):
        super(MatchingThread, self).__init__()
        self.isPause = False
        self.isCancel = False
        self.cond = PyQt5.QtCore.QWaitCondition()
        self.mutex = PyQt5.QtCore.QMutex()
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
    def end_do(if_end, handle_title):
        """
        :param if_end: 程序正常结束后动作：电脑关机、关闭目标窗体、关闭脚本、不执行任何操作
        :param handle_title: 目标窗体的标题名称
        :return: 无
        """
        if if_end == '电脑关机':
            print("已完成，60秒后自动关机！")
            system('shutdown /s /t 60')
        elif if_end == '不执行任何操作':
            print("已完成！")
        elif if_end == '关闭匹配目标窗体':
            print("已完成，%s即将退出！" % handle_title)
            hwnd1 = FindWindow(None, handle_title)
            PostMessage(hwnd1, WM_CLOSE, 0, 0)  # 关闭程序
        elif if_end == '关闭脚本':
            print("已完成，%s即将退出！" % 'YYS护肝小能手')
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
        handle_title = None  # 待匹配窗体标题名称
        handle_num = None  # 待匹配窗体句柄编号
        if self.ui_info.process_num_one.isChecked():
            process_num = self.ui_info.process_num_one.text()
            handle_title = str(self.ui_info.show_handle_title.text())  # 待匹配窗体标题名称
        elif self.ui_info.process_num_more.isChecked():
            process_num = self.ui_info.process_num_more.text()
            handle_num = int(self.ui_info.show_handle_num.text())  # 待匹配窗体句柄编号
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
        custom_target_path = None
        if self.ui_info.select_target_path_mode_combobox.currentText() == '自定义':
            custom_target_path = self.ui_info.show_target_path.text()

        return connect_mod, target_path_mode, handle_title, click_deviation, interval_seconds, loop_min, img_compress_val, match_method, run_mode, custom_target_path, process_num, handle_num, if_end, debug_status

    # 运行(入口)
    def run(self):
        """
        多线程执行，避免界面卡顿，通过线程锁实现暂停、终止的操作，通过信号实现传参到界面
        """
        # print("线程开始")
        info = self.get_ui_info()

        if info[0] == "Windows程序窗体" and info[11] == 0:  # 检测如果选择多开，是否已经获取句柄编号
            print("请运行多个脚本，并点击【选择窗体】获取目标窗体的句柄编号！")
            self.finished_signal.emit(True)
            return

        if_end = info[12]
        debug_status = info[13]
        interval_seconds = int(info[4])
        start_match = StartMatch(info[:12])
        print("初始化中…")

        # 对UI参数初始化，计算匹配的次数、导入需要检测的目标图片
        loop_times, screen_method, target_info, t1 = start_match.set_init()

        # 检测游戏时间是否太晚，进行提示
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
            progress = int((i + 1) / loop_times * 100)
            self.progress_val_signal.emit(progress)

            # 下面是Qthread中的循环匹配代码--------------

            # 开始匹配
            run_status, match_status = start_match.start_match_click(i, loop_times, screen_method, target_info,
                                                                     debug_status)

            # 计算匹配成功的次数,每成功匹配100次，休息2分钟，避免异常
            if match_status:
                success_times = success_times + 1
                print(f"已成功匹配 [ {success_times} ] 次")
                if success_times % 100 == 0:
                    for t in range(120):
                        print(f"已成功匹配100次，为防止异常，[ {120 - t} ] 秒后继续……")
                        sleep(1)

            # 检测是否正常运行，否则终止
            if not run_status:
                self.mutex.unlock()
                self.finished_signal.emit(True)
                break

            # 每匹配11次后，随机在窗口点击3次，防止点击太规律被识别为异常
            # if (i + 1) % 11 == 0:
            #     print("----------------每循环11次后模拟真实点击-----------------")
            #     start_match.simulates_real_clicks()
            #     start_match.simulates_real_clicks()
            #     start_match.simulates_real_clicks()

            # 判断是否结束
            if i == loop_times - 1:
                print("---已执行完成!---")
                self.end_do(if_end, info[2])
                self.mutex.unlock()
                self.finished_signal.emit(True)
                break
            else:
                # 倒推剩余时间（时分秒格式）
                ts = uniform(0.1, 1.5)  # 设置随机延时，防检测
                remaining_time = time_transform(int(((loop_times - i - 1) / (60 / (interval_seconds + t1))) * 60 - ts))
                print(f"--- [ {round(interval_seconds + ts, 2)} ] 秒后继续，[ {remaining_time} ] 后结束---")
                print("----------------------------------------------------------")
                sleep(interval_seconds + ts)

            # 上面是Qthread中的循环匹配代码--------------

            # 线程锁off
            self.mutex.unlock()

        # 运行结束重置按钮可用状态
        self.finished_signal.emit(True)


def except_out_config(exc_type, value, tb):
    print('Error Information:')
    print('Type:', exc_type)
    print('Value:', value)
    print('Traceback:', tb)


if __name__ == '__main__':
    if windll.shell32.IsUserAnAdmin():  # 是否以管理员身份运行
        sys.excepthook = except_out_config
        app = QApplication(sys.argv)
        myWindow = MainWindow()
        myWindow.setWindowTitle('痒痒鼠护肝小助手')  # 设置窗口标题
        myWindow.show()
        sys.exit(app.exec_())
    else:
        windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)  # 调起UAC以管理员身份重新执行
        sys.exit(0)
