#!/bin/bash

# 云服务器部署脚本
# 适用于 Ubuntu 20.04+ / CentOS 8+

echo "🚀 开始部署私募基金净值管理系统到云服务器"

# 1. 更新系统
echo "📦 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 2. 安装Python和必要工具
echo "🐍 安装Python环境..."
sudo apt install -y python3 python3-pip python3-venv git nginx

# 3. 创建应用目录
echo "📁 创建应用目录..."
sudo mkdir -p /var/www/fund-management
sudo chown -R $USER:$USER /var/www/fund-management
cd /var/www/fund-management

# 4. 克隆代码（需要先上传到Git仓库）
echo "📥 下载应用代码..."
# git clone https://github.com/你的用户名/fund-management.git .

# 5. 创建虚拟环境
echo "🔧 创建Python虚拟环境..."
python3 -m venv venv
source venv/bin/activate

# 6. 安装依赖
echo "📦 安装依赖包..."
pip install streamlit pandas plotly numpy openpyxl gunicorn

# 7. 创建systemd服务文件
echo "⚙️ 创建系统服务..."
sudo tee /etc/systemd/system/fund-management.service > /dev/null <<EOF
[Unit]
Description=Fund Management Streamlit App
After=network.target

[Service]
Type=exec
User=$USER
WorkingDirectory=/var/www/fund-management
Environment=PATH=/var/www/fund-management/venv/bin
ExecStart=/var/www/fund-management/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 8. 配置Nginx反向代理
echo "🌐 配置Nginx..."
sudo tee /etc/nginx/sites-available/fund-management > /dev/null <<EOF
server {
    listen 80;
    server_name 你的域名或IP;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

# 9. 启用配置
sudo ln -s /etc/nginx/sites-available/fund-management /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# 10. 启动服务
echo "🎯 启动服务..."
sudo systemctl daemon-reload
sudo systemctl enable fund-management
sudo systemctl start fund-management

# 11. 配置防火墙
echo "🔒 配置防火墙..."
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw --force enable

echo "✅ 部署完成！"
echo "🌐 访问地址：http://你的服务器IP"
echo "📊 查看状态：sudo systemctl status fund-management"
echo "📝 查看日志：sudo journalctl -u fund-management -f"
