# 百炼 API Key 配置说明

## 🔑 获取百炼 API Key

1. 访问阿里云百炼控制台：https://bailian.console.aliyun.com/
2. 登录阿里云账号
3. 进入「API-KEY 管理」页面
4. 创建新的 API Key 或使用已有的 Key
5. 复制 Key 到安全位置

## ⚙️ 配置方式

### 方式一：.env 文件（推荐）

在 `smart-cs` 目录下创建 `.env` 文件：

```bash
cd /home/node/.openclaw/workspace-dashen/dashen-repo/smart-cs
cat > .env <<EOF
# 百炼 API Key
BAILIAN_API_KEY=sk-your-api-key-here

# 服务器端口
SERVER_PORT=8080

# 日志级别
LOG_LEVEL=debug
EOF
```

### 方式二：直接修改配置文件

编辑 `configs/config.yml`：

```yaml
ai:
  provider: "bailian"
  api_key: "sk-your-api-key-here"  # 直接填写
  model: "qwen-plus"
```

### 方式三：环境变量

```bash
export BAILIAN_API_KEY=sk-your-api-key-here
```

## 🧪 测试配置

使用测试配置文件：

```bash
cd smart-cs
cp configs/config.test.yml configs/config.yml
```

测试配置特点：
- 关闭 SSL
- 使用测试数据库
- 关闭敏感词过滤
- 调试日志级别

## ✅ 配置验证

配置完成后，运行服务器时会看到：

```
✅ 已加载环境变量：.env
✅ 数据库连接成功
✅ 数据库表结构创建成功
✅ 默认数据初始化完成
🚀 智能客服系统启动中... 监听地址：0.0.0.0:8080
```

## 🔒 安全提示

- ⚠️ 不要将 `.env` 文件提交到 Git
- ⚠️ 不要将 API Key 硬编码到代码中
- ⚠️ 生产环境使用独立的 API Key
- ⚠️ 定期轮换 API Key

## 📚 相关文档

- [TESTING.md](./TESTING.md) - 测试指南
- [configs/config.example.yml](./configs/config.example.yml) - 配置示例
