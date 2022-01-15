import os
import win32con
import win32gui
from gooey import Gooey, GooeyParser
from AutoClick import auto_click

"""
窗体程序
"""


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

    parser.add_argument('hwnd', metavar='窗口标题名称', help='请输入程序窗口标题', default='阴阳师-网易游戏')
    parser.add_argument("mode", metavar='选择功能', help="请选择功能模式", choices=['御魂', '探索', '突破', '活动', '觉醒', '百鬼夜行', '微信红包'],
                        default='御魂')  # 百鬼夜行，要么多截点图（每个式神的脚+桥中间的图案，可以辨识），要么单独写个百鬼夜行的方法
    parser.add_argument('loop_min', metavar='运行时长', help='请输入运行分钟数', default=120)
    parser.add_argument('interval_seconds', metavar='间隔秒数', help='请输入间隔秒数', default=5)
    parser.add_argument('move_var', metavar='偏移量', help='请输入点击偏移范围', default=20)

    parser.add_argument("end_do", metavar='执行完成后操作', help="请选择运行完成后需执行的操作",
                        choices=['不执行任何操作', '关机', '关闭目标程序'], default='不执行任何操作')

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

    auto_click(args.mode, args.hwnd, args.move_var, args.interval_seconds, args.loop_min)  # 执行脚本

    # 下面这个可以作为函数放在另一个文件里面
    if args.end_do == '关机':
        print("已完成，60秒后自动关机！")
        os.system('shutdown /s /t 60')
    elif args.end_do == '不执行任何操作':
        print("已完成！")
    elif args.end_do == '关闭目标程序':
        print("已完成，%s即将退出！" % args.hwnd)
        hwnd1 = win32gui.FindWindow(None, args.hwnd)
        win32gui.PostMessage(hwnd1, win32con.WM_CLOSE, 0, 0)  # 关闭程序


if __name__ == '__main__':
    main()
