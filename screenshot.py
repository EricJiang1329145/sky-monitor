# 截图工具模块
# 本模块提供安卓设备屏幕截图功能
# 可以作为模块被导入使用，也可以直接运行执行一次截图
import subprocess
import cv2
import sys
import os
import glob
import numpy as np
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
    
    try:
        # 使用 exec-out 命令直接获取二进制数据（优化性能，只需一次ADB命令）
        # exec-out 不经过shell，直接输出二进制数据，避免换行符问题
        cmd = [adb_path]
        
        # 如果指定了设备ID，添加 -s 参数指定设备
        if device_id:
            cmd.extend(["-s", device_id])
        
        # 添加截图命令：exec-out screencap -p
        # -p 参数表示以PNG格式输出
        cmd.extend(["exec-out", "screencap", "-p"])
        
        # 执行命令并获取截图数据
        # stdout=subprocess.PIPE 表示捕获标准输出（截图数据）
        # stderr=subprocess.PIPE 表示捕获错误输出
        # timeout=10 表示命令执行超时时间为10秒
        result = subprocess.run(cmd, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             timeout=10)
        
        # 检查命令执行是否成功
        # returncode为0表示成功，非0表示失败
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise Exception(f"截图失败 (返回码 {result.returncode}): {error_msg}")
        
        # 将二进制截图数据转换为numpy数组
        screenshot_data = result.stdout
        
        # 将二进制数据转换为numpy数组（uint8类型）
        img_array = np.frombuffer(screenshot_data, np.uint8)
        
        # 使用OpenCV解码图像数据
        # cv2.IMREAD_COLOR 表示以彩色模式读取图像
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
        
        if img is None:
            raise Exception("图像解码失败，返回的数据可能不是有效的PNG格式")
        
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
        list: 设备信息字典列表，每个元素包含设备详细信息
              如果获取失败或没有设备，返回空列表
    """
    # 如果没有指定ADB路径，使用配置文件中的路径
    if adb_path is None:
        adb_path = ADB_PATH
    
    try:
        # 执行adb devices -l命令获取详细设备列表
        # -l 参数表示长格式，包含设备详细信息
        # capture_output=True表示捕获标准输出和错误输出
        # text=True表示以文本形式返回输出
        # timeout=5表示命令执行超时时间为5秒
        result = subprocess.run([adb_path, "devices", "-l"], 
                             capture_output=True, 
                             text=True, 
                             timeout=5)
        
        # 解析命令输出结果
        # 输出格式：每行是一个设备信息，用空格分隔
        lines = result.stdout.strip().split('\n')
        devices = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 设备信息格式：用空格分隔的多个字段
                # 例如："12345678 device usb:1-2 product:model transport_id:1"
                parts = line.split()
                
                # 只处理状态为"device"的设备（表示设备已连接且可用）
                if len(parts) >= 2 and parts[1] == "device":
                    device_info = {
                        'id': parts[0],  # 设备ID
                        'status': parts[1],  # 设备状态
                        'name': '',  # 设备名称（通过adb shell getprop获取）
                        'model': '',  # 设备型号（通过adb shell getprop获取）
                        'android_version': '',  # Android版本（通过adb shell getprop获取）
                    }
                    
                    # 尝试获取设备名称
                    try:
                        name_result = subprocess.run([adb_path, "-s", parts[0], "shell", "getprop", "ro.product.model"],
                                                  capture_output=True, text=True, timeout=3)
                        if name_result.returncode == 0:
                            device_info['name'] = name_result.stdout.strip()
                    except:
                        pass
                    
                    # 尝试获取设备型号
                    try:
                        model_result = subprocess.run([adb_path, "-s", parts[0], "shell", "getprop", "ro.product.device"],
                                                  capture_output=True, text=True, timeout=3)
                        if model_result.returncode == 0:
                            device_info['model'] = model_result.stdout.strip()
                    except:
                        pass
                    
                    # 尝试获取Android版本
                    try:
                        version_result = subprocess.run([adb_path, "-s", parts[0], "shell", "getprop", "ro.build.version.release"],
                                                  capture_output=True, text=True, timeout=3)
                        if version_result.returncode == 0:
                            device_info['android_version'] = version_result.stdout.strip()
                    except:
                        pass
                    
                    devices.append(device_info)
        
        return devices
    except Exception as e:
        # 如果执行过程中出现异常，打印错误信息并返回空列表
        print(f"获取设备列表失败: {e}")
        return []


def tap(x, y, device_id=None, adb_path=None):
    """在安卓设备屏幕上模拟点击操作
    
    Args:
        x: 点击的X坐标
        y: 点击的Y坐标
        device_id: 要操作的设备ID，如果为None则使用默认设备
        adb_path: ADB命令路径，如果为None则使用配置文件中的路径
    
    Returns:
        bool: 点击操作是否成功
    """
    # 如果没有指定ADB路径，使用配置文件中的路径
    if adb_path is None:
        adb_path = ADB_PATH
    
    try:
        # 构建ADB命令
        cmd = [adb_path]
        
        # 如果指定了设备ID，添加 -s 参数指定设备
        if device_id:
            cmd.extend(["-s", device_id])
        
        # 添加点击命令：shell input tap x y
        cmd.extend(["shell", "input", "tap", str(x), str(y)])
        
        # 执行命令
        result = subprocess.run(cmd, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             timeout=5)
        
        # 检查命令执行是否成功
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise Exception(f"点击失败 (返回码 {result.returncode}): {error_msg}")
        
        return True
    except subprocess.TimeoutExpired:
        print("错误：命令执行超时")
        return False
    except Exception as e:
        # 如果点击过程中出现异常，打印错误信息并返回False
        print(f"点击失败: {e}")
        return False


def input_text(text, device_id=None, adb_path=None):
    """在安卓设备上输入文本（使用ADBKeyboard）
    
    Args:
        text: 要输入的文本内容
        device_id: 要操作的设备ID，如果为None则使用默认设备
        adb_path: ADB命令路径，如果为None则使用配置文件中的路径
    
    Returns:
        bool: 输入操作是否成功
    """
    # 如果没有指定ADB路径，使用配置文件中的路径
    if adb_path is None:
        adb_path = ADB_PATH
    
    try:
        # 构建ADB命令
        cmd = [adb_path]
        
        # 如果指定了设备ID，添加 -s 参数指定设备
        if device_id:
            cmd.extend(["-s", device_id])
        
        # 检查当前输入法是否为 ADBKeyboard
        check_cmd = cmd.copy()
        check_cmd.extend(["shell", "settings", "get", "secure", "default_input_method"])
        
        check_result = subprocess.run(check_cmd,
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE,
                                     timeout=5)
        
        current_ime = check_result.stdout.decode('utf-8', errors='ignore').strip()
        adbkeyboard_ime = "com.android.adbkeyboard/.AdbIME"
        
        # 保存原来的输入法
        original_ime = current_ime
        
        # 如果当前输入法不是 ADBKeyboard，切换到 ADBKeyboard
        if current_ime != adbkeyboard_ime:
            switch_cmd = cmd.copy()
            switch_cmd.extend(["shell", "ime", "set", adbkeyboard_ime])
            
            switch_result = subprocess.run(switch_cmd,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         timeout=5)
            
            if switch_result.returncode != 0:
                raise Exception(f"切换输入法失败: {switch_result.stderr.decode('utf-8', errors='ignore')}")
        
        # 使用ADBKeyboard的broadcast命令输入文本
        # 注意：需要先点击到输入框，让输入框获得焦点
        input_cmd = cmd.copy()
        input_cmd.extend(["shell", "am", "broadcast", "-a", "ADB_INPUT_BROADCAST", "--es", f"msg '{text}'"])
        
        # 执行命令
        result = subprocess.run(input_cmd, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             timeout=5)
        
        # 检查命令执行是否成功
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise Exception(f"输入文本失败 (返回码 {result.returncode}): {error_msg}")
        
        # 如果原来不是 ADBKeyboard，切换回原来的输入法
        if original_ime != adbkeyboard_ime:
            restore_cmd = cmd.copy()
            restore_cmd.extend(["shell", "ime", "set", original_ime])
            
            restore_result = subprocess.run(restore_cmd,
                                           stdout=subprocess.PIPE,
                                           stderr=subprocess.PIPE,
                                           timeout=5)
            
            if restore_result.returncode != 0:
                print(f"警告：切换回原输入法失败: {restore_result.stderr.decode('utf-8', errors='ignore')}")
        
        return True
    except subprocess.TimeoutExpired:
        print("错误：命令执行超时")
        return False
    except Exception as e:
        # 如果输入过程中出现异常，打印错误信息并返回False
        print(f"输入文本失败: {e}")
        return False


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
