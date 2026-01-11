#!/bin/bash

echo
echo "========================================"
echo "   ASI-ACE 全能自动化整合系统 - 本地启动"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3，请先安装Python 3.7+"
    echo "   下载地址: https://www.python.org/downloads/"
    exit 1
fi

# 检查主文件是否存在
if [ ! -f "ASI_ACE_FULL_INTEGRATION.py" ]; then
    echo "❌ 错误: 主文件 ASI_ACE_FULL_INTEGRATION.py 不存在"
    exit 1
fi

# 检查部署文件是否存在
if [ ! -f "deploy/local_deployment.py" ]; then
    echo "❌ 错误: 部署文件 deploy/local_deployment.py 不存在"
    exit 1
fi

echo "✅ Python环境检测通过"
echo "✅ 系统文件检查通过"
echo
echo "🚀 正在启动ASI-ACE系统..."

# 启动本地部署
python3 deploy/local_deployment.py

echo
echo "========================================"
echo "    系统已关闭"
echo "========================================"