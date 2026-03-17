#!/bin/bash
# 智能客服系统 - 每日汇报脚本
# 用于生成日报并发送到飞书群

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
REPORT_FILE="$PROJECT_DIR/reports/daily-$(date +%Y-%m-%d).md"

# 创建报告目录
mkdir -p "$PROJECT_DIR/reports"

# 生成日报内容
cat > "$REPORT_FILE" <<EOF
# 智能客服系统 - 每日汇报

**日期**：$(date +%Y-%m-%d)
**汇报时间**：$(date +%H:%M)

## 📊 昨日进度

### 已完成
- [待填充]

### 进行中
- [待填充]

### 遇到问题
- [待填充]

## 🔧 系统状态

### 服务器
- **地址**：150.158.52.215 (腾讯云 2 核 2G)
- **状态**：待检查

### API 调用
- **百炼 API**：正常
- **调用次数**：待统计

### 错误日志
- **数量**：待检查

## 📋 今日计划

1. [待填充]
2. [待填充]
3. [待填充]

## 💡 需要协助

无

---
*自动生成于 $(date +%Y-%m-%d\ %H:%M:%S)*
EOF

echo "✅ 日报已生成：$REPORT_FILE"
echo ""
echo "📝 请手动编辑补充内容，然后发送到飞书群"
