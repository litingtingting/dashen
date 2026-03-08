# iTick 盯盘技能 - 钱多多工作流集成指南

## 在 AGENTS.md 任务中的使用

### 任务 1: 早盘盯盘 (9:10-15:00)

```python
from skills.itick_monitor import MarketMonitor

# 创建监控器（A 股 ETF）
monitor = MarketMonitor([
    "510300.SH",  # 沪深 300
    "159915.SZ",  # 创业板
    "512480.SH",  # 半导体
    "518880.SH",  # 黄金
    "515030.SH",  # 新能源车
])

# 注册飞书通知回调
def send_feishu_signal(signal):
    import requests
    webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/xxx"
    msg = {
        "msg_type": "text",
        "content": {
            "text": f"买卖信号：{signal.symbol} {signal.signal_type.upper()} @ {signal.price}\n理由：{signal.reason}"
        }
    }
    requests.post(webhook, json=msg)

monitor.on_signal(send_feishu_signal)

# 启动监控
monitor.start()
```

### 任务 2: 晚间美股盯盘 (21:30-次日 4:00)

```python
# 创建监控器（美股 ETF）
monitor = MarketMonitor(["SPY", "QQQ", "ARKK"])
monitor.start()
```

### 任务 3: 信号记录（复盘用）

```python
# 收盘后导出信号
monitor.export_signals(f"review/{date}/signals.json")
```

---

## 快速命令参考

### 启动盯盘
```bash
cd skills/itick_monitor
python example_monitor.py
```

### 测试连接
```bash
cd skills/itick_monitor
python test_itick.py
```

### 安装依赖
```bash
pip install -r requirements.txt
```

---

## 环境变量配置

### 临时设置（当前会话）
```powershell
$env:ITICK_TOKEN="your_token_here"
```

### 永久设置（用户级别）
```powershell
[System.Environment]::SetEnvironmentVariable("ITICK_TOKEN", "your_token_here", "User")
```

### 验证设置
```powershell
echo $env:ITICK_TOKEN
```

---

## API 快速参考

### ItickClient
```python
client = ItickClient()
client.connect()
client.subscribe(["510300.SH"])
data = client.get_latest("510300.SH")
client.disconnect()
```

### MarketMonitor
```python
monitor = MarketMonitor(["510300.SH"])
monitor.start()
monitor.add_alert("510300.SH", "below", 4.50)
monitor.on_signal(callback)
monitor.stop()
```

---

## 注意事项

1. **Token 安全**: 不要将 token 硬编码在代码中
2. **连接管理**: 用完记得 disconnect()
3. **异常处理**: 网络波动时可能需要重连
4. **日志记录**: 建议将信号导出到 review/ 目录用于复盘

---

*钱多多备注：这个技能是我的盯盘神器，解放双手，摸鱼更安心 😎*
