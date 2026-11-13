import json

with open('site_analysis.json') as f:
    data = json.load(f)

for page, info in data.items():
    print(f"Page: {page}")
    print(f"  Url: {info['url']}")
    print(f"  Title: {info['title']}")
    print(f"  Images count: {len(info['images'])}")
    if info['iframes']:
        print(f"  Iframes: {len(info['iframes'])}")
        for ifr in info['iframes'][:5]:
            print(f"    - {ifr[:80]}")
