# TOOLS.md — 钱多多本地环境笔记

## 核心技能

### 1. iTick 实时盯盘技能
- **位置**: `skills/itick_monitor/`
- **功能**: WebSocket 实时行情、价格提醒、买卖信号
- **文档**: `skills/itick_monitor/README.md`
- **集成指南**: `skills/itick_monitor/INTEGRATION.md`

**快速使用**:
```python
from skills.itick_monitor import MarketMonitor

monitor = MarketMonitor(["510300.SH", "159915.SZ"])
monitor.start()
monitor.on_signal(callback)  # 注册信号回调
```

### 2. my_quant_skills
- 量化分析技能，提供多因子选股、热点追踪、实时监控。调用方式见技能文档。

## 环境特有配置

| 配置项 | 位置/方式 | 用途 |
|--------|-----------|------|
| **Tushare token** | `~/.tushare/token` | Tushare 数据接口 |
| **iTick token** | 环境变量 `ITICK_TOKEN` | WebSocket 实时行情 |
| **信号中心回调** | `http://localhost:5000/signal` | 推送买卖信号 |

### 设置 iTick Token（永久）
```powershell
[System.Environment]::SetEnvironmentVariable("ITICK_TOKEN", "your_token", "User")
```

## 默认监控列表

### A 股 ETF
- `510300.SH` (沪深 300)
- `159915.SZ` (创业板)
- `512480.SH` (半导体)
- `518880.SH` (黄金)
- `515030.SH` (新能源车)

### 美股 ETF
- `SPY` (标普 500)
- `QQQ` (纳斯达克 100)

## 其他

- **日志位置**: `~/.openclaw/logs/`
- **技能热重载**: 技能更新后无需重启，自动生效
- **依赖安装**: `pip install -r skills/itick_monitor/requirements.txt`

---
*最后更新：2026-03-06*
