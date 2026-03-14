#!/bin/bash
# 智能客服系统部署脚本

set -e

# 配置
SERVER_IP="150.158.52.215"
SERVER_USER="ubuntu"
SSH_KEY="/home/node/.openclaw/workspace-dashen/local_ubuntu2_2.pem"
REMOTE_DIR="/home/ubuntu/smart-cs"

echo "🚀 开始部署智能客服系统..."

# 1. 编译
echo "📦 编译项目..."
cd "$(dirname "$0")/.."
go mod tidy
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o bin/smart-cs-server cmd/server/main.go

# 2. 创建远程目录
echo "📁 创建远程目录..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" "mkdir -p $REMOTE_DIR/{bin,configs,logs,data}"

# 3. 上传文件
echo "📤 上传文件..."
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no bin/smart-cs-server "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/bin/"
scp -i "$SSH_KEY" -o StrictHostKeyChecking=no configs/config.example.yml "$SERVER_USER@$SERVER_IP:$REMOTE_DIR/configs/config.yml"

# 4. 远程启动
echo "🔄 远程启动服务..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_IP" << 'ENDSSH'
cd /home/ubuntu/smart-cs
pkill -f smart-cs-server || true
nohup ./bin/smart-cs-server > logs/server.log 2>&1 &
echo "服务已启动，PID: $!"
ENDSSH

echo "✅ 部署完成！"
echo "📊 查看日志：ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'tail -f $REMOTE_DIR/logs/server.log'"
echo "🛑 停止服务：ssh -i $SSH_KEY $SERVER_USER@$SERVER_IP 'pkill -f smart-cs-server'"
