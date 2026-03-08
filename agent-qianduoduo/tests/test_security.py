#!/usr/bin/env python3
"""
test_security.py - 安全测试（生产级别）
"""

import subprocess
import sys
import os


def test_no_env_in_dockerfile():
    """Dockerfile 中不应包含环境变量"""
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    forbidden_env_vars = [
        "ENV ITICK_TOKEN",
        "ENV TUSHARE_TOKEN",
        "ENV BRAVE_API_KEY",
    ]
    
    for var in forbidden_env_vars:
        assert var not in content, f"Dockerfile 中包含环境变量: {var}"
    
    print("✅ Dockerfile 无明文环境变量")


def test_env_file_example_exists():
    """env.example 是否存在"""
    assert os.path.exists("env.example"), "env.example 不存在"
    
    # 检查 env.example 内容是否脱敏
    with open("env.example", "r") as f:
        content = f.read()
    
    # 确保示例值是占位符
    assert "your_token_here" in content or "your_" in content, "env.example 缺少占位符"
    
    print("✅ env.example 存在且使用占位符")


def test_gitignore_excludes_env():
    """.gitignore 是否排除 .env 文件"""
    with open(".gitignore", "r") as f:
        content = f.read()
    
    assert ".env" in content, ".gitignore 未排除 .env 文件"
    print("✅ .gitignore 排除 .env 文件")


def test_dockerignore_excludes_sensitive():
    """.dockerignore 是否排除敏感文件"""
    with open(".dockerignore", "r") as f:
        content = f.read()
    
    # 检查是否排除 .env*
    assert ".env" in content, ".dockerignore 未排除 .env 文件"
    print("✅ .dockerignore 排除 .env 文件")


def test_dockerfile_non_root_user():
    """Dockerfile 是否使用非 root 用户"""
    with open("Dockerfile", "r") as f:
        content = f.read()
    
    assert "USER" in content, "Dockerfile 缺少 USER 配置"
    assert "qianbot" in content or "appuser" in content, "未使用非 root 用户"
    print("✅ Dockerfile 使用非 root 用户")


if __name__ == "__main__":
    print("=== 安全测试（生产级别）===\n")
    
    test_no_env_in_dockerfile()
    test_env_file_example_exists()
    test_gitignore_excludes_env()
    test_dockerignore_excludes_sensitive()
    test_dockerfile_non_root_user()
    
    print("\n✅ 所有安全测试通过！")
    print("🚨 安全提示：生产环境请使用密封密钥管理（Vault/Secrets Manager）")