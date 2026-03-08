# -*- coding: utf-8 -*-
"""
iTick 技能测试脚本
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 60)
print("iTick 实时盯盘技能 - 测试")
print("=" * 60)

# 检查环境变量（显示哈希，用于验证）
import hashlib
token = os.environ.get('ITICK_TOKEN')
if token:
    # 计算哈希（用于验证，不可逆）
    token_hash = hashlib.sha256(token.encode()).hexdigest()[:8]
    print(f"[OK] ITICK_TOKEN 已配置 (SHA256: {token_hash}...)")
else:
    print(f"[FAIL] ITICK_TOKEN 未配置")
    print("   请设置环境变量：$env:ITICK_TOKEN=\"your_token\"")
    sys.exit(1)

# 测试导入
try:
    from itick_monitor import ItickClient, MarketMonitor
    print("[OK] 模块导入成功")
except ImportError as e:
    print(f"[FAIL] 模块导入失败：{e}")
    print("   请安装依赖：pip install websocket-client")
    sys.exit(1)

# 测试连接
print("\n[测试] 连接 iTick...")
client = ItickClient()

if client.connect(timeout=10):
    print("[OK] 连接成功")
    
    # 测试订阅
    print("\n[测试] 订阅行情...")
    if client.subscribe(["510300.SH", "159915.SZ"]):
        print("[OK] 订阅成功")
        
        # 等待几秒获取数据
        print("\n[测试] 等待行情数据...")
        import time
        time.sleep(3)
        
        # 获取最新数据
        print("\n[测试结果]")
        for symbol in ["510300.SH", "159915.SZ"]:
            data = client.get_latest(symbol)
            if data:
                print(f"  {symbol}: {data.get('price')} ({data.get('change_pct', 0):+.2f}%)")
            else:
                print(f"  {symbol}: 暂无数据")
        
        client.disconnect()
        print("\n[OK] 测试完成")
    else:
        print("[FAIL] 订阅失败")
        client.disconnect()
else:
    print("[FAIL] 连接失败")
    print("   可能原因:")
    print("   1. 网络问题")
    print("   2. Token 无效")
    print("   3. iTick 服务不可用")

print("\n" + "=" * 60)
