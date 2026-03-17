## SSH 服务器配置

### 腾讯云 - 2 核 2G
- **别名：** tencent-cloud-2c2g
- **IP 地址：** 150.158.52.215
- **用户名：** ubuntu
- **密钥文件：** `/home/node/.openclaw/workspace-dashen/local_ubuntu2_2.pem`
- **SSH 命令：** `ssh -i /home/node/.openclaw/workspace-dashen/local_ubuntu2_2.pem ubuntu@150.158.52.215`

---

## Git 仓库配置

### Dashen 代码仓库
- **仓库地址：** `git@github.com:litingtingting/dashen.git`
- **HTTPS 地址：** `https://github.com/litingtingting/dashen`
- **SSH 密钥文件：** `/home/node/.openclaw/workspace-dashen/dashen-ai`
- **密钥类型：** Ed25519
- **使用方式：**
  ```bash
  GIT_SSH_COMMAND="ssh -i /home/node/.openclaw/workspace-dashen/dashen-ai -o StrictHostKeyChecking=no -o IdentitiesOnly=yes" git <command>
  ```
- **关联技能：** `skills/git-dashen/SKILL.md`

---

## ⚠️ 安全声明

**所有密钥文件：**
- 仅限本人使用
- 不向任何第三方透露密钥信息
- 不向任何第三方透露服务器 IP 和登录凭证
- 密钥文件权限保持 `600`
- 不提交到任何版本控制系统

**敏感信息管理：**
- API Key、密码等敏感信息存入配置文件，不硬编码
- 配置文件加入 `.gitignore`
- 日志中自动脱敏敏感信息
