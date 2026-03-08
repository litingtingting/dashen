# -*- coding: utf-8 -*-
"""
飞书通知模块
用于发送买卖信号、价格提醒等通知
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional


class FeishuNotifier:
    """飞书通知器"""
    
    def __init__(self, webhook: str = None):
        """
        初始化飞书通知器
        
        Args:
            webhook: 飞书 webhook URL，如果为 None 则从环境变量 FEISHU_WEBHOOK 读取
        """
        self.webhook = webhook or os.environ.get('FEISHU_WEBHOOK')
        
        if not self.webhook:
            print("[Feishu] 警告：FEISHU_WEBHOOK 未配置，通知功能不可用")
            print("        请在飞书群添加机器人获取 webhook URL")
            print("        或设置环境变量：$env:FEISHU_WEBHOOK=\"https://...\"")
        
        self.is_configured = bool(self.webhook)
    
    def send_text(self, text: str, mention_all: bool = False) -> bool:
        """
        发送文本消息
        
        Args:
            text: 消息内容
            mention_all: 是否@所有人
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_configured:
            return False
        
        try:
            content = {
                "msg_type": "text",
                "content": {
                    "text": text
                }
            }
            
            if mention_all:
                content["content"]["text"] = f"<at user_id=\"all\">所有人</at>\n{text}"
            
            response = requests.post(
                self.webhook,
                json=content,
                timeout=10,
                proxies={}  # 不使用代理
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get('StatusCode') == 0 or result.get('code') == 0:
                    print(f"[Feishu] ✅ 消息发送成功")
                    return True
                else:
                    print(f"[Feishu] ❌ 发送失败：{result}")
                    return False
            else:
                print(f"[Feishu] ❌ HTTP 错误：{response.status_code}")
                return False
                
        except Exception as e:
            print(f"[Feishu] ❌ 异常：{e}")
            return False
    
    def send_signal(self, signal: Dict) -> bool:
        """
        发送买卖信号通知
        
        Args:
            signal: 信号字典，包含 symbol, signal_type, price, reason 等
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_configured:
            return False
        
        # 格式化信号消息
        direction = "🟢 买入" if signal.get('signal_type') == 'buy' else "🔴 卖出"
        timestamp = signal.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        text = f"""【买卖信号提醒】

标的：{signal.get('symbol', 'N/A')}
方向：{direction}
价格：{signal.get('price', 0)}
理由：{signal.get('reason', 'N/A')}
置信度：{signal.get('confidence', 'N/A')}
时间：{timestamp}

---
钱多多自动盯盘系统"""

        return self.send_text(text)
    
    def send_alert(self, symbol: str, price: float, change_pct: float, condition: str) -> bool:
        """
        发送价格提醒通知
        
        Args:
            symbol: 标的代码
            price: 当前价格
            change_pct: 涨跌幅
            condition: 触发条件
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_configured:
            return False
        
        change_str = f"{change_pct:+.2f}%"
        trend = "🟢" if change_pct > 0 else "🔴"
        
        text = f"""【价格提醒】

{trend} {symbol}
价格：{price}
涨跌：{change_str}
触发：{condition}

---
钱多多自动盯盘系统"""

        return self.send_text(text)
    
    def send_daily_report(self, report: Dict) -> bool:
        """
        发送日报通知
        
        Args:
            report: 日报字典，包含市场 summary、推荐 ETF 等
            
        Returns:
            bool: 发送是否成功
        """
        if not self.is_configured:
            return False
        
        text = f"""【钱多多日报】

日期：{report.get('date', 'N/A')}

【市场 summary】
{report.get('summary', 'N/A')}

【推荐 ETF】
{report.get('recommendations', 'N/A')}

【风险提示】
{report.get('risks', 'N/A')}

---
详细报告请查看 workspace

钱多多自动盯盘系统"""

        return self.send_text(text)
    
    def test_connection(self) -> bool:
        """
        测试 webhook 连接
        
        Returns:
            bool: 连接是否成功
        """
        if not self.is_configured:
            print("[Feishu] ❌ Webhook 未配置")
            return False
        
        print("[Feishu] 测试连接...")
        return self.send_text("钱多多飞书通知测试 - 如果您看到这条消息，说明配置成功！✅")


# 使用示例
if __name__ == "__main__":
    print("=" * 60)
    print("飞书通知模块 - 测试")
    print("=" * 60)
    
    # 创建通知器
    notifier = FeishuNotifier()
    
    # 测试连接
    if notifier.test_connection():
        print("\n✅ 飞书通知配置成功！")
        
        # 测试买卖信号
        test_signal = {
            "symbol": "159941.SZ",
            "signal_type": "buy",
            "price": 1.234,
            "reason": "纳指回调超 2%，逢低吸纳",
            "confidence": "medium",
            "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print("\n发送测试信号...")
        notifier.send_signal(test_signal)
    else:
        print("\n❌ 飞书通知未配置")
        print("\n配置步骤:")
        print("1. 在飞书群添加自定义机器人")
        print("2. 复制 webhook URL")
        print("3. 设置环境变量：$env:FEISHU_WEBHOOK=\"https://...\"")
        print("4. 重新运行此脚本测试")
    
    print("\n" + "=" * 60)
