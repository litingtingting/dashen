# -*- coding: utf-8 -*-
"""
实时盯盘监控器
支持价格提醒、买卖信号、自动记录等功能
"""

import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any
from dataclasses import dataclass, asdict
try:
    from .itick_client import ItickClient
except ImportError:
    from itick_client import ItickClient


@dataclass
class PriceAlert:
    """价格提醒配置"""
    symbol: str
    condition: str  # "above", "below", "change_pct_above", "change_pct_below"
    threshold: float
    triggered: bool = False
    triggered_at: Optional[str] = None
    triggered_price: Optional[float] = None


@dataclass
class TradeSignal:
    """买卖信号"""
    symbol: str
    signal_type: str  # "buy", "sell", "watch"
    price: float
    reason: str
    timestamp: str
    confidence: str  # "high", "medium", "low"


class MarketMonitor:
    """市场行情监控器"""
    
    def __init__(self, watchlist: List[str] = None):
        """
        初始化监控器
        
        Args:
            watchlist: 监控列表，如 ["510300.SH", "159915.SZ", "SPY", "QQQ"]
        """
        self.watchlist = watchlist or [
            "510300.SH",  # 沪深 300
            "159915.SZ",  # 创业板
            "512480.SH",  # 半导体
            "518880.SH",  # 黄金
            "515030.SH",  # 新能源车
        ]
        
        # 初始化 iTick 客户端
        self.client = ItickClient()
        
        # 价格提醒列表
        self.alerts: List[PriceAlert] = []
        
        # 买卖信号记录
        self.signals: List[TradeSignal] = []
        
        # 信号回调函数
        self.signal_callbacks: List[Callable[[TradeSignal], None]] = []
        
        # 监控线程
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_monitor = False
        
        # 数据历史（用于简单分析）
        self.price_history: Dict[str, List[Dict]] = {s: [] for s in self.watchlist}
        self.max_history = 1000  # 每个标的最多保留 1000 条记录
        
    def start(self, auto_subscribe: bool = True) -> bool:
        """
        启动监控
        
        Args:
            auto_subscribe: 是否自动订阅监控列表
            
        Returns:
            bool: 启动是否成功
        """
        # 连接 iTick
        if not self.client.connect():
            print("[Monitor] [FAIL] iTick 连接失败")
            return False
        
        # 自动订阅
        if auto_subscribe:
            self.client.subscribe(self.watchlist)
        
        # 注册价格更新回调
        for symbol in self.watchlist:
            self.client.on_price_update(symbol, self._on_price_update)
        
        # 启动监控线程
        self.stop_monitor = False
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"[Monitor] [OK] 监控已启动，监控标的：{', '.join(self.watchlist)}")
        return True
    
    def stop(self):
        """停止监控"""
        self.stop_monitor = True
        self.client.disconnect()
        print("[Monitor] [STOP] 监控已停止")
    
    def _on_price_update(self, data: Dict):
        """价格更新回调"""
        symbol = data.get("symbol", "")
        
        # 保存历史数据
        if symbol in self.price_history:
            self.price_history[symbol].append({
                "timestamp": datetime.now().isoformat(),
                "price": data.get("price"),
                "change_pct": data.get("change_pct"),
                "volume": data.get("volume"),
            })
            # 限制历史数据长度
            if len(self.price_history[symbol]) > self.max_history:
                self.price_history[symbol] = self.price_history[symbol][-self.max_history:]
        
        # 检查价格提醒
        self._check_alerts(data)
        
        # 检查买卖信号（简单策略）
        self._check_signals(data)
    
    def _check_alerts(self, data: Dict):
        """检查价格提醒"""
        symbol = data.get("symbol", "")
        price = data.get("price", 0)
        change_pct = data.get("change_pct", 0)
        
        for alert in self.alerts:
            if alert.symbol != symbol or alert.triggered:
                continue
            
            triggered = False
            
            if alert.condition == "above" and price >= alert.threshold:
                triggered = True
            elif alert.condition == "below" and price <= alert.threshold:
                triggered = True
            elif alert.condition == "change_pct_above" and change_pct >= alert.threshold:
                triggered = True
            elif alert.condition == "change_pct_below" and change_pct <= alert.threshold:
                triggered = True
            
            if triggered:
                alert.triggered = True
                alert.triggered_at = datetime.now().isoformat()
                alert.triggered_price = price
                print(f"[ALERT] {symbol} 触发条件：{alert.condition} {alert.threshold}")
    
    def _check_signals(self, data: Dict):
        """
        检查买卖信号（简化版策略）
        实际使用中可扩展为多因子模型
        """
        symbol = data.get("symbol", "")
        price = data.get("price", 0)
        change_pct = data.get("change_pct", 0)
        
        # 简单策略示例
        signal = None
        
        # 大跌买入信号
        if change_pct <= -2.0:
            signal = TradeSignal(
                symbol=symbol,
                signal_type="buy",
                price=price,
                reason=f"跌幅达{change_pct:.2f}%，考虑逢低吸纳",
                timestamp=datetime.now().isoformat(),
                confidence="medium"
            )
        
        # 大涨卖出信号
        elif change_pct >= 3.0:
            signal = TradeSignal(
                symbol=symbol,
                signal_type="sell",
                price=price,
                reason=f"涨幅达{change_pct:.2f}%，考虑止盈",
                timestamp=datetime.now().isoformat(),
                confidence="medium"
            )
        
        if signal:
            self.signals.append(signal)
            print(f"[SIGNAL] {signal.symbol} | {signal.signal_type.upper()} | {signal.price} | {signal.reason}")
            
            # 触发回调
            for callback in self.signal_callbacks:
                callback(signal)
    
    def add_alert(self, symbol: str, condition: str, threshold: float):
        """
        添加价格提醒
        
        Args:
            symbol: 标的代码
            condition: 条件类型 ("above", "below", "change_pct_above", "change_pct_below")
            threshold: 阈值
        """
        alert = PriceAlert(
            symbol=symbol,
            condition=condition,
            threshold=threshold
        )
        self.alerts.append(alert)
        print(f"[Monitor] [ALERT] 添加提醒：{symbol} {condition} {threshold}")
    
    def remove_alert(self, symbol: str, condition: str):
        """移除提醒"""
        self.alerts = [
            a for a in self.alerts 
            if not (a.symbol == symbol and a.condition == condition)
        ]
    
    def on_signal(self, callback: Callable[[TradeSignal], None]):
        """注册信号回调"""
        self.signal_callbacks.append(callback)
    
    def get_signals(self, limit: int = 10) -> List[TradeSignal]:
        """获取最近的买卖信号"""
        return self.signals[-limit:]
    
    def get_latest_prices(self) -> Dict[str, Dict]:
        """获取最新价格"""
        return self.client.get_all_latest()
    
    def _monitor_loop(self):
        """监控主循环"""
        while not self.stop_monitor:
            try:
                # 每分钟输出一次监控状态
                prices = self.get_latest_prices()
                if prices:
                    print(f"[Monitor] {datetime.now().strftime('%H:%M:%S')} - "
                          f"监控中：{len(prices)} 个标的")
                time.sleep(60)
            except Exception as e:
                print(f"[Monitor] 监控循环错误：{e}")
                time.sleep(5)
    
    def export_signals(self, filepath: str):
        """导出信号记录到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump([asdict(s) for s in self.signals], f, ensure_ascii=False, indent=2)
        print(f"[Monitor] [SAVE] 信号已导出：{filepath}")


# 使用示例
if __name__ == "__main__":
    # 创建监控器
    monitor = MarketMonitor([
        "510300.SH",
        "159915.SZ",
        "512480.SH"
    ])
    
    # 注册信号回调
    def on_signal(signal):
        print(f"[SIGNAL CALLBACK] {signal.symbol} {signal.signal_type} @ {signal.price}")
    
    monitor.on_signal(on_signal)
    
    # 添加价格提醒
    monitor.add_alert("510300.SH", "below", 4.50)
    monitor.add_alert("510300.SH", "change_pct_below", -2.0)
    
    # 启动监控
    if monitor.start():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop()
            monitor.export_signals("signals.json")
