# uiautomator 元素获取示例程序
# 使用 uiautomator 获取屏幕上所有可点击的元素
# 需要先安装 uiautomator2: pip install uiautomator2

from uiautomator import Device

print("=== uiautomator 元素获取 ===\n")

# 连接到第三个设备
device_id = "adb-7DZHDMZ9JVTKBUZX-LLNp2o._adb-tls-connect._tcp"
print(f"正在连接到设备: {device_id}")

try:
    # 连接设备
    d = Device(device_id)
    
    # 获取设备信息
    info = d.info
    print(f"\n设备信息:")
    print(f"  产品: {info.get('product', 'N/A')}")
    print(f"  品牌: {info.get('brand', 'N/A')}")
    print(f"  型号: {info.get('model', 'N/A')}")
    print(f"  Android版本: {info.get('release', 'N/A')}")
    print(f"  分辨率: {info.get('displayWidth', 'N/A')}x{info.get('displayHeight', 'N/A')}")
    print(f"  屏幕密度: {info.get('displayDensity', 'N/A')}")
    
    # 获取当前窗口信息
    print(f"\n当前窗口信息:")
    current_window = d.info
    print(f"  当前包名: {current_window.get('currentPackageName', 'N/A')}")
    print(f"  当前Activity: {current_window.get('currentActivity', 'N/A')}")
    
    # 获取所有可点击的元素
    print(f"\n正在获取所有可点击的元素...")
    
    # 获取所有可点击的元素
    clickable_elements = []
    
    # 获取所有按钮
    buttons = d(className='android.widget.Button')
    for button in buttons:
        clickable_elements.append({
            'type': 'Button',
            'text': button.info.get('text', ''),
            'resource_id': button.info.get('resource-id', ''),
            'bounds': button.info.get('bounds', ''),
            'enabled': button.info.get('enabled', True),
            'clickable': button.info.get('clickable', False),
            'package': button.info.get('package', ''),
            'class': button.info.get('class', ''),
        })
    
    # 获取所有文本框
    edit_texts = d(className='android.widget.EditText')
    for edit_text in edit_texts:
        clickable_elements.append({
            'type': 'EditText',
            'text': edit_text.info.get('text', ''),
            'hint': edit_text.info.get('hint', ''),
            'bounds': edit_text.info.get('bounds', ''),
            'enabled': edit_text.info.get('enabled', True),
            'clickable': edit_text.info.get('clickable', False),
            'package': edit_text.info.get('package', ''),
            'class': edit_text.info.get('class', ''),
        })
    
    # 获取所有可点击的ImageView
    image_views = d(className='android.widget.ImageView')
    for image_view in image_views:
        clickable_elements.append({
            'type': 'ImageView',
            'content_description': image_view.info.get('contentDescription', ''),
            'bounds': image_view.info.get('bounds', ''),
            'enabled': image_view.info.get('enabled', True),
            'clickable': image_view.info.get('clickable', False),
            'package': image_view.info.get('package', ''),
            'class': image_view.info.get('class', ''),
        })
    
    # 获取所有可点击的TextView
    text_views = d(className='android.widget.TextView')
    for text_view in text_views:
        clickable_elements.append({
            'type': 'TextView',
            'text': text_view.info.get('text', ''),
            'bounds': text_view.info.get('bounds', ''),
            'enabled': text_view.info.get('enabled', True),
            'clickable': text_view.info.get('clickable', False),
            'package': text_view.info.get('package', ''),
            'class': text_view.info.get('class', ''),
        })
    
    # 获取所有可点击的LinearLayout
    linear_layouts = d(className='android.widget.LinearLayout')
    for layout in linear_layouts:
        clickable_elements.append({
            'type': 'LinearLayout',
            'bounds': layout.info.get('bounds', ''),
            'enabled': layout.info.get('enabled', True),
            'clickable': layout.info.get('clickable', False),
            'package': layout.info.get('package', ''),
            'class': layout.info.get('class', ''),
        })
    
    # 获取所有可点击的RelativeLayout
    relative_layouts = d(className='android.widget.RelativeLayout')
    for layout in relative_layouts:
        clickable_elements.append({
            'type': 'RelativeLayout',
            'bounds': layout.info.get('bounds', ''),
            'enabled': layout.info.get('enabled', True),
            'clickable': layout.info.get('clickable', False),
            'package': layout.info.get('package', ''),
            'class': layout.info.get('class', ''),
        })
    
    # 显示结果
    print(f"\n找到 {len(clickable_elements)} 个可点击的元素：\n")
    
    # 按类型分组显示
    element_types = {}
    for element in clickable_elements:
        element_type = element['type']
        if element_type not in element_types:
            element_types[element_type] = []
        element_types[element_type].append(element)
    
    for element_type, elements in element_types.items():
        print(f"\n{element_type} ({len(elements)} 个):")
        for i, element in enumerate(elements, 1):
            bounds = element['bounds']
            if bounds:
                coords = bounds.split('],[')
                x1, y1, x2, y2 = map(int, coords[0].split(','))
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                print(f"  {i}. 坐标: ({center_x}, {center_y})")
            
            if element['text']:
                print(f"     文本: {element['text']}")
            if element['hint']:
                print(f"     提示: {element['hint']}")
            if element['content_description']:
                print(f"     描述: {element['content_description']}")
            if element['resource_id']:
                print(f"     资源ID: {element['resource_id']}")
            if element['enabled']:
                print(f"     可用: 是")
            else:
                print(f"     可用: 否")
    
    print(f"\n总计: {len(clickable_elements)} 个可点击的元素")
    print("\n提示：")
    print("1. 可以使用这些坐标来点击元素")
    print("2. 坐标格式为 (x, y)，表示元素的中心点")
    print("3. 可以在 debug_ime.py 中使用这些坐标")
    print("4. 不同应用可能需要不同的元素坐标")
    
except Exception as e:
    print(f"\n错误：无法连接到设备或获取元素")
    print(f"错误信息: {e}")
    print("\n请检查：")
    print("1. 是否已安装 uiautomator2: pip install uiautomator2")
    print("2. 设备是否已连接")
    print("3. 是否已启用USB调试")
    print("4. 是否已授权电脑进行调试")
