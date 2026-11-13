import urllib.request
from bs4 import BeautifulSoup

vfx_raw = urllib.request.urlopen('https://pramotions.weebly.com/vfx-works.html').read().decode('utf-8', errors='ignore')
soup = BeautifulSoup(vfx_raw, 'html.parser')

image_divs = soup.find_all('div', class_=lambda c: c and 'wsite-image' in c)
for i, div in enumerate(image_divs[:15]):
    img = div.find('img')
    src = img['src'] if img else ""
    # parent anchor or link
    a = div.find('a')
    href = a.get('href', '') if a else ''
    alt = img.get('alt', '') if img else ''
    title_text = div.get_text(strip=True)
    print(f"{i}: src={src.split('?')[0].split('/')[-1][:30]} | href={href} | text={title_text}")

