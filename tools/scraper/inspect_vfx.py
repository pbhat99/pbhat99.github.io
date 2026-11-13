import urllib.request
import re

req = urllib.request.Request('https://pramotions.weebly.com/vfx-works.html', headers={'User-Agent': 'Mozilla/5.0'})
vfx_html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# find all blocks inside main content
# Let's search for text blocks or captions
elements = re.findall(r'<div class="wsite-multicol-col"[^>]*>(.*?)</div>\s*</div>', vfx_html, re.DOTALL)
print(f"Cols found: {len(elements)}")

# Let's extract all image tags with their surrounding context or captions
imgs_with_context = re.findall(r'(<div[^>]*class="[^"]*(?:wsite-image|gallery|wsite-custom)[^"]*"[^>]*>.*?</div>)', vfx_html, re.DOTALL)
print(f"Image containers: {len(imgs_with_context)}")

# Also let's print all text in vfx_html
body = re.sub(r'<(?:script|style)[^>]*>.*?</(?:script|style)>', '', vfx_html, flags=re.DOTALL | re.I)
text_lines = [line.strip() for line in re.sub(r'<[^>]+>', '\n', body).split('\n') if line.strip()]
print("\n--- VFX Text Lines (first 100) ---")
for line in text_lines[:100]:
    if 'Weebly' not in line and 'nav' not in line.lower():
        print(line)
