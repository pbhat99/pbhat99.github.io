import urllib.request
import re

def check(url, name):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    content = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    body = re.sub(r'<(?:script|style)[^>]*>.*?</(?:script|style)>', '', content, flags=re.DOTALL | re.I)
    lines = [l.strip() for l in re.sub(r'<[^>]+>', '\n', body).split('\n') if l.strip()]
    print(f"=== {name} ===")
    for l in lines[:40]:
        if 'weebly' not in l.lower() and 'nav' not in l.lower():
            print(l)

check('https://pramotions.weebly.com/blog.html', 'BLOG')
check('https://pramotions.weebly.com/ai--comfy.html', 'AI COMFY')
