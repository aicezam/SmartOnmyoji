# SmartOnmyoji

> 虽然有很多大佬有写过类似的脚本，但其实这是个学习项目，通过这个项目基本花了一个月学会了python，这里注释会比较完整，代码虽然不够简洁，功能也不够丰富，但是想要用更加优雅的方法继续完善~

### 安装方法
启动windows命令行终端cmd或powershell，安装python，克隆仓库，进入根目录下，安装 requirements.txt 依赖库：pywin32、opencv-python、PyQt5、PyAutoGUI
```
1. python安装（版本大于3.7.6都行）：https://www.python.org/ftp/python/3.7.6/python-3.7.6-amd64.exe
2. 克隆或下载本项目
3. 运行power shell 或 cmd 进入主目录：cd .\SmartOnmyoji\ 安装依赖库：pip install -r requirements.txt
```

### 使用方法
- 使用前警告：请谨慎使用辅助脚本
- 先安装python3.7（基于 python3.7.6 开发）, 再安装上述依赖库
- 【管理员身份运行IDE或CMD或powershell】, 执行 python smart_onmyoji_start.py
- 阴阳师电脑版使用模板匹配时，不要调分辨率，如果要调分辨率，需要重新截图，然后放到/img目录的对应文件夹下面
- 如果发现总是匹配失败，可能是/img模板图片大小问题，可以重新截图，或使用特征点匹配方法，或切换为 **兼容模式** ，也可自行调试代码看截图是否成功，找看看是哪儿的问题
- **支持后台点击**，但不支持部分窗体（如网易MuMu、网易云游戏），可以切换为 **兼容模式** 以兼容这些窗体，兼容模式下不能后台点击
- 支持安卓手机，需用USB连上电脑，并打开手机调试模式，使用 安卓-ADB 模式时，可以使用特征点匹配方式，不过有点慢，要不就重新截图替换/img目录下的全部图片
- 特征点匹配方法适用窗体中没有多个相同的待检测目标，而且待检测目标与周围差异比较大，否则会不准确
- 压缩率设置在0.6左右时，准确率和速度能兼顾，如果对匹配速度可以忍受，不建议修改压缩率（压缩率越低，准确度越低）
- 原理是定时截图，然后找到图片坐标，然后随机延迟并点击附近随机坐标
- 除了阴阳师，也可以其他点点点的游戏，比如连手机抢微信红包啥的~
- 只要每天正常时间内，不刷满300次，理论上不会收到鬼使黑的信，**请按正常时间运行脚本，偶尔还是用一下樱饼，使用脚本有被封号的风险**
- 不想使用cmd编译的，可以自行编译为win程序，编译后需要把img文件夹和modules文件夹放进根目录中，手动编译可使用：pyinstaller --distpath Release/ -w -i logo.ico --clean .\smart_onmyoji_start.py

### 功能预览

- UI界面、可配置参数：可修改执行时间、间隔时间、匹配方式、压缩率、执行完成后的操作等

![image](https://user-images.githubusercontent.com/39365915/160885083-5ffc81ad-7779-4a16-a82b-c0cf4426122b.png)



- 模板匹配方法：不能随意调整窗体分辨率，模板图片与窗体中的部分必须一致

![image](https://user-images.githubusercontent.com/39365915/158008385-6d661a3f-51a7-44c0-9b8b-b872cfed60eb.png)



- 特征点匹配方法：可以随便调整窗体分辨率，也可以对目标图片旋转、缩放，都可以匹配到

![image](https://user-images.githubusercontent.com/39365915/158009257-97dbc188-aa5a-4eb6-a559-03cae7e0a5d1.png)



### 计划
- [x] 支持abd模式，电脑连手机自动截图
- [x] 支持切换选择匹配模式，特征点匹配（自适应分辨率，不用重新截图，但速度略慢，且不太准确）、模板匹配（速度更快，更精确，但麻烦，不能改分辨率）
- [x] 加载图片时记录所有图片的特征信息，优化识别速度
- [x] 支持压缩图片以提升脚本识别速度，默认为1不压缩
- [x] 所有图片转灰度图，并保存在内存里，识别速度快多了
- [x] 修复中文路径报错的问题
- [x] 兼容所有windows窗体的截图和点击
- [x] 使用QT5重构UI界面
- [x] 增加选择自定义匹配图片文件夹的功能
- [ ] ~~优化百鬼夜行的选式神和砸豆子逻辑（yolov5），尝试跑了个模型，但是效果不好，会导致程序特别臃肿，而且运行速度特别慢~~ 
- [ ] 增加御灵、地域鬼王、逢魔、秘闻副本等默认场景
- [ ] 兼容常用安卓模拟器后台点击（已兼容雷电模拟器）

### 更新记录
- 2022年4月26日 调整部分默认参数，更新雷电模拟器后台点击方法（感谢 @zyhazwraith 提供的思路 https://github.com/aicezam/SmartOnmyoji/issues/7 ）
- 2022年4月07日 更新防检测异常的逻辑（虽然可能没什么用）
- 2022年4月03日 增加选择自定义匹配目标图片文件夹的功能
- 2022年4月02日 修复bug：停止匹配后，偶尔会触发继续匹配运行的bug
- 2022年3月31日 移除重复的依赖，运行时检测是否使用管理员身份运行，脚本默认包含adb程序，为代码增加部分注释
- 2022年3月25日 使用PYQT5重构GUI，使用pyautogui替换pymouse库
- 2022年3月12日 增加兼容模式，支持在所有的 windows窗体 截图和点击，包括模拟器、云游戏、scrcpy 等， 兼容模式下 **窗体会自动置顶，不再支持后台点击**
- 2022年3月10日 增加鼠标点击选择窗体的功能，（窗口标题名称 - 下拉选择 “开始后鼠标点击选择窗体”，5秒内点击要匹配窗体）
- 2022年1月27日 修复opencv在中文路径下报错的问题
- 2022年1月26日 重新加入模板匹配方法，并设为默认方法，因为发现匹配速度有点慢，准确率不太高
- 2022年1月19日 优化匹配速度，截图和读取模板图片时先转灰度，支持对截图设置压缩率，进一步优化匹配速度；更换全部匹配方法为sift匹配；增加对安卓设备的支持，通过ADB实现；
- 2022年1月15日 首次提交，自动截图、匹配、点击

### 其他说明
仅作学习用途，请勿用于其他非法途径！
