# 配置文件
# 本文件包含应用程序的所有配置参数
# 修改这些参数可以调整程序的行为

# 截图频率（秒）
# 控制两次截图之间的时间间隔
# 较小的值会提高截图频率，但会增加CPU和存储负担
# 默认值为1秒，可以在UI中动态调整
DEFAULT_SCREENSHOT_INTERVAL = 1

# ADB命令配置
# ADB（Android Debug Bridge）可执行文件的路径
# 如果ADB已添加到系统PATH中，可以直接使用"adb"
# 否则需要指定完整路径，例如："C:/Android/sdk/platform-tools/adb"
ADB_PATH = "adb"

# 图像显示配置
# 控制截图在UI界面中显示的尺寸
# 这些尺寸仅影响显示效果，不影响实际保存的截图分辨率
IMAGE_DISPLAY_WIDTH = 320
IMAGE_DISPLAY_HEIGHT = 569  # 16:9 比例，适配常见手机屏幕比例
# 图像显示的宽高比（高度/宽度）
IMAGE_ASPECT_RATIO = IMAGE_DISPLAY_HEIGHT / IMAGE_DISPLAY_WIDTH

# 日志配置
# 日志级别，可选值：DEBUG, INFO, WARNING, ERROR, CRITICAL
# 当前设置为INFO级别，会输出INFO及以上级别的日志
LOG_LEVEL = "INFO"
