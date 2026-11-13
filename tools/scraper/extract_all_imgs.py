import urllib.request
import re

pages = ['/', '/vfx-works.html', '/ai--comfy.html', '/photography.html', '/about-me.html', '/blog.html']
all_imgs = set()
for p in pages:
    req = urllib.request.Request('https://pramotions.weebly.com' + p, headers={'User-Agent': 'Mozilla/5.0'})
    html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')
    found = re.findall(r'src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', html)
    for f in found:
        all_imgs.add(f)

print(f"Total unique upload images: {len(all_imgs)}")
for img in sorted(list(all_imgs))[:30]:
    print(" ", img)
