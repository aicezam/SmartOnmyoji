# -*- coding: utf-8 -*-
# get pos by template matching and sift matching
import time

from numpy import int32, float32
from cv2 import cv2
from modules.ModuleImgProcess import ImgProcess
from modules.ModuleGetConfig import ReadConfigFile

rc = ReadConfigFile()
other_setting = rc.read_config_other_setting()


class GetPosByTemplateMatch:
    def __init__(self):
        super(GetPosByTemplateMatch, self).__init__()

    @staticmethod
    def get_pos_by_template(screen_capture, target_pic, debug_status):
        """
        模板匹配，速度快，但唯一的缺点是，改变目标窗体后，必须重新截取模板图片才能正确匹配
        :return: 返回坐标(x,y) 与opencv坐标系对应，以及与坐标相对应的图片在模板图片中的位置
        """
        screen_width = screen_capture.shape[1]
        screen_high = screen_capture.shape[0]
        # print("<br>"+len(target_pic))

        # 获取目标点位置
        pos = None
        val = 0.90  # 设置相似度
        i = 0
        # print("<br>正在匹配…")
        for i in range(len(target_pic)):
            # print(i)
            pos = GetPosByTemplateMatch.template_matching(screen_capture,
                                                          target_pic[i],
                                                          screen_width,
                                                          screen_high,
                                                          val,
                                                          debug_status,
                                                          i)
            if pos is not None:
                if debug_status:
                    if other_setting[5]:
                        draw_img = ImgProcess.draw_pos_in_img(screen_capture, pos, [screen_high / 10, screen_width / 10])
                        ImgProcess.show_img(draw_img)
                break
        return pos, i

    @staticmethod
    def template_matching(img_src, template, screen_width, screen_height, val, debug_status, i):
        """获取坐标"""
        # img_src = cv2.cvtColor(img_src, cv2.COLOR_BGR2GRAY)
        # template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        if (img_src is not None) and (template is not None):
            img_tmp_height = template.shape[0]
            img_tmp_width = template.shape[1]  # 获取模板图片的高和宽
            img_src_height = img_src.shape[0]
            img_src_width = img_src.shape[1]  # 匹配原图的宽高
            res = cv2.matchTemplate(img_src, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)  # 最小匹配度，最大匹配度，最小匹配度的坐标，最大匹配度的坐标
            if debug_status:
                print(f"<br>第 [ {i+1} ] 张图片，匹配分数：[ {round(max_val,2)} ]")
            if max_val >= val:  # 计算相对坐标
                position = [int(screen_width / img_src_width * (max_loc[0] + img_tmp_width / 2)),
                            int(screen_height / img_src_height * (max_loc[1] + img_tmp_height / 2))]
                return position
            else:
                return None


class GetPosBySiftMatch:
    def __init__(self):
        super(GetPosBySiftMatch, self).__init__()

    @staticmethod
    def get_pos_by_sift(target_sift, screen_sift, target_hw, target_img, screen_img, debug_status):
        """
        特征点匹配，准确度不好说，用起来有点难受，不是那么准确（比如有两个按钮的情况下），但是待检测的目标图片不受缩放、旋转的影响
        :return: 返回坐标(x,y) 与opencv坐标系对应，以及与坐标相对应的图片在所有模板图片中的位置
        """
        # print("正在匹配…")
        pos = None
        i = 0
        for i in range(len(target_img)):
            # print(i)
            pos = GetPosBySiftMatch.sift_matching(target_sift[i], screen_sift, target_hw[i], target_img[i], screen_img,
                                                  debug_status, i)
            if pos is not None:
                break
        return pos, i

    @staticmethod
    def sift_matching(target_sift, screen_sift, target_hw, target_img, screen_img, debug_status, i):
        """
        特征点匹配，准确度不好说，用起来有点难受，不是那么准确（比如有两个按钮的情况下），但是待检测的目标图片不受缩放、旋转的影响
        :param target_sift: 目标的特征点信息
        :param screen_sift: 截图的特征点信息
        :param target_hw: 目标的高和宽
        :param target_img: cv2格式的目标图片
        :param screen_img: cv2格式的原图
        :param debug_status: 调试模式
        :param i: 第几次匹配
        :return: 返回坐标(x,y) 与opencv坐标系对应
        """
        # 利用创建好的特征点检测器去检测两幅图像的特征关键点，
        # 其中kp含有角度、关键点坐标等多个信息，具体怎么提取出坐标点的坐标不清楚，
        # des是特征描述符，每一个特征点对应了一个特征描述符，由一维特征向量构成
        kp1 = target_sift[0]
        des1 = target_sift[1]
        kp2 = screen_sift[0]
        des2 = screen_sift[1]
        min_match_count = 10  # 匹配到的角点数量大于这个数值即匹配成功
        flann_index_kdtree = 0  # 设置Flann参数，这里是为了下一步匹配做准备
        index_params = dict(algorithm=flann_index_kdtree, trees=4)  # 指定匹配的算法和kd树的层数
        search_params = dict(checks=50)  # 指定返回的个数

        # 根据设置的参数创建特征匹配器
        flann = cv2.FlannBasedMatcher(index_params, search_params)

        # 利用创建好的特征匹配器利用k近邻算法来用模板的特征描述符去匹配图像的特征描述符，k指的是返回前k个最匹配的特征区域
        # 返回的是最匹配的两个特征点的信息，返回的类型是一个列表，列表元素的类型是Dmatch数据类型，具体是什么我也不知道
        matches = flann.knnMatch(des1, des2, k=2)

        # 设置好初始匹配值，用来存放特征点
        good = []
        for m, n in matches:
            '''
            比较最近邻距离与次近邻距离的SIFT匹配方式：
            取一幅图像中的一个SIFT关键点，并找出其与另一幅图像中欧式距离最近的前两个关键点，在这两个关键点中，如果最近的距离除以次近的距离得到的比率ratio
            少于某个阈值T，则接受这一对匹配点。因为对于错误匹配，由于特征空间的高维性，相似的距离可能有大量其他的错误匹配，从而它的ratio值比较高。
            显然降低这个比例阈值T，SIFT匹配点数目会减少，但更加稳定，反之亦然。Lowe推荐ratio的阈值为0.8，但作者对大量任意存在尺度、旋转和亮度变化的两幅图片进行匹配，
            结果表明ratio取值在0. 4~0. 6 之间最佳，小于0.4的很少有匹配点，大于0. 6的则存在大量错误匹配点，所以建议ratio的取值原则如下:
            ratio=0. 4：对于准确度要求高的匹配；
            ratio=0. 6：对于匹配点数目要求比较多的匹配；
            ratio=0. 5：一般情况。 
            '''
            if m.distance < 0.6 * n.distance:  # m表示大图像上最匹配点的距离，n表示次匹配点的距离，若比值小于0.5则舍弃
                good.append(m)
        if debug_status:
            print(f"<br>第 [ {i+1} ] 张图片，匹配角点数量：[ {len(good)} ] ,目标数量：[ {min_match_count} ]")
        if len(good) > min_match_count:
            src_pts = float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            m, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            # 绘制匹配成功的连线
            if debug_status:
                if other_setting[5]:
                    matches_mask = mask.ravel().tolist()  # ravel方法将数据降维处理，最后并转换成列表格式
                    draw_params = dict(matchColor=(0, 255, 0),  # draw matches in green color
                                       singlePointColor=None,
                                       matchesMask=matches_mask,  # draw only inliers
                                       flags=2)
                    img3 = cv2.drawMatches(target_img, kp1, screen_img, kp2, good, None, **draw_params)  # 生成cv2格式图片
                    img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)  # 转RGB
                    ImgProcess.show_img(img3)  # 测试显示

            # 计算中心坐标
            h, w = target_hw
            pts = float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
            if m is not None:
                dst = cv2.perspectiveTransform(pts, m)
                arr = int32(dst)
                pos_arr = arr[0] + (arr[2] - arr[0]) // 2
                pos = (int(pos_arr[0][0]), int(pos_arr[0][1]))
                return pos
            else:
                return None
        else:
            return None
