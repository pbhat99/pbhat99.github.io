import os
import urllib.request

os.makedirs('assets/images/portfolio', exist_ok=True)
os.makedirs('assets/images/branding', exist_ok=True)

# Key representative images from Weebly
imgs_to_download = [
    # Logo / branding
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/published/1460450240.png', 'assets/images/branding/logo.png'),
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/aligned-logos_1_orig.png', 'assets/images/branding/studio-logos.png'),
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/published/dneg-linkedin-banner.png', 'assets/images/branding/dneg-banner.png'),
    # Projects
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/buschlight-voice-of-the-mountains-longform-aubb2048h-vimeoid83680-mp4-snapshot-00-21-2023-12-14-13-11-03_orig.jpg', 'assets/images/portfolio/buschlight.jpg'),
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/adidas-create-the-answer-mp4-snapshot-01-26-2018-10-12-23-59-42_orig.jpg', 'assets/images/portfolio/adidas.jpg'),
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/mv5bote0zwi1mmitoda4ns00njm0lwjiodutyzg0y2i1ytuwytrmxkeyxkfqcgc-v1-fmjpg-uy2880_orig.jpg', 'assets/images/portfolio/goatbusters.jpg'),
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/mv5bmwjmyjcwmtmtmdu1zc00zgi5ltlmzdatodi3nda2zte5zgvlxkeyxkfqcgc-v1-fmjpg-uy4080_orig.jpg', 'assets/images/portfolio/hummer-ev.jpg'),
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/mv5bntywnmzhzjqtnzqzni00zgrhlwixmtutywi1otmwotq5ndlixkeyxkfqcgc-v1-fmjpg-uy3000_orig.jpg', 'assets/images/portfolio/pepsi-superbowl.jpg'),
    ('https://pramotions.weebly.com/uploads/8/8/2/2/8822082/927983-person-of-interest-wallpaper_orig.jpg', 'assets/images/portfolio/person-of-interest.jpg')
]

for url, dest in imgs_to_download:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp, open(dest, 'wb') as f:
            f.write(resp.read())
        print(f"Downloaded: {dest}")
    except Exception as e:
        print(f"Failed {url}: {e}")

