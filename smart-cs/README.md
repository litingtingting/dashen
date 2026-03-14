# 智能客服系统 (Smart CS)

为淘宝店铺、微信公众号、抖音等多平台提供**多租户智能客服系统**，支持不同人设风格、权限隔离、套餐计费、对话记录管理。

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
│   └── scheduler/       # 定时任务（清理 7 天数据）
├── pkg/
│   ├── db/              # 数据库操作
│   └── utils/           # 工具函数
├── configs/             # 配置文件
├── logs/                # 日志目录
└── data/                # SQLite 数据库文件
```

---

## 🚀 快速开始

### 1. 配置环境

```bash
# 复制配置文件
cp configs/config.example.yml configs/config.yml

# 编辑配置文件，填写必要参数
vim configs/config.yml
```

### 2. 必要配置项

| 配置项 | 说明 |
|--------|------|
| `server.domain` | 备案域名 |
| `server.ssl.cert_file` | HTTPS 证书路径 |
| `server.ssl.key_file` | HTTPS 密钥路径 |
| `platforms.wechat.app_id` | 微信公众号 AppID |
| `platforms.wechat.app_secret` | 微信公众号 AppSecret |
| `ai.api_key` | 百炼 AI API Key |

### 3. 编译运行

```bash
# 编译
cd cmd/server
go build -o ../../bin/smart-cs-server

# 运行
./bin/smart-cs-server
```

---

## 📋 功能特性

- ✅ **多租户架构** - 数据完全隔离，支持无限扩展
- ✅ **多平台接入** - 微信、淘宝、抖音（小红书待支持）
- ✅ **人设系统** - 不同店铺可配置不同客服人设
- ✅ **套餐计费** - 体验版/标准版/专业版/企业版
- ✅ **对话管理** - 自动记录，7 天清理
- ✅ **内容过滤** - AI 输出合规检查
- ✅ **权限控制** - 超级管理员/租户管理员/普通客服

---

## 🔐 权限系统

| 角色 | 权限 |
|------|------|
| 超级管理员 | 管理所有租户（丽斯飞书） |
| 租户管理员 | 自己店铺的全部权限 |
| 普通客服 | 仅限对话处理 |

---

## 📊 技术栈

| 组件 | 技术选型 |
|------|---------|
| 后端框架 | Go + Gin |
| 数据库 | SQLite |
| AI 接入 | 阿里云百炼 |
| 部署 | Docker + systemd |

---

## 📖 文档

- [设计文档](../../projects/smart-cs/design.md)
- [平台对接调研](../../projects/smart-cs/research/platform-integration.md)
- [开发者文档](./docs/developer-guide.md) ← 待编写
- [用户文档](./docs/user-guide.md) ← 待编写

---

## 📅 开发计划

| 阶段 | 内容 | 时间 |
|------|------|------|
| 第一阶段 | 核心功能（权限、数据库、AI 接入、过滤） | 1-2 周 |
| 第二阶段 | 平台对接（微信、淘宝、抖音） | 1-2 周 |
| 第三阶段 | 完善优化（管理后台、统计、文档） | 1 周 |

---

## 📝 更新日志

### v0.1.0 (2026-03-14)
- 项目初始化
- 完成架构设计
- 完成平台对接调研

---

*项目启动时间：2026-03-14*
*开发者：代码多多*
