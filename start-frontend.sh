#!/bin/bash
echo "启动翻译助手前端应用 (DeepSeek V3版本)..."

# 检查后端是否在运行
if ! curl -s http://localhost:5000/api/health > /dev/null && ! curl -s http://localhost:5000/api/languages > /dev/null; then
    echo "警告: 后端服务似乎没有运行!"
    echo "请先在另一个终端运行: ./start-backend.sh"
    echo "继续启动前端? [y/N]"
    read -r response
    if [[ ! "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
        echo "取消启动前端"
        exit 1
    fi
fi

# 切换到前端目录
echo "进入前端目录..."
cd frontend || {
    echo "错误: 无法进入frontend目录"
    exit 1
}

# 启动前端
echo "启动React应用 (按Ctrl+C终止)..."
echo "使用DeepSeek Chat模型提供翻译服务"
npm start
