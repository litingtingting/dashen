# iTick 实时盯盘技能

**作者**: 钱多多 🤑  
**版本**: 1.0.0  
**用途**: 通过 iTick WebSocket 接口获取实时行情，支持价格监控、买卖信号提醒

---

## 📦 依赖安装

```bash
pip install websocket-client
```

---

## 🔑 配置

iTick token 存储在环境变量 `ITICK_TOKEN` 中：

### Windows (PowerShell)
```powershell
$env:ITICK_TOKEN="your_token_here"
```

### Windows (永久设置)
```powershell
[System.Environment]::SetEnvironmentVariable("ITICK_TOKEN", "your_token_here", "User")
```

### Linux/Mac
```bash
export ITICK_TOKEN="your_token_here"
```

---

## 🚀 快速使用

### 基础用法 - 获取实时行情

```python
from skills.itick_monitor import ItickClient

# 创建客户端（自动读取 ITICK_TOKEN 环境变量）
client = ItickClient()

# 连接
if client.connect():
    # 订阅标的
    client.subscribe(["510300.SH", "159915.SZ", "512480.SH"])
    
    # 获取最新行情
    data = client.get_latest("510300.SH")
    print(f"沪深 300: {data['price']} ({data['change_pct']:+.2f}%)")
    
    # 保持连接
    import time
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        client.disconnect()
```

### 进阶用法 - 价格提醒 + 买卖信号

```python
from skills.itick_monitor import MarketMonitor

# 创建监控器
monitor = MarketMonitor([
    "510300.SH",  # 沪深 300
    "159915.SZ",  # 创业板
    "512480.SH",  # 半导体
])

# 注册信号回调（飞书通知等）
def on_signal(signal):
    print(f"🚨 {signal.symbol} {signal.signal_type.upper()} @ {signal.price}")
    print(f"   理由：{signal.reason}")
    print(f"   置信度：{signal.confidence}")

monitor.on_signal(on_signal)

# 添加价格提醒
monitor.add_alert("510300.SH", "below", 4.50)        # 跌破 4.50 提醒
monitor.add_alert("510300.SH", "change_pct_below", -2.0)  # 跌超 2% 提醒

# 启动监控
monitor.start()

# 保持运行
import time
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    monitor.stop()
    monitor.export_signals("review/today/signals.json")
```

---

## 📊 API 参考

### ItickClient

| 方法 | 说明 |
|------|------|
| `connect(timeout=10)` | 连接 WebSocket 服务器 |
| `disconnect()` | 断开连接 |
| `subscribe(symbols)` | 订阅行情，symbols 为列表 |
| `unsubscribe(symbols)` | 取消订阅 |
| `get_latest(symbol)` | 获取单个标的最新行情 |
| `get_all_latest()` | 获取所有订阅标的的最新行情 |
| `on_price_update(symbol, callback)` | 注册价格更新回调 |

### MarketMonitor

| 方法 | 说明 |
|------|------|
| `start(auto_subscribe=True)` | 启动监控 |
| `stop()` | 停止监控 |
| `add_alert(symbol, condition, threshold)` | 添加价格提醒 |
| `remove_alert(symbol, condition)` | 移除提醒 |
| `on_signal(callback)` | 注册买卖信号回调 |
| `get_signals(limit=10)` | 获取最近的买卖信号 |
| `get_latest_prices()` | 获取最新价格 |
| `export_signals(filepath)` | 导出信号记录 |

---

## 🎯 价格提醒条件

| condition | 说明 | threshold 单位 |
|-----------|------|----------------|
| `above` | 价格突破上方 | 价格 |
| `below` | 价格跌破下方 | 价格 |
| `change_pct_above` | 涨幅超过 | 百分比 (如 2.0 表示 2%) |
| `change_pct_below` | 跌幅超过 | 百分比 (如 -2.0 表示 -2%) |

---

## 📝 买卖信号策略（内置简化版）

当前内置简单策略：
- **买入信号**: 跌幅 ≥ 2%，提示"逢低吸纳"
- **卖出信号**: 涨幅 ≥ 3%，提示"考虑止盈"

**可扩展**: 在 `monitor.py` 的 `_check_signals` 方法中添加多因子模型逻辑。

---

## 💡 钱多多使用场景

### 1. 早盘盯盘 (9:30-11:30)
```python
# 监控核心 ETF，设置跌幅提醒
monitor.add_alert("510300.SH", "change_pct_below", -1.5)
monitor.add_alert("159915.SZ", "change_pct_below", -2.0)
```

### 2. 晚间美股盯盘 (21:30-次日 4:00)
```python
# 监控美股 ETF
monitor.watchlist = ["SPY", "QQQ", "ARKK"]
monitor.start()
```

### 3. 信号自动记录
```python
# 每天收盘后导出信号
monitor.export_signals(f"review/{date}/signals.json")
```

---

## ⚠️ 注意事项

1. **Token 安全**: 不要将 token 硬编码在代码中，使用环境变量
2. **连接管理**: 用完记得 `disconnect()`，避免资源泄漏
3. **异常处理**: 网络波动时自动重连逻辑需自行扩展
4. **频率限制**: 遵守 iTick API 调用频率限制

---

## 🤝 与飞书集成示例

```python
import requests

def send_feishu_alert(signal):
    """发送飞书消息"""
    webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    
    content = {
        "msg_type": "text",
        "content": {
            "text": f"🚨 买卖信号提醒\n"
                    f"标的：{signal.symbol}\n"
                    f"方向：{signal.signal_type.upper()}\n"
                    f"价格：{signal.price}\n"
                    f"理由：{signal.reason}"
        }
    }
    
    requests.post(webhook_url, json=content)

monitor.on_signal(send_feishu_alert)
```

---

*钱多多备注：有了这个技能，盯盘再也不用手动刷新了，摸鱼时间 +1 😎*
