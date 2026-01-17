# 用户界面模块
# 本模块使用tkinter创建应用程序的图形用户界面
# 包含设备选择、控制按钮、图像显示和日志输出等功能
import tkinter as tk
from tkinter import ttk, scrolledtext
from PIL import Image, ImageTk
import cv2
from config import IMAGE_DISPLAY_WIDTH, IMAGE_DISPLAY_HEIGHT

class AppUI:
    """应用程序用户界面类，负责创建和管理所有UI组件"""
    def __init__(self, root):
        # 保存主窗口的引用
        self.root = root
        
        # 设置窗口标题
        self.root.title("光遇消息检测工具")
        
        # 设置窗口初始大小为800x700像素
        self.root.geometry("800x700")
        
        # 设置ttk组件的样式
        # padding=6 设置按钮内边距，relief="flat" 设置按钮为扁平样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat")
        self.style.configure("TLabel", padding=2)
        
        # 初始化变量
        self.devices = []  # 设备列表
        self.selected_device = tk.StringVar()  # 当前选中的设备ID
        self.is_monitoring = False  # 监控状态标志
        
        # 图像数据存储列表，保持最新的两张截图
        # 用于在界面上同时显示前帧和后帧
        self.images = []
        
        # 创建主框架，使用10像素的内边距
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建左右分栏布局
        # 左侧：日志（固定宽度）
        # 右侧：设备管理、控制和屏幕截图（自适应窗口宽度）
        self.left_frame = ttk.Frame(self.main_frame, width=200)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))
        self.left_frame.pack_propagate(False)
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # 创建所有UI组件
        self.create_widgets()
    
    def create_widgets(self):
        """创建所有UI组件，包括设备选择、控制按钮、图像显示和日志区域"""
        # ========== 左侧区域：日志 ==========
        # 创建一个带标题的标签框架，用于显示操作日志
        log_frame = ttk.LabelFrame(self.left_frame, text="日志", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建可滚动的文本框，用于显示日志信息
        # wrap=tk.WORD 表示在单词边界处换行
        # 设置最小宽度，防止日志框太宽
        self.log_text = scrolledtext.ScrolledText(log_frame, width=30, height=10, wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        # 设置为只读状态，防止用户修改日志内容
        self.log_text.config(state=tk.DISABLED)
        
        # 配置日志颜色标签
        self._configure_log_tags()
        
        # ========== 右侧区域：设备管理 ==========
        # 创建一个带标题的标签框架，用于放置设备相关的控件
        # 使用固定宽度，不随窗口变化
        device_frame = ttk.LabelFrame(self.right_frame, text="设备管理", padding="5")
        device_frame.pack(fill=tk.X, pady=(0, 10))
        # 固定宽度，防止随窗口变化
        device_frame.pack_propagate(False)
        
        # 设备选择标签，显示"设备选择："文字
        ttk.Label(device_frame, text="设备选择：").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 设备下拉框，用于选择要连接的安卓设备
        # state="readonly" 表示用户只能选择，不能手动输入
        self.device_combobox = ttk.Combobox(device_frame, textvariable=self.selected_device, state="readonly")
        self.device_combobox.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W+tk.E)
        
        # 刷新设备按钮，点击时重新扫描连接的设备
        self.refresh_btn = ttk.Button(device_frame, text="刷新设备")
        self.refresh_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # ========== 控制按钮区域 ==========
        # 创建一个带标题的标签框架，用于放置控制按钮
        # 使用固定宽度，不随窗口变化
        control_frame = ttk.LabelFrame(self.right_frame, text="控制", padding="5")
        control_frame.pack(fill=tk.X, pady=(0, 10))
        # 固定宽度，防止随窗口变化
        control_frame.pack_propagate(False)
        
        # 开始按钮，点击时开始截图监控
        self.start_btn = ttk.Button(control_frame, text="开启截图")
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)
        
        # 停止按钮，点击时停止截图监控
        self.stop_btn = ttk.Button(control_frame, text="停止截图")
        self.stop_btn.grid(row=0, column=1, padx=5, pady=5)
        
        # 状态显示标签，使用粗体字体显示当前状态
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(control_frame, textvariable=self.status_var, font=("Arial", 10, "bold"))
        status_label.grid(row=0, column=2, padx=5, pady=5, sticky=tk.E)
        
        # 截图间隔设置
        ttk.Label(control_frame, text="间隔(秒):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        
        # 截图间隔输入框，允许用户设置截图间隔时间
        self.interval_var = tk.DoubleVar(value=1.0)
        self.interval_spinbox = ttk.Spinbox(control_frame, from_=0.1, to=10.0, increment=0.1, 
                                       textvariable=self.interval_var, width=10)
        self.interval_spinbox.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # 应用间隔按钮，点击时应用新的间隔设置
        self.apply_interval_btn = ttk.Button(control_frame, text="应用")
        self.apply_interval_btn.grid(row=1, column=2, padx=5, pady=5)
        
        # ========== 图像显示区域（自适应窗口大小）==========
        # 创建一个带标题的标签框架，用于显示屏幕截图
        # 使用固定宽度，不随窗口变化
        image_frame = ttk.LabelFrame(self.right_frame, text="屏幕截图", padding="5")
        image_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        # 固定宽度，防止随窗口变化
        image_frame.pack_propagate(False)
        
        # 创建图像显示的子框架，用于布局前帧和后帧
        image_content_frame = ttk.Frame(image_frame)
        image_content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 前帧显示区域
        prev_frame = ttk.Frame(image_content_frame)
        prev_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 前帧标题标签
        prev_title = ttk.Label(prev_frame, text="前帧", font=("Arial", 12, "bold"))
        prev_title.pack(pady=(0, 5))
        
        # 前帧图像显示标签
        self.prev_image_label = ttk.Label(prev_frame)
        self.prev_image_label.pack(fill=tk.BOTH, expand=True)
        
        # 后帧显示区域
        curr_frame = ttk.Frame(image_content_frame)
        curr_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 后帧标题标签
        curr_title = ttk.Label(curr_frame, text="后帧", font=("Arial", 12, "bold"))
        curr_title.pack(pady=(0, 5))
        
        # 后帧图像显示标签
        self.curr_image_label = ttk.Label(curr_frame)
        self.curr_image_label.pack(fill=tk.BOTH, expand=True)
        
        # 初始化图像显示区域，设置默认的空白图像
        self.init_image_display()
    
    def init_image_display(self):
        """初始化图像显示区域，设置默认的空白图像
        
        在程序启动时，图像显示区域会显示灰色的占位图像
        当有实际截图时，这些占位图像会被替换
        """
        # 创建一个灰色的空白图像作为占位符
        # 使用RGB模式，颜色为灰色
        # 注意：不使用固定尺寸，让label自动适应
        default_image = Image.new('RGB', (100, 100), color='gray')
        
        # 将PIL图像转换为Tkinter可显示的PhotoImage对象
        default_photo = ImageTk.PhotoImage(default_image)
        
        # 设置前帧图像标签显示占位图像
        # 注意：必须将PhotoImage对象保存到label的image属性中
        # 否则会被垃圾回收机制回收，导致图像无法显示
        self.prev_image_label.configure(image=default_photo, text="前帧")
        self.prev_image_label.image = default_photo
        
        # 设置后帧图像标签显示占位图像
        self.curr_image_label.configure(image=default_photo, text="后帧")
        self.curr_image_label.image = default_photo
    
    def _configure_log_tags(self):
        """配置日志文本的颜色标签
        
        为不同类型的日志消息配置不同的颜色：
        - info: 信息日志（蓝色）
        - success: 成功日志（绿色）
        - warning: 警告日志（橙色）
        - error: 错误日志（红色）
        - path: 文件路径（灰色）
        - processing: 处理中日志（黄色）
        """
        self.log_text.tag_config("info", foreground="#0066CC")
        self.log_text.tag_config("success", foreground="#0fffa0")
        self.log_text.tag_config("warning", foreground="#FF9900")
        self.log_text.tag_config("error", foreground="#CC0000")
        self.log_text.tag_config("path", foreground="#c0c0c0")
        self.log_text.tag_config("processing", foreground="#FFD700")
    
    def update_device_list(self, devices):
        """更新设备下拉列表
        
        Args:
            devices: 设备ID列表
        """
        # 保存设备列表到实例变量
        self.devices = devices
        
        # 更新下拉框的选项值
        self.device_combobox['values'] = devices
        
        # 如果有设备，默认选择第一个设备
        if devices:
            self.selected_device.set(devices[0])
        else:
            # 如果没有设备，清空选择并显示提示信息
            self.selected_device.set("")
            self.log_message("未检测到连接的设备", "warning")
    
    def update_images(self, image):
        """更新图像显示，保持最新的两张截图
        
        Args:
            image: 新的截图图像数据（OpenCV格式的numpy数组）
        
        说明：
            本方法维护一个图像列表，最多保存两张最新的截图
            前帧显示倒数第二张截图，后帧显示最新的截图
            这样可以方便地对比屏幕的变化
        """
        # 将新图像添加到列表末尾
        self.images.append(image)
        
        # 保持列表只包含最新的两张图像
        # 如果超过两张，删除最旧的一张（列表第一个元素）
        if len(self.images) > 2:
            self.images.pop(0)
        
        # 调用内部方法更新UI显示
        self._update_image_labels()
    
    def _update_image_labels(self):
        """更新图像标签的显示内容
        
        本方法将OpenCV格式的图像转换为Tkinter可显示的格式
        并更新前帧和后帧的显示内容
        """
        # 如果没有图像，直接返回
        if not self.images:
            return
        
        # 定义图像调整大小的内部函数
        def resize_image(img):
            """将图像调整为显示尺寸
            
            Args:
                img: OpenCV格式的图像（BGR格式的numpy数组）
            
            Returns:
                PIL.Image: 调整大小后的PIL图像对象，如果输入为None则返回None
            """
            # 转换为PIL图像
            if img is not None:
                # OpenCV图像是BGR格式，需要转换为RGB格式
                # PIL库使用RGB格式
                img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                
                # 从numpy数组创建PIL图像对象
                pil_img = Image.fromarray(img_rgb)
                
                # 按比例调整图像大小，保持宽高比
                # thumbnail方法会保持图像的宽高比
                # 不使用固定尺寸，让label自动适应窗口大小
                pil_img.thumbnail((self.root.winfo_width() - 20, self.root.winfo_height() - 20))
                
                return pil_img
            return None
        
        # 更新前帧图像（如果有两张或更多图像）
        # 前帧显示倒数第二张图像（images[-2]）
        if len(self.images) >= 2:
            prev_pil_img = resize_image(self.images[-2])
            if prev_pil_img:
                # 将PIL图像转换为Tkinter的PhotoImage对象
                prev_photo = ImageTk.PhotoImage(prev_pil_img)
                # 更新前帧标签的显示
                self.prev_image_label.configure(image=prev_photo)
                # 保存PhotoImage对象引用，防止被垃圾回收
                self.prev_image_label.image = prev_photo
        
        # 更新后帧图像（显示最新的图像 images[-1]）
        curr_pil_img = resize_image(self.images[-1])
        if curr_pil_img:
            # 将PIL图像转换为Tkinter的PhotoImage对象
            curr_photo = ImageTk.PhotoImage(curr_pil_img)
            # 更新后帧标签的显示
            self.curr_image_label.configure(image=curr_photo)
            # 保存PhotoImage对象引用，防止被垃圾回收
            self.curr_image_label.image = curr_photo
    
    def log_message(self, message, log_type="info"):
        """在日志文本框中添加一条消息
        
        Args:
            message: 要添加的日志消息内容，可以是字符串或元组列表
                     如果是字符串，整个消息使用 log_type 颜色
                     如果是元组列表，每个元组格式为 (text, log_type)，支持同一行多颜色
            log_type: 日志类型，可选值：
                      - "info": 信息日志（蓝色，默认）
                      - "success": 成功日志（绿色）
                      - "warning": 警告日志（橙色）
                      - "error": 错误日志（红色）
                      - "path": 文件路径（灰色）
                      - "processing": 处理中日志（黄色）
        
        说明：
            消息会自动添加换行符，并滚动到最新消息的位置
            日志文本框是只读的，用户不能修改内容
            不同类型的日志会以不同颜色显示
            支持同一条消息中不同部分使用不同颜色
        """
        # 临时启用文本框的可编辑状态
        self.log_text.config(state=tk.NORMAL)
        
        # 判断 message 是字符串还是元组列表
        if isinstance(message, str):
            # 如果是字符串，整个消息使用 log_type 颜色
            self.log_text.insert(tk.END, f"{message}\n", log_type)
        elif isinstance(message, list):
            # 如果是元组列表，每个部分使用不同的颜色
            for text, color_type in message:
                self.log_text.insert(tk.END, text, color_type)
            self.log_text.insert(tk.END, "\n")
        
        # 滚动到文本框末尾，显示最新消息
        self.log_text.see(tk.END)
        
        # 恢复文本框的只读状态
        self.log_text.config(state=tk.DISABLED)
    
    def update_status(self, status):
        """更新状态标签的显示内容
        
        Args:
            status: 要显示的状态文本，例如"就绪"、"截图中"、"已停止"
        """
        # 更新状态变量的值，状态标签会自动更新显示
        self.status_var.set(status)
    
    def get_interval(self):
        """获取当前设置的截图间隔时间
        
        Returns:
            float: 截图间隔时间（秒）
        """
        return self.interval_var.get()
    
    def set_monitoring_state(self, is_monitoring):
        """设置监控状态，并相应地启用或禁用相关按钮
        
        Args:
            is_monitoring: 布尔值，True表示正在监控，False表示已停止
        
        说明：
            当正在监控时：
            - 禁用开始按钮（防止重复启动）
            - 启用停止按钮
            - 禁用刷新按钮和设备选择框（防止在监控过程中切换设备）
            
            当停止监控时：
            - 启用开始按钮
            - 禁用停止按钮
            - 启用刷新按钮和设备选择框
        """
        # 更新监控状态标志
        self.is_monitoring = is_monitoring
        
        if is_monitoring:
            # 正在监控时的UI状态
            self.start_btn.state(['disabled'])  # 禁用开始按钮
            self.stop_btn.state(['!disabled'])  # 启用停止按钮
            self.refresh_btn.state(['disabled'])  # 禁用刷新按钮
            self.device_combobox.state(['disabled'])  # 禁用设备选择框
            self.interval_spinbox.state(['disabled'])  # 禁用间隔设置
            self.apply_interval_btn.state(['disabled'])  # 禁用应用按钮
        else:
            # 停止监控时的UI状态
            self.start_btn.state(['!disabled'])  # 启用开始按钮
            self.stop_btn.state(['disabled'])  # 禁用停止按钮
            self.refresh_btn.state(['!disabled'])  # 启用刷新按钮
            self.device_combobox.state(['!disabled'])  # 启用设备选择框
            self.interval_spinbox.state(['!disabled'])  # 启用间隔设置
            self.apply_interval_btn.state(['!disabled'])  # 启用应用按钮
