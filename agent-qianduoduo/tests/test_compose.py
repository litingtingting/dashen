#!/usr/bin/env python3
"""
test_compose.py - docker-compose 编排验证测试
"""

import subprocess
import sys
import os


def test_compose_exists():
    """docker-compose.yml 是否存在"""
    assert os.path.exists("docker-compose.yml"), "docker-compose.yml 不存在"
    print("✅ docker-compose.yml 存在")


def test_compose_service_count():
    """检查服务数量"""
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # 检查是否包含 openclaw 和 qianduoduo 服务
    assert "openclaw:" in content, "缺少 openclaw 服务"
    assert "qianduoduo:" in content or "- qianduoduo" in content, "缺少 qianduoduo 服务"
    print("✅ docker-compose.yml 包含 openclaw 和 qianduoduo 服务")


def test_compose_image_tag():
    """检查镜像标签是否正确"""
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # 检查镜像标签
    assert "image: qianduoduo:latest" in content, "缺少 qianduoduo:latest 镜像标签"
    print("✅ docker-compose.yml 使用正确的镜像标签 qianduoduo:latest")


def test_compose_ports():
    """检查端口配置"""
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # 检查 openclaw 是否监听 12131 端口
    assert "12131:12131" in content, "openclaw 端口配置错误"
    print("✅ docker-compose.yml 端口配置正确 (12131:12131)")


def test_compose_volumes():
    """检查数据卷配置"""
    with open("docker-compose.yml", "r") as f:
        content = f.read()
    
    # 检查 volume 挂载
    assert "volumes:" in content, "缺少 volumes 配置"
    print("✅ docker-compose.yml 包含 volumes 配置")


if __name__ == "__main__":
    print("=== docker-compose 编排验证测试 ===\n")
    
    test_compose_exists()
    test_compose_service_count()
    test_compose_image_tag()
    test_compose_ports()
    test_compose_volumes()
    
    print("\n✅ 所有 docker-compose 测试通过！")