#!/bin/bash
# Git Dashen 仓库克隆脚本
# 自动使用正确的 SSH 密钥进行克隆

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
SSH_KEY="$WORKSPACE_DIR/dashen-ai"
REPO_URL="git@github.com:litingtingting/dashen.git"
REPO_NAME="dashen-repo"

# 检查密钥文件是否存在
if [ ! -f "$SSH_KEY" ]; then
    echo "❌ 错误：SSH 密钥文件不存在：$SSH_KEY"
    exit 1
fi

# 检查是否已存在
if [ -d "$WORKSPACE_DIR/$REPO_NAME" ]; then
    echo "⚠️  仓库目录已存在：$WORKSPACE_DIR/$REPO_NAME"
    read -p "是否删除并重新克隆？(y/n): " confirm
    if [ "$confirm" = "y" ]; then
        rm -rf "$WORKSPACE_DIR/$REPO_NAME"
    else
        echo "❌ 取消克隆"
        exit 0
    fi
fi

cd "$WORKSPACE_DIR"

# 克隆
echo "🚀 克隆仓库..."
GIT_SSH_COMMAND="ssh -i $SSH_KEY -o StrictHostKeyChecking=no -o IdentitiesOnly=yes" git clone "$REPO_URL" "$REPO_NAME"

# 配置用户信息
cd "$REPO_NAME"
git config user.name "dashen-bot"
git config user.email "dashen@openclaw.local"

echo "✅ 克隆成功！"
echo "📁 仓库位置：$WORKSPACE_DIR/$REPO_NAME"
