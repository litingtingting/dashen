#!/bin/bash
# 每日 API 调用统计（统计前一天），由 cron 每日 00:10 触发
set -e
cd "$(dirname "$0")/.."
D=$(date -d yesterday +%Y-%m-%d)
mkdir -p data/stats
python3 scripts/api_stats.py --log logs/server-v2.log --date "$D" --out "data/stats/api-stats-$D.json" >> data/stats/daily.log 2>&1
