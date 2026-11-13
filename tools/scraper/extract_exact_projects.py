import urllib.request
import re
import os
import json

vfx_raw = urllib.request.urlopen('https://pramotions.weebly.com/vfx-works.html').read().decode('utf-8', errors='ignore')

# Match each wsite-image block:
blocks = re.findall(r'<div[^>]*class="[^"]*wsite-image[^"]*"[^>]*>(.*?)</div>\s*</div>', vfx_raw, re.DOTALL | re.I)
print(f"Total wsite-image blocks: {len(blocks)}")

parsed_projects = []
for b in blocks:
    img_match = re.search(r'<img[^>]+src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', b)
    link_match = re.search(r'<a[^>]+href=[\'"]([^\'"]+)[\'"]', b)
    # The title is in the child div with font-size:90% or wsite-image-title
    caption_match = re.search(r'<div[^>]*style="[^"]*font-size:[^"]*"[^>]*>(.*?)</div>', b, re.DOTALL | re.I)
    if not caption_match:
        caption_match = re.search(r'class="[^"]*wsite-image-title[^"]*"[^>]*>(.*?)</div>', b, re.DOTALL | re.I)

    if img_match:
        img_src = img_match.group(1).split('?')[0]
        basename = os.path.basename(img_src)
        local_path = f"assets/images/portfolio/{basename}"
        
        link = link_match.group(1) if link_match else ""
        caption = ""
        if caption_match:
            caption = re.sub(r'<[^>]+>', '', caption_match.group(1)).strip()

        # If caption is empty, try to derive from basename or link
        if caption and '1460450240' not in basename and 'aligned-logos' not in basename:
            # Determine category: films, commercials, music-videos
            cat = "commercials"
            if any(f in caption.lower() for f in ['film', 'sandalwood', 'anjani', 'kataka', 'samhara', 'ricky', 'badmaash', 'sihir', 'bengaluru', 'maruti', 'eradu', 'ajaramara', 'java', 'uddishya', 'mantram', 'double engine', 'patibeku', 'samyuktha', 'kamarottu', 'shankanaada', 'abhisaarike']):
                cat = "films"
            elif any(m in caption.lower() for m in ['chemical brothers', 'jay prince', 'music']):
                cat = "music-videos"
            
            parsed_projects.append({
                'title': caption,
                'category': cat,
                'image': local_path,
                'link': link
            })
            print(f"[{cat.upper()}] {caption} -> {local_path}")

print(f"\nSuccessfully parsed {len(parsed_projects)} projects with authentic titles and images!")
with open('data/weebly_extracted_projects.json', 'w', encoding='utf-8') as f:
    json.dump(parsed_projects, f, indent=2)
