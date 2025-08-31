#!/bin/bash

echo "🌐 ngrok快速设置脚本"
echo "===================="

# 检查是否已安装ngrok
if command -v ngrok &> /dev/null; then
    echo "✅ ngrok已安装"
else
    echo "📥 ngrok未安装，开始下载..."
    
    # 检测系统架构
    if [[ $(uname -m) == "arm64" ]]; then
        ARCH="arm64"
    else
        ARCH="amd64"
    fi
    
    # 下载ngrok
    curl -o ngrok.zip "https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-darwin-${ARCH}.zip"
    
    # 解压
    unzip ngrok.zip
    chmod +x ngrok
    
    # 移动到系统路径（可选）
    echo "📁 将ngrok移动到 /usr/local/bin"
    sudo mv ngrok /usr/local/bin/
    
    echo "✅ ngrok安装完成"
fi

echo ""
echo "🔑 请按以下步骤配置ngrok："
echo "1. 访问 https://ngrok.com/signup 注册免费账户"
echo "2. 登录后访问 https://dashboard.ngrok.com/get-started/your-authtoken"
echo "3. 复制您的authtoken"
echo "4. 运行命令：ngrok authtoken YOUR_AUTHTOKEN"
echo ""
echo "🚀 配置完成后，运行以下命令启动："
echo "   ngrok http 8501"
echo ""
echo "📱 然后将生成的链接发给您的合伙人即可访问！"
