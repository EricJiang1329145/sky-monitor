# Sky 输入 - 输入法切换和文本输入工具
# 切换到 ADBKeyboard，执行滑动操作，发送文本和回车，然后恢复原输入法
from keyboard import input_text, get_devices
from config import ADB_PATH
import subprocess
import time


def sky_input(device_id, x=189, y=1200, text="test", wait_time=0.3, verbose=True):
    """
    Sky 输入函数
    
    参数:
        device_id: 设备 ID
        x: 滑动坐标 X，默认 189
        y: 滑动坐标 Y，默认 1200
        text: 要发送的文本，默认 "test"
        wait_time: 滑动后的等待时间（秒），默认 0.3
        verbose: 是否打印详细日志，默认 True
    
    返回:
        bool: 操作是否成功
    """
    try:
        # 获取当前输入法
        if verbose:
            print("\n正在获取当前输入法...")
        get_ime_cmd = [ADB_PATH]
        if device_id:
            get_ime_cmd.extend(["-s", device_id, "shell", "settings", "get", "secure", "default_input_method"])
        result = subprocess.run(get_ime_cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            if verbose:
                print(f"错误：无法获取输入法 (返回码 {result.returncode})")
            return False

        current_ime = result.stdout.strip()
        if verbose:
            print(f"当前输入法: {current_ime}")

        # 切换到 ADBKeyboard
        if verbose:
            print("\n正在切换到 ADBKeyboard...")
        switch_cmd = [ADB_PATH]
        if device_id:
            switch_cmd.extend(["-s", device_id, "shell", "ime", "set", "com.android.adbkeyboard/.AdbIME"])
        result = subprocess.run(switch_cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            if verbose:
                print(f"错误：无法切换输入法 (返回码 {result.returncode})")
                print(f"错误信息: {result.stderr}")
            return False

        if verbose:
            print("✓ 已切换到 ADBKeyboard")

        # 第一次滑动屏幕
        if verbose:
            print(f"\n正在第 1 次滑动屏幕坐标 ({x}, {y}) 到 ({x}, {y})，持续 250 毫秒...")
        swipe_cmd = [ADB_PATH]
        if device_id:
            swipe_cmd.extend(["-s", device_id, "shell", "input", "swipe", str(x), str(y), str(x), str(y), "250"])
        result = subprocess.run(swipe_cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            if verbose:
                print(f"错误：无法滑动屏幕 (返回码 {result.returncode})")
                print(f"错误信息: {result.stderr}")
            return False
        else:
            if verbose:
                print("✓ 已完成第 1 次滑动")

        # 等待 0.1 秒
        if verbose:
            print("\n等待 0.1 秒...")
        time.sleep(0.1)

        # 第二次滑动屏幕
        if verbose:
            print(f"\n正在第 2 次滑动屏幕坐标 ({x}, {y}) 到 ({x}, {y})，持续 250 毫秒...")
        swipe_cmd = [ADB_PATH]
        if device_id:
            swipe_cmd.extend(["-s", device_id, "shell", "input", "swipe", str(x), str(y), str(x), str(y), "250"])
        result = subprocess.run(swipe_cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            if verbose:
                print(f"错误：无法滑动屏幕 (返回码 {result.returncode})")
                print(f"错误信息: {result.stderr}")
            return False
        else:
            if verbose:
                print("✓ 已完成第 2 次滑动")

        # 等待指定时间
        if wait_time > 0:
            if verbose:
                print(f"\n等待 {wait_time} 秒...")
            time.sleep(wait_time)

        # 发送文本
        if verbose:
            print(f"\n正在发送文本 '{text}'...")
        success = input_text(text, device_id, method='adbkeyboard', send_enter=False)

        if not success:
            if verbose:
                print("✗ 文本发送失败！")
            return False
        else:
            if verbose:
                print("✓ 文本发送成功！")

        # 等待 0.3 秒
        if verbose:
            print("\n等待 0.3 秒...")
        time.sleep(0.3)

        # 发送回车键
        if verbose:
            print("\n正在发送回车键...")
        enter_cmd = [ADB_PATH]
        if device_id:
            enter_cmd.extend(["-s", device_id, "shell", "am", "broadcast", "-a", "ADB_INPUT_CODE", "--ei", "code", "66"])
        result = subprocess.run(enter_cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            if verbose:
                print(f"错误：无法发送回车键 (返回码 {result.returncode})")
                print(f"错误信息: {result.stderr}")
            return False
        else:
            if verbose:
                print("✓ 已发送回车键")

        # 等待 3 秒
        if verbose:
            print("\n等待 3 秒...")
        time.sleep(3)

        # 恢复原输入法
        if verbose:
            print(f"\n正在恢复原输入法: {current_ime}...")
        restore_cmd = [ADB_PATH]
        if device_id:
            restore_cmd.extend(["-s", device_id, "shell", "ime", "set", current_ime])
        result = subprocess.run(restore_cmd, capture_output=True, text=True, timeout=5)

        if result.returncode != 0:
            if verbose:
                print(f"错误：无法恢复输入法 (返回码 {result.returncode})")
                print(f"错误信息: {result.stderr}")
            return False

        if verbose:
            print("✓ 已恢复原输入法")
            print("\nSky 输入完成！")

        return True

    except Exception as e:
        if verbose:
            print(f"错误：执行过程中发生异常: {e}")
        return False


if __name__ == "__main__":
    print("=== Sky 输入 ===\n")

    # 获取连接的设备列表
    print("正在获取设备列表...")
    devices = get_devices()

    if not devices:
        print("未检测到连接的设备")
        exit(1)

    # 显示设备列表
    print(f"\n发现 {len(devices)} 个设备：")
    for i, device in enumerate(devices, 1):
        print(f"  {i}. {device['id']} - {device.get('name', 'N/A')}")

    # 选择设备
    selected_device = None
    if len(devices) == 1:
        selected_device = devices[0]
        print(f"\n自动选择唯一设备: {selected_device['id']}")
    else:
        while True:
            try:
                choice = input(f"\n请选择设备 (1-{len(devices)}): ")
                choice_num = int(choice)
                if 1 <= choice_num <= len(devices):
                    selected_device = devices[choice_num - 1]
                    print(f"已选择设备: {selected_device['id']}")
                    break
                else:
                    print(f"请输入 1 到 {len(devices)} 之间的数字")
            except ValueError:
                print("请输入有效的数字")

    # 配置滑动后的等待时间（默认 0.3 秒）
    print("\n配置滑动后的等待时间（秒，默认 0.3）:")
    print("  - 短按：0.1-0.3 秒（快速点击）")
    print("  - 长按：0.5-1.0 秒（持续按压）")
    print("  - 超长按：1.0-2.0 秒（长时间按压）")
    print("  - 直接回车：0 秒（不等待）")
    wait_time_input = input("请输入等待时间（直接回车使用默认 0.3 秒）: ")

    if not wait_time_input.strip():
        wait_time = 0.3
        print(f"使用默认等待时间: {wait_time} 秒")
    else:
        try:
            wait_time = float(wait_time_input)
            if wait_time < 0:
                print("警告：等待时间不能为负数，使用默认 0.3 秒")
                wait_time = 0.3
            print(f"使用等待时间: {wait_time} 秒")
        except ValueError:
            print("错误：请输入有效的数字")
            exit(1)

    # 配置滑动坐标（可选）
    print("\n配置滑动坐标（直接回车使用默认值 189, 1200）:")
    x_input = input("请输入 X 坐标（默认 189）: ")
    y_input = input("请输入 Y 坐标（默认 1200）: ")

    if x_input.strip():
        try:
            x = int(x_input)
            print(f"使用 X 坐标: {x}")
        except ValueError:
            print("错误：请输入有效的数字，使用默认值 189")
            x = 189
    else:
        x = 189

    if y_input.strip():
        try:
            y = int(y_input)
            print(f"使用 Y 坐标: {y}")
        except ValueError:
            print("错误：请输入有效的数字，使用默认值 1200")
            y = 1200
    else:
        y = 1200

    # 配置要发送的文本（可选）
    text_input = input("\n请输入要发送的文本（直接回车使用默认 'test'）: ")
    text = text_input.strip() if text_input.strip() else "test"
    print(f"使用文本: {text}")

    # 执行 Sky 输入
    print("\n" + "="*50)
    success = sky_input(selected_device['id'], x=x, y=y, text=text, wait_time=wait_time)

    if success:
        print("\n操作成功完成！")
    else:
        print("\n操作失败！")
        exit(1)

    print("\n说明：")
    print("1. 程序已将输入法切换为 ADBKeyboard")
    print(f"2. 第 1 次滑动屏幕坐标 ({x}, {y}) 到 ({x}, {y})，持续 250 毫秒")
    print("3. 等待 0.1 秒")
    print(f"4. 第 2 次滑动屏幕坐标 ({x}, {y}) 到 ({x}, {y})，持续 250 毫秒")
    print(f"5. 等待 {wait_time} 秒")
    print(f"6. 再等待 0.3 秒后发送文本 '{text}'")
    print("7. 再等待 0.3 秒后发送回车键")
    print("8. 最后等待 3 秒后恢复原输入法")
    print("9. 请检查应用程序是否受到影响")
    print("\n提示：")
    print("- 不同应用可能需要不同的滑动持续时间")
    print("- 如果应用没有响应，可以尝试增加等待时间")
    print("- 短按：0.1-0.3 秒（快速点击）")
    print("- 长按：0.5-1.0 秒（持续按压）")
    print("- 超长按：1.0-2.0 秒（长时间按压）")
    print("- 直接回车：0 秒（不等待）")
