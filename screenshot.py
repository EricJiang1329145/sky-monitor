# 截图工具模块
# 本模块提供安卓设备屏幕截图功能
# 可以作为模块被导入使用，也可以直接运行执行一次截图
import subprocess
import cv2
import sys
import os
import glob
from datetime import datetime
from config import ADB_PATH

# 截图保存目录
SCREENSHOT_DIR = "screenshots"

# 最大保留的截图数量
MAX_SCREENSHOTS = 2


def take_screenshot(device_id=None, adb_path=None):
    """执行安卓设备屏幕截图并返回图像数据
    
    Args:
        device_id: 要截图的设备ID，如果为None则使用默认设备
        adb_path: ADB命令路径，如果为None则使用配置文件中的路径
    
    Returns:
        numpy.ndarray: OpenCV格式的图像数据（BGR格式的numpy数组）
                      如果截图失败则返回None
    """
    # 如果没有指定ADB路径，使用配置文件中的路径
    if adb_path is None:
        adb_path = ADB_PATH
    
    # 设备上的临时截图文件路径
    device_screenshot_path = "/sdcard/screenshot_temp.png"
    
    try:
        # 第一步：在设备上执行截图并保存到临时文件
        cmd1 = [adb_path]
        if device_id:
            cmd1.extend(["-s", device_id])
        cmd1.extend(["shell", "screencap", "-p", device_screenshot_path])
        
        print(f"执行命令1: {' '.join(cmd1)}")
        result1 = subprocess.run(cmd1, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              timeout=10)
        
        if result1.returncode != 0:
            error_msg = result1.stderr.decode('utf-8', errors='ignore')
            print(f"ADB命令1返回错误码: {result1.returncode}")
            print(f"错误信息: {error_msg}")
            raise Exception(f"设备端截图失败: {error_msg}")
        
        # 第二步：将截图文件从设备拉取到电脑
        import tempfile
        import os
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        cmd2 = [adb_path]
        if device_id:
            cmd2.extend(["-s", device_id])
        cmd2.extend(["pull", device_screenshot_path, temp_filename])
        
        print(f"执行命令2: {' '.join(cmd2)}")
        result2 = subprocess.run(cmd2, 
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              timeout=10)
        
        if result2.returncode != 0:
            error_msg = result2.stderr.decode('utf-8', errors='ignore')
            print(f"ADB命令2返回错误码: {result2.returncode}")
            print(f"错误信息: {error_msg}")
            # 清理临时文件
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
            raise Exception(f"拉取截图文件失败: {error_msg}")
        
        # 第三步：读取截图文件
        img = cv2.imread(temp_filename)
        
        # 清理临时文件
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
        
        if img is None:
            raise Exception("图像读取失败，文件可能已损坏")
        
        return img
    except subprocess.TimeoutExpired:
        print("错误：命令执行超时")
        return None
    except Exception as e:
        # 如果截图过程中出现异常，打印错误信息并返回None
        print(f"截图失败: {e}")
        return None


def save_screenshot(screenshot, filename=None, label=None):
    """将截图保存到本地文件，并可选地添加文本标注
    
    Args:
        screenshot: OpenCV格式的图像数据（numpy数组）
        filename: 要保存的文件路径，如果为None则自动生成文件名
        label: 要在截图上添加的文本标签，例如"前帧"、"后帧"
    
    Returns:
        str: 保存的文件路径，如果保存失败则返回None
    """
    try:
        # 确保保存目录存在，如果不存在则创建
        os.makedirs(SCREENSHOT_DIR, exist_ok=True)
        
        # 如果没有指定文件名，自动生成带时间戳的文件名
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"{SCREENSHOT_DIR}/screenshot_{timestamp}.png"
        
        # 如果提供了标签，在截图上添加文本标注
        if label:
            # 在图像左上角添加文本
            # 文本位置：(x, y) = (20, 50)
            # 字体：使用默认字体
            # 字体大小：1.5
            # 颜色：白色 (255, 255, 255)
            # 线条粗细：3
            cv2.putText(screenshot, label, (20, 50), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                      (255, 255, 255), 3)
            
            # 添加黑色边框以增强可读性
            cv2.putText(screenshot, label, (20, 50), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                      (0, 0, 0), 5)
            cv2.putText(screenshot, label, (20, 50), 
                      cv2.FONT_HERSHEY_SIMPLEX, 1.5, 
                      (255, 255, 255), 3)
        
        # 使用OpenCV的imwrite函数保存图像为PNG格式
        cv2.imwrite(filename, screenshot)
        
        # 清理旧的截图文件
        cleanup_old_screenshots()
        
        return filename
    except Exception as e:
        # 如果保存失败，打印错误信息并返回None
        print(f"保存截图失败: {e}")
        return None


def cleanup_old_screenshots():
    """清理旧的截图文件，只保留最新的 MAX_SCREENSHOTS 个文件"""
    try:
        # 获取截图目录中所有的PNG文件
        png_files = glob.glob(f"{SCREENSHOT_DIR}/screenshot_*.png")
        
        # 如果文件数量超过最大保留数量，删除最旧的文件
        if len(png_files) > MAX_SCREENSHOTS:
            # 按修改时间排序，最旧的文件在前面
            png_files.sort(key=os.path.getmtime)
            
            # 计算需要删除的文件数量
            files_to_delete = len(png_files) - MAX_SCREENSHOTS
            
            # 删除最旧的文件
            for i in range(files_to_delete):
                os.remove(png_files[i])
                print(f"已删除旧截图: {png_files[i]}")
    except Exception as e:
        # 如果清理失败，打印错误信息但不影响主流程
        print(f"清理旧截图文件失败: {e}")


def get_screenshot_count():
    """获取当前截图目录中的截图数量
    
    Returns:
        int: 截图文件的数量
    """
    try:
        png_files = glob.glob(f"{SCREENSHOT_DIR}/screenshot_*.png")
        return len(png_files)
    except Exception as e:
        print(f"获取截图数量失败: {e}")
        return 0


def list_devices(adb_path=None):
    """获取当前通过ADB连接的所有安卓设备列表
    
    Args:
        adb_path: ADB命令路径，如果为None则使用配置文件中的路径
    
    Returns:
        list: 设备ID列表，每个元素是一个字符串格式的设备ID
              如果获取失败或没有设备，返回空列表
    """
    # 如果没有指定ADB路径，使用配置文件中的路径
    if adb_path is None:
        adb_path = ADB_PATH
    
    try:
        # 执行adb devices命令获取设备列表
        # capture_output=True表示捕获标准输出和错误输出
        # text=True表示以文本形式返回输出
        # timeout=5表示命令执行超时时间为5秒
        result = subprocess.run([adb_path, "devices"], 
                             capture_output=True, 
                             text=True, 
                             timeout=5)
        
        # 解析命令输出结果
        # 输出格式：第一行是标题，后续每行是一个设备信息
        lines = result.stdout.strip().split('\n')
        devices = []
        
        # 跳过第一行（标题行），从第二行开始处理
        for line in lines[1:]:
            line = line.strip()
            if line:
                # 设备行格式："设备ID\t设备状态"
                # 例如："12345678\tdevice"
                parts = line.split('\t')
                # 只添加状态为"device"的设备（表示设备已连接且可用）
                if len(parts) == 2 and parts[1] == "device":
                    devices.append(parts[0])
        
        return devices
    except Exception as e:
        # 如果执行过程中出现异常，打印错误信息并返回空列表
        print(f"获取设备列表失败: {e}")
        return []


if __name__ == "__main__":
    """当直接运行此文件时，执行一次截图并保存"""
    print("=== 安卓设备截图工具 ===")
    
    # 获取连接的设备列表
    print("正在获取设备列表...")
    devices = list_devices()
    
    if not devices:
        print("未检测到连接的设备，请确保：")
        print("1. 设备已通过USB连接到电脑")
        print("2. 设备已开启USB调试模式")
        print("3. 已授权电脑进行调试")
        sys.exit(1)
    
    # 显示设备列表
    print(f"\n发现 {len(devices)} 个设备：")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device}")
    
    # 选择设备
    selected_device = devices[0]
    if len(devices) > 1:
        print(f"\n默认使用第一个设备: {selected_device}")
        print("如需使用其他设备，请修改代码中的 selected_device 变量")
    else:
        print(f"\n使用设备: {selected_device}")
    
    # 执行截图
    print("\n正在截图...")
    screenshot = take_screenshot(selected_device)
    
    if screenshot is None:
        print("截图失败！")
        sys.exit(1)
    
    # 保存截图
    print("正在保存截图...")
    filename = save_screenshot(screenshot)
    
    if filename:
        print(f"\n截图成功！已保存到: {filename}")
        print(f"图像尺寸: {screenshot.shape[1]}x{screenshot.shape[0]}")
    else:
        print("\n保存截图失败！")
        sys.exit(1)
