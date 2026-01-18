# 键盘输入测试脚本
# 简化版本：只选择设备，使用 ADBKeyboard 方法发送文本并自动发送回车键
from keyboard import get_devices, input_text
import time

print("=== ADB 键盘输入测试 ===\n")

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

# 输入文本内容
print("\n提示：请先点击手机上的输入框，让输入框获得焦点")
text_to_send = input("请输入要发送的文本（直接回车发送默认文本 'test'）: ")

if not text_to_send.strip():
    text_to_send = "test"
    print(f"使用默认文本: {text_to_send}")

# 发送文本
print(f"\n正在向设备 {selected_device['id']} 发送文本 '{text_to_send}'...")
success = input_text(text_to_send, selected_device['id'], method='adbkeyboard', send_enter=True)

if success:
    print("\n✓ 文本发送成功！")
else:
    print("\n✗ 文本发送失败！")
    print("请检查：")
    print("1. 手机上是否已安装 ADBKeyboard 应用")
    print("2. 是否已点击手机上的输入框")
    print("3. 输入框是否已获得焦点（显示光标）")

# 等待一秒，方便调试
print("\n等待 1 秒...")
time.sleep(1)
