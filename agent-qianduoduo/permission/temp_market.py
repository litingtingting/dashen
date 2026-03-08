import requests

session = requests.Session()
session.trust_env = False

# 腾讯财经大盘接口
stocks = [
    ('上证指数', 'sh000001'),
    ('深证成指', 'sz399001'),
    ('创业板指', 'sz399006')
]

print("=== 今日大盘行情 ===\n")

for name, code in stocks:
    url = f'http://qt.gtimg.cn/q={code}'
    try:
        r = session.get(url, timeout=5)
        r.encoding = 'gbk'
        data = r.text.strip()
        if data:
            parts = data.split('~')
            if len(parts) > 30:
                price = parts[3]
                change = parts[31]
                change_pct = parts[32]
                print(f'{name}: {price} ({change}, {change_pct}%)')
            else:
                print(f'{name}: 数据格式异常')
        else:
            print(f'{name}: 无数据')
    except Exception as e:
        print(f'{name}: 获取失败 - {e}')
