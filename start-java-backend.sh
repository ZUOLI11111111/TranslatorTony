#!/bin/bash
echo "启动Java后端数据存储服务..."

echo "使用WSL本地MySQL服务..."
echo "确保WSL本地MySQL服务已经启动"

# 检查MySQL服务是否启动
if ! service mysql status | grep -q "Server version"; then
    echo "正在启动MySQL服务..."
    sudo service mysql start
    sleep 2
fi

# 切换到Java后端目录
cd java-backend || {
    echo "错误: 无法进入java-backend目录"
    exit 1
}

# 检查本地MySQL是否可连接
echo "正在检查MySQL连接 (127.0.0.1:3306)..."
if nc -z -w5 127.0.0.1 3306; then
    echo "✅ MySQL连接成功！"
else
    echo "❌ 无法连接到MySQL服务器，请检查以下几点:"
    echo "  1. MySQL服务是否已启动 (sudo service mysql start)"
    echo "  2. MySQL用户权限是否正确"
    echo ""
    echo "您仍然可以尝试启动应用，但可能会连接失败"
    echo "是否继续? [y/N]"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "取消启动"
        exit 1
    fi
fi

# 确保数据库存在
echo "确保translator_db数据库存在..."
mysql -h 127.0.0.1 -u debian-sys-maint -pzsxGkfJ9zoDVN9pk -e "CREATE DATABASE IF NOT EXISTS translator_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" || {
    echo "警告: 无法创建数据库，可能需要手动创建"
}

# 获取WSL IP地址并显示连接信息
WSL_IP=$(hostname -I | awk '{print $1}')
echo "----------------------------------------"
echo "📢 注意: Java后端将在以下地址可访问:"
echo "   - WSL内部访问: http://localhost:8080/api"
echo "   - 从Windows访问: http://$WSL_IP:8080/api"
echo "----------------------------------------"
echo "如果前端仍使用Windows主机IP (而非WSL的IP)，您需要更新前端配置"
echo "----------------------------------------"

# 使用Maven编译并运行应用
echo "编译并启动Java应用..."
if [ -x "$(command -v mvn)" ]; then
    mvn spring-boot:run
else
    echo "警告: 未检测到Maven命令"
    echo "请确保已安装Maven并添加到PATH"
    echo "安装Maven: sudo apt-get install maven"
    exit 1
fi