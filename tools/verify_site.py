import json
import os
import re
import sys
import urllib.parse

# Ensure working directory is project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.abspath(os.getcwd()) != PROJECT_ROOT:
    os.chdir(PROJECT_ROOT)


def is_external(path):
    return path.startswith(('http://', 'https://', 'mailto:', 'tel:', '//', 'data:'))


def main():
    html_files = sorted(f for f in os.listdir('.') if f.endswith('.html'))
    print("HTML Files found:", html_files)

    all_ok = True
    for hf in html_files:
        content = open(hf, encoding='utf-8').read()

        # 1. Verify href, src, and srcset targets
        refs = re.findall(r'(?:href|src)=[\'"]([^\'"#:]+)[\'"]', content)
        for srcset_val in re.findall(r'srcset=[\'"]([^\'"]+)[\'"]', content):
            for entry in srcset_val.split(','):
                candidate = entry.strip().split()[0] if entry.strip() else ''
                if candidate:
                    refs.append(candidate)

        for ref in set(refs):
            clean = urllib.parse.unquote(ref.split('?')[0].strip())
            if clean and not is_external(clean) and not os.path.exists(clean):
                print(f"[ERROR] {hf}: Missing referenced asset '{clean}'")
                all_ok = False

        # 2. Verify inline CSS url(...) assets (background-image, --slide-bg, --slide-bg-mobile)
        bg_urls = re.findall(r'url\([\'"]([^\'")]+)[\'"]\)', content)
        for bg in set(bg_urls):
            clean = urllib.parse.unquote(bg.split('?')[0].strip())
            if clean and not is_external(clean) and not os.path.exists(clean):
                print(f"[ERROR] {hf}: Missing CSS image '{clean}'")
                all_ok = False

        # 3. Verify embedded JSON data payloads and referenced assets
        for json_id in ('photosData', 'panosData', 'blogPostsData'):
            m = re.search(rf'<script id="{json_id}" type="application/json">(.*?)</script>', content, re.S)
            if m:
                try:
                    items = json.loads(m.group(1))
                    for item in items:
                        for key in ('thumb', 'webp', 'thumbnail'):
                            val = item.get(key)
                            clean_val = urllib.parse.unquote(val.split('?')[0]) if val else ''
                            if clean_val and not is_external(clean_val) and not os.path.exists(clean_val):
                                print(f"[ERROR] {hf} ({json_id}): Missing image '{val}'")
                                all_ok = False
                except json.JSONDecodeError as je:
                    print(f"[ERROR] {hf} ({json_id}): Invalid JSON ({je})")
                    all_ok = False

        # 4. Verify no duplicate IDs inside a single page
        ids = re.findall(r'\sid=[\'"]([^\'"]+)[\'"]', content)
        dup_ids = sorted(i for i in set(ids) if ids.count(i) > 1)
        if dup_ids:
            print(f"[ERROR] {hf}: Duplicate IDs found: {dup_ids}")
            all_ok = False

    if all_ok:
        print("SUCCESS: All links, scripts, CSS, images, JSON payloads, and IDs verified!")
    else:
        print("FAILED: One or more verification checks failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
