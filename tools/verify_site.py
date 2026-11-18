import os
import sys
import re

# Ensure working directory is project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.abspath(os.getcwd()) != PROJECT_ROOT:
    os.chdir(PROJECT_ROOT)

html_files = [f for f in os.listdir('.') if f.endswith('.html')]
print("HTML Files found:", html_files)

all_ok = True
for hf in html_files:
    content = open(hf, encoding='utf-8').read()
    links = re.findall(r'href=[\'"]([^\'"#:]+)[\'"]', content)
    for l in set(links):
        clean_l = l.split('?')[0]
        if not clean_l.startswith('http') and not clean_l.startswith('mailto') and not clean_l.startswith('tel') and not clean_l.startswith('//'):
            if not os.path.exists(clean_l):
                print(f"Warning in {hf}: link {l} does not exist!")
                all_ok = False
    imgs = re.findall(r'src=[\'"]([^\'"#:]+)[\'"]', content)
    for img in set(imgs):
        clean_img = img.split('?')[0]
        if not clean_img.startswith('http') and not clean_img.startswith('//'):
            if not os.path.exists(clean_img):
                print(f"Warning in {hf}: image {img} does not exist!")
                all_ok = False

if all_ok:
    print("SUCCESS: All links, scripts, CSS, and images exist and are verified!")

