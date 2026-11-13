import urllib.request
import re

req = urllib.request.Request('https://pramotions.weebly.com/vfx-works.html', headers={'User-Agent': 'Mozilla/5.0'})
vfx_html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# find all images with src
imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*alt=[\'"]([^\'"]*)[\'"]', vfx_html, re.I)
if not imgs:
    # try without alt
    imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', vfx_html, re.I)
    print("Found images without alt:", len(imgs))
    for img in imgs[:15]:
        print("  ", img)
else:
    print(f"Found {len(imgs)} imgs with alt:")
    for src, alt in imgs[:15]:
        print(f"  {alt} -> {src}")

# Check widgetic before/after sliders
widgets = re.findall(r'widgetic\.com/wbl/app/[^\'"]+', vfx_html)
print(f"Widgetic sliders: {len(widgets)}")
for w in widgets:
    print("  ", w)
