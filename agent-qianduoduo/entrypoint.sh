#!/bin/sh
set -e

echo "========================================"
echo "钱多多智能体已启动"
echo "========================================"

if [ -z "$ITICK_TOKEN" ]; then
    echo "⚠️  警告：ITICK_TOKEN 未设置，盯盘功能不可用"
fi

if [ -z "$TUSHARE_TOKEN" ]; then
    echo "⚠️  警告：TUSHARE_TOKEN 未设置，宏观分析数据不可用"
fi

if [ -z "$BRAVE_API_KEY" ]; then
    echo "⚠️  警告：BRAVE_API_KEY 未设置，浏览器搜索功能不可用"
fi

echo "✅ 环境检查完成"
echo ""

if [ $# -gt 0 ]; then
    exec "$@"
else
    echo "Usage: docker run -it qianduoduo [python3 /app/qianduoduo/app.py]"
    
    # 启动 Flask 服务（前台运行）
    exec python3 /app/qianduoduo/app.py
fi
