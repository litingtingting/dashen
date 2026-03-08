# iTick 实时盯盘技能

**用途**: 实时行情监控、价格提醒、买卖信号生成  
**依赖**: `websocket-client`  
**Token**: 环境变量 `ITICK_TOKEN`

---

## 快速调用

### 1. 获取实时行情
```python
from skills.itick_monitor import ItickClient

client = ItickClient()  # 自动读取 ITICK_TOKEN
client.connect()
client.subscribe(["510300.SH", "159915.SZ"])
data = client.get_latest("510300.SH")
```

### 2. 启动盯盘监控
```python
from skills.itick_monitor import MarketMonitor

monitor = MarketMonitor(["510300.SH", "159915.SZ", "512480.SH"])
monitor.start()
```

### 3. 设置价格提醒
```python
monitor.add_alert("510300.SH", "below", 4.50)  # 跌破 4.50 提醒
monitor.add_alert("510300.SH", "change_pct_below", -2.0)  # 跌超 2% 提醒
```

### 4. 注册买卖信号回调
```python
def on_signal(signal):
    print(f"{signal.symbol} {signal.signal_type} @ {signal.price}")
    # 可集成飞书通知

monitor.on_signal(on_signal)
```

---

## 文件结构
```
skills/itick_monitor/
├── __init__.py          # 模块入口
├── itick_client.py      # WebSocket 客户端
├── monitor.py           # 监控器（提醒 + 信号）
├── README.md            # 详细文档
├── SKILL.md             # 技能说明（本文件）
├── test_itick.py        # 测试脚本
├── example_monitor.py   # 使用示例
└── requirements.txt     # 依赖
```

---

## 依赖安装
```bash
pip install -r skills/itick_monitor/requirements.txt
```

---

## 测试
```bash
cd skills/itick_monitor
python test_itick.py
```

---

## 运行盯盘示例
```bash
cd skills/itick_monitor
python example_monitor.py
```

---

## 与 AGENTS.md 集成

在钱多多的日常任务中：

### 早盘盯盘 (9:30-11:30)
```python
from skills.itick_monitor import MarketMonitor

monitor = MarketMonitor(["510300.SH", "159915.SZ", "512480.SH"])
monitor.start()
# 自动记录买卖信号
```

### 晚间美股盯盘 (21:30-次日 4:00)
```python
monitor = MarketMonitor(["SPY", "QQQ", "ARKK"])
monitor.start()
```

### 信号导出（复盘用）
```python
monitor.export_signals(f"review/{date}/signals.json")
```

---

*钱多多备注：有了这个技能，盯盘再也不用手动刷新了，摸鱼时间 +1 😎*
