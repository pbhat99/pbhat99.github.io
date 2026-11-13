import urllib.request
import re

urls = [
    'https://widgetic.com/wbl/app/51d57c5a1d8a0cee4a000000?wbl[wid]=c1c12f5c-eed2-4fde-89ce-6f97fdbedd1e&wbl[uid]=8822082&wbl[sid]=788885198423584805&prod&autoscale=1',
    'https://widgetic.com/wbl/app/51d57c5a1d8a0cee4a000000?wbl[wid]=f7e25c0a-06f9-4c8e-8afb-d239bcb4ecc7&wbl[uid]=8822082&wbl[sid]=788885198423584805&prod&autoscale=1',
    'https://widgetic.com/wbl/app/51d57c5a1d8a0cee4a000000?wbl[wid]=49f3965c-9ef0-4571-b242-82bfc5496f02&wbl[uid]=8822082&wbl[sid]=788885198423584805&prod&autoscale=1'
]

for i, u in enumerate(urls):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        content = urllib.request.urlopen(req, timeout=5).read().decode('utf-8', errors='ignore')
        imgs = re.findall(r'https?://[^\s\'"]+\.(?:jpg|png|webp)', content, re.I)
        print(f"Widget {i+1} images:", imgs[:5])
    except Exception as e:
        print(f"Widget {i+1} error: {e}")
