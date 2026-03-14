# 智能客服系统 - 测试配置指南

## 📋 配置步骤

### 1. 配置百炼 API Key

**方式一：使用 .env 文件（推荐）**

```bash
cd smart-cs
cp .env.test .env
# 编辑 .env，填入你的百炼 API Key
vim .env
```

**.env 文件内容：**
```env
# 百炼 API Key（必填）
BAILIAN_API_KEY=sk-your-actual-api-key-here

# 服务器配置
SERVER_PORT=8080

# 日志级别
LOG_LEVEL=debug
```

**方式二：直接设置环境变量**
```bash
export BAILIAN_API_KEY=sk-your-actual-api-key-here
```

### 2. 配置测试配置文件

```bash
cp configs/config.test.yml configs/config.yml
```

### 3. 初始化测试数据

```bash
chmod +x scripts/init-test-data.sh
./scripts/init-test-data.sh
```

### 4. 运行服务器

**方式一：使用默认配置**
```bash
cd cmd/server
go run main.go -config ../../configs/config.yml -env=true
```

**方式二：使用环境变量**
```bash
cd cmd/server
BAILIAN_API_KEY=sk-xxx go run main.go -config ../../configs/config.yml
```

### 5. 测试 API

```bash
# 健康检查
curl http://localhost:8080/api/health

# 测试 AI 对话（需要实现 handleAITest）
curl -X POST http://localhost:8080/api/ai/test \
  -H "Content-Type: application/json" \
  -d '{"prompt":"你好，请问这个商品有货吗？","tenant_id":"test-tenant-001"}'
```

## 🧪 测试数据说明

测试数据包括：
- **3 个测试租户**：淘宝店铺、微信公众号、抖音直播间
- **3 个管理员账号**：每个租户一个
- **4 条示例对话**：展示不同场景的回复
- **4 个套餐**：体验版/标准版/专业版/企业版

## 📝 配置项说明

| 环境变量 | 配置文件路径 | 说明 |
|---------|-------------|------|
| `BAILIAN_API_KEY` | `ai.api_key` | 百炼 API Key（必填） |
| `SERVER_PORT` | `server.port` | 服务器端口（默认 8080） |
| `LOG_LEVEL` | `log.level` | 日志级别（debug/info/warn/error） |

**优先级：环境变量 > 配置文件**

## ⚠️ 注意事项

1. **API Key 安全**：不要将 `.env` 文件提交到版本控制
2. **测试数据库**：测试数据使用独立的 SQLite 数据库，不影响生产数据
3. **HTTPS**：测试环境关闭 HTTPS，生产环境需配置证书

## 🔗 相关文档

- [QUICKSTART.md](./QUICKSTART.md) - 快速开始
- [README.md](./README.md) - 项目说明
- [config.example.yml](./configs/config.example.yml) - 生产配置示例
