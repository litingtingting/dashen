# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.trust_env = False

print("=" * 60)
print("Today's Market Report")
print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)
print()

# ========== 1. Major Indices ==========
print("[1] Major Indices")
print("-" * 60)

indices = [
    ('Shanghai', 'sh000001'),
    ('Shenzhen', 'sz399001'),
    ('ChiNext', 'sz399006'),
    ('STAR50', 'sh000688'),
]

for name, code in indices:
    url = f'http://qt.gtimg.cn/q={code}'
    try:
        r = session.get(url, timeout=8)
        r.encoding = 'gbk'
        text = r.text.strip()
        # Format: v_sh000001="1~上证指数~000001~4122.68~4182.59~..."
        if text and '=' in text and '"' in text:
            data = text.split('=')[1].strip('";')
            parts = data.split('~')
            # parts[3]=current, parts[4]=close_yest, parts[5]=open_today
            # parts[31]=change, parts[32]=change_pct (from test output)
            if len(parts) > 32:
                current = float(parts[3]) if parts[3] else 0
                yesterday = float(parts[4]) if parts[4] else current  # Use current as fallback
                change = float(parts[31]) if parts[31] else current - yesterday
                change_pct = float(parts[32]) if parts[32] else 0
                volume = float(parts[6]) / 10000 if parts[6] else 0  # 万手
                amount = float(parts[37]) / 100000000 if len(parts) > 37 and parts[37] else 0  # 亿
                print(f'{name}: {current:.2f}  ({change:+.2f}, {change_pct:+.2f}%)')
                print(f'  Vol: {volume:.1f}k lots  Amt: {amount:.2f}B CNY')
            else:
                print(f'{name}: Format error ({len(parts)} parts)')
                print(f'  Debug: parts[3]={parts[3] if len(parts)>3 else "N/A"}')
        else:
            print(f'{name}: No data')
    except Exception as e:
        print(f'{name}: Failed - {str(e)[:40]}')
    print()

# ========== 2. Key ETFs ==========
print("\n[2] Key ETFs")
print("-" * 60)

etfs = [
    ('CSI300', 'sh510300'),
    ('ChiNext', 'sz159915'),
    ('STAR50', 'sh588000'),
    ('CSI500', 'sh510500'),
    ('Securities', 'sh512880'),
    ('Chip', 'sz159995'),
]

for name, code in etfs:
    url = f'http://qt.gtimg.cn/q={code}'
    try:
        r = session.get(url, timeout=5)
        r.encoding = 'gbk'
        text = r.text.strip()
        if text and '=' in text and '"' in text:
            data = text.split('=')[1].strip('";')
            parts = data.split('~')
            if len(parts) > 32:
                current = float(parts[3]) if parts[3] else 0
                yesterday = float(parts[4]) if parts[4] else current
                change = float(parts[31]) if parts[31] else current - yesterday
                change_pct = float(parts[32]) if parts[32] else 0
                print(f'{name}: {current:.3f}  ({change:+.2f}, {change_pct:+.2f}%)')
            else:
                print(f'{name}: Format error')
        else:
            print(f'{name}: No data')
    except Exception as e:
        print(f'{name}: Failed')
    print()

# ========== 3. Market Summary ==========
print("\n[3] Qian Duoduo's Analysis")
print("=" * 60)

# Try to get sentiment data
url = 'https://push2.eastmoney.com/api/qt/clist/get'
params = {
    'pn': '1', 'pz': '50', 'po': '1', 'np': '1',
    'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
    'fltt': '2', 'invt': '2', 'fid': 'f3',
    'fs': 'm:0 t:6,m:0 t:80,m:1 t:2,m:1 t:23',
    'fields': 'f12,f14,f2,f3,f4'
}

try:
    r = session.get(url, params=params, timeout=10)
    data = r.json()
    if data.get('data') and data['data'].get('diff'):
        stocks = data['data']['diff']
        up_count = sum(1 for s in stocks if float(s.get('f3', 0)) > 0)
        down_count = sum(1 for s in stocks if float(s.get('f3', 0)) < 0)
        print(f'Market Breadth: Up {up_count} / Down {down_count}')
        
        # Top gainers
        print("\nTop 5 Gainers:")
        gainers = sorted(stocks, key=lambda x: float(x.get('f3', 0)), reverse=True)[:5]
        for i, s in enumerate(gainers, 1):
            code = s.get('f12', '')
            stock_name = s.get('f14', '')
            price = float(s.get('f2', 0))
            pct = float(s.get('f3', 0))
            print(f'  {i}. {stock_name}({code}): {price:.2f} ({pct:+.2f}%)')
    else:
        print('Sentiment data unavailable')
except Exception as e:
    print(f'Sentiment data unavailable: {str(e)[:40]}')

print("""
Trading Suggestions:
1. Monitor volume and sector rotation
2. Follow policy-driven themes
3. Maintain proper position control
4. Set stop-loss levels

Disclaimer:
For reference only, not investment advice.
Market involves risks, invest carefully.
""")
print("=" * 60)
print("Done!")
print("=" * 60)
