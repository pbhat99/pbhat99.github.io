from html.parser import HTMLParser
import urllib.request
import re

req = urllib.request.Request('https://pramotions.weebly.com/vfx-works.html', headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req).read().decode('utf-8', errors='ignore')

class VfxParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.cur_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if tag == 'img':
            src = attrs_dict.get('src', '')
            if 'uploads' in src:
                self.elements.append(('IMG', src))
        elif tag == 'iframe':
            src = attrs_dict.get('src', '')
            self.elements.append(('IFRAME', src))

    def handle_data(self, data):
        txt = data.strip()
        if txt and len(txt) > 2:
            self.elements.append(('TEXT', txt))

parser = VfxParser()
parser.feed(html)

print(f"Total parsed elements: {len(parser.elements)}")
# Let's inspect the sequence around VFX works
recording = False
for item_type, val in parser.elements:
    if 'VFX Works' in val:
        recording = True
    if 'Powered by' in val:
        recording = False
    if recording:
        if item_type == 'TEXT' and len(val) > 2:
            print(f"TEXT: {val}")
        elif item_type == 'IMG':
            print(f"  --> IMG: {val}")
        elif item_type == 'IFRAME':
            print(f"  --> IFRAME: {val[:60]}")
