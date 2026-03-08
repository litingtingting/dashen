# -*- coding: utf-8 -*-
"""
美股大盘盯盘脚本
监控：纳指、标普 500、费城半导体
用途：为国内 ETF 推荐提供依据
"""

import sys
import os
import time
import json
import hashlib
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from itick_monitor import MarketMonitor

print("=" * 70)
print("美股大盘盯盘系统")
print("=" * 70)
print(f"启动时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"目标：纳指、标普 500、费城半导体 → 推荐国内 ETF")
print()

# 监控标的（美股指数对应国内 ETF）
WATCHLIST = {
    # 美股指数（用于判断趋势）
    "NQ=F": "纳斯达克 100 期货",
    "ES=F": "标普 500 期货",
    "SOX": "费城半导体指数",
    
    # 国内可买 ETF（实际可交易）
    "159941.SZ": "纳指 ETF",
    "513500.SH": "标普 500ETF",
    "512480.SH": "半导体 ETF",
    "513550.SH": "恒生科技 ETF",
}

print("监控标的:")
for code, name in WATCHLIST.items():
    print(f"  {code}: {name}")
print()

# 创建监控器
monitor = MarketMonitor(list(WATCHLIST.keys()))

# 信号记录
SIGNALS_FILE = f"review/{datetime.now().strftime('%y%m%d')}/us_market_signals.json"
os.makedirs(os.path.dirname(SIGNALS_FILE), exist_ok=True)

# 信号回调
def on_signal(signal):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"\n{'='*70}")
    print(f"[{timestamp}] 买卖信号")
    print(f"{'='*70}")
    print(f"标的：{signal.symbol} ({WATCHLIST.get(signal.symbol, 'Unknown')})")
    direction = "买入" if signal.signal_type == 'buy' else "卖出"
    print(f"方向：[{direction}]")
    print(f"价格：{signal.price}")
    print(f"理由：{signal.reason}")
    print(f"置信度：{signal.confidence}")
    print(f"{'='*70}")
    
    # 记录信号
    record_signal(signal)

def record_signal(signal):
    """记录信号到文件"""
    signals = []
    if os.path.exists(SIGNALS_FILE):
        with open(SIGNALS_FILE, 'r', encoding='utf-8') as f:
            signals = json.load(f)
    
    signals.append({
        "timestamp": datetime.now().isoformat(),
        "symbol": signal.symbol,
        "name": WATCHLIST.get(signal.symbol, "Unknown"),
        "signal_type": signal.signal_type,
        "price": signal.price,
        "reason": signal.reason,
        "confidence": signal.confidence
    })
    
    with open(SIGNALS_FILE, 'w', encoding='utf-8') as f:
        json.dump(signals, f, ensure_ascii=False, indent=2)
    
    print(f"[记录] 信号已保存：{SIGNALS_FILE}")

monitor.on_signal(on_signal)

# 添加价格提醒（涨跌超 2% 提醒）
print("设置价格提醒:")
for code in ["NQ=F", "ES=F", "SOX"]:
    monitor.add_alert(code, "change_pct_above", 2.0)
    monitor.add_alert(code, "change_pct_below", -2.0)
    print(f"  {code}: 涨跌超 2% 提醒")
print()

# 启动监控
print("启动监控...")
if not monitor.start():
    print("启动失败，退出")
    sys.exit(1)

print()
print("监控运行中，按 Ctrl+C 停止")
print()

# 主循环 - 每 5 分钟输出一次行情快照
try:
    last_report_time = None
    
    while True:
        prices = monitor.get_latest_prices()
        now = datetime.now()
        
        if prices:
            # 每 5 分钟输出快照
            if last_report_time is None or (now - last_report_time).seconds >= 300:
                print(f"\n{'='*70}")
                print(f"{now.strftime('%H:%M:%S')} 大盘快照")
                print(f"{'='*70}")
                
                # 美股指数
                print("\n【美股指数】")
                for code in ["NQ=F", "ES=F", "SOX"]:
                    if code in prices:
                        data = prices[code]
                        price = data.get('price', 0)
                        change = data.get('change_pct', 0)
                        change_str = f"{change:+.2f}%" if change else "N/A"
                        trend = "🟢" if change > 0.5 else ("🔴" if change < -0.5 else "🟡")
                        print(f"  {trend} {code:<8} {price:>10.2f}  {change_str:>10}")
                
                # 国内 ETF
                print("\n【国内 ETF】")
                for code in ["159941.SZ", "513500.SH", "512480.SH", "513550.SH"]:
                    if code in prices:
                        data = prices[code]
                        price = data.get('price', 0)
                        change = data.get('change_pct', 0)
                        change_str = f"{change:+.2f}%" if change else "N/A"
                        trend = "🟢" if change > 0.5 else ("🔴" if change < -0.5 else "🟡")
                        print(f"  {trend} {code:<10} {price:>8.3f}  {change_str:>10}")
                
                print(f"{'='*70}")
                last_report_time = now
        
        time.sleep(30)  # 每 30 秒检查一次
        
except KeyboardInterrupt:
    print("\n\n停止监控...")
    monitor.stop()
    monitor.export_signals(SIGNALS_FILE)
    print(f"信号已导出：{SIGNALS_FILE}")
    
    # 生成简易复盘
    print("\n生成复盘报告...")
    generate_report()
    
    print("\n下次见！")

def generate_report():
    """生成简易复盘报告"""
    report_file = f"review/{datetime.now().strftime('%y%m%d')}/us_market_review.md"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# 美股大盘复盘 - {datetime.now().strftime('%Y-%m-%d')}\n\n")
        f.write(f"生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## 监控标的\n\n")
        for code, name in WATCHLIST.items():
            f.write(f"- {code}: {name}\n")
        f.write("\n## 信号记录\n\n")
        f.write(f"详见：{SIGNALS_FILE}\n")
        f.write("\n---\n*钱多多自动生成*\n")
    
    print(f"复盘报告：{report_file}")
