# 键盘输入模块
# 本模块提供通过ADB向安卓设备输入文本的功能
# 支持中文输入，使用ADBKeyboard应用
import subprocess
from config import ADB_PATH


def get_devices(adb_path=None):
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
        result = subprocess.run([adb_path, "devices", "-l"], 
                             capture_output=True, 
                             text=True, 
                             timeout=5)
        
        # 解析命令输出结果
        lines = result.stdout.strip().split('\n')
        devices = []
        
        for line in lines:
            line = line.strip()
            if line:
                # 设备信息格式：用空格分隔的多个字段
                parts = line.split()
                
                # 只处理状态为"device"的设备（表示设备已连接且可用）
                if len(parts) >= 2 and parts[1] == "device":
                    device_info = {
                        'id': parts[0],  # 设备ID
                        'status': parts[1],  # 设备状态
                        'name': '',  # 设备名称
                        'model': '',  # 设备型号
                        'android_version': '',  # Android版本
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
        print(f"获取设备列表失败: {e}")
        return []


def input_text_adbkeyboard(text, device_id=None, adb_path=None, send_enter=True, tap_coords=None):
    """使用ADBKeyboard输入文本（支持中文）
    
    Args:
        text: 要输入的文本内容
        device_id: 要操作的设备ID，如果为None则使用默认设备
        adb_path: ADB命令路径，如果为None则使用配置文件中的路径
        send_enter: 是否在输入文本后自动发送回车键，默认为True
        tap_coords: 点击屏幕坐标，格式为 (x, y)，如果提供则点击此位置而不是发送回车
    
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
            print(f"切换输入法: {current_ime} -> {adbkeyboard_ime}")
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
        # 使用 ADB_INPUT_TEXT action 来发送文本
        print(f"发送文本: {text}")
        input_cmd = cmd.copy()
        input_cmd.extend(["shell", "am", "broadcast", "-a", "ADB_INPUT_TEXT", "--es", "msg", text])
        
        # 执行命令
        result = subprocess.run(input_cmd, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             timeout=5)
        
        # 检查命令执行是否成功
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise Exception(f"输入文本失败 (返回码 {result.returncode}): {error_msg}")
        
        print("文本发送成功")
        
        # 处理发送后的操作：发送回车键或点击屏幕
        if tap_coords:
            # 点击指定坐标
            x, y = tap_coords
            print(f"点击屏幕坐标: ({x}, {y})")
            tap_cmd = cmd.copy()
            tap_cmd.extend(["shell", "input", "tap", str(x), str(y)])
            
            tap_result = subprocess.run(tap_cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      timeout=5)
            
            if tap_result.returncode != 0:
                error_msg = tap_result.stderr.decode('utf-8', errors='ignore')
                raise Exception(f"点击屏幕失败 (返回码 {tap_result.returncode}): {error_msg}")
        elif send_enter:
            # 使用 ADB_INPUT_CODE 发送 KEYCODE_ENTER (code=66)
            print("发送回车键...")
            enter_cmd = cmd.copy()
            enter_cmd.extend(["shell", "am", "broadcast", "-a", "ADB_INPUT_CODE", "--ei", "code", "66"])
            
            enter_result = subprocess.run(enter_cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      timeout=5)
            
            if enter_result.returncode != 0:
                error_msg = enter_result.stderr.decode('utf-8', errors='ignore')
                raise Exception(f"发送回车键失败 (返回码 {enter_result.returncode}): {error_msg}")
        
        # 如果原来不是 ADBKeyboard，切换回原来的输入法
        if original_ime != adbkeyboard_ime:
            print(f"恢复输入法: {adbkeyboard_ime} -> {original_ime}")
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


def input_text_simple(text, device_id=None, adb_path=None, send_enter=True):
    """使用adb shell input text输入文本（只支持英文和数字）
    
    Args:
        text: 要输入的文本内容（只支持英文和数字）
        device_id: 要操作的设备ID，如果为None则使用默认设备
        adb_path: ADB命令路径，如果为None则使用配置文件中的路径
        send_enter: 是否在输入文本后自动发送回车键，默认为True
    
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
        
        # 使用adb shell input text命令输入文本
        # 注意：只支持英文和数字，不支持中文
        print(f"发送文本: {text}")
        cmd.extend(["shell", "input", "text", text])
        
        # 执行命令
        result = subprocess.run(cmd, 
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             timeout=5)
        
        # 检查命令执行是否成功
        if result.returncode != 0:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            raise Exception(f"输入文本失败 (返回码 {result.returncode}): {error_msg}")
        
        # 如果需要发送回车键
        if send_enter:
            print("发送回车键...")
            enter_cmd = [adb_path]
            if device_id:
                enter_cmd.extend(["-s", device_id])
            enter_cmd.extend(["shell", "input", "keyevent", "KEYCODE_ENTER"])
            
            enter_result = subprocess.run(enter_cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      timeout=5)
            
            if enter_result.returncode != 0:
                error_msg = enter_result.stderr.decode('utf-8', errors='ignore')
                raise Exception(f"发送回车键失败 (返回码 {enter_result.returncode}): {error_msg}")
        
        print("文本发送成功")
        return True
    except subprocess.TimeoutExpired:
        print("错误：命令执行超时")
        return False
    except Exception as e:
        # 如果输入过程中出现异常，打印错误信息并返回False
        print(f"输入文本失败: {e}")
        return False


def input_text(text, device_id=None, adb_path=None, method='adbkeyboard', send_enter=True, tap_coords=None):
    """在安卓设备上输入文本
    
    Args:
        text: 要输入的文本内容
        device_id: 要操作的设备ID，如果为None则使用默认设备
        adb_path: ADB命令路径，如果为None则使用配置文件中的路径
        method: 输入方法，可选值：
                - 'adbkeyboard': 使用ADBKeyboard（支持中文，但需要输入框有焦点）
                - 'simple': 使用adb shell input text（只支持英文，不需要输入框有焦点）
        send_enter: 是否在输入文本后自动发送回车键，默认为True
        tap_coords: 点击屏幕坐标，格式为 (x, y)，如果提供则点击此位置而不是发送回车
    
    Returns:
        bool: 输入操作是否成功
    """
    if method == 'simple':
        return input_text_simple(text, device_id, adb_path, send_enter)
    else:
        return input_text_adbkeyboard(text, device_id, adb_path, send_enter, tap_coords)


if __name__ == "__main__":
    """当直接运行此文件时，执行交互式文本输入"""
    print("=== ADB 键盘输入工具 ===\n")
    
    # 获取连接的设备列表
    print("正在获取设备列表...")
    devices = get_devices()
    
    if not devices:
        print("未检测到连接的设备，请确保：")
        print("1. 设备已通过USB连接到电脑")
        print("2. 设备已开启USB调试模式")
        print("3. 已授权电脑进行调试")
        exit(1)
    
    # 显示设备列表
    print(f"\n发现 {len(devices)} 个设备：")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. 设备ID: {device['id']}")
        print(f"     设备名称: {device.get('name', 'N/A')}")
        print(f"     设备型号: {device.get('model', 'N/A')}")
        print(f"     Android版本: {device.get('android_version', 'N/A')}")
        print()
    
    # 选择设备
    selected_device = None
    if len(devices) == 1:
        selected_device = devices[0]
        print(f"自动选择唯一设备: {selected_device['id']}")
    else:
        while True:
            try:
                choice = input(f"请选择设备 (1-{len(devices)}): ")
                choice_num = int(choice)
                if 1 <= choice_num <= len(devices):
                    selected_device = devices[choice_num - 1]
                    print(f"已选择设备: {selected_device['id']}")
                    break
                else:
                    print(f"请输入 1 到 {len(devices)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")
    
    # 输入文本
    print("\n提示：发送前请先点击手机上的输入框，让输入框获得焦点")
    text_to_send = input("请输入要发送的文本（直接回车发送默认文本 'test'）: ")
    
    if not text_to_send.strip():
        text_to_send = "test"
        print(f"使用默认文本: {text_to_send}")
    
    # 发送文本
    print(f"\n正在向设备 {selected_device['id']} 发送文本...")
    success = input_text(text_to_send, selected_device['id'])
    
    if success:
        print("\n✓ 文本发送成功！")
    else:
        print("\n✗ 文本发送失败！")
        print("请检查：")
        print("1. 手机上是否已安装 ADBKeyboard 应用")
        print("2. 是否已点击手机上的输入框")
        print("3. 输入框是否已获得焦点（显示光标）")
