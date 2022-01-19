import random
import time
import win32gui
from Module_DoClick import DoClick
from Module_GetScreenCapture import GetScreenCapture
from Module_GetTargetPic import GetTargetPic
from Module_GetTargetPosSift import GetTargetPosSift
from Module_HandleSet import HandleSet


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
    # return hand_win
    return hand_win_title


def start_click(connect_mod, modname, hwd_title, move_var=20, interval_seconds=5, loop_min=120, compress_val=0.5):
    modname = modname
    hwd_title = hwd_title  # 句柄名称
    # hwd_title = get_active_window()
    move_var = int(move_var)  # 随机偏移量
    interval_seconds = int(interval_seconds)  # 每次执行间隔秒数
    loop_min = int(loop_min)  # 执行分钟数
    compress_val = float(compress_val)

    # 获取目标图片路径
    print('目标图片读取中……')
    target_pic = GetTargetPic(modname)
    target_pic_sift, target_pic_hw, target_pic_name, target_pic_path = target_pic.get_target_sift
    print('目标图片特征点提取成功！')
    # print(target_pic_info)
    print(f'目标图片读取完成！\n{target_pic_name}')

    # 计算循环次数、时间
    t1 = len(target_pic_path) / 30  # 每次循环匹配找图需要消耗的时间, 脚本每次匹配一般平均需要2.5秒（30个匹配目标）
    loop_min = int(loop_min)  # 初始化执行时间，因为不能使用字符串，所以要转一下
    interval_seconds = int(interval_seconds)  # 初始化间隔秒数
    loop_times = int(loop_min * (60 / (interval_seconds + t1)))  # 计算要一共要执行的次数

    if connect_mod == '电脑端':
        pos = None
        # 句柄信息获取
        handle_set = HandleSet(hwd_title)
        handle_num = handle_set.get_handle_num
        handle_width = handle_set.get_handle_pos[2] - handle_set.get_handle_pos[0]  # 右x - 左x 计算宽度
        handle_height = handle_set.get_handle_pos[3] - handle_set.get_handle_pos[1]  # 下y - 上y 计算高度
        handle_set.set_priority(random.randint(3, 5))  # 设置目标程序优先级，避免程序闪退

        get_screen_capture = GetScreenCapture(handle_num, handle_width, handle_height, compress_val)  # 截图方法实例化

        for i in range(loop_times):
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            progress = format((i + 1) / loop_times, '.2%')
            # print(f"当前进度：{progress}")
            print(f"第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次, 当前进度 [ {progress} ], 当前时间 [ {now_time} ]")

            # 主要功能，截图、匹配、点击
            handle_set.handle_is_active()  # 检测句柄是否存在，不存在会退出
            screen_capture = get_screen_capture.screen_capture()  # 获取截图，保存到内存

            print("匹配中……")
            screen_capture_sift = GetTargetPosSift.get_sift(screen_capture)  # 提取特征点
            u = 0
            for u in range(len(target_pic_path)):
                # print('正在匹配：', target_pic_name[u])
                pos = GetTargetPosSift.get_target_pos_sift(target_pic_sift[u], screen_capture_sift,
                                                           target_pic_hw[u])  # 获取目标图片的坐标
                if pos is not None:
                    # t_target_pic_hw = [target_pic_hw[u][0] * compress_val, target_pic_hw[u][1] * compress_val]
                    # GetTargetPosSift.draw_target_pos(pos, screen_capture, t_target_pic_hw)  # 画识别到的位置
                    break
            if pos is not None:
                pos = [int(pos[0] / compress_val), int(pos[1] / compress_val)]
                print(f'匹配成功！第[ {u} ]张图片[ {target_pic_name[u]} ], 坐标{pos}')
                click = DoClick(pos, move_var, handle_num)
                click.do_click()  # 随机范围内点击坐标

            else:
                print('匹配失败！')

            # 判断是否已经结束
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

    elif connect_mod == '手机端-ADB':
        pos = None
        # handle_set = HandleSet()
        # handle_set.adb_test()  # 检测手机是否连接

        # 开始循环执行
        for i in range(loop_times):
            now_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            progress = format((i + 1) / loop_times, '.2%')
            # print(f"当前进度：{progress}")
            print(f"第 [ {i + 1} ] 次匹配, 还剩 [ {loop_times - i - 1} ] 次, 当前进度 [ {progress} ], 当前时间 [ {now_time} ]")

            # 主要功能，截图、找图、点击
            screen_capture = GetScreenCapture.adb_screen(compress_val)  # 通过adb，保存手机截图到内存中
            # GetScreenCapture.show_screen_capture(screen_capture)  # 显示截图
            # GetScreenCapture.save_screen_capture(screen_capture)  # 保存截图
            print("识别中……")
            screen_capture_sift = GetTargetPosSift.get_sift(screen_capture)  # 提取特征点
            u = 0
            for u in range(len(target_pic_path)):
                # print('正在匹配：', target_pic_name[u])
                pos = GetTargetPosSift.get_target_pos_sift(target_pic_sift[u], screen_capture_sift,
                                                           target_pic_hw[u])  # 获取目标图片的坐标
                if pos is not None:
                    # t_target_pic_hw = [target_pic_hw[u][0] * compress_val, target_pic_hw[u][1] * compress_val]
                    # GetTargetPosSift.draw_target_pos(pos, screen_capture, t_target_pic_hw)  # 画识别到的位置
                    break
            if pos is not None:
                pos = [int(pos[0] / compress_val), int(pos[1] / compress_val)]
                print(f'匹配成功！第[ {u} ]张图片：[ {target_pic_name[u]} ], 坐标{pos}')
                click = DoClick(pos, move_var)
                click.adb_click()

            else:
                print('匹配失败！')

            # 判断是否已经结束
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
