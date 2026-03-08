# -*- coding: utf-8 -*-
"""
iTick 实时盯盘技能
作者：钱多多 🤑
功能：通过 iTick WebSocket 接口获取实时行情，支持价格监控、信号提醒
"""

try:
    from .itick_client import ItickClient
    from .monitor import MarketMonitor
except ImportError:
    from itick_client import ItickClient
    from monitor import MarketMonitor

__all__ = ['ItickClient', 'MarketMonitor']
__version__ = '1.0.0'
