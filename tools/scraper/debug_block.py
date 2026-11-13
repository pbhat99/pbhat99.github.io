import urllib.request
import re

vfx_raw = urllib.request.urlopen('https://pramotions.weebly.com/vfx-works.html').read().decode('utf-8', errors='ignore')
blocks = re.findall(r'<div[^>]*class="[^"]*wsite-image[^"]*"[^>]*>(.*?)</div>\s*</div>', vfx_raw, re.DOTALL | re.I)
for i, b in enumerate(blocks[:5]):
    print(f"Block {i}: {b[:150]}")

