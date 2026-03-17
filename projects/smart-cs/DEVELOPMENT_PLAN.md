# 🚀 智能客服系统 - 开发计划

**最后更新：** 2026-03-17  
**负责人：** dashen  
**优先级：** 🔴 最高

---

## 📋 需求确认（丽斯老板 2026-03-17 确认）

### 第一阶段：MVP（2 周）

**核心功能：**
- [x] 需求分析与设计
- [ ] Go 核心框架搭建
- [ ] 多租户权限系统
- [ ] 百炼 AI 对接
- [ ] 内容过滤（输入/输出）
- [ ] 套餐限制（每日调用次数）
- [ ] 对话记录 + 7 天自动清理
- [ ] 淘宝店铺对接
- [ ] 简易管理后台

**基础设施：**
- 服务器：腾讯云 2 核 2G（150.158.52.215）
- 端口：**80 端口**
- 域名：暂时用 IP（`http://150.158.52.215`）
- 数据库：SQLite WAL 模式

**暂缓功能：**
- 微信公众号（等认证，300 元/年）
- 支付集成（先手动开通）
- 复杂搜索（后期加）

---

## 📅 开发计划

### Week 1：核心框架（2026-03-17 ~ 2026-03-23）

#### Day 1-2：项目骨架
- [ ] 初始化 Go 项目
- [ ] 数据库设计实现
- [ ] 基础 API 路由
- [ ] Docker 配置

#### Day 3-4：多租户权限
- [ ] 租户 CRUD
- [ ] 用户认证（JWT）
- [ ] 角色权限（admin/operator）
- [ ] 套餐订阅管理

#### Day 5-7：AI 对接
- [ ] 百炼 API 封装
- [ ] 人设 prompt 注入
- [ ] 输入内容过滤
- [ ] 输出内容过滤
- [ ] 调用次数限制

### Week 2：平台对接 + 后台（2026-03-24 ~ 2026-03-30）

#### Day 1-3：淘宝对接
- [ ] 阿里开放平台注册
- [ ] 淘宝消息格式解析
- [ ] 回调接口实现
- [ ] 测试环境联调

#### Day 4-5：管理后台
- [ ] 前端框架（Vue/React）
- [ ] 订单管理页面
- [ ] 用户管理页面
- [ ] 对话记录页面

#### Day 6-7：测试部署
- [ ] 单元测试
- [ ] 集成测试
- [ ] 服务器部署
- [ ] 生产环境测试

### Week 3：优化完善（2026-03-31 ~ 2026-04-06）

- [ ] 性能优化
- [ ] 日志系统完善
- [ ] 监控告警
- [ ] 文档完善

---

## 🗄️ 数据库设计（最终版）

```sql
-- 租户表
CREATE TABLE tenants (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    type            TEXT NOT NULL,  -- taobao|wechat
    platform_id     TEXT,           -- 店铺 ID
    api_key         TEXT,           -- 加密存储
    api_secret      TEXT,           -- 加密存储
    persona_config  TEXT,           -- JSON
    status          INTEGER DEFAULT 1,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    username        TEXT NOT NULL,
    password_hash   TEXT NOT NULL,
    role            TEXT NOT NULL,  -- admin|operator
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- 套餐表
CREATE TABLE plans (
    id              TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    daily_limit     INTEGER NOT NULL,
    price_month     REAL,
    price_year      REAL,
    features        TEXT,           -- JSON
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 租户订阅表
CREATE TABLE subscriptions (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL UNIQUE,
    plan_id         TEXT NOT NULL,
    start_date      DATETIME NOT NULL,
    end_date        DATETIME NOT NULL,
    status          TEXT NOT NULL,  -- active|expired|cancelled
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);

-- 对话记录表
CREATE TABLE conversations (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    customer_id     TEXT NOT NULL,
    customer_info   TEXT,           -- JSON
    message_type    TEXT NOT NULL,  -- inbound|outbound
    content         TEXT NOT NULL,
    ai_response     TEXT,
    filtered        INTEGER DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- 使用量统计表
CREATE TABLE usage_stats (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    date            DATE NOT NULL,
    message_count   INTEGER DEFAULT 0,
    ai_call_count   INTEGER DEFAULT 0,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    UNIQUE(tenant_id, date)
);

-- 订单表
CREATE TABLE orders (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL,
    plan_id         TEXT NOT NULL,
    amount          REAL NOT NULL,
    status          TEXT NOT NULL,  -- pending|paid|cancelled
    payment_method  TEXT,           -- alipay|wechat
    paid_at         DATETIME,
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id),
    FOREIGN KEY (plan_id) REFERENCES plans(id)
);

-- 索引（优化查询）
CREATE INDEX idx_conversations_tenant ON conversations(tenant_id, created_at);
CREATE INDEX idx_usage_stats_tenant_date ON usage_stats(tenant_id, date);
CREATE INDEX idx_orders_tenant ON orders(tenant_id, created_at);
```

---

## 🔧 技术栈

| 组件 | 技术选型 | 说明 |
|------|---------|------|
| **后端** | Go 1.21 + Gin | 轻量高性能 |
| **数据库** | SQLite (WAL) | 嵌入式，无需单独服务 |
| **前端** | Vue 3 + Element Plus | 快速开发 |
| **认证** | JWT | 无状态认证 |
| **加密** | AES-256 | API Key 加密存储 |
| **部署** | Docker + systemd | 简单可靠 |

---

## 📁 项目结构

```
/srv/smart-cs/
├── cmd/
│   └── server/          # 主程序入口
├── internal/
│   ├── api/             # HTTP API
│   │   ├── handlers/    # 请求处理
│   │   ├── middleware/  # 中间件（认证、限流）
│   │   └── router.go    # 路由配置
│   ├── auth/            # 权限验证
│   ├── tenant/          # 多租户管理
│   ├── conversation/    # 对话管理
│   ├── ai/              # 百炼 AI 接入
│   ├── filter/          # 内容过滤
│   └── scheduler/       # 定时任务
├── pkg/
│   ├── db/              # 数据库操作
│   ├── encrypt/         # 加密工具
│   └── utils/           # 工具函数
├── web/                 # 管理后台前端
│   ├── src/
│   └── dist/            # 编译后静态文件
├── configs/
│   └── config.yml       # 配置文件
├── logs/                # 日志目录
└── data/                # SQLite 数据库
```

---

## 🔐 安全设计

### 1. API Key 加密
```go
// 存储前加密
encrypted := encrypt.AES256(apiKey, os.Getenv("ENCRYPTION_KEY"))

// 使用时解密
apiKey := encrypt.AES256Decrypt(encrypted, os.Getenv("ENCRYPTION_KEY"))
```

### 2. 租户隔离
```go
// 所有查询强制带 tenant_id
func GetConversations(tenantID string) {
    db.Where("tenant_id = ?", tenantID).Find(...)
}
```

### 3. 限流保护
```go
// 全局限流（防止 API 超限）
var globalLimiter = rate.NewLimiter(10, 10)

// 租户限流（防止单个租户占满）
limiter := tenantLimiters.Get(tenantID)
if !limiter.Allow() {
    return ErrRateLimitExceeded
}
```

---

## 📊 每日 8:00 汇报模板

```markdown
# 📊 智能客服系统 - 开发日报

**日期：** YYYY-MM-DD  
**阶段：** Week X Day Y

## ✅ 今日完成
- 

## 🐛 遇到的问题
- 

## 📋 明日计划
- 

## 🖥️ 服务器状态
- CPU: 
- 内存：
- 磁盘：

## ⚠️ 需要确认
- 
```

---

## 🎯 关键里程碑

| 日期 | 里程碑 | 状态 |
|------|--------|------|
| 2026-03-23 | 核心框架完成 | ⏳ 待开始 |
| 2026-03-30 | 淘宝对接完成 | ⏳ 待开始 |
| 2026-03-30 | 管理后台完成 | ⏳ 待开始 |
| 2026-03-30 | 生产环境部署 | ⏳ 待开始 |
| 2026-04-06 | 正式上线 | ⏳ 待开始 |

---

## 📞 需要丽斯老板提供的

### 🔴 高优先级（现在就要）
- [ ] 淘宝店铺名称/ID
- [ ] 阿里开放平台账号（可以晚点注册）

### 🟡 中优先级（下周）
- [ ] 百炼 API Key（我可以帮你申请）
- [ ] 管理后台登录账号密码

### 🟢 低优先级（上线前）
- [ ] 域名备案（暂时用 IP）
- [ ] 微信认证（暂时不做）

---

*创建时间：2026-03-17 18:36*  
*创建人：dashen*
