import urllib.request
import re
import os
import json

base_url = 'https://pramotions.weebly.com'
vfx_html = urllib.request.urlopen(f"{base_url}/vfx-works.html").read().decode('utf-8', errors='ignore')

# In Weebly pages, content is arranged in rows and columns:
# e.g., <div class="paragraph">Title</div> ... <img src="..." />
# Let's extract all image tags in vfx_html with their src attribute
imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', vfx_html)
print(f"Total uploads images in VFX page: {len(imgs)}")

# Let's clean the URLs (remove query params for deduplication)
unique_imgs = []
seen = set()
for img in imgs:
    clean = img.split('?')[0]
    if clean not in seen and '1460450240' not in clean: # not the logo
        seen.add(clean)
        unique_imgs.append(img)

print(f"Unique project images to download: {len(unique_imgs)}")

# Let's download them into assets/images/portfolio/
downloaded = {}
for i, img_url in enumerate(unique_imgs):
    if img_url.startswith('/'):
        full_url = base_url + img_url
    else:
        full_url = img_url
    
    # Get filename
    basename = os.path.basename(img_url.split('?')[0])
    dest_path = os.path.join('assets/images/portfolio', basename).replace('\\', '/')
    
    if not os.path.exists(dest_path):
        try:
            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if len(data) > 500:
                    with open(dest_path, 'wb') as f:
                        f.write(data)
                    print(f"[{i+1}/{len(unique_imgs)}] Downloaded {basename} ({len(data)} bytes)")
                    downloaded[img_url] = dest_path
        except Exception as e:
            print(f"Failed {basename}: {e}")
    else:
        downloaded[img_url] = dest_path

print(f"\nFinished downloading {len(downloaded)} project images!")

