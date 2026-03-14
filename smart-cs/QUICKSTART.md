# 智能客服系统 - 快速开始

## 🚀 部署到服务器

### 方式一：使用部署脚本（推荐）

```bash
cd /home/node/.openclaw/workspace-dashen/dashen-repo/smart-cs

# 编辑部署脚本，确认服务器信息
vim scripts/deploy.sh

# 执行部署
./scripts/deploy.sh
```

### 方式二：手动部署

```bash
# 1. 本地编译
cd smart-cs
go mod tidy
CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -o bin/smart-cs-server cmd/server/main.go

# 2. 上传到服务器
scp -i local_ubuntu2_2.pem bin/smart-cs-server ubuntu@150.158.52.215:/home/ubuntu/smart-cs/bin/
scp -i local_ubuntu2_2.pem configs/config.yml ubuntu@150.158.52.215:/home/ubuntu/smart-cs/configs/

# 3. 远程启动
ssh -i local_ubuntu2_2.pem ubuntu@150.158.52.215
cd /home/ubuntu/smart-cs
nohup ./bin/smart-cs-server > logs/server.log 2>&1 &
```

---

## ⚙️ 配置说明

### 最小配置（可运行）

编辑 `configs/config.yml`：

```yaml
server:
  host: "0.0.0.0"
  port: 8080
  domain: "your-domain.com"  # 暂时可填 localhost

database:
  type: "sqlite"
  sqlite:
    path: "./data/smart-cs.db"

ai:
  provider: "bailian"
  api_key: "sk-xxx"  # TODO: 替换为你的百炼 API Key
  model: "qwen-plus"
  filter:
    enabled: true
    max_response_length: 500

admin:
  super_admin:
    tenant_id: "lishi-feishu"
    username: "admin"
    password_hash: "admin123"  # TODO: 修改密码
```

### 获取百炼 API Key

1. 访问 https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 开通百炼服务
4. 创建 API Key
5. 复制到配置文件

---

## 🧪 测试接口

### 1. 健康检查

```bash
curl http://localhost:8080/health
# 预期输出：{"status":"ok"}
```

### 2. 创建租户

```bash
curl -X POST http://localhost:8080/api/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "测试店铺",
    "type": "taobao",
    "platform_id": "shop123",
    "status": 1
  }'
```

### 3. 创建用户

```bash
curl -X POST http://localhost:8080/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "租户 ID",
    "username": "test",
    "password_hash": "test123",
    "role": "admin"
  }'
```

### 4. 发送对话

```bash
curl -X POST http://localhost:8080/api/conversations \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "租户 ID",
    "customer_id": "customer123",
    "content": "你好，有什么推荐？"
  }'
```

### 5. AI 测试

```bash
curl -X POST http://localhost:8080/api/ai/test \
  -H "Content-Type: application/json" \
  -d '{"prompt": "你好"}'
```

---

## 📊 查看日志

```bash
# 实时日志
ssh ubuntu@150.158.52.215 "tail -f /home/ubuntu/smart-cs/logs/server.log"

# 最近 100 行
ssh ubuntu@150.158.52.215 "tail -100 /home/ubuntu/smart-cs/logs/server.log"
```

---

## 🛑 管理服务

```bash
# 停止服务
ssh ubuntu@150.158.52.215 "pkill -f smart-cs-server"

# 重启服务
ssh ubuntu@150.158.52.215 "
  cd /home/ubuntu/smart-cs
  pkill -f smart-cs-server || true
  nohup ./bin/smart-cs-server > logs/server.log 2>&1 &
"

# 查看进程
ssh ubuntu@150.158.52.215 "ps aux | grep smart-cs"
```

---

## 📁 服务器目录结构

```
/home/ubuntu/smart-cs/
├── bin/
│   └── smart-cs-server    # 编译后的程序
├── configs/
│   └── config.yml         # 配置文件
├── logs/
│   └── server.log         # 运行日志
├── data/
│   └── smart-cs.db        # SQLite 数据库
└── scripts/
    └── deploy.sh          # 部署脚本（本地）
```

---

## ✅ 完成检查清单

- [ ] Go 环境已安装（服务器）
- [ ] 代码已编译（Linux AMD64）
- [ ] 配置文件已编辑
- [ ] 百炼 API Key 已配置
- [ ] 服务已启动
- [ ] 健康检查通过
- [ ] 日志正常输出

---

*文档版本：v0.2.0*
*更新时间：2026-03-14*
