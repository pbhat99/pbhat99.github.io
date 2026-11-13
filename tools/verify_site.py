import os
import re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]
print("HTML Files found:", html_files)

all_ok = True
for hf in html_files:
    content = open(hf, encoding='utf-8').read()
    links = re.findall(r'href=[\'"]([^\'"#:]+)[\'"]', content)
    for l in set(links):
        if not l.startswith('http') and not l.startswith('mailto') and not l.startswith('tel') and not l.startswith('//'):
            if not os.path.exists(l):
                print(f"Warning in {hf}: link {l} does not exist!")
                all_ok = False
    imgs = re.findall(r'src=[\'"]([^\'"#:]+)[\'"]', content)
    for img in set(imgs):
        if not img.startswith('http') and not img.startswith('//'):
            if not os.path.exists(img):
                print(f"Warning in {hf}: image {img} does not exist!")
                all_ok = False

if all_ok:
    print("SUCCESS: All links, scripts, CSS, and images exist and are verified!")

