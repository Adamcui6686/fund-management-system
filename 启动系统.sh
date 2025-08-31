#!/bin/bash

echo "==================================="
echo "🚀 启动私募基金净值管理系统"
echo "==================================="

# 检查Python是否安装
if ! command -v python3 &> /dev/null
then
    echo "❌ Python3 未安装，请先安装Python3"
    exit 1
fi

# 检查是否在正确目录
if [ ! -f "app.py" ]; then
    echo "❌ 请在净值管理项目目录下运行此脚本"
    exit 1
fi

# 安装依赖
echo "📦 检查并安装依赖包..."
pip3 install -r requirements.txt

# 启动系统
echo "🎯 启动系统..."
echo "系统将在浏览器中自动打开："
echo "🌐 http://localhost:8501"
echo ""
echo "使用 Ctrl+C 停止系统"
echo "==================================="

streamlit run app.py
