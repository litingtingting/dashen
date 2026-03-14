#!/bin/bash
# 智能客服系统 - 测试数据初始化脚本
# 用于创建测试租户、用户和对话数据

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DB_PATH="$PROJECT_DIR/data/smart-cs-test.db"

echo "🔧 初始化测试数据..."

# 创建数据目录
mkdir -p "$PROJECT_DIR/data"
mkdir -p "$PROJECT_DIR/logs"

# 检查数据库是否存在
if [ ! -f "$DB_PATH" ]; then
    echo "❌ 数据库不存在，请先运行服务器初始化表结构"
    exit 1
fi

# 使用 sqlite3 插入测试数据
echo "📝 创建测试租户..."
sqlite3 "$DB_PATH" <<EOF
-- 测试租户
INSERT OR REPLACE INTO tenants (id, name, type, platform_id, persona_config, status) 
VALUES 
    ('test-tenant-001', '测试店铺 A', 'taobao', 'tb_123456', '{"name":"小智","tone":"亲切友好","greeting":"亲，您好呀~","emojis":"😊🌟💕","address_style":"亲"}', 1),
    ('test-tenant-002', '测试店铺 B', 'wechat', 'wx_789012', '{"name":"小慧","tone":"专业严谨","greeting":"您好，很高兴为您服务","emojis":"👍✅","address_style":"您"}', 1),
    ('test-tenant-003', '测试直播间', 'douyin', 'dy_345678', '{"name":"小萌","tone":"活泼可爱","greeting":"哈喽哈喽~","emojis":"🎉🌈✨","address_style":"宝子"}', 1);

-- 测试用户（管理员）
INSERT OR REPLACE INTO users (id, tenant_id, username, password_hash, role)
VALUES
    ('user-001', 'test-tenant-001', 'admin001', 'pbkdf2:sha256:260000\$salty\$hash001', 'admin'),
    ('user-002', 'test-tenant-002', 'admin002', 'pbkdf2:sha256:260000\$salty\$hash002', 'admin'),
    ('user-003', 'test-tenant-003', 'admin003', 'pbkdf2:sha256:260000\$salty\$hash003', 'admin');

-- 测试对话记录
INSERT OR REPLACE INTO conversations (id, tenant_id, customer_id, customer_info, message_type, content, ai_response, filtered)
VALUES
    ('conv-001', 'test-tenant-001', 'cust-001', '{"nickname":"小明","level":"VIP"}', 'text', '这个商品有货吗？', '亲，您好呀~ 这款商品目前有现货哦，可以正常下单的！😊', 0),
    ('conv-002', 'test-tenant-001', 'cust-001', '{"nickname":"小明","level":"VIP"}', 'text', '什么时候发货？', '亲，一般下单后 24 小时内发货哦~ 我们会尽快为您安排的！🌟', 0),
    ('conv-003', 'test-tenant-002', 'cust-002', '{"nickname":"张女士"}', 'text', '如何退换货？', '您好，我们支持 7 天无理由退换货。您需要在订单页面申请，审核通过后寄回即可。✅', 0),
    ('conv-004', 'test-tenant-003', 'cust-003', '{"nickname":"宝宝"}', 'text', '有什么优惠吗？', '哈喽哈喽~ 现在关注直播间可以领 10 元优惠券哦！还有满减活动~ 🎉', 0);

-- 测试使用量统计
INSERT OR REPLACE INTO usage_stats (id, tenant_id, date, message_count, ai_call_count)
VALUES
    ('stat-001', 'test-tenant-001', date('now'), 100, 95),
    ('stat-002', 'test-tenant-002', date('now'), 50, 48),
    ('stat-003', 'test-tenant-003', date('now'), 200, 180);

-- 测试订阅
INSERT OR REPLACE INTO subscriptions (id, tenant_id, plan_id, start_date, end_date, status)
VALUES
    ('sub-001', 'test-tenant-001', 'standard', datetime('now'), datetime('now', '+30 days'), 'active'),
    ('sub-002', 'test-tenant-002', 'pro', datetime('now'), datetime('now', '+30 days'), 'active'),
    ('sub-003', 'test-tenant-003', 'enterprise', datetime('now'), datetime('now', '+365 days'), 'active');
EOF

echo "✅ 测试数据初始化完成！"
echo ""
echo "📊 测试数据概览:"
echo "  - 租户：3 个（淘宝/微信/抖音各 1 个）"
echo "  - 用户：3 个（管理员）"
echo "  - 对话：4 条"
echo "  - 套餐：4 个（体验版/标准版/专业版/企业版）"
echo ""
echo "🔑 测试账号:"
echo "  店铺 A: admin001"
echo "  店铺 B: admin002"
echo "  直播间：admin003"
echo ""
echo "🚀 下一步：运行服务器测试 API"
