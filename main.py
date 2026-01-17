# 主程序入口
# 本程序用于通过ADB连接安卓设备，定时截取屏幕并保存到本地
# 支持多设备选择，实时显示截图，并记录操作日志
import tkinter as tk
import threading
import time
from datetime import datetime
from adb_manager import ADBManager
from ui import AppUI
from config import DEFAULT_SCREENSHOT_INTERVAL

# 导入截图工具模块
from screenshot import save_screenshot as screenshot_save_screenshot

# 截图保存目录
SCREENSHOT_DIR = "screenshots"

class SkyMonitorApp:
    """光遇消息检测应用主类"""
    def __init__(self):
        # 创建主窗口
        self.root = tk.Tk()
        
        # 初始化ADB管理器，用于与安卓设备通信
        self.adb_manager = ADBManager()
        
        # 初始化UI界面，创建所有界面组件
        self.ui = AppUI(self.root)
        
        # 初始化变量
        self.monitor_thread = None  # 监控线程对象
        self.is_running = False  # 监控运行状态标志
        
        # 绑定事件处理，将按钮点击事件与处理函数关联
        self.bind_events()
        
        # 初始刷新设备列表，自动检测已连接的设备
        self.refresh_devices()
    
    def bind_events(self):
        """绑定按钮点击事件到对应的处理函数"""
        # 刷新设备按钮：点击时调用 refresh_devices 方法
        self.ui.refresh_btn.configure(command=self.refresh_devices)
        
        # 开始截图按钮：点击时调用 start_monitoring 方法
        self.ui.start_btn.configure(command=self.start_monitoring)
        
        # 停止截图按钮：点击时调用 stop_monitoring 方法
        self.ui.stop_btn.configure(command=self.stop_monitoring)
        
        # 应用间隔按钮：点击时应用新的截图间隔设置
        self.ui.apply_interval_btn.configure(command=self.apply_interval)
    
    def refresh_devices(self):
        """刷新连接的安卓设备列表"""
        # 在日志中显示正在刷新的提示信息
        self.ui.log_message("正在刷新设备列表...")
        
        # 通过ADB管理器获取当前连接的所有设备
        devices = self.adb_manager.get_devices()
        
        # 更新UI界面的设备下拉列表
        self.ui.update_device_list(devices)
        
        # 在日志中显示发现的设备数量
        self.ui.log_message(f"发现 {len(devices)} 个设备")
    
    def start_monitoring(self):
        """开始截图监控功能"""
        # 检查是否有设备选择
        selected_device = self.ui.selected_device.get()
        if not selected_device:
            # 如果没有选择设备，提示用户并返回
            self.ui.log_message("请先选择设备")
            return
        
        # 设置运行状态为True
        self.is_running = True
        
        # 更新UI状态，禁用开始按钮，启用停止按钮
        self.ui.set_monitoring_state(True)
        
        # 更新状态显示为"截图中"
        self.ui.update_status("截图中")
        
        # 在日志中记录开始监控的信息
        self.ui.log_message("开始截图监控")
        
        # 创建并启动监控线程
        # 使用线程避免阻塞主UI界面
        self.monitor_thread = threading.Thread(target=self.monitor_loop, args=(selected_device,))
        self.monitor_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        self.monitor_thread.start()  # 启动线程
    
    def stop_monitoring(self):
        """停止截图监控功能"""
        # 设置运行状态为False，监控循环会检测到此标志并退出
        self.is_running = False
        
        # 更新UI状态，启用开始按钮，禁用停止按钮
        self.ui.set_monitoring_state(False)
        
        # 更新状态显示为"已停止"
        self.ui.update_status("已停止")
        
        # 在日志中记录停止监控的信息
        self.ui.log_message("停止截图监控")
    
    def apply_interval(self):
        """应用新的截图间隔设置"""
        interval = self.ui.get_interval()
        self.ui.log_message(f"截图间隔已设置为 {interval} 秒")
    
    def monitor_loop(self, device_id):
        """监控循环函数，在独立线程中运行，定时执行截图操作
        
        Args:
            device_id: 要截图的安卓设备ID
        """
        # 持续循环，直到 is_running 标志变为 False
        while self.is_running:
            try:
                # 在日志中显示正在截图的提示
                self.ui.log_message("正在截图...")
                
                # 通过ADB管理器执行截图操作
                screenshot = self.adb_manager.take_screenshot(device_id)
                
                if screenshot is not None:
                    # 截图成功，使用 root.after 在主线程中更新图像显示
                    # 这是因为Tkinter的UI更新必须在主线程中进行
                    self.root.after(0, self.ui.update_images, screenshot)
                    
                    # 生成带时间戳的文件名，格式：screenshot_YYYYMMDD_HHMMSS_mmm.png
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"{SCREENSHOT_DIR}/screenshot_{timestamp}.png"
                    
                    # 保存截图到本地文件（不添加文本标注，由UI负责显示）
                    self.save_screenshot(screenshot, filename)
                    
                    # 在日志中显示截图成功的信息
                    self.ui.log_message(f"截图成功，已保存到 {filename}")
                else:
                    # 截图失败，在日志中显示错误信息
                    self.ui.log_message("截图失败")
                
                # 等待指定的截图间隔时间（秒）
                interval = self.ui.get_interval()
                time.sleep(interval)
            
            except Exception as e:
                # 捕获异常并记录错误信息
                self.ui.log_message(f"监控错误: {e}")
                # 短暂等待1秒后继续尝试，避免错误循环
                time.sleep(1)
    
    def save_screenshot(self, screenshot, filename, label=None):
        """将截图保存到本地文件
        
        Args:
            screenshot: OpenCV格式的图像数据（numpy数组）
            filename: 要保存的文件路径
            label: 要在截图上添加的文本标签
        """
        # 调用 screenshot 模块的 save_screenshot 函数
        result = screenshot_save_screenshot(screenshot, filename, label)
        if result is None:
            # 如果保存失败，在日志中记录错误信息
            self.ui.log_message(f"保存截图失败")
    
    def run(self):
        """运行应用程序"""
        self.root.mainloop()

if __name__ == "__main__":
    app = SkyMonitorApp()
    app.run()
