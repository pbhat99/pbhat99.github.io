import urllib.request
import re
from bs4 import BeautifulSoup
import os
import json

base_url = 'https://pramotions.weebly.com'
vfx_raw = urllib.request.urlopen(f"{base_url}/vfx-works.html").read().decode('utf-8', errors='ignore')
soup = BeautifulSoup(vfx_raw, 'html.parser')

image_divs = soup.find_all('div', class_=lambda c: c and 'wsite-image' in c)
print(f"Total wsite-image elements: {len(image_divs)}")

all_parsed = []
film_keywords = [
    'anjaniputra', 'abhisaarike', 'samhara', 'shankanaada', 'bmw',
    'kamarottu', 'saguva', 'samyuktha', 'kataka', 'double engine',
    'patibeku', 'mantram', 'java', 'uddishya', 'sihir', 'bengaluru',
    'ajaramara', 'eradu', 'maruti', 'badmaash', 'ricky', 'smile please',
    'sandalwood', 'movie', 'film'
]

music_keywords = [
    'chemical brothers', 'jay prince', 'music'
]

for div in image_divs:
    img = div.find('img')
    if not img or not img.get('src'):
        continue
    
    src = img['src'].split('?')[0]
    if '1460450240' in src: # logo
        continue
    
    basename = os.path.basename(src)
    local_path = f"assets/images/portfolio/{basename}"
    
    # Check if local file exists
    if not os.path.exists(local_path):
        # try to download
        try:
            full_src = base_url + src if src.startswith('/') else src
            req = urllib.request.Request(full_src, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as resp:
                with open(local_path, 'wb') as f:
                    f.write(resp.read())
        except Exception as e:
            print(f"Error downloading {src}: {e}")

    # Find caption / title
    caption_div = div.find('div')
    title = caption_div.get_text(strip=True) if caption_div else ""
    
    # If title is empty, check neighboring elements
    if not title:
        # Check next sibling
        sib = div.find_next_sibling(['div', 'p'])
        if sib:
            title = sib.get_text(strip=True)

    link = div.find('a')
    href = link.get('href') if link else ""

    # Filter out empty or general layout items
    if not title and 'aligned-logos' in basename:
        continue
    if not title and 'dneg' in basename:
        continue

    title_clean = title if title else basename.replace('_orig', '').replace('-', ' ').title()
    
    # Categorize
    cat = "commercials"
    title_lower = title_clean.lower()
    if any(k in title_lower for k in film_keywords):
        cat = "films"
    elif any(k in title_lower for k in music_keywords):
        cat = "music-videos"
    elif 'super bowl' in title_lower or 'pepsi' in title_lower:
        cat = "commercials"

    all_parsed.append({
        'id': re.sub(r'[^a-z0-9]+', '-', title_clean.lower()).strip('-'),
        'title': title_clean,
        'category': cat,
        'image': local_path,
        'link': href,
        'hasBeforeAfter': False
    })
    print(f"[{cat.upper()}] {title_clean} -> {local_path}")

print(f"\nTotal extracted VFX projects: {len(all_parsed)}")

with open('data/weebly_extracted_projects.json', 'w', encoding='utf-8') as f:
    json.dump(all_parsed, f, indent=2)
