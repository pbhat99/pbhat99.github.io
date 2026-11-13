import urllib.request
from html.parser import HTMLParser
import re

def get_page(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# Check VFX Works page in detail
vfx_html = get_page('https://pramotions.weebly.com/vfx-works.html')
about_html = get_page('https://pramotions.weebly.com/about-me.html')
home_html = get_page('https://pramotions.weebly.com/')

print("=== ABOUT ME DETAILS ===")
# extract text inside wsite-content or similar
about_clean = re.sub(r'<script.*?</script>', '', about_html, flags=re.DOTALL | re.I)
about_clean = re.sub(r'<style.*?</style>', '', about_clean, flags=re.DOTALL | re.I)
# find all paragraphs and headings
paragraphs = re.findall(r'<(?:p|h1|h2|h3|h4|div class="paragraph")[^>]*>(.*?)</(?:p|h1|h2|h3|h4|div)>', about_clean, re.I | re.DOTALL)
for p in paragraphs:
    t = re.sub(r'<[^>]+>', ' ', p).strip()
    if len(t) > 20 and 'Weebly' not in t:
        print("-", t)

print("\n=== VFX WORKS PROJECTS ===")
vfx_clean = re.sub(r'<script.*?</script>', '', vfx_html, flags=re.DOTALL | re.I)
vfx_clean = re.sub(r'<style.*?</style>', '', vfx_clean, flags=re.DOTALL | re.I)
# Look for titles or project headers
titles = re.findall(r'<(?:h1|h2|h3|h4|font)[^>]*>(.*?)</(?:h1|h2|h3|h4|font)>', vfx_clean, re.I | re.DOTALL)
for t in set(titles):
    txt = re.sub(r'<[^>]+>', '', t).strip()
    if 3 < len(txt) < 80 and 'Weebly' not in txt and 'Home' not in txt:
        print("VFX Heading/Project:", txt)

print("\n=== HOME DETAILS ===")
home_clean = re.sub(r'<script.*?</script>', '', home_html, flags=re.DOTALL | re.I)
home_clean = re.sub(r'<style.*?</style>', '', home_clean, flags=re.DOTALL | re.I)
home_paras = re.findall(r'<(?:p|h1|h2|h3|h4)[^>]*>(.*?)</(?:p|h1|h2|h3|h4)>', home_clean, re.I | re.DOTALL)
for p in home_paras:
    t = re.sub(r'<[^>]+>', ' ', p).strip()
    if len(t) > 10 and 'Weebly' not in t:
        print("Home:", t)
