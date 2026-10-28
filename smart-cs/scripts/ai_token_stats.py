#!/usr/bin/env python3
"""
智能客服系统 - 百炼 AI Token 消耗统计

解析 smart-cs 日志中的结构化埋点行，统计指定日期的真实 AI 调用成本：
- AI 调用次数 / 成功率
- prompt / completion / total Token 消耗
- 平均 / 最大单次调用耗时
- 按模型分组的 Token 消耗

数据源（由 internal/ai/bailian.go 的 logUsage 输出）：
  [BAILIAN_USAGE] 2026-10-28T08:12:33.123 model=qwen-plus status=200 prompt_tokens=130 \
      completion_tokens=16 total_tokens=146 cached_tokens=0 latency_ms=812

用法:
  python3 ai_token_stats.py --log /home/ubuntu/smart-cs/logs/server-v2.log --date 2026-10-27
  python3 ai_token_stats.py --log ... --date 2026-10-27 --out data/stats/ai-token-stats-2026-10-27.json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

USAGE_RE = re.compile(
    r"^\[BAILIAN_USAGE\]\s+(?P<ts>\d{4}-\d{2}-\d{2}T[\d:.]+)\s+"
    r"model=(?P<model>\S+)\s+status=(?P<status>\d+)\s+"
    r"prompt_tokens=(?P<prompt>\d+)\s+completion_tokens=(?P<completion>\d+)\s+"
    r"total_tokens=(?P<total>\d+)\s+cached_tokens=(?P<cached>\d+)\s+"
    r"latency_ms=(?P<latency>\d+)"
)

# 阿里云百炼 qwen-plus 参考单价（元 / 千 Token，输入 / 输出）
# 仅用于粗略估算，实际账单以阿里云控制台为准
REFERENCE_PRICE_PER_1K = {
    "qwen-plus": {"prompt": 0.002, "completion": 0.006},
}


def collect(log_path: str, date_str: str) -> dict:
    if not os.path.exists(log_path):
        raise FileNotFoundError(f"日志文件不存在: {log_path}")

    calls = 0
    failed = 0
    prompt_tokens = 0
    completion_tokens = 0
    total_tokens = 0
    cached_tokens = 0
    latencies = []
    per_model = defaultdict(lambda: {"calls": 0, "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
    status_counts = Counter()
    parse_errors = 0

    with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if "[BAILIAN_USAGE]" not in line:
                continue
            m = USAGE_RE.match(line.strip())
            if not m:
                parse_errors += 1
                continue
            if not m.group("ts").startswith(date_str):
                continue

            calls += 1
            status = int(m.group("status"))
            status_counts[status] += 1
            if status != 200:
                failed += 1

            p = int(m.group("prompt"))
            c = int(m.group("completion"))
            t = int(m.group("total"))
            cached = int(m.group("cached"))
            prompt_tokens += p
            completion_tokens += c
            total_tokens += t
            cached_tokens += cached
            latencies.append(int(m.group("latency")))

            model = m.group("model")
            per_model[model]["calls"] += 1
            per_model[model]["prompt_tokens"] += p
            per_model[model]["completion_tokens"] += c
            per_model[model]["total_tokens"] += t

    latencies.sort()

    def pct(p: float) -> int:
        if not latencies:
            return 0
        k = int(len(latencies) * p)
        return latencies[min(k, len(latencies) - 1)]

    # 粗略成本估算（元）
    cost = 0.0
    for model, agg in per_model.items():
        price = REFERENCE_PRICE_PER_1K.get(model)
        if price:
            cost += agg["prompt_tokens"] / 1000 * price["prompt"]
            cost += agg["completion_tokens"] / 1000 * price["completion"]

    return {
        "date": date_str,
        "log_file": log_path,
        "ai_calls": calls,
        "ai_failed_calls": failed,
        "success_rate_pct": round((calls - failed) / calls * 100, 2) if calls else 0.0,
        "status_counts": dict(sorted(status_counts.items())),
        "tokens": {
            "prompt": prompt_tokens,
            "completion": completion_tokens,
            "total": total_tokens,
            "cached": cached_tokens,
        },
        "latency_ms": {
            "p50": pct(0.50),
            "p95": pct(0.95),
            "max": latencies[-1] if latencies else 0,
            "avg": round(sum(latencies) / len(latencies), 1) if latencies else 0.0,
        },
        "per_model": {k: dict(v) for k, v in sorted(per_model.items())},
        "estimated_cost_cny": round(cost, 6),
        "parse_errors": parse_errors,
    }


def render_text(s: dict) -> str:
    lines = [f"🤖 百炼 AI Token 统计 - {s['date']}", ""]
    lines.append(f"AI 调用次数    : {s['ai_calls']}  (失败 {s['ai_failed_calls']}，成功率 {s['success_rate_pct']}%)")
    t = s["tokens"]
    lines.append(f"Token 消耗     : 输入 {t['prompt']} / 输出 {t['completion']} / 合计 {t['total']} (缓存命中 {t['cached']})")
    lat = s["latency_ms"]
    lines.append(f"耗时(ms)       : p50={lat['p50']}  p95={lat['p95']}  max={lat['max']}  avg={lat['avg']}")
    lines.append(f"预估成本       : ¥{s['estimated_cost_cny']}  (参考单价，非账单)")
    if s["per_model"]:
        lines.append("")
        lines.append("分模型:")
        for model, agg in s["per_model"].items():
            lines.append(f"  {model}: {agg['calls']} 次, {agg['total_tokens']} tokens")
    else:
        lines.append("")
        lines.append("⚠️ 当日无 AI 调用埋点记录")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="smart-cs 百炼 AI Token 统计")
    ap.add_argument("--log", required=True, help="server-v2.log 路径")
    ap.add_argument("--date", default=datetime.now().strftime("%Y-%m-%d"), help="统计日期 YYYY-MM-DD")
    ap.add_argument("--out", help="输出 JSON 文件路径")
    ap.add_argument("--json", action="store_true", help="以 JSON 输出到 stdout")
    args = ap.parse_args()

    try:
        stats = collect(args.log, args.date)
    except FileNotFoundError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1

    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(stats, fh, ensure_ascii=False, indent=2)
        print(f"✅ 已写入 {args.out}")

    if args.json:
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    else:
        print(render_text(stats))
    return 0


if __name__ == "__main__":
    sys.exit(main())
