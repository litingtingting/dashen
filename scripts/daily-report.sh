#!/bin/bash
# 智能客服系统 - 每日汇报生成脚本
# 自动汇总：API 调用统计 + AI Token 成本 + 服务器健康 → 生成日报 Markdown
#
# 用法：
#   ./scripts/daily-report.sh [YYYY-MM-DD]   # 默认统计前一天
#   ./scripts/daily-report.sh 2026-10-30      # 指定统计日期
#
# 数据来源：
#   smart-cs/data/stats/api-stats-YYYY-MM-DD.json       (api_stats.py 产出)
#   smart-cs/data/stats/ai-token-stats-YYYY-MM-DD.json (ai_token_stats.py 产出)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
STATS_DIR="${STATS_DIR:-$PROJECT_DIR/smart-cs/data/stats}"

STAT_DATE="${1:-$(date -d 'yesterday' +%Y-%m-%d)}"
REPORT_FILE="$PROJECT_DIR/reports/$(date +%y%m%d).md"

API_STATS="$STATS_DIR/api-stats-$STAT_DATE.json"
AI_STATS="$STATS_DIR/ai-token-stats-$STAT_DATE.json"

mkdir -p "$PROJECT_DIR/reports"

# ---------- 通用 JSON 取值（避免依赖 jq）----------
json_get() {
  # $1=file  $2=python 表达式（以 d 引用已解析的 dict）
  python3 - "$1" "$2" <<'PY' 2>/dev/null || echo "N/A"
import json, sys
try:
    with open(sys.argv[1], encoding="utf-8") as f:
        d = json.load(f)
    v = eval(sys.argv[2], {"d": d, "sum": sum, "len": len, "round": round})
    print(v)
except Exception:
    print("N/A")
PY
}

# ---------- 服务器健康 ----------
# SERVER_SSH 走远程；RUN_LOCAL=1 直接在本机采集（脚本跑在服务器上时用）
collect_health() {
  echo "UPTIME=$(uptime -p | sed "s/^up //")"
  echo "LOAD=$(cut -d" " -f1-3 /proc/loadavg)"
  echo "CPU=$(top -bn1 | grep "%Cpu(s)" | awk "{print 100-\$8}" | cut -d. -f1)%"
  echo "MEM_USED=$(free -m | awk "/^Mem:/{print \$3}")"
  echo "MEM_TOTAL=$(free -m | awk "/^Mem:/{print \$2}")"
  echo "MEM_AVAIL=$(free -m | awk "/^Mem:/{print \$7}")"
  echo "DISK_USED=$(df -h / | awk "NR==2{print \$3}")"
  echo "DISK_TOTAL=$(df -h / | awk "NR==2{print \$2}")"
  echo "DISK_PCT=$(df -h / | awk "NR==2{print \$5}")"
  echo "F2B_BAN=$(sudo -n fail2ban-client status sshd 2>/dev/null | awk "/Total banned/{print \$4}")"
}

if [ "${RUN_LOCAL:-0}" = "1" ]; then
  HEALTH_RAW="$(collect_health 2>/dev/null || true)"
elif [ -n "${SERVER_SSH:-}" ]; then
  SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no -o BatchMode=yes"
  [ -n "${SSH_KEY:-}" ] && SSH_OPTS="$SSH_OPTS -i $SSH_KEY"
  # shellcheck disable=SC2086
  HEALTH_RAW="$(ssh $SSH_OPTS "$SERVER_SSH" "$(declare -f collect_health); collect_health" 2>/dev/null || true)"
else
  HEALTH_RAW=""
fi

get_health() {
  local v
  v="$(printf '%s\n' "$HEALTH_RAW" | grep "^$1=" | cut -d= -f2- | head -1 || true)"
  echo "${v:-N/A}"
}

UPTIME="$(get_health UPTIME)";      UPTIME="${UPTIME:-N/A}"
LOAD="$(get_health LOAD)";          LOAD="${LOAD:-N/A}"
CPU="$(get_health CPU)";            CPU="${CPU:-N/A}"
MEM_USED="$(get_health MEM_USED)";  MEM_USED="${MEM_USED:-N/A}"
MEM_TOTAL="$(get_health MEM_TOTAL)";MEM_TOTAL="${MEM_TOTAL:-N/A}"
MEM_AVAIL="$(get_health MEM_AVAIL)";MEM_AVAIL="${MEM_AVAIL:-N/A}"
DISK_USED="$(get_health DISK_USED)";DISK_USED="${DISK_USED:-N/A}"
DISK_TOTAL="$(get_health DISK_TOTAL)";DISK_TOTAL="${DISK_TOTAL:-N/A}"
DISK_PCT="$(get_health DISK_PCT)";  DISK_PCT="${DISK_PCT:-N/A}"
F2B_BAN="$(get_health F2B_BAN)";    F2B_BAN="${F2B_BAN:-N/A}"

# ---------- API 统计 ----------
API_TOTAL="$(json_get "$API_STATS" "d.get('total_requests', 'N/A')")"
API_2XX="$(json_get "$API_STATS" "d.get('status_class', {}).get('2xx', 'N/A')")"
API_4XX="$(json_get "$API_STATS" "d.get('status_class', {}).get('4xx', 'N/A')")"
API_5XX="$(json_get "$API_STATS" "d.get('status_class', {}).get('5xx', 'N/A')")"
API_BIZ="$(json_get "$API_STATS" "d.get('business_requests', 'N/A')")"
API_NOISE="$(json_get "$API_STATS" "d.get('noise_requests', 'N/A')")"
API_IPS="$(json_get "$API_STATS" "d.get('unique_ips', 'N/A')")"
API_P95="$(json_get "$API_STATS" "round(d.get('latency_ms', {}).get('p95', 0), 2)")"
API_MAX="$(json_get "$API_STATS" "round(d.get('latency_ms', {}).get('max', 0), 2)")"
API_PARSE_ERR="$(json_get "$API_STATS" "d.get('parse_errors', 'N/A')")"

# ---------- AI Token 统计（成本看板）----------
AI_CALLS="$(json_get "$AI_STATS" "d.get('ai_calls', 'N/A')")"
AI_FAILED="$(json_get "$AI_STATS" "d.get('ai_failed_calls', 'N/A')")"
AI_RATE="$(json_get "$AI_STATS" "d.get('success_rate_pct', 'N/A')")"
TOK_PROMPT="$(json_get "$AI_STATS" "d.get('tokens', {}).get('prompt', 'N/A')")"
TOK_COMP="$(json_get "$AI_STATS" "d.get('tokens', {}).get('completion', 'N/A')")"
TOK_TOTAL="$(json_get "$AI_STATS" "d.get('tokens', {}).get('total', 'N/A')")"
TOK_CACHED="$(json_get "$AI_STATS" "d.get('tokens', {}).get('cached', 'N/A')")"
AI_COST="$(json_get "$AI_STATS" "round(d.get('estimated_cost_cny', 0), 4)")"
AI_LAT_P95="$(json_get "$AI_STATS" "round(d.get('latency_ms', {}).get('p95', 0), 1)")"
AI_MODELS="$(json_get "$AI_STATS" "', '.join(sorted(d.get('per_model', {}).keys())) or '无'")"

# ---------- 生成报告 ----------
cat > "$REPORT_FILE" <<EOF
# 📊 智能客服系统 - 每日汇报

**统计日期**：$STAT_DATE　**生成时间**：$(date +'%Y-%m-%d %H:%M')

---

## 📈 API 调用统计（$STAT_DATE）

| 指标 | 数值 |
|---|---|
| 总请求 | $API_TOTAL |
| 业务请求 | $API_BIZ |
| 扫描噪音 | $API_NOISE |
| 2xx / 4xx / 5xx | $API_2XX / $API_4XX / $API_5XX |
| 独立来源 IP | $API_IPS |
| 延迟 p95 / max | ${API_P95}ms / ${API_MAX}ms |
| 日志解析错误 | $API_PARSE_ERR |

## 💰 AI 成本看板（$STAT_DATE）

| 指标 | 数值 |
|---|---|
| AI 调用次数 | $AI_CALLS |
| 调用失败 | $AI_FAILED |
| 成功率 | $AI_RATE% |
| Token (prompt / completion) | $TOK_PROMPT / $TOK_COMP |
| Token 合计 / 缓存命中 | $TOK_TOTAL / $TOK_CACHED |
| 预估成本 | ¥$AI_COST |
| 延迟 p95 | ${AI_LAT_P95}ms |
| 涉及模型 | $AI_MODELS |

## 🖥️ 服务器健康

| 指标 | 数值 |
|---|---|
| 运行时间 | $UPTIME |
| 负载 | $LOAD |
| CPU | $CPU |
| 内存 | ${MEM_USED}MiB / ${MEM_TOTAL}MiB（可用 ${MEM_AVAIL}MiB） |
| 磁盘 | ${DISK_USED} / ${DISK_TOTAL}（${DISK_PCT}） |
| fail2ban 累计封禁 | $F2B_BAN |

---
*由 scripts/daily-report.sh 自动生成*
EOF

echo "✅ 日报已生成：$REPORT_FILE"
