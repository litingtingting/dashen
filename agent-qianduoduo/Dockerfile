# Dockerfile for 钱多多 (qian-duoduo) Agent
# 使用国内镜像源加速构建，绕过 PEP 668 限制

# 第一阶段：构建环境（使用 Alpine + Python）
FROM alpine:3.19

WORKDIR /app/qianduoduo

# 使用阿里云镜像源加速
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/' /etc/apk/repositories && \
    apk add --no-cache python3 py3-pip py3-openssl py3-requests curl && \
    pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖（绕过 PEP 668 限制）
RUN pip3 install --break-system-packages --no-cache-dir \
    websocket-client>=1.6.0 \
    && pip3 cache purge

# 复制代码
COPY skills/ ./skills/
COPY AGENTS.md ./AGENTS.md
COPY TOOLS.md ./TOOLS.md
COPY permission/ ./permission/

# 创建非 root 用户
RUN adduser -D -g '' qianbot && \
    chown -R qianbot:qianbot /app/qianduoduo
USER qianbot

# 启动脚本（COPY 时自动保留执行权限）
COPY --chmod=755 entrypoint.sh /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
