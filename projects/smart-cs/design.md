# 智能客服系统 - 设计方案

## 📋 项目概述

为淘宝店铺、微信公众号、小红书等多平台提供**多租户智能客服系统**，支持不同人设风格、权限隔离、套餐计费、对话记录管理。

---

## 🏗️ 系统架构

### 技术栈选择（轻量级优先）

| 组件 | 技术选型 | 理由 |
|------|---------|------|
| **后端框架** | Go + Gin | 高性能、低内存占用、编译为单二进制 |
| **数据库** | SQLite | 无需单独服务、轻量、足够支撑中小规模 |
| **缓存** | 内存缓存（可选Redis） | 2G内存优先用内存，量大再上Redis |
| **AI接入** | 百炼API | 阿里云百炼大模型 |
| **部署** | Docker + systemd | 简单可靠 |

### 目录结构

```
/srv/smart-cs/
├── cmd/
│   └── server/          # 主程序入口
├── internal/
│   ├── api/             # HTTP API
│   ├── auth/            # 权限验证
│   ├── tenant/          # 多租户管理
│   ├── conversation/    # 对话管理
│   ├── ai/              # 百炼AI接入
│   ├── filter/          # 内容过滤
│   └── scheduler/       # 定时任务（清理7天数据）
├── pkg/
│   ├── db/              # 数据库操作
│   └── utils/           # 工具函数
├── configs/             # 配置文件
├── logs/                # 日志目录
└── data/                # SQLite数据库文件
```

---

## 🔐 权限系统设计

### 角色定义

| 角色 | 权限 | 说明 |
|------|------|------|
| **超级管理员** | 全部权限 | 丽斯飞书主体，管理所有租户 |
| **租户管理员** | 自己店铺的全部权限 | 店铺/公众号负责人 |
| **普通客服** | 仅限对话处理 | 不能查看配置、账单等 |

### 主体（租户）信息

```sql
-- 主体表
tenants (
    id              TEXT PRIMARY KEY,      -- 租户ID
    name            TEXT,                   -- 主体名称
    type            TEXT,                   -- 类型：taobao|wechat|xiaohongshu
    platform_id     TEXT,                   -- 平台ID（店铺ID等）
    api_key         TEXT,                   -- 平台API密钥（加密存储）
    persona_config  TEXT,                   -- 人设配置JSON
    status          INTEGER,                -- 状态：1启用 0禁用
    created_at      DATETIME,
    updated_at      DATETIME
)

-- 用户表
users (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT,                   -- 所属租户
    username        TEXT,
    password_hash   TEXT,                   -- 密码哈希
    role            TEXT,                   -- admin|operator
    created_at      DATETIME
)

-- 套餐表
plans (
    id              TEXT PRIMARY KEY,
    name            TEXT,                   -- 套餐名称
    daily_limit     INTEGER,                -- 每日对话上限
    price_month     REAL,                   -- 月费
    price_year      REAL,                   -- 年费
    features        TEXT                    -- 功能列表JSON
)

-- 租户订阅表
subscriptions (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT,
    plan_id         TEXT,
    start_date      DATETIME,
    end_date        DATETIME,
    status          TEXT                    -- active|expired|cancelled
)

-- 对话记录表
conversations (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT,
    customer_id     TEXT,                   -- 客户ID
    customer_info   TEXT,                   -- 客户信息JSON
    message_type    TEXT,                   -- inbound|outbound
    content         TEXT,                   -- 消息内容
    ai_response     TEXT,                   -- AI回复（如有）
    filtered        INTEGER,                -- 是否经过过滤
    created_at      DATETIME                -- 用于7天清理
)

-- 使用量统计表
usage_stats (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT,
    date            DATE,
    message_count   INTEGER,
    ai_call_count   INTEGER
)
```

---

## 🎭 人设系统

### 人设配置示例

```json
{
  "name": "贴心小助手",
  "tone": "温暖亲切",
  "style": "姐妹风",
  "greeting": "亲～欢迎来到小店！有什么可以帮您的吗？💕",
  "forbidden_topics": ["政治", "敏感话题"],
  "response_rules": [
    "不用AI腔调，像真人聊天",
    "多用表情符号",
    "避免长篇大论",
    "不确定时引导人工客服"
  ]
}
```

### 不同平台风格建议

| 平台 | 风格建议 |
|------|---------|
| **淘宝** | 亲切热情，"亲～"风格，多用表情 |
| **微信公众号** | 专业友好，适度活泼 |
| **小红书** | 姐妹风，真实分享感 |

---

## 🔄 对话处理流程

```
用户消息
   ↓
1. 权限验证（租户是否有效、是否超限）
   ↓
2. 内容安全检查（输入过滤）
   ↓
3. 百炼AI调用（带人设prompt）
   ↓
4. AI输出过滤（敏感词、合规检查）
   ↓
5. 人味化处理（去AI腔调）
   ↓
6. 记录对话（存入数据库）
   ↓
7. 返回给用户
```

### 内容过滤规则

```go
// 过滤规则示例
var forbiddenPatterns = []string{
    "密钥", "密码", "token", "api_key",
    "政治敏感词", "违法违规内容",
    // ... 可配置
}

// AI输出去味处理
func humanizeResponse(aiText string) string {
    // 去掉"作为AI助手"这类话
    // 缩短过长回复
    // 添加适当语气词
    // ...
}
```

---

## 🧹 数据清理策略

### 7天自动清理

```go
// 每日凌晨2点执行
func cleanupOldConversations() {
    cutoff := time.Now().AddDate(0, 0, -7)
    db.Exec("DELETE FROM conversations WHERE created_at < ?", cutoff)
}
```

### 可选：重要对话标记

```sql
-- 重要对话可标记保留
ALTER TABLE conversations ADD COLUMN keep_forever BOOLEAN DEFAULT 0;
```

---

## 💰 套餐设计

| 套餐 | 日限额 | 月费 | 年费 | 功能 |
|------|--------|------|------|------|
| **体验版** | 50次 | 免费 | - | 基础对话、1个人设 |
| **标准版** | 500次 | ¥99 | ¥999 | 多个人设、对话记录、基础统计 |
| **专业版** | 2000次 | ¥299 | ¥2999 | 无限人设、高级统计、API接入 |
| **企业版** | 定制 | 面议 | 面议 | 私有部署、定制开发 |

---

## 🔒 安全设计

### 1. 密钥管理
- 所有API密钥**加密存储**（AES-256）
- 密钥**永不输出**到日志或响应
- 配置文件权限`600`

### 2. 租户隔离
- 每个租户只能访问自己的数据
- SQL查询强制带`tenant_id`条件
- API验证租户身份

### 3. AI输出过滤
- 敏感词过滤
- 合规检查（广告法、平台规则）
- 人工审核开关（可疑内容标记）

### 4. 访问控制
- 管理员后台需登录
- API调用需验证token
- 操作日志记录

---

## 📦 部署方案

### 服务器资源分配（2核2G）

| 组件 | 内存占用 | 说明 |
|------|---------|------|
| Go服务 | ~50MB | 编译后单二进制 |
| SQLite | ~20MB | 嵌入式数据库 |
| 系统预留 | ~500MB | 系统和其他进程 |
| 可用余量 | ~1.4GB | 足够支撑 |

### 部署步骤

```bash
# 1. 创建目录
sudo mkdir -p /srv/smart-cs/{configs,logs,data}

# 2. 上传编译好的二进制
scp smart-cs-server ubuntu@150.158.52.215:/srv/smart-cs/

# 3. 创建systemd服务
sudo vim /etc/systemd/system/smart-cs.service

# 4. 启动服务
sudo systemctl enable smart-cs
sudo systemctl start smart-cs

# 5. 配置Nginx反向代理（可选）
```

---

## 📅 开发计划

### 第一阶段：核心功能（1-2周）
- [ ] 基础框架搭建
- [ ] 多租户权限系统
- [ ] 数据库设计实现
- [ ] 百炼AI接入
- [ ] 内容过滤

### 第二阶段：平台对接（1-2周）
- [ ] 淘宝店铺接入
- [ ] 微信公众号接入
- [ ] 小红书接入（如有API）

### 第三阶段：完善优化（1周）
- [ ] 管理后台
- [ ] 数据统计
- [ ] 性能优化
- [ ] 文档完善

---

## ⚠️ 注意事项

1. **服务器安全**：配置防火墙，仅开放必要端口
2. **数据备份**：定期备份SQLite数据库
3. **日志轮转**：避免日志占满磁盘
4. **监控告警**：服务异常及时通知

---

*设计时间：2026-03-14*
*设计师：代码多多*
