#!/usr/bin/env python3
"""
智能客服系统 - API 调用统计脚本

解析 smart-cs 的 Gin 访问日志（server-v2.log），输出指定日期的 API 调用指标：
- 请求总量、按状态码分布（2xx/4xx/5xx）
- 业务 API 请求量（过滤 404 扫描噪音）
- 延迟统计（p50 / p95 / max）
- 独立来源 IP 数
- 扫描型请求 Top 路径

用法:
  python3 api_stats.py --log /home/ubuntu/smart-cs/logs/server-v2.log --date 2026-10-24
  python3 api_stats.py --log ... --date 2026-10-24 --json   # 输出 JSON
  python3 api_stats.py --log ... --date 2026-10-24 --out /tmp/api-stats.json
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime

# [GIN] 2026/10/24 - 16:19:04 | 404 |         932ns |    137.23.38.53 | GET      "/api-docs"
LINE_RE = re.compile(
    r"^\[GIN\]\s+(?P<date>\d{4}/\d{2}/\d{2})\s+-\s+(?P<time>\d{2}:\d{2}:\d{2})\s+"
    r"\|\s+(?P<status>\d{3})\s+\|\s+(?P<latency>[\d.]+)(?P<unit>ns|µs|ms|s)\s+\|"
    r"\s+(?P<ip>[\d.]+)\s+\|\s+(?P<method>[A-Z]+)\s+\"(?P<path>[^\"]*)\""
)

UNIT_NS = {"ns": 1.0, "µs": 1_000.0, "ms": 1_000_000.0, "s": 1_000_000_000.0}

# 本地健康检查，不计入业务统计
HEALTH_PATHS = {"/health", "/healthz", "/ready"}


def parse_latency(value: str, unit: str) -> float:
    return float(value) * UNIT_NS.get(unit, 1.0)


def percentile(sorted_vals: list[float], pct: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    k = (len(sorted_vals) - 1) * pct
    lo = int(k)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = k - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[hi] * frac


def collect(log_path: str, date_str: str) -> dict:
    """date_str 形如 2026-10-24，转成日志里的 2026/10/24"""
    log_date = date_str.replace("-", "/")

    status_counts = Counter()
    path_counts = Counter()
    method_counts = Counter()
    ips = set()
    business_paths = Counter()
    business_latencies = []
    scan_latencies = []
    latencies = []
    total = 0
    business_total = 0
    errors_5xx = []
    parse_errors = 0

    if not os.path.exists(log_path):
        raise FileNotFoundError(f"日志文件不存在: {log_path}")

    with open(log_path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if log_date not in line:
                continue
            m = LINE_RE.match(line)
            if not m:
                if "[" in line and "GIN" in line:
                    parse_errors += 1
                continue

            total += 1
            status = int(m.group("status"))
            path = m.group("path")
            method = m.group("method")
            ip = m.group("ip")
            lat = parse_latency(m.group("latency"), m.group("unit"))

            status_counts[status] += 1
            path_counts[path] += 1
            method_counts[method] += 1
            ips.add(ip)
            latencies.append(lat)

            # 业务请求：非 404、非本地健康检查、非常见扫描探测
            is_scan = status == 404 or path in HEALTH_PATHS or ip == "127.0.0.1"
            if not is_scan:
                business_total += 1
                business_paths[f"{method} {path}"] += 1
                business_latencies.append(lat)
            else:
                scan_latencies.append(lat)

            if 500 <= status <= 599:
                errors_5xx.append(
                    {
                        "time": m.group("time"),
                        "status": status,
                        "ip": ip,
                        "method": method,
                        "path": path,
                    }
                )

    latencies.sort()
    business_latencies.sort()

    def ms(vals: list[float]) -> float:
        return round(vals[-1] / 1_000_000, 2) if vals else 0.0

    return {
        "date": date_str,
        "log_file": log_path,
        "total_requests": total,
        "status_counts": dict(sorted(status_counts.items())),
        "status_class": {
            "2xx": sum(v for k, v in status_counts.items() if 200 <= k < 300),
            "3xx": sum(v for k, v in status_counts.items() if 300 <= k < 400),
            "4xx": sum(v for k, v in status_counts.items() if 400 <= k < 500),
            "5xx": sum(v for k, v in status_counts.items() if 500 <= k < 600),
        },
        "business_requests": business_total,
        "noise_requests": total - business_total,
        "unique_ips": len(ips),
        "methods": dict(method_counts),
        "latency_ms": {
            "p50": ms([percentile(latencies, 0.50)]) if latencies else 0.0,
            "p95": ms([percentile(latencies, 0.95)]) if latencies else 0.0,
            "max": ms(latencies),
            "avg": round(sum(latencies) / len(latencies) / 1_000_000, 2) if latencies else 0.0,
        },
        "business_latency_ms": {
            "p50": ms([percentile(business_latencies, 0.50)]) if business_latencies else 0.0,
            "p95": ms([percentile(business_latencies, 0.95)]) if business_latencies else 0.0,
        },
        "top_paths": [{"path": p, "count": c} for p, c in path_counts.most_common(10)],
        "top_business_paths": [
            {"path": p, "count": c} for p, c in business_paths.most_common(10)
        ],
        "errors_5xx": errors_5xx,
        "parse_errors": parse_errors,
    }


def render_text(s: dict) -> str:
    lines = []
    lines.append(f"📊 API 调用统计 - {s['date']}")
    lines.append(f"日志文件: {s['log_file']}")
    lines.append("")
    lines.append(f"总请求数        : {s['total_requests']}")
    sc = s["status_class"]
    lines.append(
        f"状态分布        : 2xx={sc['2xx']}  3xx={sc['3xx']}  4xx={sc['4xx']}  5xx={sc['5xx']}"
    )
    lines.append(f"业务请求数      : {s['business_requests']}   (噪音/健康检查: {s['noise_requests']})")
    lines.append(f"独立来源 IP     : {s['unique_ips']}")
    lat = s["latency_ms"]
    lines.append(
        f"延迟(ms)        : p50={lat['p50']}  p95={lat['p95']}  max={lat['max']}  avg={lat['avg']}"
    )
    if s["top_business_paths"]:
        lines.append("")
        lines.append("业务接口 Top:")
        for item in s["top_business_paths"]:
            lines.append(f"  {item['count']:>6}  {item['path']}")
    else:
        lines.append("")
        lines.append("⚠️ 今日无真实业务接口调用（全部为 404 扫描或本地健康检查）")
    if s["errors_5xx"]:
        lines.append("")
        lines.append(f"❌ 5xx 错误 {len(s['errors_5xx'])} 条:")
        for e in s["errors_5xx"][:10]:
            lines.append(f"  {e['time']} {e['status']} {e['ip']} {e['method']} {e['path']}")
    else:
        lines.append("")
        lines.append("✅ 5xx 错误: 0 条")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="smart-cs API 调用统计")
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
