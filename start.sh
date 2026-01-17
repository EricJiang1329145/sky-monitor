#!/bin/bash

# 光遇消息检测工具启动脚本

# 激活conda环境
echo "正在激活conda环境..."
source activate sky-monitor

# 检查环境激活是否成功
if [ $? -ne 0 ]; then
    echo "激活conda环境失败，请确保sky-monitor环境已创建"
    exit 1
fi

# 运行主程序
echo "启动光遇消息检测工具..."
python main.py
