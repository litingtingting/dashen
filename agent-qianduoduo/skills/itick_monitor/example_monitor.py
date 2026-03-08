# -*- coding: utf-8 -*-
"""
钱多多实时盯盘示例脚本
用法：python example_monitor.py
"""

import sys
import os
import time
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from itick_monitor import MarketMonitor

print("=" * 70)
print("钱多多实时盯盘系统")
print("=" * 70)
print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 监控列表（可根据需要调整）
WATCHLIST = [
    "510300.SH",  # 沪深 300
    "159915.SZ",  # 创业板
    "512480.SH",  # 半导体
    "518880.SH",  # 黄金
    "515030.SH",  # 新能源车
]

print(f"监控标的：{', '.join(WATCHLIST)}")
print()

# 创建监控器
monitor = MarketMonitor(WATCHLIST)

# 信号回调 - 这里可以集成飞书通知
def on_signal(signal):
    print(f"\n{'='*70}")
    print("买卖信号")
    print(f"{'='*70}")
    print(f"标的：{signal.symbol}")
    direction = "买入" if signal.signal_type == 'buy' else "卖出"
    print(f"方向：[{direction}]")
    print(f"价格：{signal.price}")
    print(f"理由：{signal.reason}")
    print(f"置信度：{signal.confidence}")
    print(f"时间：{signal.timestamp}")
    print(f"{'='*70}")
    
    # TODO: 在这里添加飞书通知逻辑
    # send_feishu_notification(signal)

monitor.on_signal(on_signal)

# 添加价格提醒
print("设置价格提醒:")
monitor.add_alert("510300.SH", "change_pct_below", -1.5)
print("  - 沪深 300 跌超 1.5% 提醒")
monitor.add_alert("159915.SZ", "change_pct_below", -2.0)
print("  - 创业板 跌超 2% 提醒")
monitor.add_alert("512480.SH", "change_pct_above", 2.0)
print("  - 半导体 涨超 2% 提醒")
print()

# 启动监控
print("启动监控...")
if not monitor.start():
    print("启动失败，退出")
    sys.exit(1)

print()
print("监控运行中，按 Ctrl+C 停止")
print()

# 主循环 - 每分钟输出一次行情快照
try:
    while True:
        prices = monitor.get_latest_prices()
        if prices:
            print(f"\n{datetime.now().strftime('%H:%M:%S')} 行情快照:")
            print("-" * 70)
            for symbol, data in prices.items():
                price = data.get('price', 0)
                change = data.get('change_pct', 0)
                change_str = f"{change:+.2f}%" if change else "N/A"
                print(f"  {symbol:<12} {price:>8}  {change_str:>10}")
            print("-" * 70)
        
        time.sleep(60)  # 每分钟更新一次
        
except KeyboardInterrupt:
    print("\n\n停止监控...")
    monitor.stop()
    
    # 导出信号记录
    output_file = f"review/{datetime.now().strftime('%y%m%d')}/signals.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    monitor.export_signals(output_file)
    print(f"信号已导出：{output_file}")
    
    print("\n下次见！")
