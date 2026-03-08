# agent-qianduoduo - 钱多多智能体 Docker 化部署

## 📜 目录
- [快速开始](#-快速开始)
- [环境准备](#-环境准备)
- [部署步骤](#-部署步骤)
- [运行测试](#-运行测试)
- [进阶：容器编排](#-进阶容器编排)
- [常见问题](#-常见问题)

---

## 🚀 快速开始

> **3 分钟快速部署**（适用于有 Docker 基础的用户）

```bash
# 1. 克隆仓库
git clone https://github.com/litingtingting/dashen.git
cd dashen

# 2. 复制关键文件（从钱多多智能体工作区）
# Windows 路径（WSL 下）
cp -r /mnt/d/丽斯/AI公司/agents/qianduoduo/skills ./skills/
cp /mnt/d/丽斯/AI公司/agents/qianduoduo/AGENTS.md ./AGENTS.md
cp /mnt/d/丽斯/AI公司/agents/qianduoduo/TOOLS.md ./TOOLS.md
cp -r /mnt/d/丽斯/AI公司/agents/qianduoduo/permission ./permission/

# 3. 创建环境变量文件
cp env.example .env
# 编辑 .env，填入真实密钥

# 4. 构建镜像
docker build -t qianduoduo:latest .

# 5. 运行测试
docker run -it --env-file .env qianduoduo:latest
```

---

## 🔧 环境准备

### 1. Docker 安装

| 平台 | 链接 | 命令验证 |
|------|------|---------|
| Windows | [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) | `docker --version` |
| macOS | [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) | `docker --version` |
| Linux/WSL | [Docker Engine](https://docs.docker.com/engine/install/) | `docker --version` |

### 2. 确认安装成功

```bash
# 检查 Docker
docker --version
# 输出示例：Docker version 24.0.7, build afdd53b

# 检查 docker-compose（可选）
docker-compose --version
```

### 3. WSL 用户特别说明（Windows）

- Docker Desktop 需启用 **WSL2 集成**
- 挂载路径：`/mnt/d/丽斯/AI公司/...` ↔ `D:\丽斯\AI公司\...`

---

## 🛠️ 部署步骤

### 步骤 1：克隆仓库

```bash
git clone https://github.com/litingtingting/dashen.git
cd dashen
```

> ✅ 当前目录结构：
> ```
> dashen/
> ├── Dockerfile
> ├── README.md
> ├── AGENTS.md
> ├── TOOLS.md
> ├── entrypoint.sh
> ├── env.example
> ├── skills/      ← 要从钱多多复制
> └── permission/  ← 要从钱多多复制
> ```

### 步骤 2：复制钱多多的技能代码

> 💡 **为什么需要复制？**
> - `skills/` 包含实时盯盘、宏观分析等核心逻辑
> - `permission/` 包含密钥保护策略
> - 这些代码需要与您的本地钱多多智能体同步

```bash
# Windows + WSL 用户（路径映射）
cp -r /mnt/d/丽斯/AI公司/agents/qianduoduo/skills ./skills/
cp /mnt/d/丽斯/AI公司/agents/qianduoduo/AGENTS.md ./AGENTS.md
cp /mnt/d/丽斯/AI公司/agents/qianduoduo/TOOLS.md ./TOOLS.md
cp -r /mnt/d/丽斯/AI公司/agents/qianduoduo/permission ./permission/
```

> 📌 说明：
> - `/mnt/d/丽斯/AI公司/...` 是 WSL 对 Windows 的挂载路径
> - 如果不在 WSL，直接用 Windows 原路径（如 `D:\丽斯\AI公司\agents\qianduoduo\`）

### 步骤 3：配置密钥

```bash
# 复制模板
cp env.example .env

# 编辑密钥（使用 VS Code / Notepad++ 等）
# -----------------------------------------------------
# 编辑 .env，填入您的真实密钥：

ITICK_TOKEN=your_iTick_api_token_here
TUSHARE_TOKEN=your_tushare_api_token_here
BRAVE_API_KEY=your_brave_api_key_here
# -----------------------------------------------------
```

> 🔐 **安全提示**：
> - `.env` 已在 `.gitignore` 中，**不会提交到 GitHub**
> - 切勿将 `.env` 分享给他人

### 步骤 4：构建 Docker 镜像

```bash
# 在 dashen/ 目录下
docker build -t qian-duoduo:latest .
```

> ⏱️ **首次构建时间**：5-10 分钟（下载基础镜像 + 安装依赖）
> 
> ✅ 成功标志：`Successfully built xxx` + `Successfully tagged qian-duoduo:latest`

### 步骤 5：运行测试

```bash
# 交互模式（调试用）
docker run -it --env-file .env qian-duoduo:latest

# 或直接运行预制分析脚本
docker run --env-file .env qian-duoduo:latest python skills/pre_market_analysis.py
```

> 🎯 **预期输出**：
> ```
> ========================================
> 美股开盘前大盘趋势分析
> ========================================
> 分析时间：2026-03-08 19:00:00
> 美股开盘：21:30 (北京时间)
> ...
> ```

---

## 🧪 运行测试

### 方式 1：交互式调试

```bash
docker run -it --env-file .env qian-duoduo:latest /bin/sh

# 进入容器后测试
python -c "import websocket; print('✅ websocket-client OK')"
```

### 方式 2：运行正式脚本

```bash
# 早盘分析
docker run --env-file .env qian-duoduo:latest python skills/pre_market_analysis.py

# 美股盯盘
docker run --env-file .env qian-duoduo:latest python skills/us_market_monitor.py
```

---

## 🔌 进阶：容器编排

### 使用 docker-compose（推荐）

如果您希望同时运行 `openclaw` 网关 + `qianduoduo`，使用以下配置：

```yaml
# docker-compose.yml（已包含在仓库中）
version: '3.8'

services:
  openclaw:
    image: openclaw/openclaw:latest
    ports:
      - "12131:12131"
    volumes:
      - openclaw-data:/openclaw/data
    env_file:
      - .env.openclaw
    privileged: true

  qianduoduo:
    build: .
    env_file:
      - .env
    depends_on:
      - openclaw
    network_mode: service:openclaw
```

启动命令：

```bash
docker-compose up -d
docker-compose logs -f
```

---

## ❓ 常见问题

### Q1：构建失败 "WebSocket 链接失败"

**原因**：iTick 服务需要网络连接

**解决**：
```bash
# 检查网络
ping api.itick.io

# 或使用代理
docker build --network=host -t qian-duoduo:latest .
```

### Q2：找不到 `ITICK_TOKEN`

**原因**：密钥未配置

**解决**：
```bash
# 检查 .env 文件
cat .env

# 或手动设置环境变量
docker run -e ITICK_TOKEN="xxx" ...
```

### Q3：WSL 路径找不到

**原因**：Windows 路径映射问题

**解决**：
```bash
# 确认挂载点
ls /mnt/d/

# 如果为空，重启 Docker Desktop
# 或检查 WSL 设置
```

### Q4：Python 依赖安装超时

**解决**：使用国内镜像源
```bash
# 已在 Dockerfile 中配置，无需手动操作
# 镜像源：https://pypi.tuna.tsinghua.edu.cn/simple
```

---

## 📚 更多资源

- [iTick Official Docs](https://docs.itick.io)
- [Tushare Documentation](https://tushare.pro/document/2)
- [Docker Best Practices](https://docs.docker.com/develop/)

---

## 🤝 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

---

## 📝 许可证

MIT License - See `LICENSE` file for details.

---

*最后更新：2026-03-08 | 作者：dashen*
