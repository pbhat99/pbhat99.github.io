import urllib.request
import re
import json
import os

base_url = 'https://pramotions.weebly.com'

# Let's inspect VFX Works specifically to extract:
# Each project's title, image URL, link (IMDb, YouTube, Vimeo, etc.), and caption.
vfx_url = 'https://pramotions.weebly.com/vfx-works.html'
req = urllib.request.Request(vfx_url, headers={'User-Agent': 'Mozilla/5.0'})
vfx_html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

# In Weebly, projects are often inside <div class="wsite-image ..."> or columns.
# Let's search for image blocks:
# <div class="wsite-image ..."><a href="(link)"><img src="(src)" ... /></a><div class="wsite-image-title">(title)</div></div>
# or paragraphs with headings followed by image.

# Let's find all blocks containing an image
blocks = re.findall(r'(<div[^>]*class="[^"]*wsite-image[^"]*"[^>]*>.*?</div>\s*</div>)', vfx_html, re.DOTALL | re.I)
print(f"Total wsite-image blocks in VFX: {len(blocks)}")

projects = []
for b in blocks:
    img_match = re.search(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', b)
    link_match = re.search(r'<a[^>]+href=[\'"]([^\'"]+)[\'"]', b)
    title_match = re.search(r'class="wsite-image-title"[^>]*>(.*?)</div>', b, re.DOTALL)
    caption_match = re.search(r'class="paragraph"[^>]*>(.*?)</div>', b, re.DOTALL)
    
    img_src = img_match.group(1) if img_match else None
    link = link_match.group(1) if link_match else None
    title = re.sub(r'<[^>]+>', '', title_match.group(1)).strip() if title_match else ''
    caption = re.sub(r'<[^>]+>', '', caption_match.group(1)).strip() if caption_match else ''
    
    if img_src and 'counter.weebly' not in img_src:
        projects.append({
            'img_src': img_src,
            'link': link,
            'title': title,
            'caption': caption,
            'raw_block': b[:200]
        })

print(f"Parsed {len(projects)} image blocks. Samples:")
for p in projects[:15]:
    print(f"Img: {p['img_src']}")
    print(f"  Link: {p['link']}")
    print(f"  Title: {p['title']}")
    print(f"  Caption: {p['caption']}")
    print("---")

