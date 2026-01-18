# ADB设备管理模块
# 本模块封装了ADB（Android Debug Bridge）命令的调用
# 提供设备列表查询、屏幕截图、点击和文本输入功能
from config import ADB_PATH

# 导入截图工具模块
from screenshot import take_screenshot as screenshot_take_screenshot
from screenshot import list_devices as screenshot_list_devices
from screenshot import tap as screenshot_tap

# 导入键盘输入模块
from keyboard import input_text as keyboard_input_text
from keyboard import get_devices as keyboard_get_devices

class ADBManager:
    """ADB管理器类，用于与安卓设备进行通信"""
    def __init__(self):
        # 初始化ADB命令路径
        self.adb_path = ADB_PATH
    
    def get_devices(self):
        """获取当前通过ADB连接的所有安卓设备列表
        
        Returns:
            list: 设备信息字典列表，每个元素包含设备详细信息
                  如果获取失败或没有设备，返回空列表
        """
        # 调用 keyboard 模块的 get_devices 函数
        return keyboard_get_devices(self.adb_path)
    
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
    
    def input_text(self, text, device_id=None, method='adbkeyboard', send_enter=True, tap_coords=None):
        """在安卓设备上输入文本
        
        Args:
            text: 要输入的文本内容
            device_id: 要操作的设备ID，如果为None则使用默认设备
            method: 输入方法，可选值：
                    - 'adbkeyboard': 使用ADBKeyboard（支持中文，但需要输入框有焦点）
                    - 'simple': 使用adb shell input text（只支持英文，不需要输入框有焦点）
            send_enter: 是否在输入文本后自动发送回车键，默认为True
            tap_coords: 点击屏幕坐标，格式为 (x, y)，如果提供则点击此位置而不是发送回车
        
        Returns:
            bool: 输入操作是否成功
        """
        # 调用 keyboard 模块的 input_text 函数
        # 默认使用 ADBKeyboard 方法，自动发送回车
        return keyboard_input_text(text, device_id, self.adb_path, method=method, send_enter=send_enter, tap_coords=tap_coords)
