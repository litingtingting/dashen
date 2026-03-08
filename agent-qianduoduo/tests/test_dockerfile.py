#!/usr/bin/env python3
"""
test_dockerfile.py - Dockerfile 构建验证测试
"""

import subprocess
import sys
import os


def test_dockerfile_exists():
    """Dockerfile 是否存在"""
    assert os.path.exists("Dockerfile"), "Dockerfile 不存在"
    print("✅ Dockerfile 存在")


def test_dockerfile_syntax():
    """Dockerfile 语法检查（基础）"""
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    required_lines = [
        "FROM python:3.11-slim-alpine",
        "WORKDIR /app/qianduoduo",
        "COPY skills/",
        "COPY AGENTS.md",
        "COPY entrypoint.sh",
        "ENTRYPOINT",
    ]
    
    for line in required_lines:
        assert line in content, f"Dockerfile 缺少必要行: {line}"
    
    print("✅ Dockerfile 语法检查通过")


def test_dockerfile_no_credentials():
    """Dockerfile 是否包含明文凭据"""
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    forbidden_patterns = [
        "ITICK_TOKEN=",
        "TUSHARE_TOKEN=",
        "BRAVE_API_KEY=",
    ]
    
    for pattern in forbidden_patterns:
        assert pattern not in content, f"DockerFile 包含明文凭据: {pattern}"
    
    print("✅ Dockerfile 无明文凭据")


if __name__ == "__main__":
    print("=== Dockerfile 构建验证测试 ===\n")
    
    test_dockerfile_exists()
    test_dockerfile_syntax()
    test_dockerfile_no_credentials()
    
    print("\n✅ 所有 Dockerfile 测试通过！")
