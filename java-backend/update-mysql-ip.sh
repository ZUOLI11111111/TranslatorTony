#!/bin/bash
# 获取WSL中Windows主机的IP地址

# 从/etc/resolv.conf获取IP
WINDOWS_IP=$(grep nameserver /etc/resolv.conf | awk '{print $2}')
echo "检测到Windows主机IP地址: $WINDOWS_IP"

# 更新application.properties文件
CONFIG_FILE="src/main/resources/application.properties"
if [ -f "$CONFIG_FILE" ]; then
    # 生成临时文件
    TMP_FILE=$(mktemp)
    
    # 替换IP地址
    cat "$CONFIG_FILE" | sed "s|jdbc:mysql://[^:]*:|jdbc:mysql://$WINDOWS_IP:|g" > "$TMP_FILE"
    
    # 将临时文件移回原位
    mv "$TMP_FILE" "$CONFIG_FILE"
    
    # 更新连接参数
    sed -i 's/createDatabaseIfNotExist=true/createDatabaseIfNotExist=true\&useUnicode=true\&characterEncoding=utf8/g' "$CONFIG_FILE"
    
    echo "已更新配置文件中的MySQL连接地址为 $WINDOWS_IP"
    echo "新的连接URL:"
    grep "spring.datasource.url" "$CONFIG_FILE" | head -1
else
    echo "错误: 找不到配置文件 $CONFIG_FILE"
    exit 1
fi

echo "完成! 现在可以尝试启动应用" 