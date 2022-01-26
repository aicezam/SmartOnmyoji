# -*- coding: utf-8 -*-
import os
import win32con
import win32gui
from gooey import Gooey, GooeyParser
from modules.ModuleStart import start_click


@Gooey(
    richtext_controls=True,  # 打开终端对颜色支持
    program_name="YYS护肝小能手",  # 程序名称
    encoding="utf-8",  # 设置编码格式，打包的时候遇到问题
    progress_regex=r"^当前进度：(\d+)%$",  # 正则，用于模式化运行时进度信息
    # progress_regex=r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
    # progress_expr="current / total * 100",
    language='chinese',
)
def main():
    settings_msg = '选择模式，设置运行长，点击开始！'
    parser = GooeyParser(description=settings_msg)

    parser.add_argument('connect_mod', metavar='连接模式', help='请选择在电脑使用还是手机端使用',
                        choices=['windows-程序', 'Android-Adb'], default='windows-程序')

    parser.add_argument('hwd_title', metavar='窗口标题名称', help='请输入程序窗口标题', default='阴阳师-网易游戏')
    parser.add_argument("modname", metavar='选择功能', help="请选择功能模式", choices=['御魂', '探索', '突破', '活动', '觉醒', '百鬼夜行', '微信红包'],
                        default='御魂')

    parser.add_argument('loop_min', metavar='运行时长', help='请输入运行分钟数', default=120)
    parser.add_argument('interval_seconds', metavar='间隔秒数', help='请输入间隔秒数', default=5)
    parser.add_argument('click_deviation', metavar='偏移量', help='请输入点击偏移范围', default=10)

    parser.add_argument("match_method", metavar='匹配方法', help="模板匹配的准确度高些，但是程序的窗口大小改变就需要重新截检测目标图片",
                        choices=['模板匹配', '特征点匹配'], default='模板匹配')

    parser.add_argument('compress_val', metavar='压缩率', help='数值越低精度越低，匹配速度越快，1为不压缩', default=1)

    parser.add_argument("end_do", metavar='执行完成后操作', help="选择运行完成后需执行的操作",
                        choices=['不执行任何操作', '关机', '关闭目标程序', '关闭脚本'], default='不执行任何操作')

    # parser.add_argument("start_p", metavar='是否启动程序', help="请选择是否启动该程序",
    #                     choices=['不启动', '启动'], default='不启动')
    # parser.add_argument('exe_path', metavar='目标程序', help="选择目标程序路径", widget="FileChooser",
    #                     default=r'D:\Program Files (x86)\Onmyoji\Launch.exe')

    args = parser.parse_args()

    # if args.start_p == '启动':
    #     os.popen(args.exe_path)  # 启动程序
    #     print("程序启动中，启动完成后，重新开始！")
    #     sys.exit(0)
    # elif args.start_p == '不启动':

    start_click(args.connect_mod, args.modname, args.hwd_title, args.click_deviation, args.interval_seconds,
                args.loop_min, args.compress_val, args.match_method)

    if args.end_do == '关机':
        print("已完成，60秒后自动关机！")
        os.system('shutdown /s /t 60')
    elif args.end_do == '不执行任何操作':
        print("已完成！")
    elif args.end_do == '关闭目标程序':
        print("已完成，%s即将退出！" % args.hwnd)
        hwnd1 = win32gui.FindWindow(None, args.hwnd)
        win32gui.PostMessage(hwnd1, win32con.WM_CLOSE, 0, 0)  # 关闭程序
    elif args.end_do == '关闭脚本':
        print("已完成，%s即将退出！" % 'YYS护肝小能手')
        hwnd2 = win32gui.FindWindow(None, 'YYS护肝小能手')
        win32gui.PostMessage(hwnd2, win32con.WM_CLOSE, 0, 0)  # 关闭脚本


if __name__ == '__main__':
    main()
