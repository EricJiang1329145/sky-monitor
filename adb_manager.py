# ADB设备管理模块
# 本模块封装了ADB（Android Debug Bridge）命令的调用
# 提供设备列表查询和屏幕截图功能
# 注意：本模块已重构，实际功能由 screenshot.py 模块提供
from config import ADB_PATH

# 导入截图工具模块
from screenshot import take_screenshot as screenshot_take_screenshot
from screenshot import list_devices as screenshot_list_devices
from screenshot import tap as screenshot_tap

class ADBManager:
    """ADB管理器类，用于与安卓设备进行通信"""
    def __init__(self):
        # 初始化ADB命令路径
        self.adb_path = ADB_PATH
    
    def get_devices(self):
        """获取当前通过ADB连接的所有安卓设备列表
        
        Returns:
            list: 设备ID列表，每个元素是一个字符串格式的设备ID
                  如果获取失败或没有设备，返回空列表
        """
        # 调用 screenshot 模块的 list_devices 函数
        return screenshot_list_devices(self.adb_path)
    
    def take_screenshot(self, device_id=None):
        """执行安卓设备屏幕截图并返回图像数据
        
        Args:
            device_id: 要截图的设备ID，如果为None则使用默认设备
        
        Returns:
            numpy.ndarray: OpenCV格式的图像数据（BGR格式的numpy数组）
                          如果截图失败则返回None
        """
        # 调用 screenshot 模块的 take_screenshot 函数
        return screenshot_take_screenshot(device_id, self.adb_path)
    
    def tap(self, x, y, device_id=None):
        """在安卓设备屏幕上模拟点击操作
        
        Args:
            x: 点击的X坐标
            y: 点击的Y坐标
            device_id: 要操作的设备ID，如果为None则使用默认设备
        
        Returns:
            bool: 点击操作是否成功
        """
        # 调用 screenshot 模块的 tap 函数
        return screenshot_tap(x, y, device_id, self.adb_path)
