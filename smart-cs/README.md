# 智能客服系统 - Smart CS

**多租户智能客服系统** - 为淘宝店铺、微信公众号等平台提供 AI 客服能力

---

## 🚀 快速开始

### 1. 环境准备

```bash
# 安装 Go 1.21+
go version

# 安装依赖
go mod download
```

### 2. 配置环境变量

```bash
# 复制 .env.example 为 .env
cp .env.example .env

# 编辑 .env 填写实际值
vim .env
```

### 3. 启动服务

```bash
# 开发模式
go run cmd/server/main.go

# 生产模式
go build -o bin/smart-cs ./cmd/server/main.go
./bin/smart-cs
```

---

## 📁 项目结构

```
smart-cs/
├── cmd/
│   └── server/          # 主程序入口
├── internal/
│   ├── api/             # HTTP API
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
├── configs/
│   └── config.yml       # 配置文件
├── logs/                # 日志目录
├── data/                # SQLite 数据库
└── web/                 # 管理后台前端
```

---

## 🔧 配置说明

### 环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `CUSTOMER_BAILIAN_BASEURL` | 百炼 API 地址 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `CUSTOMER_APIKEY` | 百炼 API Key | `sk-e9c...` |

### 配置文件

```yaml
server:
  port: 80

database:
  wal_mode: true  # 启用 WAL 模式支持并发

bailian:
  model: "qwen-plus"
  timeout_ms: 30000
```

---

## 📊 开发进度

- [x] 项目初始化
- [x] 数据库设计
- [ ] 多租户权限系统
- [ ] 百炼 AI 对接
- [ ] 内容过滤
- [ ] 淘宝店铺对接
- [ ] 管理后台

---

## 📝 API 接口

### 对话接口

```
POST /api/conversation
Content-Type: application/json

{
  "tenant_id": "xxx",
  "customer_id": "xxx",
  "message": "你好"
}
```

---

*最后更新：2026-03-17*
