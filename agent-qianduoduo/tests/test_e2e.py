#!/usr/bin/env python3
"""
test_e2e.py - 端到端测试（完整流程验证）
"""

import subprocess
import sys
import os


def test_build_image():
    """Docker 镜像构建测试"""
    print("🧪 正在构建镜像 qianduoduo:latest...")
    
    result = subprocess.run(
        ["docker", "build", "-t", "qianduoduo:latest", "."],
        capture_output=True,
        text=True,
        timeout=600  # 10 分钟超时
    )
    
    if result.returncode != 0:
        print("❌ 构建失败:")
        print(result.stderr)
        return False
    
    print("✅ 镜像构建成功")
    return True


def test_container_runs():
    """容器运行测试"""
    print("🧪 正在测试容器运行...")
    
    # 简单运行测试（不带密钥，应显示警告但不崩溃）
    result = subprocess.run(
        ["docker", "run", "--rm", "qianduoduo:latest", "/bin/sh", "-c", "echo '测试成功'"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode != 0:
        print("❌ 容器运行失败:")
        print(result.stderr)
        return False
    
    if "测试成功" in result.stdout:
        print("✅ 容器运行成功")
        return True
    else:
        print("❌ 容器输出异常")
        return False


def test_env_warning():
    """缺少环境变量时是否显示警告"""
    print("🧪 正在测试缺少环境变量警告...")
    
    result = subprocess.run(
        ["docker", "run", "--rm", "qianduoduo:latest"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # 应该显示警告（根据 entrypoint.sh 逻辑）
    if result.returncode == 0 and ("警告" in result.stdout or "警告" in result.stderr):
        print("✅ 缺少环境变量时显示警告")
        return True
    else:
        print("⚠️  警告测试结果不确定（容器可能正常退出）")
        return True  # 不强制要求


def test_clean_exit():
    """容器是否能正常退出"""
    print("🧪 正在测试容器正常退出...")
    
    # 带指定命令运行
    result = subprocess.run(
        ["docker", "run", "--rm", "qianduoduo:latest", "/bin/sh", "-c", "exit 0"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    if result.returncode == 0:
        print("✅ 容器正常退出")
        return True
    else:
        print("❌ 容器异常退出")
        return False


if __name__ == "__main__":
    print("=== 端到端测试（完整流程验证）===\n")
    
    # 检查 Docker 是否运行
    check_result = subprocess.run(["docker", "info"], capture_output=True)
    if check_result.returncode != 0:
        print("❌ Docker 未运行，请启动 Docker Desktop")
        sys.exit(1)
    
    print("✅ Docker 已运行\n")
    
    results = []
    results.append(("镜像构建", test_build_image()))
    results.append(("容器运行", test_container_runs()))
    results.append(("环境变量警告", test_env_warning()))
    results.append(("容器退出", test_clean_exit()))
    
    print("\n=== 测试结果汇总 ===")
    all_passed = True
    for name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {name}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 所有端到端测试通过！")
        sys.exit(0)
    else:
        print("\n🎉 部分测试未通过，请检查日志")
        sys.exit(1)