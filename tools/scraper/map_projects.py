import re
import json
import os

html = open('tools/scraper/scraped_pages.json').read()
# Let's inspect vfx-works HTML again to pair titles with their exact image
vfx_html = urllib.request = open('tools/scraper/scraped_pages.json')

# Let's fetch vfx-works.html from memory or download
import urllib.request
vfx_raw = urllib.request.urlopen('https://pramotions.weebly.com/vfx-works.html').read().decode('utf-8', errors='ignore')

# Weebly structure:
# Project title is in:
# <div class="paragraph">...<b>Project Title</b>...</div> or similar
# followed by <div class="wsite-image ..."><img src="..." /></div>

# Let's split by wsite-multicol-col or paragraph blocks
# Let's find all pairs of (text, img_src)
# Let's find all img tags and what text appeared immediately before or after them
img_tags = re.findall(r'(<div[^>]*class="[^"]*paragraph[^"]*"[^>]*>.*?</div>.*?<img[^>]+src=[\'"]([^\'"]+)[\'"]|<img[^>]+src=[\'"]([^\'"]+)[\'"].*?<div[^>]*class="[^"]*paragraph[^"]*"[^>]*>(.*?)</div>)', vfx_raw, re.DOTALL | re.I)

print(f"Matched pairs: {len(img_tags)}")
