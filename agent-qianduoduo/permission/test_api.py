# -*- coding: utf-8 -*-
import requests
import sys

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.trust_env = False

# Test Shanghai index
url = 'http://qt.gtimg.cn/q=sh000001'
print(f"Testing: {url}")
print("-" * 60)

try:
    r = session.get(url, timeout=10)
    print(f"Status Code: {r.status_code}")
    print(f"Content-Type: {r.headers.get('Content-Type')}")
    print(f"Raw Content ({len(r.content)} bytes):")
    print(r.content[:500])
    print()
    print("Text Content:")
    r.encoding = 'gbk'
    text = r.text
    print(text[:500] if text else "Empty")
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
