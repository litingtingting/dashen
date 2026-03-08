FROM python:3.11-slim-alpine

WORKDIR /app/qianduoduo

# 使用国内镜像源加速
RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.aliyun.com/' /etc/apk/repositories

RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    openssl-dev \
    libwebsockets-dev \
    curl \
    && rm -rf /var/cache/apk/*

# pip 国内源加速
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

RUN pip install --no-cache-dir \
    websocket-client>=1.6.0 \
    tushare \
    requests \
    && pip cache purge

COPY skills/ ./skills/
COPY AGENTS.md ./AGENTS.md
COPY TOOLS.md ./TOOLS.md
COPY permission/ ./permission/

RUN adduser -D -g '' qianbot && \
    chown -R qianbot:qianbot /app/qianduoduo
USER qianbot

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
