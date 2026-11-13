import os
import shutil
import json

# 1. Home
home_content = {
    "name": "Prasannakumar T Bhat",
    "designation": "Senior Visual Effects Compositor @ DNEG",
    "tagline": "CG is not just faking, its adding beautiful layers of lie on the ugly truth.",
    "ctaText": "View VFX Works",
    "ctaLink": "vfx-works.html"
}
with open('pages/01_home/content.json', 'w', encoding='utf-8') as f:
    json.dump(home_content, f, indent=2)

# Copy a subtle cinematic background to pages/01_home/background.jpg
if os.path.exists('assets/images/portfolio/pepsi-the-call-super-bowl-56-mp4-snapshot-00-21-2023-12-14-13-14-22_orig.jpg'):
    shutil.copy('assets/images/portfolio/pepsi-the-call-super-bowl-56-mp4-snapshot-00-21-2023-12-14-13-14-22_orig.jpg', 'pages/01_home/background.jpg')

# 2. VFX Works
# Copy all portfolio images into pages/02_vfx-works/projects/
for f in os.listdir('assets/images/portfolio'):
    src = os.path.join('assets/images/portfolio', f)
    dst = os.path.join('pages/02_vfx-works/projects', f)
    if os.path.isfile(src) and not os.path.exists(dst):
        shutil.copy(src, dst)

# Copy projects.json
shutil.copy('data/projects.json', 'pages/02_vfx-works/projects.json')

# 3. AI / Comfy
if os.path.exists('assets/images/blog/blog_img_2.png'):
    shutil.copy('assets/images/blog/blog_img_2.png', 'pages/03_ai-comfy/workflows/comfyui-production-pipeline.png')
shutil.copy('data/comfy_workflows.json', 'pages/03_ai-comfy/workflows.json')

# 4. Photography
for f in os.listdir('assets/images/portfolio'):
    if any(k in f.lower() for k in ['buschlight', 'pepsi', 'adidas', '25398209', 'xbox']):
        src = os.path.join('assets/images/portfolio', f)
        dst = os.path.join('pages/04_photography/gallery', f)
        if not os.path.exists(dst):
            shutil.copy(src, dst)
shutil.copy('data/photography.json', 'pages/04_photography/photography.json')

# 5. About Me
if os.path.exists('assets/images/branding/about_me_2.jpg'):
    shutil.copy('assets/images/branding/about_me_2.jpg', 'pages/05_about-me/profile.jpg')
if os.path.exists('assets/images/branding/dneg-banner.png'):
    shutil.copy('assets/images/branding/dneg-banner.png', 'pages/05_about-me/banner.png')

about_data = {
    "name": "Prasannakumar T Bhat",
    "role": "Compositing Artist @ DNEG",
    "experience": "10+ Years Visual Effects Experience",
    "phone": "+91 9449267068",
    "github": "https://github.com/pbhat99",
    "location": "#09, Ghattimane, Donagar, Po: Idgundi, Tq: Yellapur, Dist: Uttara Kannada, Karnataka, India - 581337"
}
with open('pages/05_about-me/bio.json', 'w', encoding='utf-8') as f:
    json.dump(about_data, f, indent=2)

# 6. Blog
shutil.copy('data/blog.json', 'pages/06_blog/blog.json')

print("pages/ structure successfully initialized with content!")
