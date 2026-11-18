import os
import sys

# Ensure script working directory is always repository root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.abspath(os.getcwd()) != PROJECT_ROOT:
    os.chdir(PROJECT_ROOT)

import re
import json
import html
import yaml
import markdown
import glob
import datetime

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text).strip('-')
    return text

def format_title_from_filename(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'^[0-9]+[-_]', '', name)
    name = name.replace('_orig', '').replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()

def get_page_background_and_overlay(page_dir):
    """
    Finds the background image for a page folder, falling back to pages/01_home/background.jpg.
    Also resolves overlayOpacity (0 = full image display, 100 = solid dark #0e1733), falling back to home's setting.
    """
    bg_candidates = ["background.webp", "background.jpg", "background.jpeg", "background.png"]
    resolved_bg = None
    
    # 1. Look in page_dir first
    for cand in bg_candidates:
        path = os.path.join(page_dir, cand)
        if os.path.exists(path):
            resolved_bg = path.replace("\\", "/")
            break
            
    # 2. Fall back to pages/01_home
    if not resolved_bg:
        home_dir = "pages/01_home"
        for cand in bg_candidates:
            path = os.path.join(home_dir, cand)
            if os.path.exists(path):
                resolved_bg = path.replace("\\", "/")
                break

    # 3. Resolve overlayOpacity
    raw_opacity = None
    page_content = os.path.join(page_dir, "content.json")
    if os.path.exists(page_content):
        try:
            with open(page_content, "r", encoding="utf-8") as f:
                d = json.load(f)
                raw_opacity = d.get("overlayOpacity") or d.get("bgOverlayOpacity") or d.get("opacity")
        except Exception:
            pass

    if raw_opacity is None:
        home_content = "pages/01_home/content.json"
        if os.path.exists(home_content):
            try:
                with open(home_content, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    raw_opacity = d.get("overlayOpacity") or d.get("bgOverlayOpacity") or d.get("opacity")
            except Exception:
                pass

    try:
        opacity_num = float(raw_opacity) if raw_opacity is not None else 65.0
        if 0.0 < opacity_num < 1.0:
            opacity_num = opacity_num * 100.0
        opacity_num = max(0.0, min(100.0, opacity_num))
    except (ValueError, TypeError):
        opacity_num = 65.0

    overlay_alpha = round(opacity_num / 100.0, 3)

    # Append cache-busting timestamp query parameter so browsers/CDNs always fetch updated images
    resolved_bg_url = resolved_bg
    if resolved_bg and os.path.exists(resolved_bg):
        try:
            mtime = int(os.path.getmtime(resolved_bg))
            resolved_bg_url = f"{resolved_bg}?v={mtime}"
        except OSError:
            pass

    bg_img_html = f'<div class="site-bg-image" style="background-image: url(\'{resolved_bg_url}\');"></div>' if resolved_bg else ''
    bg_overlay_html = f'<div class="site-bg-overlay" style="opacity: {overlay_alpha};"></div>' if resolved_bg else ''

    return bg_img_html, bg_overlay_html, resolved_bg_url, overlay_alpha

def get_tracking_tags():
    """
    Resolves Google Analytics (GA4) ID and Google Tag Manager (GTM) ID
    from siteConfig.json, config.json, or pages/01_home/content.json.
    Returns (head_tracking_html, body_tracking_html).
    """
    ga_id = None
    gtm_id = None

    for cand_file in ["tools/siteConfig.json", "siteConfig.json", "config.json", "pages/01_home/content.json"]:
        if os.path.exists(cand_file):
            try:
                with open(cand_file, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    if not ga_id:
                        val = (
                            d.get("googleAnalyticsId")
                            or d.get("gaId")
                            or d.get("analyticsId")
                            or d.get("googleAnalytics")
                            or d.get("ga_id")
                        )
                        if val and isinstance(val, str) and val.strip():
                            ga_id = val.strip()
                    if not gtm_id:
                        val = (
                            d.get("googleTagManagerId")
                            or d.get("gtmId")
                            or d.get("tagManagerId")
                            or d.get("googleTagManager")
                            or d.get("gtm_id")
                        )
                        if val and isinstance(val, str) and val.strip():
                            gtm_id = val.strip()
            except Exception:
                pass

    if not ga_id:
        ga_id = "G-PTGZPG59ZS"
    if not gtm_id:
        gtm_id = "GTM-WZLPRH6G"

    head_snippets = []
    body_snippets = []

    # 1. Google Tag Manager (Script in <head> and noscript in <body>)
    if gtm_id and gtm_id != "GTM-XXXXXXXX":
        head_snippets.append(f'''  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
  new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
  j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
  'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
  }})(window,document,'script','dataLayer','{gtm_id}');</script>
  <!-- End Google Tag Manager -->''')

        body_snippets.append(f'''  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id={gtm_id}"
  height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <!-- End Google Tag Manager (noscript) -->''')

    # 2. Google Analytics 4 (gtag.js script in <head>)
    if ga_id and ga_id != "G-XXXXXXXXXX":
        head_snippets.append(f'''  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());

    gtag('config', '{ga_id}');
  </script>''')

    head_html = "\n".join(head_snippets)
    body_html = "\n".join(body_snippets)
    return head_html, body_html

def get_google_analytics_tag():
    head_html, _ = get_tracking_tags()
    return head_html

def get_seo_meta_tags(page_url, page_title, page_desc, is_private=False, image_url=None):
    """
    Generates standard SEO meta tags, Open Graph tags, Twitter Card tags, and canonical link.
    If is_private=True, sets robots to noindex, nofollow, noarchive and omits canonical/OG.
    """
    site_url = "https://pbhat99.github.io"
    for cand_file in ["tools/siteConfig.json", "siteConfig.json", "config.json"]:
        if os.path.exists(cand_file):
            try:
                with open(cand_file, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    val = d.get("siteUrl") or d.get("url")
                    if val and isinstance(val, str) and val.strip():
                        site_url = val.strip().rstrip('/')
            except Exception:
                pass

    if is_private:
        return '''  <!-- SEO: Strictly Private Page (Excluded from Google Indexing) -->
  <meta name="robots" content="noindex, nofollow, noarchive">'''

    canonical_url = f"{site_url}/{page_url}" if page_url else site_url
    if not image_url:
        image_url = f"{site_url}/_engine/images/logo.png"
    elif not image_url.startswith("http"):
        image_url = f"{site_url}/{image_url.lstrip('/')}"

    clean_title = (page_title or "").replace('"', '&quot;').strip()
    clean_desc = (page_desc or "").replace('"', '&quot;').strip()

    return f'''  <!-- SEO & Canonical Link -->
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical_url}">

  <!-- Open Graph / Social Media Sharing (Facebook, LinkedIn, Discord) -->
  <meta property="og:type" content="website">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:title" content="{clean_title}">
  <meta property="og:description" content="{clean_desc}">
  <meta property="og:image" content="{image_url}">

  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{canonical_url}">
  <meta name="twitter:title" content="{clean_title}">
  <meta name="twitter:description" content="{clean_desc}">
  <meta name="twitter:image" content="{image_url}">'''

def generate_sitemap_and_robots():
    """
    Generates robots.txt and sitemap.xml.
    Excludes private pages (/more and /extra) from indexing.
    """
    site_url = "https://pbhat99.github.io"
    for cand_file in ["tools/siteConfig.json", "siteConfig.json", "config.json"]:
        if os.path.exists(cand_file):
            try:
                with open(cand_file, "r", encoding="utf-8") as f:
                    d = json.load(f)
                    val = d.get("siteUrl") or d.get("url")
                    if val and isinstance(val, str) and val.strip():
                        site_url = val.strip().rstrip('/')
            except Exception:
                pass

    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # 1. robots.txt
    robots_content = f"""# robots.txt for Pra - Motions ({site_url})
User-agent: *
Allow: /

# Private / Utility Pages (Excluded from Google Indexing)
Disallow: /more
Disallow: /more.html
Disallow: /more/
Disallow: /extra
Disallow: /extra.html
Disallow: /extra/
Disallow: /pages/07_more/
Disallow: /pages/08_extra/

# XML Sitemap
Sitemap: {site_url}/sitemap.xml
"""
    with open("robots.txt", "w", encoding="utf-8") as f:
        f.write(robots_content)
    print("  -> Generated robots.txt (Allows public pages, blocks /more and /extra, links sitemap)")

    # 2. sitemap.xml (Public pages only, strictly excludes more and extra)
    public_entries = [
        ("", "1.0", "weekly"),
        ("vfx.html", "0.9", "weekly"),
        ("ai-comfy.html", "0.8", "monthly"),
        ("photography.html", "0.8", "monthly"),
        ("about.html", "0.8", "monthly"),
        ("blog.html", "0.8", "weekly"),
    ]

    urls_xml = []
    for rel_path, priority, freq in public_entries:
        loc = f"{site_url}/{rel_path}" if rel_path else f"{site_url}/"
        urls_xml.append(f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{priority}</priority>
  </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"\n".join(urls_xml)}
</urlset>
"""
    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_content)
    print("  -> Generated sitemap.xml (All 6 public pages listed, /more and /extra excluded)")

def hex_to_rgba(hex_str, opacity_val=100):
    """Converts a hex string like #0e1733 and opacity (0-100 or 0.0-1.0) to rgba(...)"""
    if not hex_str:
        return "rgba(14, 23, 51, 0.85)"
    s = hex_str.strip().lstrip('#')
    if len(s) == 3:
        s = ''.join([c*2 for c in s])
    try:
        r = int(s[0:2], 16)
        g = int(s[2:4], 16)
        b = int(s[4:6], 16)
    except Exception:
        return "rgba(14, 23, 51, 0.85)"
    try:
        op = float(opacity_val)
        if op > 1.0:
            op = op / 100.0
        op = max(0.0, min(1.0, op))
    except Exception:
        op = 0.85
    return f"rgba({r}, {g}, {b}, {op:.2f})"

def generate_nav_html(active_page="home"):
    """
    Renders the unified transparent header with clean 6-item navigation (VFX instead of VFX Works, NO contact button).
    """
    nav_items = [
        ("index.html", "home", "Home"),
        ("vfx.html", "vfx", "VFX"),
        ("ai-comfy.html", "ai-comfy", "AI / Comfy"),
        ("photography.html", "photography", "Photography"),
        ("about.html", "about", "About"),
        ("blog.html", "blog", "Blog"),
    ]

    links_html = []
    for href, key, label in nav_items:
        active_cls = ' class="active"' if key == active_page else ''
        links_html.append(f'<li><a href="{href}"{active_cls}>{label}</a></li>')

    return f'''  <header class="site-header">
    <div class="nav-wrapper">
      <a href="index.html" class="brand-logo">
        <img src="_engine/images/logo.png" alt="Pra Motions Logo" width="34" height="34" style="border-radius: 6px;">
        <span>Pra - <span class="brand-badge">Motions</span></span>
      </a>

      <button class="mobile-nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>

      <ul class="nav-links">
        {"".join(links_html)}
      </ul>
    </div>
  </header>'''

BACK_TO_TOP_HTML = '''  <!-- Jump to Top Floating Button (Visible past 1 screen height) -->
  <button id="back-to-top" class="back-to-top" aria-label="Jump to top" title="Jump to top">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="18 15 12 9 6 15"></polyline>
    </svg>
  </button>'''

def convert_all_pages_images_to_webp(root_dir="pages"):
    """
    Site-wide WebP conversion:
    Scans root_dir (default 'pages/').
    Converts any non-webp source image (.jpg, .jpeg, .png, .avif, .gif, .bmp, .tiff)
    to optimized .webp:
    - Maintains original dimensions.
    - Preserves alpha transparency for RGBA/palette images.
    - Quality: 90 for alpha, 85 for RGB.
    - Replaces the original image file (removes source file).
    - Automatically updates references in .json and .md files under root_dir.
    """
    if not os.path.exists(root_dir):
        return

    from PIL import Image
    valid_exts = {'.jpg', '.jpeg', '.png', '.avif', '.gif', '.bmp', '.tiff'}
    replacements = {}

    # 1. Walk root_dir and convert non-webp images
    for current_root, dirs, files in os.walk(root_dir):
        # Preserve original files in forDownload directories
        if "fordownload" in current_root.replace("\\", "/").lower():
            continue
        for f in files:
            if f.startswith('.'):
                continue
            base, ext = os.path.splitext(f)
            ext_lower = ext.lower()
            if ext_lower in valid_exts:
                src_path = os.path.join(current_root, f)
                webp_path = os.path.join(current_root, f"{base}.webp")
                try:
                    with Image.open(src_path) as im:
                        if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
                            im_conv = im.convert('RGBA')
                            im_conv.save(webp_path, 'WEBP', quality=90, method=6)
                        else:
                            im_conv = im.convert('RGB')
                            im_conv.save(webp_path, 'WEBP', quality=85, method=6)
                    
                    if os.path.exists(src_path):
                        try:
                            os.remove(src_path)
                        except OSError as rm_err:
                            if os.path.exists(src_path):
                                print(f"  [Warning] Could not remove {src_path}: {rm_err}")
                    
                    replacements[f] = f"{base}.webp"
                    print(f"  [Site WebP] Converted & replaced: {src_path} -> {base}.webp")
                except Exception as err:
                    print(f"  [WebP Error] {src_path}: {err}")

    # 2. Update references in .json and .md files under root_dir
    if replacements:
        for current_root, dirs, files in os.walk(root_dir):
            for f in files:
                if f.lower().endswith(('.json', '.md')):
                    file_path = os.path.join(current_root, f)
                    try:
                        with open(file_path, "r", encoding="utf-8") as rf:
                            content = rf.read()
                        new_content = content
                        for old_name, new_name in replacements.items():
                            if old_name in new_content:
                                new_content = new_content.replace(old_name, new_name)
                        if new_content != content:
                            with open(file_path, "w", encoding="utf-8") as wf:
                                wf.write(new_content)
                            print(f"  [Ref Update] Updated references in {file_path}")
                    except Exception as ref_err:
                        print(f"  [Ref Update Error] {file_path}: {ref_err}")

def sync_all(convert_webp=False):
    print("=== Syncing site (Site-wide WebP, VFX company structure, Proportional Backgrounds) ===")
    if convert_webp:
        print("  -> [WebP Optimization] Converting source images across pages/ to WebP...")
        convert_all_pages_images_to_webp("pages")

    ga_head_tag, ga_body_tag = get_tracking_tags()
    ga_tag = ga_head_tag

    json_ld_person = '''  <!-- Structured Data (JSON-LD) for Google Rich Results -->
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "Person",
    "name": "Prasannakumar T Bhat",
    "jobTitle": "Visual Effects Compositor",
    "url": "https://pbhat99.github.io",
    "image": "https://pbhat99.github.io/_engine/images/logo.png",
    "sameAs": [
      "https://github.com/pbhat99",
      "https://www.imdb.com/name/nm9329447/",
      "https://www.linkedin.com/in/pbhat99",
      "https://vimeo.com/662339422"
    ]
  }
  </script>'''

    # --------------------------------------------------------------------------
    # 1. SYNC HOME PAGE (pages/01_home)
    # --------------------------------------------------------------------------
    home_dir = "pages/01_home"
    content_file = os.path.join(home_dir, "content.json")
    
    home_data = {
        "designation": "Senior Visual Effects Compositor @ DNEG",
        "tagline": "CG is not just faking, its adding beautiful layers of lie on the ugly truth.",
        "overlayOpacity": 60
    }
    if os.path.exists(content_file):
        try:
            with open(content_file, "r", encoding="utf-8") as f:
                home_data.update(json.load(f))
        except Exception as e:
            print(f"Notice reading {content_file}: {e}")

    fixed_name = "Prasannakumar T Bhat"
    designation = home_data.get("designation", "").strip()
    tagline = home_data.get("tagline", "").strip()

    _, _, home_bg_path, home_alpha = get_page_background_and_overlay(home_dir)

    designation_html = f'<p class="hero-designation-plain">{designation}</p>' if designation else ""
    tagline_html = f'<p class="hero-tagline-plain">"{tagline}"</p>' if tagline else ""

    home_bg_img_html = f'<div class="home-bg-image" style="background-image: url(\'{home_bg_path}\');"></div>' if home_bg_path else ''
    home_bg_overlay_html = f'<div class="home-bg-overlay" style="opacity: {home_alpha};"></div>' if home_bg_path else ''

    home_desc = f"{fixed_name} - {designation}. {tagline}".strip()
    home_seo_meta = get_seo_meta_tags("", f"{fixed_name} | Visual Effects Compositor", home_desc)

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{fixed_name}</title>
  <meta name="description" content="{fixed_name} - {designation}">
{home_seo_meta}
{json_ld_person}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  
  <!-- Ubuntu Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/glightbox.min.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  
  <style>
    /* Full-Page Fixed Non-Scrollable Viewport */
    html, body {{
      margin: 0;
      padding: 0;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      position: fixed;
      inset: 0;
      background-color: var(--bg-primary);
      font-family: 'Ubuntu', sans-serif;
    }}

    /* Seamless Navigation: No borders, no lines, no background */
    .site-header {{
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      z-index: 100;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}

    .home-fullscreen-container {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding-inline: 24px;
      background-color: var(--bg-primary);
      overflow: hidden;
    }}

    /* Non-stretching, automatic proportional fit */
    .home-bg-image {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      background-size: cover;
      background-position: center center;
      background-repeat: no-repeat;
      z-index: 0;
      pointer-events: none;
    }}

    /* Controlled Overlay Layer: opacity 0 = full image, 100 = solid background */
    .home-bg-overlay {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      background-color: var(--bg-primary);
      z-index: 1;
      pointer-events: none;
      transition: opacity 0.3s ease;
    }}

    #bg-canvas {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 2;
    }}

    /* Center Stage: Stacked 3 Lines, Perfectly Centered */
    .home-center-stage {{
      position: relative;
      z-index: 10;
      max-width: 900px;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      text-align: center;
      gap: 16px;
    }}

    /* 1st Line: Fixed Name */
    .hero-name-main {{
      font-family: 'Ubuntu', sans-serif;
      font-size: clamp(2.4rem, 5.5vw, 4.4rem);
      font-weight: 700;
      color: var(--text-main);
      letter-spacing: -0.02em;
      line-height: 1.1;
      margin: 0;
      text-shadow: 0 0 45px rgba(249, 134, 3, 0.25);
    }}

    /* 2nd Line: Designation (Pure text, no box or outline) */
    .hero-designation-plain {{
      font-family: 'Ubuntu', sans-serif;
      font-size: clamp(1.05rem, 2vw, 1.45rem);
      font-weight: 500;
      color: var(--accent-primary);
      letter-spacing: 0.05em;
      margin: 0;
      line-height: 1.3;
    }}

    /* 3rd Line: Tagline (Pure text, off-white italic) */
    .hero-tagline-plain {{
      font-family: 'Ubuntu', sans-serif;
      font-size: clamp(0.95rem, 1.6vw, 1.25rem);
      font-weight: 400;
      font-style: italic;
      color: var(--text-muted);
      max-width: 740px;
      margin: 0;
      line-height: 1.5;
    }}

    .hero-about-wrap {{
      margin-top: 24px;
    }}

    .btn-about {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 11px 40px;
      font-size: 0.95rem;
      font-weight: 500;
      font-family: 'Ubuntu', sans-serif;
      border-radius: var(--radius-full);
      background: var(--accent-primary);
      color: #ffffff;
      box-shadow: 0 4px 18px rgba(249, 134, 3, 0.4);
      transition: all var(--transition-fast);
      letter-spacing: 0.02em;
    }}

    .btn-about:hover {{
      background: var(--accent-hover);
      transform: translateY(-2px);
      box-shadow: 0 6px 25px rgba(249, 134, 3, 0.55);
    }}
  </style>
</head>
<body>
{ga_body_tag}

{generate_nav_html("home")}

  <!-- Full-Screen Interactive Viewport -->
  <main class="home-fullscreen-container">
    {home_bg_img_html}
    {home_bg_overlay_html}

    <!-- Interactive Canvas Background -->
    <canvas id="bg-canvas"></canvas>

    <!-- Center Stage: 3 Lines Centered + About Button -->
    <div class="home-center-stage">
      <h1 class="hero-name-main">{fixed_name}</h1>
      {designation_html}
      {tagline_html}

      <div class="hero-about-wrap">
        <a href="about-me.html" class="btn-about">About</a>
      </div>
    </div>
  </main>

  <script type="module">
    import {{ initInteractiveBackground }} from './_engine/js/interactive-bg.js';
    import './_engine/js/main.js';
    initInteractiveBackground('bg-canvas');

    // Live sync overlay opacity if content.json is edited
    fetch('pages/01_home/content.json')
      .then(r => r.json())
      .then(d => {{
        const raw = d.overlayOpacity ?? d.bgOverlayOpacity ?? d.opacity;
        if (raw !== undefined) {{
          let num = parseFloat(raw);
          if (num > 1) num = num / 100;
          const overlay = document.querySelector('.home-bg-overlay');
          if (overlay) overlay.style.opacity = Math.max(0, Math.min(1, num));
        }}
      }}).catch(() => {{}});
  </script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("  -> Updated index.html (Nav: VFX, Proportional Background)")

    # --------------------------------------------------------------------------
    # 2. SYNC VFX PAGE (pages/02_VFX -> vfx.html)
    # --------------------------------------------------------------------------
    vfx_dir = "pages/02_VFX"
    content_file = os.path.join(vfx_dir, "content.json")

    vfx_content = {
        "title": "Visual Effects & Compositing",
        "description": "Production shots, feature film breakdowns, and commercials across world-class visual effects studios."
    }
    if os.path.exists(content_file):
        try:
            with open(content_file, "r", encoding="utf-8") as f:
                vfx_content.update(json.load(f))
        except Exception:
            pass

    vfx_title = vfx_content.get('title', 'Visual Effects & Compositing')
    vfx_desc = vfx_content.get('description', '')
    vfx_title_inner = vfx_title.strip() if vfx_title else '&nbsp;'
    vfx_desc_inner = vfx_desc.strip() if vfx_desc else '&nbsp;'

    vfx_bg_img_html, vfx_bg_overlay_html, _, _ = get_page_background_and_overlay(vfx_dir)

    company_subdirs = sorted([d for d in os.listdir(vfx_dir) if os.path.isdir(os.path.join(vfx_dir, d)) and not d.startswith('.')], reverse=True) if os.path.exists(vfx_dir) else []
    
    company_sections_html = []
    total_projects_count = 0
    all_categories = set()
    valid_img_exts = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'}

    for comp_folder in company_subdirs:
        comp_path = os.path.join(vfx_dir, comp_folder)
        comp_slug = slugify(comp_folder)

        # 1. Company Info
        comp_info = {
            "companyName": format_title_from_filename(comp_folder),
            "period": "Aug-2021 to Present",
            "designation": "",
            "description": "",
            "color": "#0e1733",
            "cardBgColor": "#131e42",
            "cardBgOpacity": 85,
            "link": ""
        }
        comp_info_file = os.path.join(comp_path, "companyInfo.json")
        if not os.path.exists(comp_info_file):
            comp_info_file = os.path.join(comp_path, "company.json")
        if os.path.exists(comp_info_file):
            try:
                with open(comp_info_file, "r", encoding="utf-8") as f:
                    comp_info.update(json.load(f))
            except Exception:
                pass

        company_name = comp_info.get("companyName") or comp_info.get("name") or format_title_from_filename(comp_folder)
        comp_period = comp_info.get("period", "")
        comp_designation = comp_info.get("designation", "")
        comp_description = comp_info.get("description", "")
        comp_color = comp_info.get("color", "#0e1733")
        comp_link = (comp_info.get("link") or "").strip()
        card_bg_color = comp_info.get("cardBgColor", "#131e42")
        card_bg_opacity = comp_info.get("cardBgOpacity", 85)
        tile_bg_rgba = hex_to_rgba(card_bg_color, card_bg_opacity)

        # 2. Company Banner Logo (right edge fit)
        banner_path = None
        for f in os.listdir(comp_path):
            if os.path.isfile(os.path.join(comp_path, f)) and os.path.splitext(f)[1].lower() in valid_img_exts:
                if 'banner' in f.lower() or 'logo' in f.lower():
                    banner_path = f"{comp_path}/{f}".replace("\\", "/")
                    break

        # 3. Project Folders inside Company
        proj_subdirs = [d for d in os.listdir(comp_path) if os.path.isdir(os.path.join(comp_path, d)) and not d.startswith('.')]
        
        # Sort project folders in descending order as requested
        proj_subdirs.sort(reverse=True)

        tiles_html = []
        for p_folder in proj_subdirs:
            p_folder_path = os.path.join(comp_path, p_folder)
            
            # Find project image (projectImage.jpg / thumb.* / first image)
            proj_img_path = None
            for f in os.listdir(p_folder_path):
                if os.path.splitext(f)[1].lower() in valid_img_exts:
                    if 'projectimage' in f.lower() or 'thumb' in f.lower() or 'image' in f.lower():
                        proj_img_path = f"{p_folder_path}/{f}".replace("\\", "/")
                        break
            if not proj_img_path:
                for f in os.listdir(p_folder_path):
                    if os.path.splitext(f)[1].lower() in valid_img_exts:
                        proj_img_path = f"{p_folder_path}/{f}".replace("\\", "/")
                        break

            if not proj_img_path:
                continue

            # Read projectInfo.json
            proj_info = {
                "title": format_title_from_filename(p_folder),
                "description": "",
                "category": "commercials",
                "year": "",
                "tags": [],
                "orientation": "horizontal",
                "link": ""
            }
            proj_info_file = os.path.join(p_folder_path, "projectInfo.json")
            if not os.path.exists(proj_info_file):
                proj_info_file = os.path.join(p_folder_path, "info.json")
            if os.path.exists(proj_info_file):
                try:
                    with open(proj_info_file, "r", encoding="utf-8") as f:
                        proj_info.update(json.load(f))
                except Exception:
                    pass

            p_title = proj_info.get("title") or format_title_from_filename(p_folder)
            p_desc = proj_info.get("description", "")
            p_category = (proj_info.get("category") or "commercials").strip().lower()
            all_categories.add(p_category)
            p_year = proj_info.get("year", "")
            p_orientation = proj_info.get("orientation", "horizontal").lower()
            if p_orientation not in ("horizontal", "vertical", "square"):
                p_orientation = "horizontal"

            p_link = (proj_info.get("link") or "").strip()
            more_link_html = f'<a href="{p_link}" target="_blank" rel="noopener noreferrer" class="tile-more-link" title="Open project details in new tab">more...</a>' if p_link else ''

            # Tags processing
            raw_tags = proj_info.get("tags") or proj_info.get("tools") or []
            if isinstance(raw_tags, str):
                p_tags = [t.strip() for t in raw_tags.split(",") if t.strip()]
            else:
                p_tags = [str(t).strip() for t in raw_tags if str(t).strip()]

            cat_label = "Commercial"
            if p_category == "films": cat_label = "Feature Film"
            elif p_category == "music-videos": cat_label = "Music Video"
            elif p_category == "other": cat_label = "Other"
            else: cat_label = p_category.replace('-', ' ').replace('_', ' ').title()

            year_span = f'<span class="tile-year">{p_year}</span>' if p_year else ''
            desc_html = f'<p class="tile-desc">{p_desc}</p>' if p_desc else ''
            
            tags_csv = ",".join(p_tags)
            tags_buttons = "".join([f'<button class="tile-tag" data-tag="{t}">{t}</button>' for t in p_tags])
            tags_html = f'<div class="tile-tags-wrap">{tags_buttons}</div>' if p_tags else ''

            tiles_html.append(f'''
            <article class="project-tile aspect-{p_orientation}" data-category="{p_category}" data-tags="{tags_csv}">
              <div class="tile-circling-border" aria-hidden="true"></div>
              <div class="tile-inner">
                <img src="{proj_img_path}" alt="{p_title}" class="tile-img" loading="lazy">
                <button class="tile-category-pill" data-filter-category="{p_category}" title="Filter by {cat_label}">{cat_label}</button>
                {more_link_html}
                <div class="tile-hover-overlay">
                  <div class="tile-hover-content">
                    <h3 class="tile-title">
                      <span>{p_title}</span>
                      {year_span}
                    </h3>
                    {desc_html}
                    {tags_html}
                  </div>
                </div>
              </div>
            </article>''')
            total_projects_count += 1

        # Company Banner HTML (Reduced Height Strip with Right-Edge Flush Logo)
        meta_items = []
        if comp_period:
            meta_items.append(f'<span class="company-banner-period">{comp_period}</span>')
        if comp_designation:
            meta_items.append(f'<span class="company-banner-designation">{comp_designation}</span>')

        meta_html = f'<div class="company-banner-meta">{"<span class=\"company-banner-sep\"> - </span>".join(meta_items)}</div>' if meta_items else ''
        description_html = f'<div class="company-banner-desc">{comp_description}</div>' if comp_description else ''

        if banner_path:
            if comp_link:
                logo_html = f'''
        <a href="{comp_link}" target="_blank" rel="noopener noreferrer" class="company-banner-logo-wrap is-clickable" title="Visit {company_name}">
          <img src="{banner_path}" alt="{company_name} Logo" class="company-banner-logo-img">
        </a>'''
            else:
                logo_html = f'''
        <div class="company-banner-logo-wrap">
          <img src="{banner_path}" alt="{company_name} Logo" class="company-banner-logo-img">
        </div>'''
        else:
            logo_html = ''

        company_banner_html = f'''
        <div class="company-banner-strip" style="background-color: {comp_color};">
          <div class="company-banner-info">
            <h2 class="company-banner-heading">{company_name}</h2>
            {meta_html}
            {description_html}
          </div>
          {logo_html}
        </div>'''

        company_sections_html.append(f'''
        <section class="company-section" id="{comp_slug}" data-company="{comp_slug}">
          {company_banner_html}
          <div class="portfolio-grid company-project-grid" style="--tile-bg: {tile_bg_rgba};">
            {"".join(tiles_html)}
          </div>
        </section>''')

    # Dynamic Category Filter Pills (Ordered with 'All' first without count)
    CATEGORY_LABELS = {
        "commercials": "Commercials",
        "films": "Feature Films",
        "music-videos": "Music Videos",
        "other": "Other"
    }

    preferred_order = ["commercials", "films", "music-videos", "other"]
    sorted_categories = []
    for c in preferred_order:
        if c in all_categories:
            sorted_categories.append(c)
    for c in sorted(all_categories):
        if c not in sorted_categories:
            sorted_categories.append(c)

    filter_buttons_html = ['<button class="filter-btn active" data-filter="all">All</button>']
    for cat in sorted_categories:
        label = CATEGORY_LABELS.get(cat, cat.replace('-', ' ').replace('_', ' ').title())
        filter_buttons_html.append(f'<button class="filter-btn" data-filter="{cat}">{label}</button>')

    vfx_seo_meta = get_seo_meta_tags(
        "vfx.html",
        "Visual Effects & Compositing | Pra - Motions",
        "Visual Effects & Compositing portfolio of Prasannakumar T Bhat across DNEG, The Mill, and feature film productions."
    )

    vfx_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VFX | Pra - Motions</title>
  <meta name="description" content="Visual Effects & Compositing portfolio of Prasannakumar T Bhat across DNEG, The Mill, and feature film productions.">
{vfx_seo_meta}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/glightbox.min.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
{ga_body_tag}
  {vfx_bg_img_html}
  {vfx_bg_overlay_html}

{generate_nav_html("vfx")}

  <main style="padding-block: clamp(24px, 4vw, 56px);">
    <div class="container-wide">
      <div class="section-header">
        <h1 class="section-title">{vfx_title_inner}</h1>
        <p class="section-desc">{vfx_desc_inner}</p>
      </div>

      <!-- Filter Controls: Dynamic Categories (No count on 'All', dynamically appends any added category) -->
      <div class="filter-bar filter-bar-center">
        {"".join(filter_buttons_html)}
        <span class="tag-filter-status" style="display: none;"></span>
      </div>

      <!-- Company Sections with Banners & Project Grids -->
      <div class="vfx-companies-container">
        {"".join(company_sections_html)}
      </div>
    </div>
  </main>

  <script src="_engine/js/glightbox.min.js"></script>
  <script type="module" src="_engine/js/lightbox.js"></script>
  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("vfx.html", "w", encoding="utf-8") as f:
        f.write(vfx_html)
    print(f"  -> Updated vfx.html ({len(company_subdirs)} companies, {total_projects_count} projects, auto-sorted descending)")

    # --------------------------------------------------------------------------
    # 3. SYNC PHOTOGRAPHY (pages/04_photography -> photos/ and panos/)
    # --------------------------------------------------------------------------
    photo_dir = "pages/04_photography"
    photos_dir = os.path.join(photo_dir, "photos")
    panos_dir = os.path.join(photo_dir, "panos")
    os.makedirs(photos_dir, exist_ok=True)
    os.makedirs(panos_dir, exist_ok=True)
    photo_bg_img_html, photo_bg_overlay_html, _, _ = get_page_background_and_overlay(photo_dir)

    # Read Photography content.json if present
    photo_page_info = {
        "title": "Photography & Panoramas",
        "description": "High-resolution 360° environment captures, HDRI light probes, and cinematic stills gallery."
    }
    photo_content_json = os.path.join(photo_dir, "content.json")
    if os.path.exists(photo_content_json):
        try:
            with open(photo_content_json, "r", encoding="utf-8") as f:
                photo_page_info.update(json.load(f))
        except Exception:
            pass

    photo_title = photo_page_info.get("title", "Photography & Panoramas")
    photo_desc = photo_page_info.get("description", "")
    photo_title_inner = photo_title.strip() if photo_title else '&nbsp;'
    photo_desc_inner = photo_desc.strip() if photo_desc else '&nbsp;'

    def clean_photo_title(filename):
        name_no_ext = os.path.splitext(filename)[0]
        # Remove leading numbers and separators e.g. 001_, 01 -, etc.
        clean = re.sub(r'^\d+[\s_-]*', '', name_no_ext)
        clean = clean.replace('_', ' ').replace('-', ' ')
        clean = ' '.join(clean.split())
        return clean.strip() or name_no_ext

    def process_photo_collection(dir_path):
        if not os.path.exists(dir_path):
            return []

        # 1. Convert any non-webp source image to webp and replace original file
        if convert_webp:
            from PIL import Image
            for fname in os.listdir(dir_path):
                if fname.startswith('.'):
                    continue
                base, ext = os.path.splitext(fname)
                ext_lower = ext.lower()
                if ext_lower in ('.jpg', '.jpeg', '.png', '.avif', '.gif', '.bmp', '.tiff'):
                    src_path = os.path.join(dir_path, fname)
                    webp_path = os.path.join(dir_path, f"{base}.webp")
                    try:
                        with Image.open(src_path) as im:
                            if im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info):
                                im_conv = im.convert('RGBA')
                                im_conv.save(webp_path, 'WEBP', quality=90, method=6)
                            else:
                                im_conv = im.convert('RGB')
                                im_conv.save(webp_path, 'WEBP', quality=85, method=6)
                        print(f"  [WebP Conversion] Replaced {fname} -> {base}.webp")
                        try:
                            os.remove(src_path)
                        except OSError as rm_err:
                            print(f"  [Warning] Could not remove original {src_path}: {rm_err}")
                    except Exception as err:
                        print(f"  [WebP Error] {src_path}: {err}")

        # 2. Read and index all .webp files
        from PIL import Image
        webp_files = sorted([f for f in os.listdir(dir_path) if f.lower().endswith('.webp') and not f.startswith('.')])
        items = []
        for f in webp_files:
            base, _ = os.path.splitext(f)
            webp_path = os.path.join(dir_path, f)
            w, h, aspect = 1920, 1080, 1.778
            try:
                with Image.open(webp_path) as im:
                    w, h = im.size
                    aspect = round(w / h, 3)
            except Exception:
                pass

            items.append({
                "id": slugify(base),
                "filename": f,
                "title": clean_photo_title(f),
                "webp": webp_path.replace("\\", "/"),
                "width": w,
                "height": h,
                "aspect": aspect
            })
        return items

    # Convert photography background.jpg to background.webp if present and delete original
    photo_bg_jpg = os.path.join(photo_dir, "background.jpg")
    photo_bg_webp = os.path.join(photo_dir, "background.webp")
    if convert_webp and os.path.exists(photo_bg_jpg):
        try:
            from PIL import Image
            with Image.open(photo_bg_jpg) as im:
                im.convert('RGB').save(photo_bg_webp, 'WEBP', quality=85, method=6)
            os.remove(photo_bg_jpg)
            print("  [WebP] Converted & replaced photography background.jpg -> background.webp")
        except Exception as bg_err:
            print(f"  [WebP Error] {photo_bg_jpg}: {bg_err}")

    photos_list = process_photo_collection(photos_dir)
    panos_list = process_photo_collection(panos_dir)

    photos_json_str = json.dumps(photos_list)
    panos_json_str = json.dumps(panos_list)

    def get_mondrian_class(idx, aspect):
        if aspect <= 0.82:
            return "mondrian-tall"
        elif aspect >= 1.6 and (idx % 2 == 1 or idx == 0):
            return "mondrian-wide"
        elif aspect >= 1.9:
            return "mondrian-wide"
        else:
            return "mondrian-standard"

    # 1. Normal Photos HTML (Mondrian Style Mosaic Grid with 3-5 images horizontally)
    photo_tiles_html = []
    for idx, p in enumerate(photos_list):
        m_class = get_mondrian_class(idx, p['aspect'])
        photo_tiles_html.append(f'''
        <div class="photo-mondrian-item {m_class}">
          <article class="project-tile photo-tile" onclick="openPhotoViewer({idx})" title="{p['title']}">
            <div class="tile-circling-border" aria-hidden="true"></div>
            <div class="tile-inner">
              <img src="{p['webp']}" alt="{p['title']}" class="tile-img" loading="lazy">
              <div class="tile-hover-overlay">
                <div class="tile-hover-content">
                  <h3 class="tile-title">
                    <span>{p['title']}</span>
                  </h3>
                </div>
              </div>
            </div>
          </article>
        </div>''')

    # 2. 360 Panoramas HTML (2:1 images 2 per row)
    pano_tiles_html = []
    for idx, p in enumerate(panos_list):
        pano_tiles_html.append(f'''
        <article class="project-tile pano-tile" onclick="openPanoViewer({idx})" title="{p['title']}">
          <div class="tile-circling-border" aria-hidden="true"></div>
          <div class="tile-inner">
            <img src="{p['webp']}" alt="{p['title']}" class="tile-img" loading="lazy">
            <span class="pano-badge">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
              360° Panorama
            </span>
            <div class="pano-center-indicator" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" style="margin-left: 2px;"><polygon points="6 3 20 12 6 21 6 3"/></svg>
            </div>
            <div class="tile-hover-overlay">
              <div class="tile-hover-content">
                <h3 class="tile-title">
                  <span>{p['title']}</span>
                </h3>
              </div>
            </div>
          </div>
        </article>''')

    photo_seo_meta = get_seo_meta_tags(
        "photography.html",
        f"{photo_title} | Pra - Motions",
        photo_desc or "Photography and 360 interactive panoramas by Prasannakumar T Bhat."
    )

    photography_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{photo_title} | Pra - Motions</title>
{photo_seo_meta}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/pannellum.css">
  <link rel="stylesheet" href="_engine/css/photography.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
{ga_body_tag}
  {photo_bg_img_html}
  {photo_bg_overlay_html}

{generate_nav_html("photography")}

  <main style="padding-block: clamp(24px, 4vw, 56px);">
    <div class="container-wide">
      <div class="section-header">
        <h1 class="section-title">{photo_title_inner}</h1>
        <p class="section-desc">{photo_desc_inner}</p>
      </div>

      <!-- Gallery Filter Tabs (1st: 360 Panos, 2nd: Photos) -->
      <div class="gallery-tab-bar">
        <button type="button" class="gallery-tab-btn active" id="tabBtnPanos" data-tab="panos" onclick="switchGalleryTab('panos')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
          <span>360° Panoramas</span>
          <span class="tab-pill-count">{len(panos_list)}</span>
        </button>

        <button type="button" class="gallery-tab-btn" id="tabBtnPhotos" data-tab="photos" onclick="switchGalleryTab('photos')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
          <span>Photos</span>
          <span class="tab-pill-count">{len(photos_list)}</span>
        </button>
      </div>

      <!-- TAB 1: 360° PANORAMA ENVIRONMENTS (Active by default, 2:1 Grid 2 per Row) -->
      <section class="photo-gallery-section" id="panos-section">
        <div class="gallery-section-heading">
          <h2 class="gallery-section-title">
            <span>360° Panoramic Environments</span>
            <span class="gallery-section-count">{len(panos_list)}</span>
          </h2>
        </div>

        <div class="pano-grid">
          {"".join(pano_tiles_html)}
        </div>
      </section>

      <!-- TAB 2: STILLS & PHOTOS (Mondrian Grid 3-5 Horizontally) -->
      <section class="photo-gallery-section" id="photos-section" style="display: none;">
        <div class="gallery-section-heading">
          <h2 class="gallery-section-title">
            <span>Stills & Photography</span>
            <span class="gallery-section-count">{len(photos_list)}</span>
          </h2>
        </div>

        <div class="photo-mondrian-grid">
          {"".join(photo_tiles_html)}
        </div>
      </section>

    </div>
  </main>

  <!-- Fullscreen Photo Viewer Modal with Bottom Filmstrip -->
  <div id="photoViewerModal" class="fullscreen-viewer-modal" aria-hidden="true" role="dialog">
    <div class="viewer-top-bar">
      <div class="viewer-title-wrap">
        <h3 class="viewer-title" id="photoViewerTitle">Photo</h3>
        <span class="viewer-counter" id="photoViewerCounter">1 / 1</span>
      </div>
      <div class="viewer-top-actions">
        <button type="button" class="viewer-close-btn" id="photoViewerCloseBtn" onclick="closePhotoViewer()" aria-label="Close viewer" title="Close (Esc)">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <div class="viewer-stage" id="photoViewerStage">
      <button type="button" class="viewer-side-arrow viewer-prev-arrow" onclick="navPhotoViewer(-1)" aria-label="Previous photo" title="Previous photo (←)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>

      <div class="viewer-img-container">
        <img id="photoViewerImg" src="" alt="Photo" class="viewer-main-img">
      </div>

      <button type="button" class="viewer-side-arrow viewer-next-arrow" onclick="navPhotoViewer(1)" aria-label="Next photo" title="Next photo (→)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
    </div>

    <div class="viewer-filmstrip-bar">
      <div class="filmstrip-track" id="photoFilmstripTrack"></div>
    </div>
  </div>

  <!-- Fullscreen 360 Panorama Viewer Modal with Bottom Filmstrip -->
  <div id="panoViewerModal" class="fullscreen-viewer-modal" aria-hidden="true" role="dialog">
    <div class="viewer-top-bar">
      <div class="viewer-title-wrap">
        <span class="pano-modal-tag">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
          360° Photosphere
        </span>
        <h3 class="viewer-title" id="panoViewerTitle">Panorama</h3>
        <span class="viewer-counter" id="panoViewerCounter">1 / 1</span>
      </div>
      <div class="viewer-top-actions">
        <button type="button" class="viewer-close-btn" id="panoViewerCloseBtn" onclick="closePanoViewer()" aria-label="Close viewer" title="Close (Esc)">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <div class="pano-stage">
      <div id="fullscreenPanoContainer" class="pano-webgl-viewport"></div>

      <button type="button" class="viewer-side-arrow viewer-prev-arrow" onclick="navPanoViewer(-1)" aria-label="Previous panorama" title="Previous panorama (←)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
          <polyline points="15 18 9 12 15 6"></polyline>
        </svg>
      </button>

      <button type="button" class="viewer-side-arrow viewer-next-arrow" onclick="navPanoViewer(1)" aria-label="Next panorama" title="Next panorama (→)">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22">
          <polyline points="9 18 15 12 9 6"></polyline>
        </svg>
      </button>
    </div>

    <div class="viewer-filmstrip-bar">
      <div class="filmstrip-track" id="panoFilmstripTrack"></div>
    </div>
  </div>

  <script id="photosData" type="application/json">
{photos_json_str}
  </script>
  <script id="panosData" type="application/json">
{panos_json_str}
  </script>
  <script src="_engine/js/pannellum.js"></script>
  <script src="_engine/js/photography.js"></script>
  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("photography.html", "w", encoding="utf-8") as f:
        f.write(photography_html)
    print(f"  -> Updated photography.html (Nav: Photography, {len(photos_list)} Stills Masonry, {len(panos_list)} 360 Panoramas 2:1)")

    # --------------------------------------------------------------------------
    # 4. SYNC ABOUT PAGE (pages/05_about -> about.html & about-me.html redirect)
    # --------------------------------------------------------------------------
    about_dir = "pages/05_about" if os.path.exists("pages/05_about") else "pages/05_about-me"
    about_bg_img_html, about_bg_overlay_html, _, _ = get_page_background_and_overlay(about_dir)

    about_data = {
        "name": "Prasannakumar T Bhat",
        "designation": "Visual Effects Compositor",
        "experience": "",
        "info": "For <strong>10+ years</strong>, I've been weaving magic with pixels in the world of visual effects. It's thrilling to take raw footage, images, and 3D elements, and mold them into the final image that graces the big screen or TV. Seeing my work come to life is an unparalleled reward!\n\nI'm a relentless explorer, always pushing the boundaries of what's possible with the latest software in <strong>feature films, commercials, and TV projects</strong>.\n\nMy passion for innovation extends beyond the screen. In my spare time, I delve into research, <strong>crafting tools and automating tasks with scripts</strong>. With deep expertise in compositing, I'm currently bringing my vision to life as a <strong>Compositing Artist at DNEG</strong>.",
        "showreelLink": "https://vimeo.com/835414002"
    }

    # Load from content.json (or aboutMe.json fallback)
    for cand_json in ["content.json", "aboutMe.json"]:
        cand_path = os.path.join(about_dir, cand_json)
        if os.path.exists(cand_path):
            try:
                with open(cand_path, "r", encoding="utf-8") as f:
                    about_data.update(json.load(f))
            except Exception:
                pass

    name = about_data.get("name", "Prasannakumar T Bhat")
    designation = about_data.get("designation", "Visual Effects Compositor")
    experience = about_data.get("experience", "")
    info_raw = about_data.get("info", "")
    resume_link = about_data.get("resumeLink") or (f"{about_dir}/resume.pdf" if os.path.exists(f"{about_dir}/resume.pdf") else "#")
    cover_letter_link = about_data.get("coverLetterLink") or (f"{about_dir}/coverLetter.pdf" if os.path.exists(f"{about_dir}/coverLetter.pdf") else "#")
    showreel_title = (
        about_data.get("showreelTitle")
        or about_data.get("showreel title")
        or about_data.get("showreelHeading")
        or about_data.get("videoTitle")
        or ""
    ).strip()
    info_bg_color = about_data.get("infoBGcolor") or about_data.get("infoBgColor") or "#131e42"
    info_bg_opacity = about_data.get("infoBGopacity", about_data.get("infoBgOpacity", about_data.get("info_bg_opacity", 75)))
    info_bg_rgba = hex_to_rgba(info_bg_color, info_bg_opacity)

    showreel_url = (
        about_data.get("showreelLink")
        or about_data.get("showreel link")
        or about_data.get("showreel")
        or about_data.get("showreelUrl")
        or about_data.get("showreel url")
        or about_data.get("vimeoUrl")
        or about_data.get("vimeoLink")
        or about_data.get("vimeo")
        or ""
    ).strip()
    phone = about_data.get("phone", "+91 9449267068")
    email = about_data.get("email", "pbhat99@gmail.com")
    github_link = about_data.get("github", "https://github.com/pbhat99")
    location = about_data.get("location", "Karnataka, India - 581337")

    # Format info paragraphs with line break support (\n\n -> <p>, \n -> <br>)
    info_paras = [p.strip() for p in info_raw.split("\n\n") if p.strip()]
    if not info_paras and info_raw:
        info_paras = [info_raw.strip()]
    paragraphs_html = "\n".join([f"<p>{p.replace(chr(10), '<br>')}</p>" for p in info_paras])

    # Find profile picture (profilePic.webp or fallback)
    profile_img = "_engine/images/logo.png"
    for cand_img in ["profilePic.webp", "profilePic.jpg", "profilePic.png", "profile.webp", "profile.jpg", "profile.png"]:
        p_path = os.path.join(about_dir, cand_img)
        if os.path.exists(p_path):
            profile_img = p_path.replace("\\", "/")
            break

    # Auto-load known tools from knownTools/ folder (single row fitted to overall width)
    known_tools_dir = os.path.join(about_dir, "knownTools")
    tools_cards_html = []
    if os.path.exists(known_tools_dir):
        tool_files = sorted([f for f in os.listdir(known_tools_dir) if os.path.splitext(f)[1].lower() in valid_img_exts])
        for tf in tool_files:
            tf_path = f"{known_tools_dir}/{tf}".replace("\\", "/")
            raw_name = os.path.splitext(tf)[0]
            # Strip numeric prefix like '01_' if present to get clean tool name without extension
            tool_name = re.sub(r'^\d+[\s_-]*', '', raw_name).replace('_', ' ').replace('-', ' ').title()
            tools_cards_html.append(f'''
          <div class="known-tool-card" title="{tool_name}">
            <img src="{tf_path}" alt="{tool_name}" class="known-tool-img" loading="lazy">
            <div class="known-tool-hover">
              <span class="known-tool-name">{tool_name}</span>
            </div>
          </div>''')

    tools_section_html = ""
    if tools_cards_html:
        num_tools = len(tools_cards_html)
        # Dynamically set gap and padding based on number of tools:
        # - Fewer tools (e.g. 3-4) -> larger padding & gap, perfectly centered
        # - More tools (up to 15) -> smaller padding & gap to fit strictly in a single line
        # - Fixed height is 82px (80% of original 10-tool arrangement)
        if num_tools <= 4:
            tool_gap = "clamp(24px, 3.5vw, 42px)"
            tool_pad = "12px"
        elif num_tools <= 7:
            tool_gap = "clamp(16px, 2.2vw, 26px)"
            tool_pad = "9px"
        elif num_tools <= 10:
            tool_gap = "clamp(10px, 1.5vw, 18px)"
            tool_pad = "7px"
        elif num_tools <= 12:
            tool_gap = "clamp(7px, 1.1vw, 13px)"
            tool_pad = "5px"
        else:
            # 13 to 15+ tools: reduced padding to make room for all
            tool_gap = "clamp(4px, 0.8vw, 8px)"
            tool_pad = "4px"

        tools_section_html = f'''
      <section class="known-tools-section">
        <div class="known-tools-strip" style="--tool-count: {num_tools}; --tool-gap: {tool_gap}; --tool-pad: {tool_pad};">
          {"".join(tools_cards_html)}
        </div>
      </section>'''

    # Showreel Video Embed (Vimeo or YouTube)
    showreel_section_html = ""
    if showreel_url:
        embed_src = None
        allow_attr = "autoplay; fullscreen; picture-in-picture"
        
        # Check YouTube
        yt_match = re.search(r'(?:youtube\.com\/(?:watch\?.*?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', showreel_url)
        if yt_match:
            yt_id = yt_match.group(1)
            embed_src = f"https://www.youtube.com/embed/{yt_id}?rel=0"
            allow_attr = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        else:
            # Check Vimeo
            vimeo_match = re.search(r'vimeo\.com\/(?:video\/|channels\/[^\/]+\/|manage\/videos\/)?(\d{6,})', showreel_url)
            if not vimeo_match and "vimeo" in showreel_url.lower():
                vimeo_match = re.search(r'(\d{6,})', showreel_url)
            if vimeo_match:
                vimeo_id = vimeo_match.group(1)
                embed_src = f"https://player.vimeo.com/video/{vimeo_id}?title=0&byline=0&portrait=0"
                allow_attr = "autoplay; fullscreen; picture-in-picture"
            elif "embed" in showreel_url:
                embed_src = showreel_url
                allow_attr = "autoplay; fullscreen; picture-in-picture"

        if embed_src:
            video_header_html = f'''
        <div class="about-video-header">
          <h2 class="about-video-heading">{showreel_title}</h2>
        </div>''' if showreel_title else ""

            showreel_section_html = f'''
      <section class="about-video-card" style="--info-bg: {info_bg_rgba};">
        {video_header_html}
        <div class="about-video-container">
          <iframe src="{embed_src}"
                  allow="{allow_attr}" allowfullscreen
                  title="{showreel_title or 'VFX Showreel'} - {name}"></iframe>
        </div>
      </section>'''

    meta_role = f'{designation}'
    if experience:
        meta_role += f' &bull; {experience}'

    page_title = about_data.get("title", "About Me")
    page_desc = about_data.get("description", "")
    title_inner = page_title.strip() if page_title else '&nbsp;'
    desc_inner = page_desc.strip() if page_desc else '&nbsp;'

    # 1. Contact Info Lines (separate key section in aboutMe.json, one per line, expands height)
    contact_lines_data = (
        about_data.get("contactInfoLines")
        or about_data.get("contactLines")
        or about_data.get("infoLines")
    )
    contact_lines_html = []
    if contact_lines_data and isinstance(contact_lines_data, list):
        for item in contact_lines_data:
            if isinstance(item, dict):
                label = item.get("label") or item.get("key") or ""
                val = str(item.get("value") or item.get("text") or item.get("val") or "")
                link = item.get("link") or item.get("url") or ""
                
                label_html = f'<span class="contact-line-label">{label}:</span>' if label else ''
                if link:
                    val_html = f'<a href="{link}" target="_blank" rel="noopener noreferrer">{val}</a>'
                elif '@' in val and not val.startswith('http'):
                    val_html = f'<a href="mailto:{val}">{val}</a>'
                else:
                    val_html = f'<strong>{val}</strong>' if 'phone' in label.lower() else val
                contact_lines_html.append(f'<div class="contact-line-item">{label_html}<span class="contact-line-val">{val_html}</span></div>')
            elif isinstance(item, str) and item.strip():
                contact_lines_html.append(f'<div class="contact-line-item"><span class="contact-line-val">{item.strip()}</span></div>')

    if not contact_lines_html:
        # Fallback to standard contact info
        if phone:
            contact_lines_html.append(f'<div class="contact-line-item"><span class="contact-line-label">Phone:</span><span class="contact-line-val"><strong>{phone}</strong></span></div>')
        if email:
            contact_lines_html.append(f'<div class="contact-line-item"><span class="contact-line-label">Email:</span><span class="contact-line-val"><a href="mailto:{email}">{email}</a></span></div>')
        if github_link:
            contact_lines_html.append(f'<div class="contact-line-item"><span class="contact-line-label">GitHub:</span><span class="contact-line-val"><a href="{github_link}" target="_blank" rel="noopener">{github_link.replace("https://", "")}</a></span></div>')
        if location:
            contact_lines_html.append(f'<div class="contact-line-item"><span class="contact-line-label">Location:</span><span class="contact-line-val">{location}</span></div>')

    # 2. Right-Aligned Contact Image (Auto-detected from folder: contact.jpg, contact.png, etc.; no JSON key needed)
    contact_img_html = ""
    contact_img_path = None
    for cand in ["contact.webp", "contact.jpg", "contact.png", "contact.jpeg"]:
        p = os.path.join(about_dir, cand)
        if os.path.exists(p):
            contact_img_path = p.replace("\\", "/")
            break

    if contact_img_path:
        contact_img_html = f'''
          <div class="contact-image-wrap">
            <img src="{contact_img_path}" alt="Contact Visual" class="contact-img" loading="lazy">
          </div>'''

    # 3. Social Media Section (from pages/05_about/social/ or socialMedia/)
    social_tiles_html = []
    social_folder = None
    for folder_cand in ["social", "socialMedia"]:
        cand_dir = os.path.join(about_dir, folder_cand)
        if os.path.exists(cand_dir) and os.path.isdir(cand_dir):
            social_folder = cand_dir
            break

    if social_folder:
        social_json_file = None
        for jcand in ["social.json", "socialMedia.json", "links.json"]:
            jp = os.path.join(social_folder, jcand)
            if os.path.exists(jp):
                social_json_file = jp
                break

        if social_json_file:
            try:
                with open(social_json_file, "r", encoding="utf-8") as sf:
                    social_items = json.load(sf)
                    if isinstance(social_items, list):
                        for s_item in social_items:
                            img_name = s_item.get("image") or s_item.get("image name") or s_item.get("icon") or ""
                            s_link = s_item.get("link") or s_item.get("url") or "#"
                            s_name = s_item.get("name") or s_item.get("title") or os.path.splitext(img_name)[0].title()
                            
                            # Prefer .webp if converted
                            img_base = os.path.splitext(img_name)[0]
                            resolved_img = img_name
                            for cand_ext in [".webp", ".png", ".jpg", ".jpeg"]:
                                if os.path.exists(os.path.join(social_folder, f"{img_base}{cand_ext}")):
                                    resolved_img = f"{img_base}{cand_ext}"
                                    break

                            s_img_path = f"{social_folder}/{resolved_img}".replace("\\", "/")
                            if os.path.exists(os.path.join(social_folder, resolved_img)):
                                social_tiles_html.append(f'''
            <a href="{s_link}" target="_blank" rel="noopener noreferrer" class="social-tile" title="{s_name}">
              <img src="{s_img_path}" alt="{s_name}" class="social-icon-img" loading="lazy">
            </a>''')
            except Exception as e:
                print("Notice reading social.json:", e)

    social_section_html = ""
    if social_tiles_html:
        social_section_html = f'''
          <div class="about-social-row">
            {"".join(social_tiles_html)}
          </div>'''

    about_seo_meta = get_seo_meta_tags(
        "about.html",
        f"About {name} | {designation}",
        f"{name} - {designation}. {experience}. Production visual effects, compositing breakdown, and workflow automation.",
        image_url=profile_img
    )

    about_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About | {name}</title>
  <meta name="description" content="{name} - {designation}. {experience}.">
{about_seo_meta}
{json_ld_person}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/glightbox.min.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
{ga_body_tag}
  {about_bg_img_html}
  {about_bg_overlay_html}

{generate_nav_html("about")}

  <main style="padding-block: clamp(36px, 5vw, 64px);">
    <div class="container-wide">
      
      <!-- Page Header (With Title & Description; spacing preserved even if empty) -->
      <div class="section-header">
        <h1 class="section-title">{title_inner}</h1>
        <p class="section-desc">{desc_inner}</p>
      </div>

      <!-- Profile & Bio Grid (40:60 Ratio, Vertical Project-Tile Photo, Paragraphs with Line Breaks) -->
      <div class="about-grid">
        <div class="about-profile-col">
          <div class="project-tile aspect-vertical about-profile-tile">
            <div class="tile-circling-border" aria-hidden="true"></div>
            <div class="tile-inner">
              <img src="{profile_img}" alt="{name}" class="tile-img">
            </div>
          </div>
        </div>

        <div class="about-bio-col" style="--info-bg: {info_bg_rgba};">
          <div class="about-bio-top">
            <h1 class="about-name">{name}</h1>
            <div class="about-role-strip">{meta_role}</div>
            <div class="about-paragraphs">
              {paragraphs_html}
            </div>
          </div>
          <div class="about-bio-bottom">
            {social_section_html}
            <div class="about-actions-wrap">
              <a href="{resume_link}" class="btn btn-primary" download>Resume</a>
              <a href="{cover_letter_link}" class="btn btn-primary" download>Cover Letter</a>
            </div>
          </div>
        </div>
      </div>

      <!-- Showreel Video Embed (Vimeo or YouTube) -->
      {showreel_section_html}

      <!-- Known Tools Strip (Single Row Auto-Fitted Across Full Width) -->
      {tools_section_html}

      <!-- Contact Information Card (Lines List on Left, Optional Right-Aligned Image) -->
      <section id="contact" class="contact-card">
        <div class="contact-content-grid">
          <div class="contact-info-col">
            <h2 class="contact-heading">Contact Information</h2>
            <div class="contact-lines-list">
              {"".join(contact_lines_html)}
            </div>
          </div>
          {contact_img_html}
        </div>
      </section>

    </div>
  </main>

  <script src="_engine/js/glightbox.min.js"></script>
  <script type="module" src="_engine/js/lightbox.js"></script>
  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("about.html", "w", encoding="utf-8") as f:
        f.write(about_html)
    print("  -> Updated about.html (Nav: About, Vertical Photo Tile, Known Tools Strip, Showreel Embed)")

    # Also generate about-me.html meta-refresh redirect to about.html
    about_redirect_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=about.html">
  <title>Redirecting to About...</title>
  <link rel="canonical" href="about.html">
</head>
<body>
  <p>Redirecting to <a href="about.html">About</a>...</p>
</body>
</html>'''
    with open("about-me.html", "w", encoding="utf-8") as f:
        f.write(about_redirect_html)
    print("  -> Updated about-me.html (Permanent redirect to about.html)")

    # --------------------------------------------------------------------------
    # 5. SYNC AI / COMFY (pages/03_ai-comfy)
    # --------------------------------------------------------------------------
    ai_dir = "pages/03_ai-comfy"
    ai_bg_img_html, ai_bg_overlay_html, _, _ = get_page_background_and_overlay(ai_dir)

    # Read AI / Comfy content.json if present
    ai_page_info = {
        "title": "ComfyUI Pipelines & AI Toolsets",
        "description": "Bridging the gap between cutting-edge Diffusion models and film-grade visual effects pipelines. Custom ComfyUI node workflows, automated plate inpainting, and depth-guided dynamic relighting."
    }
    ai_content_json = os.path.join(ai_dir, "content.json")
    if os.path.exists(ai_content_json):
        try:
            with open(ai_content_json, "r", encoding="utf-8") as f:
                ai_page_info.update(json.load(f))
        except Exception:
            pass

    ai_title = ai_page_info.get("title", "ComfyUI Pipelines & AI Toolsets")
    ai_desc = ai_page_info.get("description", "")
    ai_title_inner = ai_title.strip() if ai_title else '&nbsp;'
    ai_desc_inner = ai_desc.strip() if ai_desc else '&nbsp;'

    # Resolve Before/After Inpaint Demo images
    ba_before_img = ""
    ba_after_img = ""
    for gb_match in glob.glob("pages/02_VFX/*/*goatbusters*"):
        for cand_ext in [".webp", ".jpg", ".jpeg", ".png"]:
            cand = os.path.join(gb_match, f"projectImage{cand_ext}").replace("\\", "/")
            if os.path.exists(cand):
                ba_before_img = cand
                break
        if ba_before_img:
            break

    for gmc_match in glob.glob("pages/02_VFX/*/*gmc-hummer*"):
        for cand_ext in [".webp", ".jpg", ".jpeg", ".png"]:
            cand = os.path.join(gmc_match, f"projectImage{cand_ext}").replace("\\", "/")
            if os.path.exists(cand):
                ba_after_img = cand
                break
        if ba_after_img:
            break

    # Resolve Workflow Architecture image
    workflow_img = "pages/03_ai-comfy/workflows/comfyui-production-pipeline.webp"
    if not os.path.exists(workflow_img):
        workflow_img = "pages/03_ai-comfy/workflows/comfyui-production-pipeline.png"

    ai_seo_meta = get_seo_meta_tags(
        "ai-comfy.html",
        f"{ai_title} | Pra - Motions",
        ai_desc or "ComfyUI pipelines, automated cleanup nodes, and custom AI VFX workflows."
    )

    ai_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ai_title} | Pra - Motions</title>
  <meta name="description" content="{ai_desc}">
{ai_seo_meta}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/glightbox.min.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
{ga_body_tag}
  {ai_bg_img_html}
  {ai_bg_overlay_html}

{generate_nav_html("ai-comfy")}

  <main style="padding-block: clamp(36px, 6vw, 72px);">
    <div class="container-wide">
      
      <!-- Page Header -->
      <div class="section-header">
        <h1 class="section-title">{ai_title_inner}</h1>
        <p class="section-desc">{ai_desc_inner}</p>
      </div>

      <!-- Production ComfyUI Workflow Architecture -->
      <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: clamp(20px, 4vw, 36px); margin-bottom: 48px;">
        <div style="margin-bottom: 20px;">
          <span style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent-primary); text-transform: uppercase;">Production Workflow Graph</span>
          <h2 style="font-size: 1.4rem; font-weight: 700;">ComfyUI VFX Production Pipeline Graph</h2>
          <p style="font-size: 0.9rem; color: var(--text-muted);">
            Full interactive visual graph. Click image to open high-resolution zoom in Lightbox.
          </p>
        </div>
        <div style="border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--border-subtle); background: #000;">
          <img src="{workflow_img}" alt="ComfyUI Production Pipeline Architecture" style="width: 100%; object-fit: contain; cursor: zoom-in;" data-lightbox data-caption="ComfyUI Master VFX Production Workflow Architecture">
        </div>
      </div>

      <!-- Before & After Wipe Slider: AI Inpainting Demo -->
      <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: clamp(20px, 4vw, 36px); margin-bottom: 48px;">
        <div style="margin-bottom: 20px;">
          <span style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent-primary); text-transform: uppercase;">Interactive Demo</span>
          <h2 style="font-size: 1.4rem; font-weight: 700;">Plate Inpainting: Rig Removal with ControlNet + LaMa</h2>
          <p style="font-size: 0.9rem; color: var(--text-muted);">
            Slide to compare the raw live-action plate with tracking markers against the AI generative inpaint with preserved film grain.
          </p>
        </div>

        <div style="max-width: 900px; margin-inline: auto;">
          <div class="before-after-container">
            <div class="ba-image-layer ba-before-layer">
              <img src="{ba_before_img}" alt="Raw Live Plate with Markers">
              <span class="ba-badge ba-badge-before">Raw Plate + Tracking Markers</span>
            </div>
            <div class="ba-image-layer ba-after-layer">
              <img src="{ba_after_img}" alt="AI Inpainted Clean Plate">
              <span class="ba-badge ba-badge-after">AI Inpainted Clean Plate</span>
            </div>
            <div class="ba-handle">
              <div class="ba-handle-circle">
                <div class="ba-handle-arrows"><span>&#9664;</span><span>&#9654;</span></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Workflow Cards Grid -->
      <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 24px;">Production ComfyUI Workflows</h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 380px), 1fr)); gap: 28px;">

        <!-- Workflow 1 -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 24px; display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-primary); background: rgba(249,134,3,0.1); padding: 3px 8px; border-radius: 4px;">PLATE INPAINTING</span>
            <span style="font-size: 0.78rem; color: var(--text-subtle);">ComfyUI + LaMa</span>
          </div>
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 10px;">Automated 4K Clean-Plate Generator</h3>
          <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 16px; flex-grow: 1;">
            Converts roto tracking markers and harness wires into seamless 4K background textures without seam artifacts or optical degradation.
          </p>
          <div style="background: var(--bg-secondary); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 16px; font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted);">
            <div><strong>Inputs:</strong> Live Plate + Roto Matte</div>
            <div><strong>Outputs:</strong> 16-bit Float EXR Clean Plate</div>
          </div>
          <a href="blog.html#comfyui-portable-custom-nodes" class="btn btn-secondary" style="font-size: 0.82rem; padding: 8px 16px;">
            <span>Read Setup Tutorial</span>
          </a>
        </div>

        <!-- Workflow 2 -->
        <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: 24px; display: flex; flex-direction: column;">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
            <span style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-hover); background: rgba(255,155,38,0.1); padding: 3px 8px; border-radius: 4px;">RELIGHTING / COMP</span>
            <span style="font-size: 0.78rem; color: var(--text-subtle);">Marigold + IC-Light</span>
          </div>
          <h3 style="font-size: 1.2rem; font-weight: 700; margin-bottom: 10px;">Depth-Guided Shot Relighting</h3>
          <p style="font-size: 0.9rem; color: var(--text-muted); margin-bottom: 16px; flex-grow: 1;">
            Derives photoreal metric depth maps and surface normals directly from 2D footage to cast directional rim lights, specular glints, and volume fog.
          </p>
          <div style="background: var(--bg-secondary); border-radius: var(--radius-sm); padding: 12px; margin-bottom: 16px; font-family: var(--font-mono); font-size: 0.78rem; color: var(--text-muted);">
            <div><strong>Nodes:</strong> Marigold Depth, IC-Light, VHS</div>
            <div><strong>Outputs:</strong> Normal Pass + Rim Key Light</div>
          </div>
          <a href="blog.html#facefusion-windows-portable" class="btn btn-secondary" style="font-size: 0.82rem; padding: 8px 16px;">
            <span>View Implementation</span>
          </a>
        </div>

      </div>

    </div>
  </main>

  <script src="_engine/js/glightbox.min.js"></script>
  <script type="module" src="_engine/js/lightbox.js"></script>
  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("ai-comfy.html", "w", encoding="utf-8") as f:
        f.write(ai_html)
    print("  -> Updated ai-comfy.html (Nav: VFX, ComfyUI Workflows, Inpaint Wipe Demo)")

    # --------------------------------------------------------------------------
    # 6. SYNC BLOG (pages/06_blog)
    # --------------------------------------------------------------------------
    blog_dir = "pages/06_blog"
    blog_bg_img_html, blog_bg_overlay_html, blog_resolved_bg, blog_overlay_alpha = get_page_background_and_overlay(blog_dir)
    reader_bg_html = f'<div class="reader-bg-image" style="background-image: url(\'{blog_resolved_bg}\');"></div>\n    <div class="reader-bg-overlay" style="opacity: {blog_overlay_alpha};"></div>' if blog_resolved_bg else ''

    # 1. Read Blog content.json (title, description, overlayOpacity)
    blog_page_info = {
        "title": "Technical Blog & Guides",
        "description": "Practical setups, automation scripts, compositing breakdowns, and workflow optimization for VFX & AI artists."
    }
    blog_content_json = os.path.join(blog_dir, "content.json")
    if os.path.exists(blog_content_json):
        try:
            with open(blog_content_json, "r", encoding="utf-8") as f:
                blog_page_info.update(json.load(f))
        except Exception:
            pass

    blog_title = blog_page_info.get("title", "Technical Blog & Guides")
    blog_desc = blog_page_info.get("description", "")
    blog_title_inner = blog_title.strip() if blog_title else '&nbsp;'
    blog_desc_inner = blog_desc.strip() if blog_desc else '&nbsp;'

    # 2. Discover and Parse all Dated Post Folders in pages/06_blog/posts/
    posts_base_dir = os.path.join(blog_dir, "posts")
    parsed_posts = []

    month_names = ["January", "February", "March", "April", "May", "June",
                   "July", "August", "September", "October", "November", "December"]

    if os.path.exists(posts_base_dir):
        post_subdirs = sorted([d for d in os.listdir(posts_base_dir) if os.path.isdir(os.path.join(posts_base_dir, d))], reverse=True)
        for folder_name in post_subdirs:
            folder_path = os.path.join(posts_base_dir, folder_name)
            
            # Post Metadata
            post_meta = {
                "title": format_title_from_filename(folder_name),
                "date": "2026-01-01",
                "category": "General",
                "tags": [],
                "subheading": "",
                "thumbnail": "",
                "author": "Prasannakumar T Bhat",
                "readTime": "5 min read"
            }

            # Date extraction strictly from folder name: YYYY-MM-DD... (single source of truth)
            date_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})', folder_name)
            post_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else "2026-01-01"
            post_meta["date"] = post_date

            # Load post.json if present
            post_json_path = os.path.join(folder_path, "post.json")
            if os.path.exists(post_json_path):
                try:
                    with open(post_json_path, "r", encoding="utf-8") as f:
                        loaded_json = json.load(f)
                        if isinstance(loaded_json, dict):
                            loaded_json.pop("date", None) # strictly fetched from folder name
                            post_meta.update(loaded_json)
                except Exception:
                    pass

            # Read post.md content
            md_content = ""
            for md_cand in ["post.md", "index.md", "article.md", "README.md"]:
                md_p = os.path.join(folder_path, md_cand)
                if os.path.exists(md_p):
                    with open(md_p, "r", encoding="utf-8") as f:
                        md_content = f.read()
                    break

            # If metadata was in YAML frontmatter in post.md
            if md_content.startswith("---"):
                parts = md_content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        frontmatter = yaml.safe_load(parts[1])
                        if isinstance(frontmatter, dict):
                            frontmatter.pop("date", None) # strictly fetched from folder name
                            post_meta.update(frontmatter)
                            md_content = parts[2].strip()
                    except Exception:
                        pass

            # Enforce date strictly from folder name
            post_meta["date"] = post_date

            # Resolve thumbnail image
            thumbnail_path = ""
            if post_meta.get("thumbnail"):
                cand_thumb = os.path.join(folder_path, post_meta["thumbnail"])
                if os.path.exists(cand_thumb):
                    thumbnail_path = cand_thumb.replace("\\", "/")
                elif os.path.exists(post_meta["thumbnail"]):
                    thumbnail_path = post_meta["thumbnail"].replace("\\", "/")

            if not thumbnail_path:
                for img_cand in ["cover.webp", "cover.jpg", "cover.png", "thumbnail.webp", "thumbnail.jpg", "thumbnail.png"]:
                    p = os.path.join(folder_path, img_cand)
                    if os.path.exists(p):
                        thumbnail_path = p.replace("\\", "/")
                        break

            if not thumbnail_path:
                # Fallback to any image in post folder
                for f in sorted(os.listdir(folder_path)):
                    if os.path.splitext(f)[1].lower() in valid_img_exts:
                        thumbnail_path = f"{folder_path}/{f}".replace("\\", "/")
                        break

            # Parse date for Year and Month
            post_date = post_meta.get("date", "2026-01-01")
            d_parts = post_date.split("-")
            year_str = d_parts[0] if len(d_parts) > 0 else "2026"
            month_idx = int(d_parts[1]) - 1 if len(d_parts) > 1 and d_parts[1].isdigit() else 0
            month_name = month_names[month_idx] if 0 <= month_idx < 12 else "January"

            # Render Markdown into HTML
            rendered_html = ""
            if md_content:
                # 1. Process relative image paths: e.g. src="image.png" -> src="pages/06_blog/posts/.../image.webp"
                def fix_md_img(m):
                    alt, src = m.group(1), m.group(2)
                    if not src.startswith("http") and not src.startswith("/") and not src.startswith("pages/"):
                        base_s, _ = os.path.splitext(src)
                        if os.path.exists(os.path.join(folder_path, f"{base_s}.webp")):
                            src = f"{folder_path}/{base_s}.webp".replace("\\", "/")
                        else:
                            src = f"{folder_path}/{src}".replace("\\", "/")
                    return f'![{alt}]({src})'
                fixed_md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_md_img, md_content)

                # Process code blocks into collapsible cards with copy button
                def process_markdown_code_blocks(md_text):
                    code_pattern = re.compile(r'```([a-zA-Z0-9_-]*)\r?\n(.*?)```', re.DOTALL)
                    def code_repl(m):
                        lang = m.group(1).strip() or 'text'
                        code_raw = m.group(2).rstrip()
                        code_esc = html.escape(code_raw)
                        line_count = len(code_raw.splitlines())
                        if line_count <= 3:
                            # 3 or fewer lines: show expanded by default, omit expand/collapse button
                            return f'''<div class="code-block-card">
  <div class="code-block-header">
    <span class="code-lang-badge">{lang}</span>
    <div class="code-actions">
      <button type="button" class="btn-code-copy" onclick="copyCodeBlock(this)">Copy</button>
    </div>
  </div>
  <pre><code class="language-{lang}">{code_esc}</code></pre>
</div>'''
                        else:
                            # Greater than 3 lines: collapsed by default (3 lines), include expand/collapse toggle
                            return f'''<div class="code-block-card is-collapsed">
  <div class="code-block-header">
    <span class="code-lang-badge">{lang}</span>
    <div class="code-actions">
      <button type="button" class="btn-code-toggle" onclick="toggleCodeBlock(this)">Expand</button>
      <button type="button" class="btn-code-copy" onclick="copyCodeBlock(this)">Copy</button>
    </div>
  </div>
  <pre><code class="language-{lang}">{code_esc}</code></pre>
</div>'''
                    return code_pattern.sub(code_repl, md_text)

                md_with_code = process_markdown_code_blocks(fixed_md)
                compiled_html = markdown.markdown(md_with_code, extensions=['tables'])

                # Also fix any <img src="relative"> in html:
                def fix_html_img(m):
                    pfx, src, sfx = m.group(1), m.group(2), m.group(3)
                    if not src.startswith("http") and not src.startswith("/") and not src.startswith("pages/"):
                        base_s, _ = os.path.splitext(src)
                        if os.path.exists(os.path.join(folder_path, f"{base_s}.webp")):
                            src = f"{folder_path}/{base_s}.webp".replace("\\", "/")
                        else:
                            src = f"{folder_path}/{src}".replace("\\", "/")
                    return f'{pfx}{src}{sfx}'
                rendered_html = re.sub(r'(<img[^>]+src=[\'"])([^\'"]+)([\'"][^>]*>)', fix_html_img, compiled_html)

            # Generate Post ID / slug
            post_id = slugify(folder_name)
            slug = re.sub(r'^\d{4}-\d{2}-\d{2}[-_]*', '', folder_name) or post_id

            parsed_posts.append({
                "id": post_id,
                "slug": slug,
                "folder": folder_path.replace("\\", "/"),
                "title": post_meta.get("title", ""),
                "date": post_date,
                "year": year_str,
                "month_name": month_name,
                "category": post_meta.get("category", "General"),
                "tags": post_meta.get("tags", []),
                "subheading": post_meta.get("subheading", ""),
                "thumbnail": thumbnail_path,
                "author": post_meta.get("author", "Prasannakumar T Bhat"),
                "readTime": post_meta.get("readTime", "5 min read"),
                "rendered_html": rendered_html
            })

    # Sort parsed posts descending by date
    parsed_posts.sort(key=lambda x: x["date"], reverse=True)

    # 3. Build Tree Data: Year -> Month -> Posts
    tree_hierarchy = {}
    categories_set = set()
    tags_set = set()
    for p in parsed_posts:
        y = p["year"]
        m = p["month_name"]
        if y not in tree_hierarchy:
            tree_hierarchy[y] = {}
        if m not in tree_hierarchy[y]:
            tree_hierarchy[y][m] = []
        tree_hierarchy[y][m].append(p)
        if p.get("category"):
            categories_set.add(p["category"])
        if p.get("tags") and isinstance(p["tags"], list):
            for t in p["tags"]:
                if t and isinstance(t, str) and t.strip():
                    tags_set.add(t.strip())

    tree_items_html = []
    for y in sorted(tree_hierarchy.keys(), reverse=True):
        year_total = sum(len(tree_hierarchy[y][m]) for m in tree_hierarchy[y])
        months_html = []
        for m in sorted(tree_hierarchy[y].keys()):
            m_count = len(tree_hierarchy[y][m])
            months_html.append(f'''
              <li class="tree-item tree-month" data-year="{y}" data-month="{m}" onclick="filterByMonth('{y}', '{m}')">
                <span class="tree-left-wrap">
                  <span class="tree-bullet">&bull;</span>
                  <span class="tree-label">{m}</span>
                </span>
                <span class="tree-count">{m_count}</span>
              </li>''')

        tree_items_html.append(f'''
          <li class="tree-item tree-year" data-year="{y}">
            <div class="tree-node" onclick="toggleTreeNode(this, '{y}')">
              <span class="tree-left-wrap">
                <span class="tree-arrow">&#9660;</span>
                <span class="tree-label">{y}</span>
              </span>
              <span class="tree-count">{year_total}</span>
            </div>
            <ul class="tree-children">
              {"".join(months_html)}
            </ul>
          </li>''')

    categories_pills = ['<button type="button" class="filter-pill category-filter-pill active" data-category="all" onclick="filterByCategory(\'all\')">All</button>']
    for cat in sorted(categories_set):
        cat_esc = html.escape(cat)
        categories_pills.append(f'<button type="button" class="filter-pill category-filter-pill" data-category="{cat_esc}" onclick="filterByCategory(\'{cat_esc}\')">{cat_esc}</button>')

    tags_pills = ['<button type="button" class="filter-pill tag-filter-pill active" data-tag="all" onclick="filterByTag(\'all\')">All</button>']
    for tag in sorted(tags_set, key=lambda x: x.lower()):
        tag_esc = html.escape(tag)
        tags_pills.append(f'<button type="button" class="filter-pill tag-filter-pill" data-tag="{tag_esc}" onclick="filterByTag(\'{tag_esc}\')">{tag_esc}</button>')

    posts_json_str = json.dumps(parsed_posts)

    blog_seo_meta = get_seo_meta_tags(
        "blog.html",
        f"{blog_title} | Pra - Motions",
        blog_desc or "Technical blog, practical VFX setups, automation scripts, and workflow optimization."
    )

    blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{blog_title} | Pra - Motions</title>
  <meta name="description" content="{blog_desc}">
{blog_seo_meta}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/glightbox.min.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  <link rel="stylesheet" href="_engine/css/prism.css">
  <link rel="stylesheet" href="_engine/css/blog.css">
</head>
<body>
{ga_body_tag}
  {blog_bg_img_html}
  {blog_bg_overlay_html}

{generate_nav_html("blog")}

  <main style="padding-block: clamp(36px, 5vw, 64px);">
    <div class="container-wide">
      
      <!-- Page Header -->
      <div class="section-header">
        <h1 class="section-title">{blog_title_inner}</h1>
        <p class="section-desc">{blog_desc_inner}</p>
      </div>

      <!-- Blog Layout: Sidebar Tree + 3-Tile Grid -->
      <div class="blog-layout">
        
        <!-- Left Sidebar: Independent Filters & Archive Cards -->
        <aside class="blog-sidebar">
          
          <!-- Box 1: Content Filters Card (Categories & Tags First) -->
          <div class="blog-tree-card blog-filter-card">
            <div class="tree-header">
              <h3 class="tree-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon></svg>
                Filters
              </h3>
              <button type="button" class="tree-reset-btn" onclick="resetBlogFilter()" title="Reset all filters">Reset All</button>
            </div>

            <!-- Categories Section -->
            <div class="tree-categories-wrap">
              <h4 class="tree-subtitle">Categories</h4>
              <div class="tree-pill-list" id="categoryPillList">
                {"".join(categories_pills)}
              </div>
            </div>

            <div class="tree-section-divider"></div>

            <!-- Tags Section -->
            <div class="tree-tags-wrap">
              <h4 class="tree-subtitle">Tags</h4>
              <div class="tree-pill-list" id="tagPillList">
                {"".join(tags_pills)}
              </div>
            </div>
          </div>

          <!-- Box 2: Independent Date / Archive Filter Card -->
          <div class="blog-tree-card blog-archive-card">
            <div class="tree-header">
              <h3 class="tree-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                Archive
              </h3>
              <button type="button" class="tree-reset-btn" onclick="filterByTree('all')" title="Reset date filter">All Dates</button>
            </div>

            <ul class="tree-root">
              <li class="tree-item tree-all active" onclick="filterByTree('all')">
                <span class="tree-left-wrap">
                  <span class="tree-label">All Posts</span>
                </span>
                <span class="tree-count">{len(parsed_posts)}</span>
              </li>
              {"".join(tree_items_html)}
            </ul>
          </div>

        </aside>

        <!-- Main Blog Area: Post Grid & Pagination -->
        <section class="blog-content-area">
          <div class="blog-grid" id="blogGrid">
            <!-- Populated dynamically by blog.js with initial server-side fallback -->
          </div>

          <!-- Pagination Controls -->
          <div class="blog-pagination" id="blogPagination">
            <button type="button" class="page-nav-btn prev-btn" id="prevPageBtn" onclick="changePage(-1)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
              <span>Previous</span>
            </button>
            
            <div class="page-numbers-wrap" id="pageNumbers"></div>

            <button type="button" class="page-nav-btn next-btn" id="nextPageBtn" onclick="changePage(1)">
              <span>Next</span>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </div>
        </section>

      </div>

    </div>
  </main>

  <!-- Full Post Reader Modal (Expanded Reading View) -->
  <div id="blogReaderOverlay" class="blog-reader-overlay" aria-hidden="true">

    <!-- Reader Background Layers (matches blog page background and overlay opacity settings) -->
    {reader_bg_html}

    <!-- Pinned Floating Close Button (Viewport top-right, always visible) -->
    <button type="button" class="reader-floating-close" onclick="closePostModal()" aria-label="Close article" title="Close article (Esc)">
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>

    <!-- Pinned Side Navigation Arrows: Left (Previous Post) & Right (Next Post) -->
    <button type="button" class="reader-side-nav reader-side-prev" id="readerSidePrev" onclick="navigatePost(-1)" aria-label="Previous Post" title="Previous Post">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
        <polyline points="15 18 9 12 15 6"></polyline>
      </svg>
    </button>

    <button type="button" class="reader-side-nav reader-side-next" id="readerSideNext" onclick="navigatePost(1)" aria-label="Next Post" title="Next Post">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="20" height="20">
        <polyline points="9 18 15 12 9 6"></polyline>
      </svg>
    </button>

    <!-- Pinned Floating Move-to-Top Button (Viewport bottom-right, matches VFX page) -->
    <button type="button" class="back-to-top reader-back-to-top" id="readerBackToTop" onclick="scrollReaderToTop()" aria-label="Scroll to top" title="Scroll to top">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="18 15 12 9 6 15"></polyline>
      </svg>
    </button>

    <!-- Full-page scrolling viewport container -->
    <div class="blog-reader-scroll" id="blogReaderScroll">
      <div class="blog-reader-dialog" role="dialog" aria-modal="true">
        
        <article class="blog-reader-content">
          <header class="reader-header">
            <h1 class="reader-title" id="readerTitle">Title</h1>
            <p class="reader-subheading" id="readerSubheading">Subheading</p>
            <div class="reader-meta">
              <span id="readerDate">Date</span>
              <span>&bull;</span>
              <span id="readerReadTime">Read Time</span>
              <span>&bull;</span>
              <span id="readerAuthor">Author</span>
            </div>
            <div class="reader-tags" id="readerTags"></div>
          </header>

          <div class="reader-hero-image-wrap" id="readerHeroWrap">
            <img id="readerHeroImg" src="" alt="Hero Image" class="reader-hero-img">
          </div>

          <div class="reader-body" id="readerBody"></div>

          <!-- Bottom Post Navigation: Move to Previous & Next Post (50/50 full area, 2 lines with arrow) -->
          <nav class="reader-footer-nav">
            <button type="button" class="reader-nav-btn prev-post-btn" id="readerPrevBtn" onclick="navigatePost(-1)" title="Previous Post">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="15 18 9 12 15 6"></polyline></svg>
              <span class="nav-title" id="readerPrevTitle">Previous Post</span>
            </button>

            <button type="button" class="reader-nav-btn next-post-btn" id="readerNextBtn" onclick="navigatePost(1)" title="Next Post">
              <span class="nav-title" id="readerNextTitle">Next Post</span>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 18 15 12 9 6"></polyline></svg>
            </button>
          </nav>

        </article>

      </div>
    </div>

  </div>

  <script id="blogPostsData" type="application/json">
{posts_json_str}
  </script>

  <script src="_engine/js/prism.js"></script>
  <script src="_engine/js/glightbox.min.js"></script>
  <script type="module" src="_engine/js/lightbox.js"></script>
  <script src="_engine/js/blog.js"></script>
  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(blog_html)
    print("  -> Updated blog.html (Nav: Blog, 3-Tile Grid, Archive Tree, Modal Reader, Code Highlights)")

    # --------------------------------------------------------------------------
    # 7. SYNC MORE / RESOURCES PAGE (pages/07_more -> more.html, not in nav)
    # --------------------------------------------------------------------------
    more_dir = "pages/07_more" if os.path.exists("pages/07_more") else "pages/more"
    more_bg_img_html, more_bg_overlay_html, _, _ = get_page_background_and_overlay(more_dir)

    more_data = {
        "title": "More & Resources",
        "description": "Direct downloads, project files, and curated links.",
        "linksSectionTitle": "Useful Links",
        "downloadsSectionTitle": "Downloads",
        "overlayOpacity": 75
    }

    more_content_json = os.path.join(more_dir, "content.json")
    if os.path.exists(more_content_json):
        try:
            with open(more_content_json, "r", encoding="utf-8") as f:
                more_data.update(json.load(f))
        except Exception:
            pass

    page_title = more_data.get("title", "More & Resources")
    page_desc = more_data.get("description", "")
    title_inner = page_title.strip() if page_title else '&nbsp;'
    desc_inner = page_desc.strip() if page_desc else '&nbsp;'
    links_section_title = more_data.get("linksSectionTitle", "Useful Links").strip()
    downloads_section_title = more_data.get("downloadsSectionTitle", "Downloads").strip()

    # 1. Parse Useful Links (usefullLinks.json, usefulLinks.json, links.json)
    useful_links_list = []
    for cand_json in ["usefullLinks.json", "usefulLinks.json", "links.json"]:
        cand_path = os.path.join(more_dir, cand_json)
        if os.path.exists(cand_path):
            try:
                with open(cand_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        useful_links_list = data
                        break
            except Exception as e:
                print(f"Notice reading {cand_path}:", e)

    links_cards_html = []
    for item in useful_links_list:
        if not isinstance(item, dict):
            continue
        l_name = (item.get("name") or item.get("title") or "Link").strip()
        l_url = (item.get("link") or item.get("url") or item.get("href") or "#").strip()
        l_desc = (item.get("description") or item.get("desc") or "").strip()
        if not l_desc and l_url.startswith("http"):
            domain_part = re.sub(r'^https?:\/\/(?:www\.)?', '', l_url).split('/')[0]
            l_desc = domain_part

        links_cards_html.append(f'''
          <a href="{l_url}" target="_blank" rel="noopener noreferrer" class="more-link-card" title="{l_name}">
            <div class="more-link-content">
              <div class="more-link-icon-wrap" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                </svg>
              </div>
              <div class="more-link-text">
                <span class="more-link-title">{l_name}</span>
                <span class="more-link-desc">{l_desc}</span>
              </div>
            </div>
            <div class="more-link-arrow" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="7" y1="17" x2="17" y2="7"></line>
                <polyline points="7 7 17 7 17 17"></polyline>
              </svg>
            </div>
          </a>''')

    if links_cards_html:
        links_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">
            <span>{links_section_title}</span>
            <span class="more-section-badge">{len(links_cards_html)}</span>
          </h2>
        </div>
        <div class="more-links-grid">
          {"".join(links_cards_html)}
        </div>
      </section>'''
    else:
        links_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">{links_section_title}</h2>
        </div>
        <p class="more-empty-msg">No links listed yet. Add entries to <code>{more_dir}/usefullLinks.json</code>.</p>
      </section>'''

    # 2. Parse Files for Download (forDownload/ folder)
    downloads_dir = os.path.join(more_dir, "forDownload")
    if not os.path.exists(downloads_dir):
        downloads_dir = "forDownload"

    download_cards_html = []
    if os.path.exists(downloads_dir):
        raw_files = [f for f in os.listdir(downloads_dir) if not f.startswith(".") and os.path.isfile(os.path.join(downloads_dir, f))]
        raw_files.sort(key=lambda s: s.lower())

        def _fmt_size(b):
            if b < 1024:
                return f"{b} B"
            elif b < 1024 * 1024:
                return f"{b / 1024:.1f} KB"
            elif b < 1024 * 1024 * 1024:
                return f"{b / (1024 * 1024):.1f} MB"
            else:
                return f"{b / (1024 * 1024 * 1024):.1f} GB"

        for fname in raw_files:
            fpath = os.path.join(downloads_dir, fname)
            frel_path = fpath.replace("\\", "/")
            fsize_bytes = os.path.getsize(fpath)
            fsize_str = _fmt_size(fsize_bytes)
            ext = os.path.splitext(fname)[1].lower().lstrip(".")
            badge_text = ext.upper() if ext else "FILE"

            badge_cls = "badge-other"
            if ext in ["zip", "rar", "7z", "tar", "gz"]:
                badge_cls = "badge-zip"
            elif ext in ["json", "js", "ts", "py"]:
                badge_cls = "badge-json"
            elif ext in ["html", "htm", "css", "xml"]:
                badge_cls = "badge-html"
            elif ext in ["jpg", "jpeg", "png", "webp", "gif", "svg", "bmp"]:
                badge_cls = "badge-img"

            download_cards_html.append(f'''
          <div class="more-download-card">
            <div class="more-download-info-wrap">
              <span class="more-file-badge {badge_cls}">{badge_text}</span>
              <div class="more-download-text">
                <span class="more-download-name" title="{fname}">{fname}</span>
                <span class="more-download-meta">{fsize_str} &bull; {badge_text}</span>
              </div>
            </div>
            <a href="{frel_path}" download="{fname}" class="btn btn-primary more-download-btn" title="Download {fname}">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              <span>Download</span>
            </a>
          </div>''')

    if download_cards_html:
        downloads_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">
            <span>{downloads_section_title}</span>
            <span class="more-section-badge">{len(download_cards_html)}</span>
          </h2>
        </div>
        <div class="more-downloads-grid">
          {"".join(download_cards_html)}
        </div>
      </section>'''
    else:
        downloads_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">{downloads_section_title}</h2>
        </div>
        <p class="more-empty-msg">No files currently in <code>{downloads_dir}/</code>. Upload any files here to list them for download.</p>
      </section>'''

    more_seo_meta = get_seo_meta_tags("more.html", page_title, page_desc, is_private=True)

    more_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title} | Prasannakumar T Bhat</title>
  <meta name="description" content="{page_desc}">
{more_seo_meta}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
{ga_body_tag}
  {more_bg_img_html}
  {more_bg_overlay_html}

{generate_nav_html("")}

  <main style="padding-block: clamp(36px, 5vw, 64px);">
    <div class="container-wide">
      
      <!-- Page Header -->
      <div class="section-header">
        <h1 class="section-title">{title_inner}</h1>
        <p class="section-desc">{desc_inner}</p>
      </div>

      <!-- Useful Links Section -->
      {links_section_html}

      <!-- Downloads Section -->
      {downloads_section_html}

    </div>
  </main>

  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("more.html", "w", encoding="utf-8") as f:
        f.write(more_html)
    print("  -> Updated more.html (Unlisted Page: Useful Links & forDownload Assets)")

    # Also generate more/index.html meta-redirect so /more or /more/ works everywhere
    os.makedirs("more", exist_ok=True)
    more_redirect_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=../more.html">
  <title>Redirecting to More...</title>
</head>
<body>
  <script>window.location.replace("../more.html");</script>
</body>
</html>'''
    with open("more/index.html", "w", encoding="utf-8") as f:
        f.write(more_redirect_html)

    # --------------------------------------------------------------------------
    # 8. SYNC EXTRA / UTILITIES PAGE (pages/08_extra -> extra.html, not in nav)
    # --------------------------------------------------------------------------
    extra_dir = "pages/08_extra" if os.path.exists("pages/08_extra") else "pages/extra"
    extra_bg_img_html, extra_bg_overlay_html, _, _ = get_page_background_and_overlay(extra_dir)

    extra_data = {
        "title": "Extra & Utilities",
        "description": "Additional utilities, downloadable packages, and curated links.",
        "linksSectionTitle": "Useful Links",
        "downloadsSectionTitle": "Downloads",
        "overlayOpacity": 75
    }

    extra_content_json = os.path.join(extra_dir, "content.json")
    if os.path.exists(extra_content_json):
        try:
            with open(extra_content_json, "r", encoding="utf-8") as f:
                extra_data.update(json.load(f))
        except Exception:
            pass

    page_title = extra_data.get("title", "Extra & Utilities")
    page_desc = extra_data.get("description", "")
    title_inner = page_title.strip() if page_title else '&nbsp;'
    desc_inner = page_desc.strip() if page_desc else '&nbsp;'
    links_section_title = extra_data.get("linksSectionTitle", "Useful Links").strip()
    downloads_section_title = extra_data.get("downloadsSectionTitle", "Downloads").strip()

    # 1. Parse Useful Links (usefullLinks.json, usefulLinks.json, links.json)
    extra_links_list = []
    for cand_json in ["usefullLinks.json", "usefulLinks.json", "links.json"]:
        cand_path = os.path.join(extra_dir, cand_json)
        if os.path.exists(cand_path):
            try:
                with open(cand_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        extra_links_list = data
                        break
            except Exception as e:
                print(f"Notice reading {cand_path}:", e)

    extra_links_cards_html = []
    for item in extra_links_list:
        if not isinstance(item, dict):
            continue
        l_name = (item.get("name") or item.get("title") or "Link").strip()
        l_url = (item.get("link") or item.get("url") or item.get("href") or "#").strip()
        l_desc = (item.get("description") or item.get("desc") or "").strip()
        if not l_desc and l_url.startswith("http"):
            domain_part = re.sub(r'^https?:\/\/(?:www\.)?', '', l_url).split('/')[0]
            l_desc = domain_part

        extra_links_cards_html.append(f'''
          <a href="{l_url}" target="_blank" rel="noopener noreferrer" class="more-link-card" title="{l_name}">
            <div class="more-link-content">
              <div class="more-link-icon-wrap" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                </svg>
              </div>
              <div class="more-link-text">
                <span class="more-link-title">{l_name}</span>
                <span class="more-link-desc">{l_desc}</span>
              </div>
            </div>
            <div class="more-link-arrow" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="7" y1="17" x2="17" y2="7"></line>
                <polyline points="7 7 17 7 17 17"></polyline>
              </svg>
            </div>
          </a>''')

    if extra_links_cards_html:
        extra_links_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">
            <span>{links_section_title}</span>
            <span class="more-section-badge">{len(extra_links_cards_html)}</span>
          </h2>
        </div>
        <div class="more-links-grid">
          {"".join(extra_links_cards_html)}
        </div>
      </section>'''
    else:
        extra_links_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">{links_section_title}</h2>
        </div>
        <p class="more-empty-msg">No links listed yet. Add entries to <code>{extra_dir}/usefullLinks.json</code>.</p>
      </section>'''

    # 2. Parse Files for Download (forDownload/ folder)
    extra_downloads_dir = os.path.join(extra_dir, "forDownload")
    if not os.path.exists(extra_downloads_dir):
        extra_downloads_dir = "forDownload"

    extra_download_cards_html = []
    if os.path.exists(extra_downloads_dir):
        raw_files = [f for f in os.listdir(extra_downloads_dir) if not f.startswith(".") and os.path.isfile(os.path.join(extra_downloads_dir, f))]
        raw_files.sort(key=lambda s: s.lower())

        def _fmt_size(b):
            if b < 1024:
                return f"{b} B"
            elif b < 1024 * 1024:
                return f"{b / 1024:.1f} KB"
            elif b < 1024 * 1024 * 1024:
                return f"{b / (1024 * 1024):.1f} MB"
            else:
                return f"{b / (1024 * 1024 * 1024):.1f} GB"

        for fname in raw_files:
            fpath = os.path.join(extra_downloads_dir, fname)
            frel_path = fpath.replace("\\", "/")
            fsize_bytes = os.path.getsize(fpath)
            fsize_str = _fmt_size(fsize_bytes)
            ext = os.path.splitext(fname)[1].lower().lstrip(".")
            badge_text = ext.upper() if ext else "FILE"

            badge_cls = "badge-other"
            if ext in ["zip", "rar", "7z", "tar", "gz"]:
                badge_cls = "badge-zip"
            elif ext in ["json", "js", "ts", "py"]:
                badge_cls = "badge-json"
            elif ext in ["html", "htm", "css", "xml"]:
                badge_cls = "badge-html"
            elif ext in ["jpg", "jpeg", "png", "webp", "gif", "svg", "bmp"]:
                badge_cls = "badge-img"

            extra_download_cards_html.append(f'''
          <div class="more-download-card">
            <div class="more-download-info-wrap">
              <span class="more-file-badge {badge_cls}">{badge_text}</span>
              <div class="more-download-text">
                <span class="more-download-name" title="{fname}">{fname}</span>
                <span class="more-download-meta">{fsize_str} &bull; {badge_text}</span>
              </div>
            </div>
            <a href="{frel_path}" download="{fname}" class="btn btn-primary more-download-btn" title="Download {fname}">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                <polyline points="7 10 12 15 17 10"></polyline>
                <line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              <span>Download</span>
            </a>
          </div>''')

    if extra_download_cards_html:
        extra_downloads_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">
            <span>{downloads_section_title}</span>
            <span class="more-section-badge">{len(extra_download_cards_html)}</span>
          </h2>
        </div>
        <div class="more-downloads-grid">
          {"".join(extra_download_cards_html)}
        </div>
      </section>'''
    else:
        extra_downloads_section_html = f'''
      <section class="more-section">
        <div class="more-section-header">
          <h2 class="more-section-title">{downloads_section_title}</h2>
        </div>
        <p class="more-empty-msg">No files currently in <code>{extra_downloads_dir}/</code>. Upload any files here to list them for download.</p>
      </section>'''

    extra_seo_meta = get_seo_meta_tags("extra.html", page_title, page_desc, is_private=True)

    extra_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{page_title} | Prasannakumar T Bhat</title>
  <meta name="description" content="{page_desc}">
{extra_seo_meta}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
{ga_body_tag}
  {extra_bg_img_html}
  {extra_bg_overlay_html}

{generate_nav_html("")}

  <main style="padding-block: clamp(36px, 5vw, 64px);">
    <div class="container-wide">
      
      <!-- Page Header -->
      <div class="section-header">
        <h1 class="section-title">{title_inner}</h1>
        <p class="section-desc">{desc_inner}</p>
      </div>

      <!-- Useful Links Section -->
      {extra_links_section_html}

      <!-- Downloads Section -->
      {extra_downloads_section_html}

    </div>
  </main>

  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("extra.html", "w", encoding="utf-8") as f:
        f.write(extra_html)
    print("  -> Updated extra.html (Unlisted Page: Useful Links & forDownload Assets)")

    # Also generate extra/index.html meta-redirect so /extra or /extra/ works everywhere
    os.makedirs("extra", exist_ok=True)
    extra_redirect_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=../extra.html">
  <title>Redirecting to Extra...</title>
</head>
<body>
  <script>window.location.replace("../extra.html");</script>
</body>
</html>'''
    with open("extra/index.html", "w", encoding="utf-8") as f:
        f.write(extra_redirect_html)

    # --------------------------------------------------------------------------
    # 9. GENERATE SITEMAP & ROBOTS.TXT (Exclude /more and /extra)
    # --------------------------------------------------------------------------
    generate_sitemap_and_robots()

    print("\nSUCCESS: All pages synchronized cleanly!")

if __name__ == "__main__":
    convert_flag = ("--convert-webp" in sys.argv) or ("-w" in sys.argv)
    sync_all(convert_webp=convert_flag)
