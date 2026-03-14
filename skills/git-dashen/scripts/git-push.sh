#!/bin/bash
# Git Dashen 仓库推送脚本
# 自动使用正确的 SSH 密钥进行推送

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
REPO_DIR="$WORKSPACE_DIR/dashen-repo"
SSH_KEY="$WORKSPACE_DIR/dashen-ai"

# 检查密钥文件是否存在
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ 错误：SSH 密钥文件不存在：$SSH_KEY"
    exit 1
fi

# 检查仓库目录是否存在
if [ ! -d "$REPO_DIR" ]; then
    echo "❌ 错误：仓库目录不存在：$REPO_DIR"
    exit 1
fi

cd "$REPO_DIR"

# 显示当前状态
echo "📊 当前 Git 状态："
git status --short

# 询问是否继续
read -p "是否继续推送？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "❌ 取消推送"
    exit 0
fi

# 推送
echo "🚀 推送到远程仓库..."
GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o IdentitiesOnly=yes" git push origin master

echo "✅ 推送成功！"
