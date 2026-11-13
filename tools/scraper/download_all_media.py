import urllib.request
import re
import os
import json
import hashlib

base_url = 'https://pramotions.weebly.com'

os.makedirs('assets/images/portfolio', exist_ok=True)
os.makedirs('assets/images/branding', exist_ok=True)
os.makedirs('assets/images/photography', exist_ok=True)
os.makedirs('assets/images/blog', exist_ok=True)

def download_image(img_url, dest_folder, custom_name=None):
    if not img_url:
        return None
    if img_url.startswith('//'):
        full_url = 'https:' + img_url
    elif img_url.startswith('/'):
        full_url = base_url + img_url
    elif img_url.startswith('http'):
        full_url = img_url
    else:
        full_url = f"{base_url}/{img_url}"

    # clean query params for extension
    clean_url = full_url.split('?')[0]
    ext = os.path.splitext(clean_url)[1].lower()
    if not ext or len(ext) > 5:
        ext = '.jpg'

    if custom_name:
        filename = f"{custom_name}{ext}"
    else:
        base_name = os.path.basename(clean_url)
        if len(base_name) < 4:
            base_name = hashlib.md5(full_url.encode()).hexdigest()[:12]
        filename = base_name

    dest_path = os.path.join(dest_folder, filename).replace('\\', '/')
    
    # Download if not exists
    if not os.path.exists(dest_path):
        try:
            req = urllib.request.Request(full_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                if len(data) > 500: # not an empty/error pixel
                    with open(dest_path, 'wb') as f:
                        f.write(data)
                    print(f"Downloaded: {dest_path} ({len(data)} bytes)")
                    return dest_path
        except Exception as e:
            print(f"Failed to download {full_url}: {e}")
            return None
    else:
        return dest_path

print("Starting asset download from pramotions.weebly.com...")

# 1. Download Photography page images
photo_html = urllib.request.urlopen(f"{base_url}/photography.html").read().decode('utf-8', errors='ignore')
photo_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', photo_html)
print(f"Photography images found: {len(photo_imgs)}")
downloaded_photos = []
for i, p_img in enumerate(photo_imgs):
    local_path = download_image(p_img, 'assets/images/photography', f'photo_{i+1}')
    if local_path:
        downloaded_photos.append(local_path)

# 2. Download Blog page images
blog_html = urllib.request.urlopen(f"{base_url}/blog.html").read().decode('utf-8', errors='ignore')
blog_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', blog_html)
print(f"Blog images found: {len(blog_imgs)}")
downloaded_blog_imgs = []
for i, b_img in enumerate(blog_imgs):
    local_path = download_image(b_img, 'assets/images/blog', f'blog_img_{i+1}')
    if local_path:
        downloaded_blog_imgs.append(local_path)

# 3. Download About Me images
about_html = urllib.request.urlopen(f"{base_url}/about-me.html").read().decode('utf-8', errors='ignore')
about_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', about_html)
print(f"About Me images found: {len(about_imgs)}")
for i, a_img in enumerate(about_imgs):
    download_image(a_img, 'assets/images/branding', f'about_me_{i+1}')

# 4. Download Home page images
home_html = urllib.request.urlopen(f"{base_url}/").read().decode('utf-8', errors='ignore')
home_imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', home_html)
for i, h_img in enumerate(home_imgs):
    download_image(h_img, 'assets/images/branding', f'home_hero_{i+1}')

print("Base images downloaded successfully!")
