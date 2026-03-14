# 智能客服系统 - 开发者文档

## 📁 项目结构

```
smart-cs/
├── cmd/
│   └── server/          # 主程序入口
├── internal/
│   ├── api/             # HTTP API 路由和处理器
│   ├── auth/            # 权限验证和 JWT
│   ├── tenant/          # 多租户管理
│   ├── conversation/    # 对话管理和存储
│   ├── ai/              # 百炼 AI 接入
│   ├── filter/          # 内容过滤和人味化
│   └── scheduler/       # 定时任务
├── pkg/
│   ├── db/              # 数据库操作封装
│   └── utils/           # 工具函数
├── configs/
│   ├── config.example.yml  # 配置模板
│   └── config.yml          # 实际配置（不提交）
├── logs/                # 日志目录
├── data/                # SQLite 数据库文件
└── docs/                # 文档目录
```

---

## 🛠️ 开发环境搭建

### 1. 安装依赖

```bash
# Go 1.21+
go version

# 安装依赖
cd smart-cs
go mod init smart-cs
go mod tidy
```

### 2. 配置文件

```bash
# 复制配置模板
cp configs/config.example.yml configs/config.yml

# 编辑配置
vim configs/config.yml
```

### 3. 本地运行

```bash
# 开发模式运行
go run cmd/server/main.go

# 或编译后运行
go build -o bin/smart-cs-server cmd/server/main.go
./bin/smart-cs-server
```

---

## 📐 架构设计

### 核心模块

#### 1. 多租户系统 (`internal/tenant/`)

```go
// 租户管理
type Tenant struct {
    ID           string    // 租户 ID
    Name         string    // 主体名称
    Type         string    // taobao|wechat|xiaohongshu
    PlatformID   string    // 平台 ID
    PersonaConfig Persona   // 人设配置
    Status       int       // 1 启用 0 禁用
}

// 租户隔离中间件
func TenantMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        tenantID := c.GetHeader("X-Tenant-ID")
        // 验证租户有效性
        // 注入到上下文
    }
}
```

#### 2. 权限系统 (`internal/auth/`)

```go
// 角色定义
type Role string

const (
    RoleSuperAdmin Role = "super_admin"  // 丽斯飞书
    RoleTenantAdmin Role = "tenant_admin" // 租户管理员
    RoleOperator   Role = "operator"     // 普通客服
)

// JWT 验证
func VerifyToken(tokenString string) (*Claims, error) {
    // 解析 JWT
    // 验证签名
    // 返回用户声明
}
```

#### 3. 对话管理 (`internal/conversation/`)

```go
// 对话记录
type Conversation struct {
    ID          string
    TenantID    string
    CustomerID  string
    Message     string
    AIResponse  string
    CreatedAt   time.Time
}

// 自动清理（7 天）
func CleanupOldConversations() error {
    cutoff := time.Now().AddDate(0, 0, -7)
    return db.Delete("conversations", "created_at < ?", cutoff)
}
```

#### 4. AI 接入 (`internal/ai/`)

```go
// 百炼 AI 调用
type BailianClient struct {
    APIKey string
    Model  string
}

func (c *BailianClient) Chat(prompt string, persona Persona) (string, error) {
    // 构建带人设的 prompt
    // 调用百炼 API
    // 返回原始响应
}
```

#### 5. 内容过滤 (`internal/filter/`)

```go
// 敏感词过滤
func FilterSensitiveWords(text string) string {
    // 加载敏感词库
    // 替换敏感词
    // 返回过滤后文本
}

// 人味化处理
func HumanizeResponse(aiText string) string {
    // 去掉"作为 AI 助手"等话术
    // 缩短过长回复
    // 添加语气词
}
```

---

## 🔌 API 接口

### 租户管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/tenants` | 创建租户 |
| GET | `/api/tenants/:id` | 获取租户信息 |
| PUT | `/api/tenants/:id` | 更新租户 |
| DELETE | `/api/tenants/:id` | 删除租户 |

### 对话管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/conversations` | 发送消息 |
| GET | `/api/conversations` | 获取对话列表 |
| GET | `/api/conversations/:id` | 获取单条对话 |

### 平台回调

| 方法 | 路径 | 说明 |
|------|------|------|
| GET/POST | `/api/wechat/callback` | 微信回调 |
| POST | `/api/taobao/callback` | 淘宝回调 |
| POST | `/api/douyin/callback` | 抖音回调 |

---

## 📝 数据库设计

### SQLite 表结构

```sql
-- 租户表
CREATE TABLE tenants (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    platform_id TEXT,
    persona_config TEXT,
    status INTEGER DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用户表
CREATE TABLE users (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- 对话记录表
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    customer_id TEXT,
    customer_info TEXT,
    message_type TEXT,
    content TEXT,
    ai_response TEXT,
    filtered INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 使用量统计表
CREATE TABLE usage_stats (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    date DATE NOT NULL,
    message_count INTEGER DEFAULT 0,
    ai_call_count INTEGER DEFAULT 0,
    UNIQUE(tenant_id, date)
);

-- 创建索引
CREATE INDEX idx_conversations_tenant ON conversations(tenant_id);
CREATE INDEX idx_conversations_created ON conversations(created_at);
CREATE INDEX idx_usage_tenant_date ON usage_stats(tenant_id, date);
```

---

## 🔒 安全注意事项

### 1. 密钥管理

```yaml
# ❌ 不要硬编码
api_key: "sk-xxxxx"

# ✅ 使用环境变量
api_key: ${BAILOAN_API_KEY}
```

### 2. SQL 注入防护

```go
// ❌ 危险
db.Query("SELECT * FROM users WHERE id = " + userID)

// ✅ 安全
db.Query("SELECT * FROM users WHERE id = ?", userID)
```

### 3. 日志脱敏

```go
// 敏感信息脱敏
log.Printf("API Key: %s", maskString(apiKey))

func maskString(s string) string {
    if len(s) < 8 {
        return "****"
    }
    return s[:2] + "****" + s[len(s)-2:]
}
```

---

## 🧪 测试

### 单元测试

```bash
# 运行所有测试
go test ./...

# 运行特定包测试
go test ./internal/auth/...

# 带覆盖率
go test -cover ./...
```

### 集成测试

```bash
# 启动测试数据库
./scripts/test-setup.sh

# 运行集成测试
go test -tags=integration ./...
```

---

## 📦 部署

### Docker 部署

```dockerfile
FROM golang:1.21-alpine AS builder
WORKDIR /app
COPY . .
RUN go build -o smart-cs-server cmd/server/main.go

FROM alpine:latest
COPY --from=builder /app/smart-cs-server /smart-cs-server
COPY --from=builder /app/configs /configs
CMD ["/smart-cs-server"]
```

### Systemd 服务

```ini
# /etc/systemd/system/smart-cs.service
[Unit]
Description=Smart CS Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/srv/smart-cs
ExecStart=/srv/smart-cs/smart-cs-server
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## 🐛 调试技巧

### 1. 启用调试日志

```yaml
log:
  level: "debug"
```

### 2. 查看实时日志

```bash
tail -f logs/server.log
```

### 3. 数据库检查

```bash
sqlite3 data/smart-cs.db ".tables"
sqlite3 data/smart-cs.db "SELECT * FROM tenants;"
```

---

## 📚 参考资源

- [Gin 框架文档](https://gin-gonic.com/docs/)
- [SQLite 文档](https://www.sqlite.org/docs.html)
- [阿里云百炼 API](https://help.aliyun.com/zh/bailian/)
- [微信公众号 API](https://developers.weixin.qq.com/doc/)

---

*文档版本：v0.1.0*
*最后更新：2026-03-14*
