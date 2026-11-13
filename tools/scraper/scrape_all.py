import urllib.request
from html.parser import HTMLParser
import re
import os
import json

base_url = 'https://pramotions.weebly.com'
pages = {
    'home': '/',
    'vfx-works': '/vfx-works.html',
    'ai-comfy': '/ai--comfy.html',
    'photography': '/photography.html',
    'about-me': '/about-me.html',
    'blog': '/blog.html'
}

os.makedirs('assets/images/portfolio', exist_ok=True)
os.makedirs('assets/images/branding', exist_ok=True)
os.makedirs('assets/images/photography', exist_ok=True)
os.makedirs('assets/images/blog', exist_ok=True)

# Parse each page in detail
page_data = {}

for page_key, path in pages.items():
    url = base_url + path
    print(f"\n--- Scraping {page_key} ({url}) ---")
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        content = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        continue

    # Find all images with context
    # In Weebly: <div class="wsite-image ..."><a ...><img src="..." alt="..." /></a><div class="wsite-image-title">...</div></div>
    # or gallery items
    imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"][^>]*>', content, re.I)
    
    clean_imgs = []
    for img_tag in imgs:
        if 'theme' in img_tag or 'counter.weebly.com' in img_tag or 'pixel' in img_tag:
            continue
        clean_imgs.append(img_tag)
    
    print(f"Found {len(clean_imgs)} images on {page_key}")
    page_data[page_key] = {
        'html': content,
        'images': clean_imgs
    }

with open('tools/scraper/scraped_pages.json', 'w', encoding='utf-8') as f:
    # Save image lists
    summary = {k: v['images'] for k, v in page_data.items()}
    json.dump(summary, f, indent=2)

print("\nScraped pages summary saved to tools/scraper/scraped_pages.json")
