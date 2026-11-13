import urllib.request
import re
import os
import json

vfx_raw = urllib.request.urlopen('https://pramotions.weebly.com/vfx-works.html').read().decode('utf-8', errors='ignore')

# Clean scripts and styles
vfx_clean = re.sub(r'<(?:script|style)[^>]*>.*?</(?:script|style)>', '', vfx_raw, flags=re.DOTALL | re.I)

# Let's find all occurrences of:
# (1) <img ... src="...uploads/..." ...>
# (2) text blocks with titles
tokens = []
# Tokenize by tags
parts = re.split(r'(<[^>]+>)', vfx_clean)
cur_tag = ''
for p in parts:
    p_strip = p.strip()
    if not p_strip:
        continue
    if p_strip.startswith('<'):
        cur_tag = p_strip
        img_m = re.search(r'<img[^>]+src=[\'"]([^\'"]+uploads/[^\'"]+)[\'"]', p_strip, re.I)
        if img_m:
            tokens.append(('IMG', img_m.group(1).split('?')[0]))
    else:
        # text
        if len(p_strip) > 2 and 'theme' not in p_strip and 'weebly' not in p_strip.lower():
            tokens.append(('TEXT', p_strip))

print(f"Total tokens: {len(tokens)}")

# Pair titles with images
projects = []
cur_title = None

titles_list = [
    "DirecTV - GOATbusters",
    "Hummer EV",
    "BuschLight - Voice of the Mountains",
    "Pepsi - 'The Call' Super Bowl",
    "Ralph Lauren",
    "xbox forza getaway driver",
    "Three 5G",
    "The Disney Wish",
    "Comcast",
    "Michelob Ultra",
    "ServiceNow",
    "Mayans",
    "The Odd One Out",
    "ARXIV/ Archive",
    "Walmart | Famous Cars",
    "BudLight - HBO Joust",
    "JAY PRINCE - Beamlight",
    "THE CHEMICAL BROTHERS - Free Yourself",
    "ASDA - Christmas is Coming",
    "The Most Vicious Cycle",
    "Adidas - Create The Answer",
    "Dick's Sporting Goods- Play Like You Own It",
    "Doller Shave Club - Get Ready",
    "Anjaniputra",
    "Abhisaarike",
    "Samhara",
    "Shankanaada",
    "BMW",
    "Kamarottu CheckPost",
    "Saguva Dariyalli",
    "Samyuktha-2",
    "Kataka",
    "Double Engine",
    "PatiBeku.com",
    "Mantram",
    "Java",
    "Uddishya",
    "Sihir",
    "Bengaluru Underworld",
    "Ajaramara",
    "Eradu Kanasu",
    "Jai Maruti 800",
    "Badmaash",
    "Ricky",
    "Smile Please",
    "JiNi Analytics",
    "BCL Sandalwood"
]

project_map = []
for i, (ttype, val) in enumerate(tokens):
    if ttype == 'TEXT':
        for t in titles_list:
            if t.lower() in val.lower() or val.lower() in t.lower():
                # Find closest image forward or backward within 5 tokens
                found_img = None
                for look in range(1, 8):
                    if i + look < len(tokens) and tokens[i+look][0] == 'IMG':
                        found_img = tokens[i+look][1]
                        break
                    elif i - look >= 0 and tokens[i-look][0] == 'IMG':
                        found_img = tokens[i-look][1]
                        break
                
                # check local file
                basename = os.path.basename(found_img) if found_img else None
                local_path = f"assets/images/portfolio/{basename}" if basename else None
                
                project_map.append({
                    'title': t,
                    'raw_text': val,
                    'img_url': found_img,
                    'local_path': local_path
                })
                break

print(f"Matched {len(project_map)} projects:")
for p in project_map[:20]:
    print(f"{p['title']} -> {p['local_path']}")

with open('tools/scraper/mapped_projects.json', 'w', encoding='utf-8') as f:
    json.dump(project_map, f, indent=2)

