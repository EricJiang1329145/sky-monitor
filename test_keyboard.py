# 键盘输入测试脚本
# 手动选择设备并发送 "test" 文本
from keyboard import get_devices, input_text

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

# 选择输入方法
print("\n请选择输入方法：")
print("  1. Simple (只支持英文，不需要输入框有焦点)")
print("  2. ADBKeyboard (支持中文，但需要输入框有焦点)")

while True:
    try:
        choice = input("请选择 (1-2，默认1): ")
        if not choice.strip():
            choice = "1"
        choice_num = int(choice)
        if choice_num == 1:
            method = 'simple'
            print("已选择: Simple 方法")
            break
        elif choice_num == 2:
            method = 'adbkeyboard'
            print("已选择: ADBKeyboard 方法")
            print("\n提示：请先点击手机上的输入框，让输入框获得焦点")
            break
        else:
            print("请输入 1 或 2")
    except ValueError:
        print("请输入有效的数字")

# 选择是否发送回车或点击搜索按钮
send_enter = True
tap_coords = None

while True:
    try:
        choice = input("\n输入文本后的操作：\n  1. 发送回车键\n  2. 点击搜索按钮\n  3. 不做任何操作\n请选择 (1-3，默认1): ")
        if not choice.strip():
            choice = "1"
        choice_num = int(choice)
        if choice_num == 1:
            send_enter = True
            tap_coords = None
            print("已选择: 发送回车键")
            break
        elif choice_num == 2:
            send_enter = False
            # 获取搜索按钮坐标
            while True:
                try:
                    x = input("请输入搜索按钮的X坐标: ")
                    y = input("请输入搜索按钮的Y坐标: ")
                    tap_coords = (int(x), int(y))
                    print(f"已设置搜索按钮坐标: ({x}, {y})")
                    break
                except ValueError:
                    print("请输入有效的数字")
            break
        elif choice_num == 3:
            send_enter = False
            tap_coords = None
            print("已选择: 不做任何操作")
            break
        else:
            print("请输入 1、2 或 3")
    except ValueError:
        print("请输入有效的数字")

# 发送测试文本
if method == 'adbkeyboard':
    input("\n按回车继续发送 'test' 文本...")

print(f"\n正在向设备 {selected_device['id']} 发送文本 'test'...")
success = input_text("test", selected_device['id'], method=method, send_enter=send_enter, tap_coords=tap_coords)

if success:
    print("\n✓ 文本发送成功！")
else:
    print("\n✗ 文本发送失败！")
    if method == 'adbkeyboard':
        print("请检查：")
        print("1. 手机上是否已安装 ADBKeyboard 应用")
        print("2. 是否已点击手机上的输入框")
        print("3. 输入框是否已获得焦点（显示光标）")
