import urllib.request
import re
import json

pages = {
    'Home': '/',
    'VFX Works': '/vfx-works.html',
    'AI / Comfy': '/ai--comfy.html',
    'Photography': '/photography.html',
    'About Me': '/about-me.html',
    'Blog': '/blog.html'
}

base = 'https://pramotions.weebly.com'
results = {}

for name, p in pages.items():
    url = base + p
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8', errors='ignore')
            title = re.findall(r'<title>(.*?)</title>', content, re.I)
            imgs = re.findall(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', content, re.I)
            imgs = [img for img in imgs if 'theme' not in img and ('uploads' in img or 'weebly' not in img)]
            iframes = re.findall(r'<iframe[^>]+src=[\'"]([^\'"]+)[\'"]', content, re.I)
            
            # Find paragraphs or main text blocks
            body_text = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL | re.I)
            body_text = re.sub(r'<style.*?</style>', '', body_text, flags=re.DOTALL | re.I)
            clean_text = re.sub(r'<[^>]+>', ' ', body_text)
            clean_text = ' '.join(clean_text.split())
            
            results[name] = {
                'url': url,
                'title': title[0] if title else '',
                'images': imgs,
                'iframes': iframes,
                'text_preview': clean_text[:400]
            }
            print(f"=== {name} ===")
            print(f"Title: {title[0] if title else ''}")
            print(f"Images count: {len(imgs)}")
            print(f"Iframes: {iframes}")
            print(f"Text preview: {clean_text[:250]}\n")
    except Exception as e:
        print(f"Error {name}: {e}")

with open('site_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2)
