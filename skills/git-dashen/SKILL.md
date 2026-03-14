---
name: git-dashen
description: 管理 dashen 代码仓库的 Git 操作技能。用于代码提交、推送、分支管理等。仓库地址：https://github.com/litingtingting/dashen，使用 SSH 密钥认证。
---

# Git Dashen 仓库管理

## 仓库信息

| 项目 | 值 |
|------|-----|
| **仓库地址** | `git@github.com:litingtingting/dashen.git` |
| **HTTPS 地址** | `https://github.com/litingtingting/dashen` |
| **SSH 密钥路径** | 见 `TOOLS.md` 中的 `dashen-ai` 文件 |
| **分支策略** | `master` 为主分支 |
| **项目目录** | 每个项目在根目录创建独立文件夹 |

---

## 🔐 密钥管理（重要）

### 密钥位置

SSH 密钥文件存储在工作区根目录：
- **文件路径：** `/home/node/.openclaw/workspace-dashen/dashen-ai`
- **权限：** `600`（仅所有者可读写）
- **类型：** Ed25519 SSH 私钥

### 安全要求

⚠️ **绝对禁止：**
1. ❌ 不要将密钥内容输出到日志
2. ❌ 不要将密钥提交到任何仓库
3. ❌ 不要在公开场合提及密钥路径
4. ❌ 不要将密钥复制给任何人

✅ **正确做法：**
1. ✅ 使用 `GIT_SSH_COMMAND` 环境变量指定密钥
2. ✅ 密钥文件权限保持 `600`
3. ✅ 仅在 Git 操作时临时使用

---

## 🚀 基本使用

### 克隆仓库

```bash
cd /home/node/.openclaw/workspace-dashen
GIT_SSH_COMMAND="ssh -i ./dashen-ai -o StrictHostKeyChecking=no -o IdentitiesOnly=yes" \
  git clone git@github.com:litingtingting/dashen.git dashen-repo
```

### 配置用户信息

```bash
cd dashen-repo
git config user.name "dashen-bot"
git config user.email "dashen@openclaw.local"
```

### 添加新项目

```bash
# 1. 创建项目目录
mkdir -p <project-name>/{cmd,internal,pkg,configs,docs}

# 2. 添加文件
git add <project-name>/

# 3. 提交
git commit -m "feat: 初始化 <project-name> 项目

- 项目结构搭建
- README 文档
- 配置文件示例"

# 4. 推送
GIT_SSH_COMMAND="ssh -i ../dashen-ai -o StrictHostKeyChecking=no -o IdentitiesOnly=yes" \
  git push origin master
```

### 日常提交流程

```bash
cd /home/node/.openclaw/workspace-dashen/dashen-repo

# 1. 查看状态
git status

# 2. 添加变更
git add <files>

# 3. 提交（遵循约定式提交）
git commit -m "type: description

- detail 1
- detail 2"

# 4. 推送
GIT_SSH_COMMAND="ssh -i ../dashen-ai -o StrictHostKeyChecking=no -o IdentitiesOnly=yes" \
  git push origin master
```

---

## 📝 提交信息规范

采用 [约定式提交](https://www.conventionalcommits.org/)：

### 类型（type）

| 类型 | 说明 |
|------|------|
| `feat` | 新功能 |
| `fix` | 修复 bug |
| `docs` | 文档更新 |
| `style` | 代码格式（不影响功能） |
| `refactor` | 重构 |
| `test` | 测试相关 |
| `chore` | 构建/工具/配置 |

### 格式

```
<type>: <简短描述>

<详细正文（可选）>

- 变更点 1
- 变更点 2

Closes #123  # 关联 issue（可选）
```

### 示例

```bash
# 新功能
git commit -m "feat: 添加智能客服系统项目

- 项目结构搭建
- README 文档
- 配置模板

Closes #1"

# 文档更新
git commit -m "docs: 添加开发者文档和用户文档

- 开发者文档：项目结构、API 接口、部署指南
- 用户文档：快速开始、套餐说明、FAQ"

# Bug 修复
git commit -m "fix: 修复配置文件加载错误

- 修复 YAML 解析问题
- 添加配置验证"
```

---

## 📁 项目组织规范

### 仓库根目录结构

```
dashen/
├── agent-qianduoduo/     # 钱多多盯盘助手
├── smart-cs/             # 智能客服系统
└── <新项目>/             # 未来项目
```

### 单个项目结构

```
<project-name>/
├── README.md             # 项目说明（必需）
├── docs/
│   ├── developer-guide.md  # 开发者文档
│   └── user-guide.md       # 用户文档
├── cmd/                  # 程序入口
├── internal/             # 内部包
├── pkg/                  # 公共包
├── configs/              # 配置文件
└── scripts/              # 脚本工具
```

---

## 🔧 常用 Git 命令

### 查看状态

```bash
# 查看变更
git status

# 查看提交历史
git log --oneline -10

# 查看文件差异
git diff <file>
```

### 分支管理

```bash
# 创建新分支
git checkout -b <branch-name>

# 切换分支
git checkout <branch-name>

# 合并分支
git merge <branch-name>

# 删除分支
git branch -d <branch-name>
```

### 撤销操作

```bash
# 撤销工作区修改
git checkout -- <file>

# 撤销暂存
git reset HEAD <file>

# 撤销提交（保留修改）
git reset --soft HEAD~1

# 撤销提交（丢弃修改）
git reset --hard HEAD~1
```

---

## ⚠️ 注意事项

### 1. 推送前检查

```bash
# 确保本地是最新的
git pull origin master

# 查看要推送的内容
git log origin/master..HEAD

# 确认无误后再推送
git push
```

### 2. 大文件处理

不要提交大文件（>10MB）到仓库：
- 二进制文件使用 Git LFS
- 配置文件使用 `.gitignore` 排除
- 敏感信息使用环境变量

### 3. .gitignore 示例

```gitignore
# 配置文件（含敏感信息）
configs/config.yml
*.env
*.pem
*.key

# 编译产物
bin/
dist/
*.exe
*.so

# 依赖
node_modules/
vendor/

# 日志
logs/
*.log

# 系统文件
.DS_Store
Thumbs.db
```

---

## 📚 参考文档

- [Git 官方文档](https://git-scm.com/doc)
- [约定式提交规范](https://www.conventionalcommits.org/)
- [GitHub SSH 连接指南](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)

---

*技能版本：v0.1.0*
*创建时间：2026-03-14*
