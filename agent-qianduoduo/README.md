# 安装
### 先安装必要的软件
```
sudo yum install -y yum-utils device-mapper-persistent-data lvm2
# 更新缓存并安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# 启动 Docker 并设置开机自启
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
sudo docker run hello-world
```

### 配置docker的镜像地址：编辑/etc/docker/daemon.json
```
{
  "registry-mirrors": [
        "https://xxxx.mirror.aliyuncs.com",   #自己的阿里云加速地址
        "https://docker.m.daocloud.io",
        "https://dockerproxy.com"
  ]
}
```

### 阿里云自带的docker-compose版本比较低的话，可以接下来执行以下操作
```
# 下载最新版 Docker Compose 二进制文件
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 赋予执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 创建软链接（可选，让 docker-compose 命令全局可用）
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 验证
docker-compose --version
```

### 下载本仓库地址
```
mkdir -p /home/user/projects/qianduoduo
cd   /home/user/projects/qianduoduo
git clone git@github.com:litingtingting/dashen.git .
```


### openclaw文档：https://docs.openclaw.ai/install/docker
### 开始下载openclaw
```
mkdir -p /home/user/projects/openclaw
cd /home/user/projects/openclaw
git clone https://github.com/openclaw/openclaw.git .
export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"

# 运行安装脚本
./docker-setup.sh

# 将大神中仓库中的agent-qianduoduo目录下的docker-compose.yml和.env.openclaw移到当前目录，并改相关环境变量

# 运行openclaw的相关配置向导，可以以极简为主，skip to now
docker compose run --rm openclaw-cli onboard

#可自己再修改相关配置
#模型配置
"models": {
    "mode": "merge",
    "providers": {
      "bailian": {
        "baseUrl": "${BAILIAN_BASEURL}",
        "apiKey": "${BAILIAN_APIKEY}",
        "api": "openai-completions",
        "models": [
          {
            "id": "qwen3.5-plus",
            "name": "qwen3.5-plus",
            "reasoning": false,
            "input": [
              "text",
              "image"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "qwen3-max-2026-01-23",
            "name": "qwen3-max-2026-01-23",
            "reasoning": false,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 262144,
            "maxTokens": 65536
          },
          {
            "id": "qwen3-coder-next",
            "name": "qwen3-coder-next",
            "reasoning": false,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 262144,
            "maxTokens": 65536
          },
          {
            "id": "qwen3-coder-plus",
            "name": "qwen3-coder-plus",
            "reasoning": false,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 1000000,
            "maxTokens": 65536
          },
          {
            "id": "MiniMax-M2.5",
            "name": "MiniMax-M2.5",
            "reasoning": false,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 204800,
            "maxTokens": 131072
          },
          {
            "id": "glm-5",
            "name": "glm-5",
            "reasoning": false,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 202752,
            "maxTokens": 16384
          },
          {
            "id": "glm-4.7",
            "name": "glm-4.7",
            "reasoning": false,
            "input": [
              "text"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 202752,
            "maxTokens": 16384
          },
          {
            "id": "kimi-k2.5",
            "name": "kimi-k2.5",
            "reasoning": false,
            "input": [
              "text",
              "image"
            ],
            "cost": {
              "input": 0,
              "output": 0,
              "cacheRead": 0,
              "cacheWrite": 0
            },
            "contextWindow": 262144,
            "maxTokens": 32768
          }
        ]
      }
    }
  }
#agent配置
"agents": {
    "defaults": {
      "model": {
        "primary": "bailian/qwen3.5-plus"
      },
      "models": {
        "bailian/qwen3.5-plus": {},
        "bailian/qwen3-max-2026-01-23": {},
        "bailian/qwen3-coder-next": {},
        "bailian/qwen3-coder-plus": {},
        "bailian/MiniMax-M2.5": {},
        "bailian/glm-5": {},
        "bailian/glm-4.7": {},
        "bailian/kimi-k2.5": {}
      },
      "workspace": "C:\\Users\\61010\\.openclaw\\workspace",
      "compaction": {
        "mode": "safeguard"
      },
      "maxConcurrent": 4,
      "subagents": {
        "maxConcurrent": 8
      }
    },
    "list": [
      {
      "id": "main",
      "name": "主智能体",
      "model": "bailian/qwen3.5-plus",
      "workspace": "~/.openclaw/workspace-main"
    },
    {
      "id": "qianduoduo",
      "name": "钱多多",
      "type": "http",
      "url": "http://qianduoduo:5000/webhook",  // 通过容器名访问
      "timeout": 30000,
      "workspace": "~/.openclaw/workspace-qianduoduo"  // 可选
    }
  ]
}
# 飞书配置
 "channels": {
    "feishu": {
      "enabled": true,
      "accounts": {
        "qianduoduo_bot": {
          "appId": "${FS_APPID}",
          "appSecret": "${FS_APPSECRET}"
        }
      }
    }
  },
  "bindings": [
    {
      "agentId": "qianduoduo",
      "match": {
        "channel": "feishu",
        "accountId": "qianduoduo_bot"
      }
    }
  ],


# 设置权限
chown -R 1000:1000  /home/user/projects/

# 重启相关容器
docker-compose up -d

```




