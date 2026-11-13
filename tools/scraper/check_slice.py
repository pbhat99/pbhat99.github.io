import urllib.request
import re

vfx_raw = urllib.request.urlopen('https://pramotions.weebly.com/vfx-works.html').read().decode('utf-8', errors='ignore')

# print slice around DirecTV and Hummer EV
start = vfx_raw.find('DirecTV')
print(vfx_raw[start-200:start+600])
