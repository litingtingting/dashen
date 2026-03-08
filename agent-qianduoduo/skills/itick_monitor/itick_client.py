# -*- coding: utf-8 -*-
"""
iTick WebSocket 客户端
用于获取 A 股/美股/港股实时行情
"""

import os
import json
import websocket
import threading
import time
from datetime import datetime
from typing import Dict, List, Callable, Optional, Any


class ItickClient:
    """iTick WebSocket 行情客户端"""
    
    def __init__(self, token: str = None):
        """
        初始化 iTick 客户端
        
        Args:
            token: iTick API token，如果为 None 则从环境变量 ITICK_TOKEN 读取
        """
        self.token = token or os.environ.get('ITICK_TOKEN')
        if not self.token:
            raise ValueError("iTick token 未提供，请设置 ITICK_TOKEN 环境变量")
        
        # 安全提示：不要在日志中输出完整 token
        self._token_masked = f"{self.token[:4]}...{self.token[-4:]}" if len(self.token) > 8 else "***"
        
        self.ws_url = "wss://api.itick.io/ws"  # iTick WebSocket 地址
        self.ws: Optional[websocket.WebSocketApp] = None
        self.is_connected = False
        self.subscribed_symbols: set = set()
        self.latest_data: Dict[str, Dict] = {}  # 最新行情数据
        self.callbacks: Dict[str, List[Callable]] = {}  # 价格回调函数
        
        # 心跳线程
        self.heartbeat_thread: Optional[threading.Thread] = None
        self.stop_heartbeat = False
        
    def connect(self, timeout: int = 10) -> bool:
        """
        连接 WebSocket 服务器
        
        Args:
            timeout: 连接超时时间（秒）
            
        Returns:
            bool: 连接是否成功
        """
        try:
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self._on_open,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close,
                header={
                    "Authorization": f"Bearer {self.token}",
                    "Content-Type": "application/json"
                }
            )
            
            # 启动 WebSocket 线程
            self.ws_thread = threading.Thread(target=self.ws.run_forever, daemon=True)
            self.ws_thread.start()
            
            # 等待连接
            start_time = time.time()
            while not self.is_connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if self.is_connected:
                print(f"[iTick] [OK] 连接成功")
                # 启动心跳
                self._start_heartbeat()
                return True
            else:
                print(f"[iTick] [FAIL] 连接超时")
                return False
                
        except Exception as e:
            print(f"[iTick] [FAIL] 连接失败：{e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.stop_heartbeat = True
        if self.ws:
            self.ws.close()
        self.is_connected = False
        print(f"[iTick] [DISCONNECT] 已断开连接")
    
    def _on_open(self, ws):
        """连接打开回调"""
        self.is_connected = True
        # 发送登录消息
        login_msg = {
            "action": "login",
            "token": self.token
        }
        ws.send(json.dumps(login_msg))
    
    def _on_message(self, ws, message):
        """收到消息回调"""
        try:
            data = json.loads(message)
            
            # 处理不同类型的消息
            msg_type = data.get("type", "")
            
            if msg_type == "heartbeat_ack":
                # 心跳响应
                pass
            elif msg_type == "quote":
                # 实时行情
                symbol = data.get("symbol", "")
                self.latest_data[symbol] = data
                # 触发回调
                if symbol in self.callbacks:
                    for callback in self.callbacks[symbol]:
                        callback(data)
            elif msg_type == "error":
                print(f"[iTick] 错误：{data.get('message', '')}")
                
        except Exception as e:
            print(f"[iTick] 消息处理错误：{e}")
    
    def _on_error(self, ws, error):
        """错误回调"""
        print(f"[iTick] WebSocket 错误：{error}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """连接关闭回调"""
        self.is_connected = False
        print(f"[iTick] 连接关闭：{close_status_code} - {close_msg}")
    
    def _start_heartbeat(self):
        """启动心跳线程"""
        def heartbeat_loop():
            while not self.stop_heartbeat and self.is_connected:
                try:
                    if self.ws and self.is_connected:
                        heartbeat_msg = {"action": "heartbeat"}
                        self.ws.send(json.dumps(heartbeat_msg))
                except:
                    pass
                time.sleep(30)  # 30 秒心跳
        
        self.heartbeat_thread = threading.Thread(target=heartbeat_loop, daemon=True)
        self.heartbeat_thread.start()
    
    def subscribe(self, symbols: List[str]) -> bool:
        """
        订阅行情
        
        Args:
            symbols: 标的列表，如 ["510300.SH", "159915.SZ", "SPY", "QQQ"]
            
        Returns:
            bool: 订阅是否成功
        """
        if not self.is_connected:
            print("[iTick] 未连接，无法订阅")
            return False
        
        try:
            sub_msg = {
                "action": "subscribe",
                "symbols": symbols
            }
            self.ws.send(json.dumps(sub_msg))
            self.subscribed_symbols.update(symbols)
            print(f"[iTick] [SUBSCRIBE] 已订阅：{', '.join(symbols)}")
            return True
        except Exception as e:
            print(f"[iTick] 订阅失败：{e}")
            return False
    
    def unsubscribe(self, symbols: List[str]) -> bool:
        """取消订阅"""
        if not self.is_connected:
            return False
        
        try:
            unsub_msg = {
                "action": "unsubscribe",
                "symbols": symbols
            }
            self.ws.send(json.dumps(unsub_msg))
            self.subscribed_symbols.difference_update(symbols)
            print(f"[iTick] [UNSUBSCRIBE] 已取消订阅：{', '.join(symbols)}")
            return True
        except Exception as e:
            print(f"[iTick] 取消订阅失败：{e}")
            return False
    
    def get_latest(self, symbol: str) -> Optional[Dict]:
        """获取最新行情数据"""
        return self.latest_data.get(symbol)
    
    def get_all_latest(self) -> Dict[str, Dict]:
        """获取所有订阅标的的最新行情"""
        return self.latest_data.copy()
    
    def on_price_update(self, symbol: str, callback: Callable[[Dict], None]):
        """
        注册价格更新回调
        
        Args:
            symbol: 标的代码
            callback: 回调函数，接收行情数据字典
        """
        if symbol not in self.callbacks:
            self.callbacks[symbol] = []
        self.callbacks[symbol].append(callback)
    
    def remove_callback(self, symbol: str, callback: Callable):
        """移除回调"""
        if symbol in self.callbacks:
            self.callbacks[symbol].remove(callback)


# 使用示例
if __name__ == "__main__":
    # 测试连接
    client = ItickClient()
    if client.connect():
        # 订阅 A 股 ETF
        client.subscribe(["510300.SH", "159915.SZ"])
        
        # 注册回调
        def on_update(data):
            print(f"📊 {data.get('symbol')}: {data.get('price')} ({data.get('change_pct', 0):+.2f}%)")
        
        client.on_price_update("510300.SH", on_update)
        client.on_price_update("159915.SZ", on_update)
        
        # 保持运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            client.disconnect()
