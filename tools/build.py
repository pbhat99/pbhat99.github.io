"""Site compiler for Pra - Motions portfolio (WebP conversion, static HTML generation, sitemap/robots)."""

import datetime
import html
import json
import os
import re
import sys
import urllib.parse

import markdown
import yaml

# Ensure script working directory is always repository root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.abspath(os.getcwd()) != PROJECT_ROOT:
    os.chdir(PROJECT_ROOT)

VALID_IMG_EXTS = {'.jpg', '.jpeg', '.jfif', '.png', '.avif', '.gif', '.bmp', '.tiff'}
PAGE_IMG_EXTS = {'.webp', '.jpg', '.jpeg', '.jfif', '.png', '.avif'}
DISPLAY_IMG_EXTS = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'}

_SITE_CONFIG_CACHE = None


# ------------------------------------------------------------------------------
# Shared Utilities
# ------------------------------------------------------------------------------
def esc(text):
    """HTML-escape text including quotes for safe attribute interpolation."""
    return html.escape(str(text or ""), quote=True)


def natural_sort_key(filename):
    """Sort key splitting digit runs numerically for deterministic folder/file order."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', filename)]


def slugify(text):
    return re.sub(r'[^a-z0-9]+', '-', str(text).lower()).strip('-')


def format_title_from_filename(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'^[0-9]+[-_]', '', name)
    name = name.replace('_orig', '').replace('_', ' ').replace('-', ' ')
    return re.sub(r'\s+', ' ', name).strip().title()


def load_json(path, defaults=None):
    """Load JSON safely, optionally merging into a shallow copy of defaults dict."""
    data = dict(defaults) if isinstance(defaults, dict) else defaults
    if not path or not os.path.exists(path):
        return data
    try:
        with open(path, "r", encoding="utf-8") as f:
            loaded = json.load(f)
        if isinstance(data, dict) and isinstance(loaded, dict):
            data.update(loaded)
            return data
        return loaded
    except Exception as e:
        print(f"Notice reading {path}: {e}")
        return data


def get_site_config():
    """Load siteConfig.json once per process."""
    global _SITE_CONFIG_CACHE
    if _SITE_CONFIG_CACHE is not None:
        return _SITE_CONFIG_CACHE

    cfg = {}
    for cand in ("tools/siteConfig.json", "siteConfig.json", "config.json"):
        if os.path.exists(cand):
            loaded = load_json(cand, {})
            if isinstance(loaded, dict):
                cfg.update(loaded)
                break
    _SITE_CONFIG_CACHE = cfg
    return cfg


def hex_to_rgba(hex_str, opacity_val=100):
    """Convert #RRGGBB/#RGB + opacity (0-100 or 0.0-1.0) to CSS rgba()."""
    if not hex_str:
        return "rgba(14, 23, 51, 0.85)"
    s = hex_str.strip().lstrip('#')
    if len(s) == 3:
        s = ''.join(c * 2 for c in s)
    try:
        r, g, b = int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    except Exception:
        return "rgba(14, 23, 51, 0.85)"
    try:
        op = float(opacity_val)
        if op > 1.0:
            op /= 100.0
        op = max(0.0, min(1.0, op))
    except Exception:
        op = 0.85
    return f"rgba({r}, {g}, {b}, {op:.2f})"


def with_mtime_query(rel_path):
    """Append ?v=<mtime> cache-buster if file exists locally."""
    if rel_path and os.path.exists(rel_path):
        try:
            return f"{rel_path}?v={int(os.path.getmtime(rel_path))}"
        except OSError:
            pass
    return rel_path


def quote_asset_url(url):
    """Percent-encode spaces/reserved path characters while keeping ?v= query intact."""
    if not url:
        return url
    path, sep, query = url.partition("?")
    encoded = urllib.parse.quote(path, safe="/")
    return f"{encoded}{sep}{query}" if sep else encoded


def find_first_existing(base_dir, filenames):
    """Return forward-slash relative path for first existing candidate filename."""
    for name in filenames:
        p = os.path.join(base_dir, name)
        if os.path.exists(p):
            return p.replace("\\", "/")
    return None


def _find_background_in_dir(target_dir):
    if not os.path.exists(target_dir):
        return None
    exact = find_first_existing(target_dir, ["background.webp", "background.jpg", "background.jpeg", "background.png", "background.jfif"])
    if exact:
        return exact
    for f in sorted(os.listdir(target_dir), key=natural_sort_key):
        if f.lower().startswith("background") and os.path.splitext(f)[1].lower() in PAGE_IMG_EXTS:
            return os.path.join(target_dir, f).replace("\\", "/")
    return None


def get_page_background_and_overlay(page_dir):
    """Resolve page background image and overlay alpha (falling back to pages/01_home)."""
    resolved_bg = _find_background_in_dir(page_dir) or _find_background_in_dir("pages/01_home")

    raw_opacity = None
    for json_path in (os.path.join(page_dir, "content.json"), "pages/01_home/content.json"):
        data = load_json(json_path, {})
        if isinstance(data, dict):
            val = data.get("overlayOpacity") or data.get("bgOverlayOpacity") or data.get("opacity")
            if val is not None:
                raw_opacity = val
                break

    try:
        opacity_num = float(raw_opacity) if raw_opacity is not None else 65.0
        if 0.0 < opacity_num < 1.0:
            opacity_num *= 100.0
        opacity_num = max(0.0, min(100.0, opacity_num))
    except (ValueError, TypeError):
        opacity_num = 65.0

    overlay_alpha = round(opacity_num / 100.0, 3)
    resolved_bg_url = with_mtime_query(resolved_bg)

    bg_img_html = f'<div class="site-bg-image" style="background-image: url(\'{resolved_bg_url}\');"></div>' if resolved_bg_url else ''
    bg_overlay_html = f'<div class="site-bg-overlay" style="opacity: {overlay_alpha};"></div>' if resolved_bg_url else ''
    return bg_img_html, bg_overlay_html, resolved_bg_url, overlay_alpha


def get_home_background_list(home_dir="pages/01_home"):
    """Return sorted [(rel_path, url_with_mtime, media_type), ...] for home backgrounds."""
    if not os.path.exists(home_dir):
        return []
    video_exts = {'.mp4', '.webm'}
    media_exts = PAGE_IMG_EXTS | video_exts
    results = []

    for f in sorted(os.listdir(home_dir), key=natural_sort_key):
        ext = os.path.splitext(f)[1].lower()
        if f.lower().startswith("background") and ext in media_exts:
            path = os.path.join(home_dir, f).replace("\\", "/")
            media_type = 'video' if ext in video_exts else 'image'
            results.append((path, with_mtime_query(path), media_type))
    return results


# ------------------------------------------------------------------------------
# Tracking, SEO, Navigation & Shared HTML Document Shell
# ------------------------------------------------------------------------------
def get_tracking_tags():
    """Resolve Google Analytics (GA4) and Google Tag Manager (GTM) snippets."""
    cfg = get_site_config()
    home_cfg = load_json("pages/01_home/content.json", {})
    sources = [cfg, home_cfg]

    ga_id = None
    gtm_id = None
    for src in sources:
        if not isinstance(src, dict):
            continue
        if not ga_id:
            for k in ("googleAnalyticsId", "gaId", "analyticsId", "googleAnalytics", "ga_id"):
                val = src.get(k)
                if isinstance(val, str) and val.strip():
                    ga_id = val.strip()
                    break
        if not gtm_id:
            for k in ("googleTagManagerId", "gtmId", "tagManagerId", "googleTagManager", "gtm_id"):
                val = src.get(k)
                if isinstance(val, str) and val.strip():
                    gtm_id = val.strip()
                    break

    ga_id = ga_id or "G-PTGZPG59ZS"
    gtm_id = gtm_id or "GTM-WZLPRH6G"

    head_snippets, body_snippets = [], []
    if gtm_id != "GTM-XXXXXXXX":
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

    if ga_id != "G-XXXXXXXXXX":
        head_snippets.append(f'''  <!-- Google tag (gtag.js) -->
  <script async src="https://www.googletagmanager.com/gtag/js?id={ga_id}"></script>
  <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){{dataLayer.push(arguments);}}
    gtag('js', new Date());
    gtag('config', '{ga_id}');
  </script>''')

    return "\n".join(head_snippets), "\n".join(body_snippets)


def get_seo_meta_tags(page_url, page_title, page_desc, is_private=False, image_url=None):
    """Generate robots, canonical, Open Graph, and Twitter Card meta tags."""
    if is_private:
        return '''  <!-- SEO: Strictly Private Page (Excluded from Google Indexing) -->
  <meta name="robots" content="noindex, nofollow, noarchive">'''

    cfg = get_site_config()
    site_url = str(cfg.get("siteUrl") or cfg.get("url") or "https://pbhat99.github.io").strip().rstrip('/')
    canonical_url = f"{site_url}/{page_url}" if page_url else site_url

    if not image_url:
        image_url = f"{site_url}/_engine/images/logo.png"
    elif not image_url.startswith("http"):
        image_url = f"{site_url}/{image_url.lstrip('/')}"

    clean_title = esc(str(page_title or "").strip())
    clean_desc = esc(str(page_desc or "").strip())

    return f'''  <!-- SEO & Canonical Link -->
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical_url}">

  <!-- Open Graph / Social Media Sharing -->
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


def generate_nav_html(active_page="home"):
    """Render unified header navigation bar."""
    nav_items = [
        ("index.html", "home", "Home"),
        ("vfx.html", "vfx", "VFX"),
        ("ai-comfy.html", "ai-comfy", "AI / Comfy"),
        ("photography.html", "photography", "Photography"),
        ("about.html", "about", "About"),
        ("blog.html", "blog", "Blog"),
    ]
    links_html = "".join(
        f'<li><a href="{href}"{" class=\"active\"" if key == active_page else ""}>{label}</a></li>'
        for href, key, label in nav_items
    )
    return f'''  <header class="site-header">
    <div class="nav-wrapper">
      <a href="index.html" class="brand-logo">
        <img src="_engine/images/logo.png" alt="Pra Motions Logo" width="34" height="34">
        <span>Pra - <span class="brand-badge">Motions</span></span>
      </a>

      <button type="button" class="mobile-nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>

      <ul class="nav-links">
        {links_html}
      </ul>
    </div>
  </header>'''


BACK_TO_TOP_HTML = '''  <button type="button" id="back-to-top" class="back-to-top" aria-label="Jump to top" title="Jump to top">
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
      <polyline points="18 15 12 9 6 15"></polyline>
    </svg>
  </button>'''

PERSON_JSON_LD = '''  <!-- Structured Data (JSON-LD) for Google Rich Results -->
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


def render_document(
    *,
    page_title,
    meta_desc,
    seo_meta,
    nav_active,
    stylesheets,
    main_html,
    tracking_tags,
    extra_head="",
    extra_body_html="",
    body_scripts="",
    bg_img_html="",
    bg_overlay_html="",
    wrap_standard_main=True,
    include_back_to_top=True,
):
    """Render shared HTML5 shell across all pages."""
    ga_head_tag, ga_body_tag = tracking_tags
    css_links = "\n".join(f'  <link rel="stylesheet" href="_engine/css/{s}">' for s in stylesheets)

    if wrap_standard_main:
        main_block = f'''  <main id="main-content" class="page-main">
    <div class="container-wide">
{main_html}
    </div>
  </main>'''
    else:
        main_block = main_html

    bg_block = "\n".join(x for x in (f"  {bg_img_html}" if bg_img_html else "", f"  {bg_overlay_html}" if bg_overlay_html else "") if x)
    extra_head_block = f"\n{extra_head}" if extra_head else ""
    extra_body_block = f"\n{extra_body_html}" if extra_body_html else ""
    scripts_block = f"\n{body_scripts}" if body_scripts else ""
    back_to_top_block = f"\n{BACK_TO_TOP_HTML}" if include_back_to_top else ""

    return f'''<!DOCTYPE html>
<html lang="en">
<head>
{ga_head_tag}
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(page_title)}</title>
  <meta name="description" content="{esc(meta_desc)}">
{seo_meta}{extra_head_block}
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link rel="stylesheet" href="_engine/css/fonts.css">
{css_links}
</head>
<body>
{ga_body_tag}
  <a href="#main-content" class="skip-link">Skip to main content</a>
{bg_block}

{generate_nav_html(nav_active)}

{main_block}{extra_body_block}{scripts_block}
{back_to_top_block}
</body>
</html>
'''


# ------------------------------------------------------------------------------
# WebP Optimization
# ------------------------------------------------------------------------------
def convert_image_to_webp(src_path, webp_path, delete_source=True):
    """Convert a raster source image to optimized WebP preserving alpha transparency."""
    from PIL import Image
    with Image.open(src_path) as im:
        has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
        im_conv = im.convert('RGBA' if has_alpha else 'RGB')
        im_conv.save(webp_path, 'WEBP', quality=(90 if has_alpha else 85), method=6)

    if delete_source and os.path.exists(src_path) and os.path.abspath(src_path) != os.path.abspath(webp_path):
        try:
            os.remove(src_path)
        except OSError as rm_err:
            print(f"  [Warning] Could not remove {src_path}: {rm_err}")


def convert_all_pages_images_to_webp(root_dir="pages"):
    """Convert non-WebP images across pages/ (excluding forDownload/) and rewrite JSON/MD refs."""
    if not os.path.exists(root_dir):
        return

    replacements = {}
    for current_root, _, files in os.walk(root_dir):
        if "fordownload" in current_root.replace("\\", "/").lower():
            continue
        for f in files:
            if f.startswith('.'):
                continue
            base, ext = os.path.splitext(f)
            if ext.lower() in VALID_IMG_EXTS:
                src_path = os.path.join(current_root, f)
                webp_path = os.path.join(current_root, f"{base}.webp")
                try:
                    convert_image_to_webp(src_path, webp_path, delete_source=True)
                    replacements[f] = f"{base}.webp"
                    print(f"  [Site WebP] Converted & replaced: {src_path} -> {base}.webp")
                except Exception as err:
                    print(f"  [WebP Error] {src_path}: {err}")

    if not replacements:
        return

    for current_root, _, files in os.walk(root_dir):
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


def _ensure_resized_webp(src_path, out_webp, max_dim=900, quality=82):
    """Create or refresh a proportionally resized WebP derivative when missing or outdated."""
    from PIL import Image

    if os.path.exists(out_webp):
        try:
            if os.path.getmtime(out_webp) >= os.path.getmtime(src_path):
                return False
        except OSError:
            pass

    os.makedirs(os.path.dirname(out_webp), exist_ok=True)
    with Image.open(src_path) as im:
        has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
        w, h = im.size
        target = im
        if max(w, h) > max_dim:
            scale = max_dim / float(max(w, h))
            new_size = (max(1, int(round(w * scale))), max(1, int(round(h * scale))))
            target = im.resize(new_size, Image.Resampling.LANCZOS)
        target = target.convert('RGBA' if has_alpha else 'RGB')
        target.save(out_webp, 'WEBP', quality=quality, method=6)
    return True


# ------------------------------------------------------------------------------
# Page Builders
# ------------------------------------------------------------------------------
def build_home_page(tracking_tags, generate_thumbs=True):
    home_dir = "pages/01_home"
    home_data = load_json(os.path.join(home_dir, "content.json"), {
        "designation": "Senior Visual Effects Compositor @ DNEG",
        "tagline": "CG is not just faking, its adding beautiful layers of lie on the ugly truth.",
        "overlayOpacity": 60
    })

    fixed_name = "Prasannakumar T Bhat"
    page_title = str(home_data.get("pageTitle", fixed_name)).strip() or fixed_name
    designation = str(home_data.get("designation", "")).strip()
    tagline = str(home_data.get("tagline", "")).strip()
    wipe_angle = str(home_data.get("wipeAngle", home_data.get("wipeFrom", "45"))).strip() or "45"

    _, _, fallback_bg, home_alpha = get_page_background_and_overlay(home_dir)
    home_bgs = get_home_background_list(home_dir)
    if not home_bgs and fallback_bg:
        home_bgs = [(fallback_bg.split('?')[0], fallback_bg, 'image')]

    # Generate mobile-only proxy strictly for slide 0 (background_00) so mobile avoids full 4K download
    home_proxy_dir = os.path.join("_engine", "proxies", "home")
    mobile_bg0_url = None
    if home_bgs and home_bgs[0][2] == 'image':
        bg0_path = home_bgs[0][0]
        proxy_name = os.path.splitext(os.path.basename(bg0_path))[0] + ".webp"
        proxy_fs = os.path.join(home_proxy_dir, proxy_name)
        if os.path.exists(home_proxy_dir):
            for stale in os.listdir(home_proxy_dir):
                if stale != proxy_name:
                    try:
                        os.remove(os.path.join(home_proxy_dir, stale))
                    except OSError:
                        pass
        if generate_thumbs:
            try:
                if _ensure_resized_webp(bg0_path, proxy_fs, max_dim=1280, quality=82):
                    print(f"  -> [Home Mobile Proxy] Generated {proxy_fs.replace(chr(92), '/')}")
            except Exception as err:
                print(f"  [Proxy Warning] {bg0_path}: {err}")
        if os.path.exists(proxy_fs):
            mobile_bg0_url = with_mtime_query(proxy_fs.replace("\\", "/"))

    slides_html = []
    for idx, (bg_path, bg_url, media_type) in enumerate(home_bgs):
        if media_type == 'video':
            ext_name = os.path.splitext(bg_path)[1].lower().lstrip('.')
            mime_type = f"video/{ext_name}"
            if idx == 0:
                slides_html.append(
                    f'      <div class="home-bg-slide is-active" data-index="{idx}" data-type="video" data-loaded="true">\n'
                    f'        <video class="home-bg-slide-video" autoplay loop muted playsinline preload="metadata">\n'
                    f'          <source src="{bg_url}" type="{mime_type}">\n'
                    f'        </video>\n'
                    f'      </div>'
                )
            else:
                slides_html.append(
                    f'      <div class="home-bg-slide" data-index="{idx}" data-type="video" data-video-src="{bg_url}" data-video-type="{mime_type}">\n'
                    f'        <video class="home-bg-slide-video" loop muted playsinline preload="none"></video>\n'
                    f'      </div>'
                )
        else:
            if idx == 0:
                desktop_bg_url = quote_asset_url(bg_url)
                mobile_srcset = quote_asset_url(mobile_bg0_url) if mobile_bg0_url else None
                if mobile_srcset:
                    media_html = (
                        f'          <picture>\n'
                        f'            <source media="(max-width: 860px)" srcset="{esc(mobile_srcset)}">\n'
                        f'            <img src="{esc(desktop_bg_url)}" alt="" class="home-bg-slide-img" fetchpriority="high" decoding="async">\n'
                        f'          </picture>'
                    )
                else:
                    media_html = f'          <img src="{esc(desktop_bg_url)}" alt="" class="home-bg-slide-img" fetchpriority="high" decoding="async">'
                slides_html.append(
                    f'      <div class="home-bg-slide is-active" data-index="{idx}" data-type="image" data-loaded="true">\n'
                    f'        <div class="home-bg-slide-inner">\n'
                    f'{media_html}\n'
                    f'        </div>\n'
                    f'      </div>'
                )
            else:
                slides_html.append(
                    f'      <div class="home-bg-slide" data-index="{idx}" data-type="image" data-bg="{bg_url}">\n'
                    f'        <div class="home-bg-slide-inner"></div>\n'
                    f'      </div>'
                )

    slider_html = (
        f'    <div class="home-bg-slider" id="home-bg-slider" data-wipe-angle="{esc(wipe_angle)}" data-wipe-from="{esc(wipe_angle)}" aria-hidden="true">\n'
        + "\n".join(slides_html)
        + "\n    </div>"
    ) if home_bgs else ""
    overlay_html = f'<div class="home-bg-overlay" style="opacity: {home_alpha};"></div>' if home_bgs else ""

    designation_html = f'<p class="hero-designation-plain">{esc(designation)}</p>' if designation else ""
    tagline_html = f'<p class="hero-tagline-plain">"{esc(tagline)}"</p>' if tagline else ""

    home_desc = f"{fixed_name} - {designation}. {tagline}".strip()
    preload_tags = []
    if home_bgs and home_bgs[0][2] == 'image':
        desktop_preload = quote_asset_url(home_bgs[0][1])
        if mobile_bg0_url:
            preload_tags.append(f'  <link rel="preload" as="image" href="{esc(desktop_preload)}" fetchpriority="high" media="(min-width: 861px)">')
            preload_tags.append(f'  <link rel="preload" as="image" href="{esc(quote_asset_url(mobile_bg0_url))}" fetchpriority="high" media="(max-width: 860px)">')
        else:
            preload_tags.append(f'  <link rel="preload" as="image" href="{esc(desktop_preload)}" fetchpriority="high">')
    extra_head = "\n".join(preload_tags + [PERSON_JSON_LD])

    main_html = f'''  <main id="main-content" class="home-fullscreen-container">
{slider_html}
    {overlay_html}
    <canvas id="bg-canvas"></canvas>
    <div class="home-center-stage">
      <h1 class="hero-name-main">{fixed_name}</h1>
      {designation_html}
      {tagline_html}
      <div class="hero-about-wrap">
        <a href="about.html" class="btn-about">About</a>
      </div>
    </div>
  </main>'''

    body_scripts = '''  <script type="module">
    import { initInteractiveBackground } from './_engine/js/interactive-bg.js';
    import { initHomeBackgroundSlider } from './_engine/js/home-bg-slider.js';
    import './_engine/js/main.js';

    initInteractiveBackground('bg-canvas');
    initHomeBackgroundSlider('home-bg-slider');

    fetch('pages/01_home/content.json')
      .then((r) => r.json())
      .then((d) => {
        const raw = d.overlayOpacity ?? d.bgOverlayOpacity ?? d.opacity;
        if (raw !== undefined) {
          let num = parseFloat(raw);
          if (num > 1) num /= 100;
          const overlay = document.querySelector('.home-bg-overlay');
          if (overlay) overlay.style.opacity = Math.max(0, Math.min(1, num));
        }
      })
      .catch(() => {});
  </script>'''

    index_html = render_document(
        page_title=page_title,
        meta_desc=f"{fixed_name} - {designation}",
        seo_meta=get_seo_meta_tags("", page_title, home_desc),
        nav_active="home",
        stylesheets=["main.css", "components.css", "home.css", "responsive.css"],
        main_html=main_html,
        tracking_tags=tracking_tags,
        extra_head=extra_head,
        body_scripts=body_scripts,
        wrap_standard_main=False,
        include_back_to_top=False,
    )
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("  -> Updated index.html")


def build_vfx_page(tracking_tags, generate_thumbs=True):
    vfx_dir = "pages/02_VFX"
    vfx_thumbs_root = os.path.join("_engine", "thumbs", "vfx")
    vfx_content = load_json(os.path.join(vfx_dir, "content.json"), {
        "title": "Visual Effects & Compositing",
        "description": "Production shots, feature film breakdowns, and commercials across world-class visual effects studios."
    })

    vfx_title = str(vfx_content.get("title", "Visual Effects & Compositing")).strip()
    vfx_desc = str(vfx_content.get("description", "")).strip()
    vfx_bg_img_html, vfx_bg_overlay_html, _, _ = get_page_background_and_overlay(vfx_dir)

    company_subdirs = sorted(
        [d for d in os.listdir(vfx_dir) if os.path.isdir(os.path.join(vfx_dir, d)) and not d.startswith('.')],
        reverse=True
    ) if os.path.exists(vfx_dir) else []

    company_sections_html = []
    total_projects_count = 0
    vfx_thumbs_updated = 0
    active_vfx_thumbs = set()
    all_categories = set()

    for comp_idx, comp_folder in enumerate(company_subdirs):
        comp_path = os.path.join(vfx_dir, comp_folder)
        comp_slug = slugify(comp_folder)

        comp_defaults = {
            "companyName": format_title_from_filename(comp_folder),
            "period": "Aug-2021 to Present",
            "designation": "",
            "description": "",
            "color": "#0e1733",
            "link": ""
        }
        comp_info_file = os.path.join(comp_path, "companyInfo.json")
        if not os.path.exists(comp_info_file):
            comp_info_file = os.path.join(comp_path, "company.json")
        comp_info = load_json(comp_info_file, comp_defaults)

        company_name = comp_info.get("companyName") or comp_info.get("name") or comp_defaults["companyName"]
        comp_period = comp_info.get("period", "")
        comp_designation = comp_info.get("designation", "")
        comp_description = comp_info.get("description", "")
        comp_color = comp_info.get("color", "#0e1733")
        comp_link = (comp_info.get("link") or "").strip()
        if not comp_link or comp_link == "#":
            comp_link = f"https://www.google.com/search?q={urllib.parse.quote_plus(company_name)}"

        banner_path = None
        for f in os.listdir(comp_path):
            if os.path.isfile(os.path.join(comp_path, f)) and os.path.splitext(f)[1].lower() in DISPLAY_IMG_EXTS:
                if 'banner' in f.lower() or 'logo' in f.lower():
                    banner_path = f"{comp_path}/{f}".replace("\\", "/")
                    break

        proj_subdirs = sorted(
            [d for d in os.listdir(comp_path) if os.path.isdir(os.path.join(comp_path, d)) and not d.startswith('.')],
            reverse=True
        )

        tiles_html = []
        for p_idx, p_folder in enumerate(proj_subdirs):
            p_folder_path = os.path.join(comp_path, p_folder)
            files_in_proj = os.listdir(p_folder_path)

            proj_img_path = None
            for f in files_in_proj:
                if os.path.splitext(f)[1].lower() in DISPLAY_IMG_EXTS:
                    if any(k in f.lower() for k in ('projectimage', 'thumb', 'image')):
                        proj_img_path = f"{p_folder_path}/{f}".replace("\\", "/")
                        break
            if not proj_img_path:
                for f in files_in_proj:
                    if os.path.splitext(f)[1].lower() in DISPLAY_IMG_EXTS:
                        proj_img_path = f"{p_folder_path}/{f}".replace("\\", "/")
                        break
            if not proj_img_path:
                continue

            # Mobile-only thumbnail derivative (desktop keeps original full-resolution image)
            thumb_name = os.path.splitext(os.path.basename(proj_img_path))[0] + ".webp"
            thumb_fs_path = os.path.join(vfx_thumbs_root, comp_folder, p_folder, thumb_name)
            if generate_thumbs:
                try:
                    if _ensure_resized_webp(proj_img_path, thumb_fs_path, max_dim=720, quality=80):
                        vfx_thumbs_updated += 1
                except Exception as thumb_err:
                    print(f"  [VFX Thumb Warning] {proj_img_path}: {thumb_err}")

            mobile_thumb_rel = thumb_fs_path.replace("\\", "/") if os.path.exists(thumb_fs_path) else None
            if mobile_thumb_rel:
                active_vfx_thumbs.add(os.path.abspath(thumb_fs_path))

            proj_info_file = os.path.join(p_folder_path, "projectInfo.json")
            if not os.path.exists(proj_info_file):
                proj_info_file = os.path.join(p_folder_path, "info.json")
            proj_info = load_json(proj_info_file, {
                "title": format_title_from_filename(p_folder),
                "description": "",
                "category": "commercials",
                "year": "",
                "tags": [],
                "orientation": "horizontal",
                "link": ""
            })

            p_title = proj_info.get("title") or format_title_from_filename(p_folder)
            p_desc = proj_info.get("description", "")
            p_category = (proj_info.get("category") or "commercials").strip().lower()
            all_categories.add(p_category)
            p_year = proj_info.get("year", "")
            p_orientation = str(proj_info.get("orientation", "horizontal")).lower()
            if p_orientation not in ("horizontal", "vertical", "square"):
                p_orientation = "horizontal"

            p_link = (proj_info.get("link") or "").strip()
            if not p_link or p_link == "#":
                p_link = f"https://www.google.com/search?q={urllib.parse.quote_plus(p_title)}"

            raw_tags = proj_info.get("tags") or proj_info.get("tools") or []
            p_tags = (
                [t.strip() for t in raw_tags.split(",") if t.strip()]
                if isinstance(raw_tags, str)
                else [str(t).strip() for t in raw_tags if str(t).strip()]
            )

            cat_label = p_category.replace('-', ' ').replace('_', ' ').title()
            year_span = f'<span class="tile-year">{esc(p_year)}</span>' if p_year else ''
            desc_html = f'<p class="tile-desc">{esc(p_desc)}</p>' if p_desc else ''
            tags_csv = esc(",".join(p_tags))
            tags_buttons = "".join(f'<button type="button" class="tile-tag" data-tag="{esc(t)}">{esc(t)}</button>' for t in p_tags)
            tags_html = f'<div class="tile-tags-wrap">{tags_buttons}</div>' if p_tags else ''

            loading_attr = "eager" if comp_idx == 0 and p_idx < 3 else "lazy"
            img_tag = f'<img src="{esc(proj_img_path)}" alt="{esc(p_title)}" class="tile-img" loading="{loading_attr}" decoding="async">'
            mobile_srcset = quote_asset_url(mobile_thumb_rel) if mobile_thumb_rel else None
            media_html = (
                f'<picture>\n                  <source media="(max-width: 860px)" srcset="{esc(mobile_srcset)}">\n                  {img_tag}\n                </picture>'
                if mobile_srcset else img_tag
            )

            tiles_html.append(f'''
            <article class="project-tile aspect-{p_orientation}" data-category="{esc(p_category)}" data-tags="{tags_csv}">
              <div class="tile-circling-border" aria-hidden="true"></div>
              <div class="tile-inner">
                {media_html}
                <button type="button" class="tile-category-pill" data-filter-category="{esc(p_category)}" title="Filter by {esc(cat_label)}">{esc(cat_label)}</button>
                <a href="{esc(p_link)}" target="_blank" rel="noopener noreferrer" class="tile-more-link" title="More information on {esc(p_title)}">more...</a>
                <div class="tile-hover-overlay">
                  <div class="tile-hover-content">
                    <h3 class="tile-title">
                      <span>{esc(p_title)}</span>
                      {year_span}
                    </h3>
                    {desc_html}
                    {tags_html}
                  </div>
                </div>
              </div>
            </article>''')
            total_projects_count += 1

        meta_items = []
        if comp_period:
            meta_items.append(f'<span class="company-banner-period">{esc(comp_period)}</span>')
        if comp_designation:
            meta_items.append(f'<span class="company-banner-designation">{esc(comp_designation)}</span>')
        meta_html = f'<div class="company-banner-meta">{"<span class=\"company-banner-sep\"> - </span>".join(meta_items)}</div>' if meta_items else ''
        description_html = f'<div class="company-banner-desc">{esc(comp_description)}</div>' if comp_description else ''

        logo_html = (
            f'\n        <a href="{esc(comp_link)}" target="_blank" rel="noopener noreferrer" class="company-banner-logo-wrap is-clickable" title="Visit {esc(company_name)}">'
            f'\n          <img src="{esc(banner_path)}" alt="{esc(company_name)} Logo" class="company-banner-logo-img" loading="{"eager" if comp_idx == 0 else "lazy"}" decoding="async">'
            f'\n        </a>'
        ) if banner_path else ''

        company_sections_html.append(f'''
        <section class="company-section" id="{comp_slug}" data-company="{comp_slug}">
          <div class="company-banner-strip" style="background-color: {esc(comp_color)};">
            <div class="company-banner-info">
              <h2 class="company-banner-heading">{esc(company_name)}</h2>
              {meta_html}
              {description_html}
            </div>{logo_html}
          </div>
          <div class="company-project-grid">
            {"".join(tiles_html)}
          </div>
        </section>''')

    if generate_thumbs and os.path.exists(vfx_thumbs_root):
        for cur_root, _, files in os.walk(vfx_thumbs_root, topdown=False):
            for tf in files:
                tp = os.path.join(cur_root, tf)
                if os.path.abspath(tp) not in active_vfx_thumbs:
                    try:
                        os.remove(tp)
                    except OSError:
                        pass
            if not os.listdir(cur_root) and cur_root != vfx_thumbs_root:
                try:
                    os.rmdir(cur_root)
                except OSError:
                    pass
    if vfx_thumbs_updated:
        print(f"  -> [VFX Mobile Thumbs] Generated/updated {vfx_thumbs_updated} mobile card thumbnails")

    preferred_order = ["commercials", "films", "feature films", "series", "music-videos", "other"]
    sorted_categories = [c for c in preferred_order if c in all_categories]
    sorted_categories.extend(c for c in sorted(all_categories) if c not in sorted_categories)

    filter_buttons = ['<button type="button" class="filter-btn active" data-filter="all">All</button>']
    for cat in sorted_categories:
        label = cat.replace('-', ' ').replace('_', ' ').title()
        filter_buttons.append(f'<button type="button" class="filter-btn" data-filter="{esc(cat)}">{esc(label)}</button>')

    vfx_page_title = str(vfx_content.get("pageTitle", "VFX | Pra - Motions")).strip() or "VFX | Pra - Motions"
    vfx_seo_desc = "Visual Effects & Compositing portfolio of Prasannakumar T Bhat across DNEG, The Mill, and feature film productions."
    vfx_json_ld = '''  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "CollectionPage",
    "name": "Visual Effects Portfolio - Prasannakumar T Bhat",
    "description": "Visual Effects & Compositing portfolio of Prasannakumar T Bhat across DNEG, The Mill, and feature film productions.",
    "author": {
      "@type": "Person",
      "name": "Prasannakumar T Bhat",
      "jobTitle": "Lead Compositor & VFX Artist"
    }
  }
  </script>'''

    main_html = f'''      <div class="section-header">
        <h1 class="section-title">{esc(vfx_title) or "&nbsp;"}</h1>
        <p class="section-desc">{esc(vfx_desc) or "&nbsp;"}</p>
      </div>
      <div class="filter-bar filter-bar-center">
        {"".join(filter_buttons)}
        <span class="tag-filter-status" style="display: none;"></span>
      </div>
      <div class="vfx-companies-container">
        {"".join(company_sections_html)}
      </div>'''

    vfx_html = render_document(
        page_title=vfx_page_title,
        meta_desc=vfx_seo_desc,
        seo_meta=get_seo_meta_tags("vfx.html", vfx_page_title, vfx_seo_desc),
        nav_active="vfx",
        stylesheets=["main.css", "components.css", "responsive.css"],
        main_html=main_html,
        tracking_tags=tracking_tags,
        extra_head=vfx_json_ld,
        body_scripts='  <script type="module" src="_engine/js/main.js"></script>',
        bg_img_html=vfx_bg_img_html,
        bg_overlay_html=vfx_bg_overlay_html,
    )
    with open("vfx.html", "w", encoding="utf-8") as f:
        f.write(vfx_html)
    print(f"  -> Updated vfx.html ({len(company_subdirs)} companies, {total_projects_count} projects)")


def build_photography_page(tracking_tags, generate_thumbs=True):
    from PIL import Image

    photo_dir = "pages/04_photography"
    photos_dir = os.path.join(photo_dir, "photos")
    panos_dir = os.path.join(photo_dir, "panos")
    thumbs_root = os.path.join("_engine", "thumbs", "photography")
    os.makedirs(photos_dir, exist_ok=True)
    os.makedirs(panos_dir, exist_ok=True)
    photo_bg_img_html, photo_bg_overlay_html, _, _ = get_page_background_and_overlay(photo_dir)

    photo_info = load_json(os.path.join(photo_dir, "content.json"), {
        "title": "Photography & Panoramas",
        "description": "High-resolution 360° environment captures, HDRI light probes, and cinematic stills gallery."
    })
    photo_title = str(photo_info.get("title", "Photography & Panoramas")).strip()
    photo_desc = str(photo_info.get("description", "")).strip()

    def clean_photo_title(filename):
        base = os.path.splitext(filename)[0]
        clean = re.sub(r'^\d+[\s_-]*', '', base).replace('_', ' ').replace('-', ' ')
        return ' '.join(clean.split()).strip() or base

    thumbs_updated = 0

    def index_collection(dir_path, sub_kind):
        nonlocal thumbs_updated
        if not os.path.exists(dir_path):
            return []

        thumb_dir = os.path.join(thumbs_root, sub_kind)
        source_files = sorted(f for f in os.listdir(dir_path) if f.lower().endswith('.webp') and not f.startswith('.'))

        # Prune deleted photo/pano thumbnails so stale thumbs never linger
        if os.path.exists(thumb_dir):
            valid_names = set(source_files)
            for existing_t in os.listdir(thumb_dir):
                if existing_t not in valid_names:
                    try:
                        os.remove(os.path.join(thumb_dir, existing_t))
                    except OSError:
                        pass

        items = []
        for f in source_files:
            webp_path = os.path.join(dir_path, f)
            thumb_fs_path = os.path.join(thumb_dir, f)
            w, h, aspect = 1920, 1080, 1.778
            try:
                with Image.open(webp_path) as im:
                    w, h = im.size
                    if h > 0:
                        aspect = round(w / h, 3)
            except Exception:
                pass

            if generate_thumbs:
                try:
                    if _ensure_resized_webp(webp_path, thumb_fs_path, max_dim=900, quality=82):
                        thumbs_updated += 1
                except Exception as thumb_err:
                    print(f"  [Thumb Warning] {webp_path}: {thumb_err}")

            resolved_thumb = thumb_fs_path.replace("\\", "/") if os.path.exists(thumb_fs_path) else webp_path.replace("\\", "/")
            items.append({
                "id": slugify(os.path.splitext(f)[0]),
                "filename": f,
                "title": clean_photo_title(f),
                "webp": webp_path.replace("\\", "/"),
                "thumb": resolved_thumb,
                "width": w,
                "height": h,
                "aspect": aspect
            })
        return items

    photos_list = index_collection(photos_dir, "photos")
    panos_list = index_collection(panos_dir, "panos")
    if thumbs_updated:
        print(f"  -> [Thumbs] Generated/updated {thumbs_updated} photography thumbnails in _engine/thumbs/photography/")

    def make_tile(item, idx, kind):
        asp = item.get("aspect", 2.0 if kind == "panos" else 1.778)
        tile_cls = "pano-tile" if kind == "panos" else "photo-tile"
        data_idx_attr = f'data-pano-idx="{idx}"' if kind == "panos" else f'data-photo-idx="{idx}"'
        thumb_src = item.get("thumb") or item["webp"]
        pano_extras = '''
              <span class="pano-badge">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/><path d="M2 12h20"/></svg>
                360° Panorama
              </span>
              <div class="pano-center-indicator" aria-hidden="true">
                <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" style="margin-left: 2px;"><polygon points="6 3 20 12 6 21 6 3"/></svg>
              </div>''' if kind == "panos" else ""

        html_chunk = f'''
        <div class="waterfall-item" data-type="{kind}" data-aspect="{asp}" style="--aspect: {asp};">
          <article class="project-tile {tile_cls}" {data_idx_attr} tabindex="0" role="button" aria-label="{esc(item['title'])}" title="{esc(item['title'])}" style="--aspect: {asp}; aspect-ratio: {asp};">
            <div class="tile-circling-border" aria-hidden="true"></div>
            <div class="tile-inner" style="aspect-ratio: {asp};">
              <img src="{esc(thumb_src)}" alt="{esc(item['title'])}" class="tile-img" loading="lazy" decoding="async">{pano_extras}
              <div class="tile-hover-overlay">
                <div class="tile-hover-content">
                  <h3 class="tile-title"><span>{esc(item['title'])}</span></h3>
                </div>
              </div>
            </div>
          </article>
        </div>'''
        return (asp, html_chunk)

    photo_tiles = [make_tile(p, idx, "photos") for idx, p in enumerate(photos_list)]
    pano_tiles = [make_tile(p, idx, "panos") for idx, p in enumerate(panos_list)]

    # Dynamically interleave panoramas and photos across 3 shortest-height columns (never IndexError on item count changes)
    interleaved = []
    pi, ph = 0, 0
    while pi < len(pano_tiles) or ph < len(photo_tiles):
        if pi < len(pano_tiles):
            interleaved.append(pano_tiles[pi])
            pi += 1
        for _ in range(2):
            if ph < len(photo_tiles):
                interleaved.append(photo_tiles[ph])
                ph += 1

    cols = [[], [], []]
    col_heights = [0.0, 0.0, 0.0]
    for asp, tile_html in interleaved:
        min_col = min(range(3), key=lambda c: col_heights[c])
        cols[min_col].append(tile_html)
        col_heights[min_col] += 1.0 / max(asp or 1.778, 0.2)

    waterfall_cols_html = "".join(
        f'\n        <div class="waterfall-col">{"".join(c)}\n        </div>'
        for c in cols
    )

    photo_page_title = str(photo_info.get("pageTitle", f"{photo_title} | Pra - Motions")).strip() or f"{photo_title} | Pra - Motions"
    photo_seo_desc = photo_desc or "Photography and 360 interactive panoramas by Prasannakumar T Bhat."

    main_html = f'''      <div class="section-header">
        <h1 class="section-title">{esc(photo_title) or "&nbsp;"}</h1>
        <p class="section-desc">{esc(photo_desc) or "&nbsp;"}</p>
      </div>
      <div class="filter-bar filter-bar-center">
        <button type="button" class="filter-btn active" id="tabBtnAll" data-tab="all">All</button>
        <button type="button" class="filter-btn" id="tabBtnPanos" data-tab="panos">Panoramas</button>
        <button type="button" class="filter-btn" id="tabBtnPhotos" data-tab="photos">Photos</button>
      </div>
      <section class="photo-gallery-section" id="gallery-container">
        <div class="waterfall-container waterfall-3-col" id="photoWaterfallContainer">{waterfall_cols_html}
        </div>
      </section>'''

    modals_html = f'''
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
            <line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
    <div class="viewer-stage" id="photoViewerStage">
      <button type="button" class="viewer-side-arrow viewer-prev-arrow" onclick="navPhotoViewer(-1)" aria-label="Previous photo" title="Previous photo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><polyline points="15 18 9 12 15 6"></polyline></svg>
      </button>
      <div class="viewer-img-container"><img id="photoViewerImg" src="" alt="Photo" class="viewer-main-img"></div>
      <button type="button" class="viewer-side-arrow viewer-next-arrow" onclick="navPhotoViewer(1)" aria-label="Next photo" title="Next photo">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><polyline points="9 18 15 12 9 6"></polyline></svg>
      </button>
    </div>
    <div class="viewer-filmstrip-bar"><div class="filmstrip-track" id="photoFilmstripTrack"></div></div>
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
            <line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>
    <div class="pano-stage">
      <div id="fullscreenPanoContainer" class="pano-webgl-viewport"></div>
      <button type="button" class="viewer-side-arrow viewer-prev-arrow" onclick="navPanoViewer(-1)" aria-label="Previous panorama" title="Previous panorama">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><polyline points="15 18 9 12 15 6"></polyline></svg>
      </button>
      <button type="button" class="viewer-side-arrow viewer-next-arrow" onclick="navPanoViewer(1)" aria-label="Next panorama" title="Next panorama">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="22" height="22"><polyline points="9 18 15 12 9 6"></polyline></svg>
      </button>
    </div>
    <div class="viewer-filmstrip-bar"><div class="filmstrip-track" id="panoFilmstripTrack"></div></div>
  </div>

  <script id="photosData" type="application/json">{json.dumps(photos_list)}</script>
  <script id="panosData" type="application/json">{json.dumps(panos_list)}</script>'''

    body_scripts = '''  <script src="_engine/js/pannellum.js"></script>
  <script src="_engine/js/photography.js"></script>
  <script type="module" src="_engine/js/main.js"></script>'''

    photography_html = render_document(
        page_title=photo_page_title,
        meta_desc=photo_seo_desc,
        seo_meta=get_seo_meta_tags("photography.html", photo_page_title, photo_seo_desc),
        nav_active="photography",
        stylesheets=["main.css", "components.css", "pannellum.css", "photography.css", "responsive.css"],
        main_html=main_html,
        tracking_tags=tracking_tags,
        extra_body_html=modals_html,
        body_scripts=body_scripts,
        bg_img_html=photo_bg_img_html,
        bg_overlay_html=photo_bg_overlay_html,
    )
    with open("photography.html", "w", encoding="utf-8") as f:
        f.write(photography_html)
    print(f"  -> Updated photography.html ({len(photos_list)} stills, {len(panos_list)} 360 panos)")


def build_about_page(tracking_tags):
    about_dir = "pages/05_about" if os.path.exists("pages/05_about") else "pages/05_about-me"
    about_bg_img_html, about_bg_overlay_html, _, _ = get_page_background_and_overlay(about_dir)

    about_data = {
        "name": "Prasannakumar T Bhat",
        "designation": "Visual Effects Compositor",
        "experience": "",
        "info": "For <strong>10+ years</strong>, I've been weaving magic with pixels in the world of visual effects.",
        "showreelLink": "https://vimeo.com/835414002"
    }
    for cand_json in ("content.json", "aboutMe.json"):
        p = os.path.join(about_dir, cand_json)
        if os.path.exists(p):
            about_data = load_json(p, about_data)

    name = str(about_data.get("name", "Prasannakumar T Bhat"))
    designation = str(about_data.get("designation", "Visual Effects Compositor"))
    experience = str(about_data.get("experience", ""))
    info_raw = str(about_data.get("info", ""))
    resume_link = about_data.get("resumeLink") or (f"{about_dir}/resume.pdf" if os.path.exists(f"{about_dir}/resume.pdf") else "#")
    cover_letter_link = about_data.get("coverLetterLink") or (f"{about_dir}/coverLetter.pdf" if os.path.exists(f"{about_dir}/coverLetter.pdf") else "#")
    showreel_title = str(
        about_data.get("showreelTitle") or about_data.get("showreel title")
        or about_data.get("showreelHeading") or about_data.get("videoTitle") or ""
    ).strip()

    info_bg_color = about_data.get("infoBGcolor") or about_data.get("infoBgColor") or "#131e42"
    info_bg_opacity = about_data.get("infoBGopacity", about_data.get("infoBgOpacity", about_data.get("info_bg_opacity", 75)))
    info_bg_rgba = hex_to_rgba(info_bg_color, info_bg_opacity)

    showreel_url = str(
        about_data.get("showreelLink") or about_data.get("showreel link") or about_data.get("showreel")
        or about_data.get("showreelUrl") or about_data.get("showreel url")
        or about_data.get("vimeoUrl") or about_data.get("vimeoLink") or about_data.get("vimeo") or ""
    ).strip()

    info_paras = [p.strip() for p in info_raw.split("\n\n") if p.strip()] or ([info_raw.strip()] if info_raw else [])
    paragraphs_html = "\n".join(f"<p>{p.replace(chr(10), '<br>')}</p>" for p in info_paras)

    profile_img = find_first_existing(about_dir, ["profilePic.webp", "profilePic.jpg", "profilePic.png", "profile.webp", "profile.jpg", "profile.png"]) or "_engine/images/logo.png"

    # Known Tools strip
    known_tools_dir = os.path.join(about_dir, "knownTools")
    tools_cards_html = []
    if os.path.exists(known_tools_dir):
        tool_files = sorted(f for f in os.listdir(known_tools_dir) if os.path.splitext(f)[1].lower() in DISPLAY_IMG_EXTS)
        for tf in tool_files:
            tf_path = f"{known_tools_dir}/{tf}".replace("\\", "/")
            raw_name = os.path.splitext(tf)[0]
            tool_name = re.sub(r'^\d+[\s_-]*', '', raw_name).replace('_', ' ').replace('-', ' ').title()
            tools_cards_html.append(f'''
          <div class="known-tool-card" title="{esc(tool_name)}">
            <img src="{esc(tf_path)}" alt="{esc(tool_name)}" class="known-tool-img" loading="lazy" decoding="async">
            <div class="known-tool-hover"><span class="known-tool-name">{esc(tool_name)}</span></div>
          </div>''')

    tools_section_html = ""
    if tools_cards_html:
        num_tools = len(tools_cards_html)
        if num_tools <= 4:
            tool_gap, tool_pad = "clamp(24px, 3.5vw, 42px)", "12px"
        elif num_tools <= 7:
            tool_gap, tool_pad = "clamp(16px, 2.2vw, 26px)", "9px"
        elif num_tools <= 10:
            tool_gap, tool_pad = "clamp(10px, 1.5vw, 18px)", "7px"
        elif num_tools <= 12:
            tool_gap, tool_pad = "clamp(7px, 1.1vw, 13px)", "5px"
        else:
            tool_gap, tool_pad = "clamp(4px, 0.8vw, 8px)", "4px"
        tools_section_html = f'''
      <section class="known-tools-section">
        <div class="known-tools-strip" style="--tool-count: {num_tools}; --tool-gap: {tool_gap}; --tool-pad: {tool_pad};">
          {"".join(tools_cards_html)}
        </div>
      </section>'''

    # Showreel Embed
    showreel_section_html = ""
    if showreel_url:
        embed_src, allow_attr = None, "autoplay; fullscreen; picture-in-picture"
        yt_match = re.search(r'(?:youtube\.com\/(?:watch\?.*?v=|embed\/|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})', showreel_url)
        if yt_match:
            embed_src = f"https://www.youtube.com/embed/{yt_match.group(1)}?rel=0"
            allow_attr = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
        else:
            vimeo_match = re.search(r'vimeo\.com\/(?:video\/|channels\/[^\/]+\/|manage\/videos\/)?(\d{6,})', showreel_url)
            if not vimeo_match and "vimeo" in showreel_url.lower():
                vimeo_match = re.search(r'(\d{6,})', showreel_url)
            if vimeo_match:
                embed_src = f"https://player.vimeo.com/video/{vimeo_match.group(1)}?title=0&byline=0&portrait=0"
            elif "embed" in showreel_url:
                embed_src = showreel_url

        if embed_src:
            video_header_html = f'<div class="about-video-header"><h2 class="about-video-heading">{esc(showreel_title)}</h2></div>' if showreel_title else ""
            showreel_section_html = f'''
      <section class="about-video-card" style="--info-bg: {info_bg_rgba};">
        {video_header_html}
        <div class="about-video-container">
          <iframe src="{esc(embed_src)}" allow="{allow_attr}" allowfullscreen loading="lazy" title="{esc(showreel_title or 'VFX Showreel')} - {esc(name)}"></iframe>
        </div>
      </section>'''

    # Contact lines
    contact_lines_data = about_data.get("contactInfoLines") or about_data.get("contactLines") or about_data.get("infoLines")
    contact_lines_html = []
    if isinstance(contact_lines_data, list):
        for item in contact_lines_data:
            if isinstance(item, dict):
                label = str(item.get("label") or item.get("key") or "")
                val = str(item.get("value") or item.get("text") or item.get("val") or "")
                link = str(item.get("link") or item.get("url") or "")
                label_html = f'<span class="contact-line-label">{esc(label)}:</span>' if label else ''
                if link:
                    val_html = f'<a href="{esc(link)}" target="_blank" rel="noopener noreferrer">{esc(val)}</a>'
                elif '@' in val and not val.startswith('http'):
                    val_html = f'<a href="mailto:{esc(val)}">{esc(val)}</a>'
                else:
                    val_html = f'<strong>{esc(val)}</strong>' if 'phone' in label.lower() else esc(val)
                contact_lines_html.append(f'<div class="contact-line-item">{label_html}<span class="contact-line-val">{val_html}</span></div>')
            elif isinstance(item, str) and item.strip():
                contact_lines_html.append(f'<div class="contact-line-item"><span class="contact-line-val">{esc(item.strip())}</span></div>')

    contact_img_path = find_first_existing(about_dir, ["contact.webp", "contact.jpg", "contact.png", "contact.jpeg"])
    contact_img_html = (
        f'\n          <div class="contact-image-wrap">\n            <img src="{esc(contact_img_path)}" alt="Contact Visual" class="contact-img" loading="lazy" decoding="async">\n          </div>'
    ) if contact_img_path else ""

    # Social Media Tiles
    social_tiles_html = []
    social_folder = next((os.path.join(about_dir, d) for d in ("social", "socialMedia") if os.path.isdir(os.path.join(about_dir, d))), None)
    if social_folder:
        social_json = next((os.path.join(social_folder, j) for j in ("social.json", "socialMedia.json", "links.json") if os.path.exists(os.path.join(social_folder, j))), None)
        social_items = load_json(social_json, []) if social_json else []
        if isinstance(social_items, list):
            for s_item in social_items:
                img_name = s_item.get("image") or s_item.get("image name") or s_item.get("icon") or ""
                s_link = (s_item.get("link") or s_item.get("url") or "").strip()
                s_name = s_item.get("name") or s_item.get("title") or os.path.splitext(img_name)[0].title()
                if not s_link or s_link == "#":
                    s_link = f"https://www.google.com/search?q={urllib.parse.quote_plus(s_name)}"

                img_base = os.path.splitext(img_name)[0]
                resolved_img = next((f"{img_base}{ext}" for ext in (".webp", ".png", ".jpg", ".jpeg") if os.path.exists(os.path.join(social_folder, f"{img_base}{ext}"))), img_name)
                if os.path.exists(os.path.join(social_folder, resolved_img)):
                    s_img_path = f"{social_folder}/{resolved_img}".replace("\\", "/")
                    social_tiles_html.append(f'''
            <a href="{esc(s_link)}" target="_blank" rel="noopener noreferrer" class="social-tile" title="{esc(s_name)}">
              <img src="{esc(s_img_path)}" alt="{esc(s_name)}" class="social-icon-img" loading="lazy" decoding="async">
            </a>''')

    social_section_html = f'<div class="about-social-row">{"".join(social_tiles_html)}</div>' if social_tiles_html else ""
    meta_role = f"{designation} &bull; {experience}" if experience else designation

    page_title = str(about_data.get("title", "")).strip()
    page_desc = str(about_data.get("description", "")).strip()
    header_html = "" if not (page_title or page_desc) else f'''      <div class="section-header">
        <p class="section-title">{esc(page_title) or "&nbsp;"}</p>
        <p class="section-desc">{esc(page_desc) or "&nbsp;"}</p>
      </div>\n'''

    about_page_title = str(about_data.get("pageTitle", f"About | {name}")).strip() or f"About | {name}"
    about_seo_desc = f"{name} - {designation}. {experience}. Production visual effects, compositing breakdown, and workflow automation."

    main_html = f'''{header_html}      <div class="about-grid">
        <div class="about-profile-col">
          <div class="project-tile aspect-vertical about-profile-tile">
            <div class="tile-circling-border" aria-hidden="true"></div>
            <div class="tile-inner">
              <img src="{esc(profile_img)}" alt="{esc(name)}" class="tile-img" decoding="async">
            </div>
          </div>
        </div>

        <div class="about-bio-col" style="--info-bg: {info_bg_rgba};">
          <div class="about-bio-top">
            <h1 class="about-name">{esc(name)}</h1>
            <div class="about-role-strip">{meta_role}</div>
            <div class="about-paragraphs">{paragraphs_html}</div>
          </div>
          <div class="about-bio-bottom">
            {social_section_html}
            <div class="about-actions-wrap">
              <a href="{esc(resume_link)}" class="btn btn-primary" download>Resume</a>
              <a href="{esc(cover_letter_link)}" class="btn btn-primary" download>Cover Letter</a>
            </div>
          </div>
        </div>
      </div>
      {showreel_section_html}
      {tools_section_html}
      <section id="contact" class="contact-card">
        <div class="contact-content-grid">
          <div class="contact-info-col">
            <h2 class="contact-heading">Contact Information</h2>
            <div class="contact-lines-list">{"".join(contact_lines_html)}</div>
          </div>{contact_img_html}
        </div>
      </section>'''

    about_html = render_document(
        page_title=about_page_title,
        meta_desc=f"{name} - {designation}. {experience}.",
        seo_meta=get_seo_meta_tags("about.html", about_page_title, about_seo_desc, image_url=profile_img),
        nav_active="about",
        stylesheets=["main.css", "components.css", "responsive.css"],
        main_html=main_html,
        tracking_tags=tracking_tags,
        extra_head=PERSON_JSON_LD,
        body_scripts='  <script type="module" src="_engine/js/main.js"></script>',
        bg_img_html=about_bg_img_html,
        bg_overlay_html=about_bg_overlay_html,
    )
    with open("about.html", "w", encoding="utf-8") as f:
        f.write(about_html)
    print("  -> Updated about.html")

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


def build_ai_comfy_page(tracking_tags):
    ai_dir = "pages/03_ai-comfy"
    ai_bg_img_html, ai_bg_overlay_html, _, _ = get_page_background_and_overlay(ai_dir)

    ai_info = load_json(os.path.join(ai_dir, "content.json"), {
        "title": "ComfyUI Pipelines & AI Toolsets",
        "description": "Bridging the gap between cutting-edge Diffusion models and film-grade visual effects pipelines."
    })
    ai_title = str(ai_info.get("title", "ComfyUI Pipelines & AI Toolsets")).strip()
    ai_desc = str(ai_info.get("description", "")).strip()

    workflow_img = "pages/03_ai-comfy/workflows/comfyui-production-pipeline.webp"
    if not os.path.exists(workflow_img):
        workflow_img = "pages/03_ai-comfy/workflows/comfyui-production-pipeline.png"

    ai_page_title = str(ai_info.get("pageTitle", f"{ai_title} | Pra - Motions")).strip() or f"{ai_title} | Pra - Motions"
    ai_seo_desc = ai_desc or "ComfyUI pipelines, automated cleanup nodes, and custom AI VFX workflows."

    main_html = f'''      <div class="section-header">
        <h1 class="section-title">{esc(ai_title) or "&nbsp;"}</h1>
        <p class="section-desc">{esc(ai_desc) or "&nbsp;"}</p>
      </div>

      <div class="ai-graph-card">
        <div class="ai-graph-header">
          <span class="ai-graph-eyebrow">Production Workflow Graph</span>
          <h2 class="ai-graph-title">ComfyUI VFX Production Pipeline Graph</h2>
          <p class="ai-graph-subtitle">Full interactive visual graph. Click image to open high-resolution zoom in Lightbox.</p>
        </div>
        <div class="ai-graph-media">
          <img src="{esc(workflow_img)}" alt="ComfyUI Production Pipeline Architecture" class="ai-graph-img" data-lightbox data-caption="ComfyUI Master VFX Production Workflow Architecture" decoding="async">
        </div>
      </div>

      <h2 class="ai-section-heading">Production ComfyUI Workflows</h2>
      <div class="ai-workflows-grid">
        <div class="ai-workflow-card">
          <div class="ai-workflow-top">
            <span class="ai-workflow-badge">PLATE INPAINTING</span>
            <span class="ai-workflow-stack">ComfyUI + LaMa</span>
          </div>
          <h3 class="ai-workflow-title">Automated 4K Clean-Plate Generator</h3>
          <p class="ai-workflow-desc">Converts roto tracking markers and harness wires into seamless 4K background textures without seam artifacts or optical degradation.</p>
          <div class="ai-workflow-io">
            <div><strong>Inputs:</strong> Live Plate + Roto Matte</div>
            <div><strong>Outputs:</strong> 16-bit Float EXR Clean Plate</div>
          </div>
          <a href="blog.html#comfyui-portable-custom-nodes" class="btn btn-secondary ai-workflow-btn"><span>Read Setup Tutorial</span></a>
        </div>

        <div class="ai-workflow-card">
          <div class="ai-workflow-top">
            <span class="ai-workflow-badge badge-alt">RELIGHTING / COMP</span>
            <span class="ai-workflow-stack">Marigold + IC-Light</span>
          </div>
          <h3 class="ai-workflow-title">Depth-Guided Shot Relighting</h3>
          <p class="ai-workflow-desc">Derives photoreal metric depth maps and surface normals directly from 2D footage to cast directional rim lights, specular glints, and volume fog.</p>
          <div class="ai-workflow-io">
            <div><strong>Nodes:</strong> Marigold Depth, IC-Light, VHS</div>
            <div><strong>Outputs:</strong> Normal Pass + Rim Key Light</div>
          </div>
          <a href="blog.html#facefusion-windows-portable" class="btn btn-secondary ai-workflow-btn"><span>View Implementation</span></a>
        </div>
      </div>'''

    body_scripts = '''  <script src="_engine/js/glightbox.min.js"></script>
  <script type="module" src="_engine/js/main.js"></script>'''

    ai_html = render_document(
        page_title=ai_page_title,
        meta_desc=ai_seo_desc,
        seo_meta=get_seo_meta_tags("ai-comfy.html", ai_page_title, ai_seo_desc),
        nav_active="ai-comfy",
        stylesheets=["main.css", "components.css", "glightbox.min.css", "responsive.css"],
        main_html=main_html,
        tracking_tags=tracking_tags,
        body_scripts=body_scripts,
        bg_img_html=ai_bg_img_html,
        bg_overlay_html=ai_bg_overlay_html,
    )
    with open("ai-comfy.html", "w", encoding="utf-8") as f:
        f.write(ai_html)
    print("  -> Updated ai-comfy.html")


def build_blog_page(tracking_tags):
    blog_dir = "pages/06_blog"
    blog_bg_img_html, blog_bg_overlay_html, blog_resolved_bg, blog_overlay_alpha = get_page_background_and_overlay(blog_dir)
    reader_bg_html = (
        f'<div class="reader-bg-image" style="background-image: url(\'{blog_resolved_bg}\');"></div>\n'
        f'    <div class="reader-bg-overlay" style="opacity: {blog_overlay_alpha};"></div>'
    ) if blog_resolved_bg else ''

    blog_info = load_json(os.path.join(blog_dir, "content.json"), {
        "title": "Technical Blog & Guides",
        "description": "Practical setups, automation scripts, compositing breakdowns, and workflow optimization for VFX & AI artists."
    })
    blog_title = str(blog_info.get("title", "Technical Blog & Guides")).strip()
    blog_desc = str(blog_info.get("description", "")).strip()

    posts_base_dir = os.path.join(blog_dir, "posts")
    parsed_posts = []
    month_names = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]

    def resolve_post_asset_path(folder_path, raw_src):
        clean = raw_src.split('?')[0].strip()
        if clean.startswith(("http", "/", "pages/")):
            return clean
        base, _ = os.path.splitext(clean)
        webp_path = os.path.join(folder_path, f"{base}.webp")
        if os.path.exists(webp_path):
            return f"{folder_path}/{base}.webp".replace("\\", "/")
        return f"{folder_path}/{clean}".replace("\\", "/")

    if os.path.exists(posts_base_dir):
        post_subdirs = sorted(
            [d for d in os.listdir(posts_base_dir) if os.path.isdir(os.path.join(posts_base_dir, d))],
            reverse=True
        )
        for folder_name in post_subdirs:
            folder_path = os.path.join(posts_base_dir, folder_name)
            date_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})', folder_name)
            post_date = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}" if date_match else "2026-01-01"

            post_meta = load_json(os.path.join(folder_path, "post.json"), {
                "title": format_title_from_filename(folder_name),
                "date": post_date,
                "category": "General",
                "tags": [],
                "subheading": "",
                "thumbnail": "",
                "author": "Prasannakumar T Bhat",
                "readTime": "5 min read"
            })
            post_meta["date"] = post_date

            md_content = ""
            for md_cand in ("post.md", "index.md", "article.md", "README.md"):
                md_p = os.path.join(folder_path, md_cand)
                if os.path.exists(md_p):
                    with open(md_p, "r", encoding="utf-8") as f:
                        md_content = f.read()
                    break

            if md_content.startswith("---"):
                parts = md_content.split("---", 2)
                if len(parts) >= 3:
                    try:
                        fm = yaml.safe_load(parts[1])
                        if isinstance(fm, dict):
                            fm.pop("date", None)
                            post_meta.update(fm)
                            md_content = parts[2].strip()
                    except Exception:
                        pass

            extracted_title = ""
            extracted_subheading = ""
            extracted_thumb = ""
            if md_content:
                m_title = re.search(r'^\s*#\s+(.+)$', md_content, re.MULTILINE)
                if m_title:
                    extracted_title = m_title.group(1).strip()

                for raw_p in re.split(r'\r?\n\s*\r?\n', md_content):
                    p_clean = raw_p.strip()
                    if not p_clean or p_clean.startswith(('#', '![', '<', '```', '>', '---')):
                        continue
                    clean_excerpt = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', p_clean)
                    clean_excerpt = ' '.join(re.sub(r'[*_`]', '', clean_excerpt).split())
                    if clean_excerpt:
                        extracted_subheading = clean_excerpt
                        break

                md_img = re.search(r'!\[([^\]]*)\]\(([^)]+)\)', md_content)
                html_img = re.search(r'<img[^>]+src=[\'"]([^\'"]+)[\'"]', md_content)
                first_src = None
                if md_img and html_img:
                    first_src = md_img.group(2) if md_img.start() < html_img.start() else html_img.group(1)
                elif md_img:
                    first_src = md_img.group(2)
                elif html_img:
                    first_src = html_img.group(1)
                if first_src:
                    cand = resolve_post_asset_path(folder_path, first_src)
                    if cand.startswith(("http", "/")) or os.path.exists(cand):
                        extracted_thumb = cand

            post_title = extracted_title or post_meta.get("title") or format_title_from_filename(folder_name)
            post_subheading = extracted_subheading or post_meta.get("subheading") or ""

            thumbnail_path = extracted_thumb or ""
            if not thumbnail_path and post_meta.get("thumbnail"):
                cand = resolve_post_asset_path(folder_path, post_meta["thumbnail"])
                if os.path.exists(cand):
                    thumbnail_path = cand
            if not thumbnail_path:
                thumbnail_path = find_first_existing(folder_path, ["cover.webp", "cover.jpg", "cover.png", "thumbnail.webp", "thumbnail.jpg", "thumbnail.png"]) or ""
            if not thumbnail_path:
                for f in sorted(os.listdir(folder_path)):
                    if os.path.splitext(f)[1].lower() in DISPLAY_IMG_EXTS:
                        thumbnail_path = f"{folder_path}/{f}".replace("\\", "/")
                        break

            d_parts = post_date.split("-")
            year_str = d_parts[0] if d_parts else "2026"
            month_idx = int(d_parts[1]) - 1 if len(d_parts) > 1 and d_parts[1].isdigit() else 0
            month_name = month_names[month_idx] if 0 <= month_idx < 12 else "January"

            rendered_html = ""
            if md_content:
                md_body = re.sub(r'^\s*#\s+[^\r\n]+(?:\r?\n)+', '', md_content, count=1)
                fixed_md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', lambda m: f'![{m.group(1)}]({resolve_post_asset_path(folder_path, m.group(2))})', md_body)

                def code_repl(m):
                    lang = m.group(1).strip() or 'text'
                    code_raw = m.group(2).rstrip()
                    code_esc = html.escape(code_raw)
                    collapsed = len(code_raw.splitlines()) > 3
                    cls_extra = " is-collapsed" if collapsed else ""
                    toggle_btn = '\n      <button type="button" class="btn-code-toggle" onclick="toggleCodeBlock(this)">Expand</button>' if collapsed else ''
                    return f'''<div class="code-block-card{cls_extra}">
  <div class="code-block-header">
    <span class="code-lang-badge">{esc(lang)}</span>
    <div class="code-actions">{toggle_btn}
      <button type="button" class="btn-code-copy" onclick="copyCodeBlock(this)">Copy</button>
    </div>
  </div>
  <pre><code class="language-{esc(lang)}">{code_esc}</code></pre>
</div>'''

                md_with_code = re.sub(r'```([a-zA-Z0-9_-]*)\r?\n(.*?)```', code_repl, fixed_md, flags=re.DOTALL)
                compiled_html = markdown.markdown(md_with_code, extensions=['tables'])
                rendered_html = re.sub(
                    r'(<img[^>]+src=[\'"])([^\'"]+)([\'"][^>]*>)',
                    lambda m: f'{m.group(1)}{resolve_post_asset_path(folder_path, m.group(2))}{m.group(3)}',
                    compiled_html
                )

            post_id = slugify(folder_name)
            slug = re.sub(r'^\d{4}-\d{2}-\d{2}[-_]*', '', folder_name) or post_id
            parsed_posts.append({
                "id": post_id,
                "slug": slug,
                "folder": folder_path.replace("\\", "/"),
                "title": post_title,
                "date": post_date,
                "year": year_str,
                "month_name": month_name,
                "category": post_meta.get("category", "General"),
                "tags": post_meta.get("tags", []),
                "subheading": post_subheading,
                "thumbnail": thumbnail_path,
                "author": post_meta.get("author", "Prasannakumar T Bhat"),
                "readTime": post_meta.get("readTime", "5 min read"),
                "rendered_html": rendered_html
            })

    parsed_posts.sort(key=lambda x: x["date"], reverse=True)

    tree_hierarchy = {}
    categories_set, tags_set = set(), set()
    for p in parsed_posts:
        tree_hierarchy.setdefault(p["year"], {}).setdefault(p["month_name"], []).append(p)
        if p.get("category"):
            categories_set.add(p["category"])
        for t in (p.get("tags") or []):
            if isinstance(t, str) and t.strip():
                tags_set.add(t.strip())

    tree_items_html = []
    for y in sorted(tree_hierarchy.keys(), reverse=True):
        year_total = sum(len(tree_hierarchy[y][m]) for m in tree_hierarchy[y])
        months_html = "".join(f'''
              <li class="tree-item tree-month" data-year="{y}" data-month="{esc(m)}" onclick="filterByMonth('{y}', '{esc(m)}')">
                <span class="tree-left-wrap"><span class="tree-bullet">&bull;</span><span class="tree-label">{esc(m)}</span></span>
                <span class="tree-count">{len(tree_hierarchy[y][m])}</span>
              </li>''' for m in sorted(tree_hierarchy[y].keys()))

        tree_items_html.append(f'''
          <li class="tree-item tree-year" data-year="{y}">
            <div class="tree-node" onclick="toggleTreeNode(this, '{y}')">
              <span class="tree-left-wrap"><span class="tree-arrow">&#9660;</span><span class="tree-label">{y}</span></span>
              <span class="tree-count">{year_total}</span>
            </div>
            <ul class="tree-children">{months_html}</ul>
          </li>''')

    categories_pills = "".join(
        f'<button type="button" class="filter-pill category-filter-pill" data-category="{esc(cat)}" onclick="filterByCategory(\'{esc(cat)}\')">{esc(cat)}</button>'
        for cat in sorted(categories_set)
    )
    tags_pills = "".join(
        f'<button type="button" class="filter-pill tag-filter-pill" data-tag="{esc(tag)}" onclick="filterByTag(\'{esc(tag)}\')">{esc(tag)}</button>'
        for tag in sorted(tags_set, key=lambda x: x.lower())
    )

    blog_page_title = str(blog_info.get("pageTitle", f"{blog_title} | Pra - Motions")).strip() or f"{blog_title} | Pra - Motions"
    blog_seo_desc = blog_desc or "Technical blog, practical VFX setups, automation scripts, and workflow optimization."

    main_html = f'''      <div class="section-header">
        <h1 class="section-title">{esc(blog_title) or "&nbsp;"}</h1>
        <p class="section-desc">{esc(blog_desc) or "&nbsp;"}</p>
      </div>
      <div class="blog-layout">
        <aside class="blog-sidebar">
          <div class="blog-tree-card blog-filter-card">
            <div class="tree-categories-wrap">
              <div class="tree-section-header">
                <h4 class="tree-subtitle">Categories</h4>
                <button type="button" class="filter-pill category-filter-pill active" data-category="all" onclick="filterByCategory('all')">All</button>
              </div>
              <div class="tree-pill-list" id="categoryPillList">{categories_pills}</div>
            </div>
            <div class="tree-section-divider"></div>
            <div class="tree-tags-wrap">
              <div class="tree-section-header">
                <h4 class="tree-subtitle">Tags</h4>
                <button type="button" class="filter-pill tag-filter-pill active" data-tag="all" onclick="filterByTag('all')">All</button>
              </div>
              <div class="tree-pill-list" id="tagPillList">{tags_pills}</div>
            </div>
          </div>

          <div class="blog-tree-card blog-archive-card">
            <div class="tree-header">
              <h3 class="tree-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                Archive
              </h3>
              <button type="button" class="filter-pill date-filter-pill active" data-date="all" onclick="filterByTree('all')" title="Reset date filter">All</button>
            </div>
            <ul class="tree-root">{"".join(tree_items_html)}</ul>
          </div>
        </aside>

        <section class="blog-content-area">
          <div class="blog-grid" id="blogGrid"></div>
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
      </div>'''

    reader_modal_html = f'''
  <div id="blogReaderOverlay" class="blog-reader-overlay" aria-hidden="true">
    {reader_bg_html}
    <div class="blog-reader-scroll" id="blogReaderScroll">
      <div class="blog-reader-dialog" role="dialog" aria-modal="true">
        <article class="blog-reader-content">
          <header class="reader-header">
            <h2 class="reader-title" id="readerTitle">Title</h2>
            <div class="reader-meta">
              <span id="readerDate">Date</span><span>&bull;</span>
              <span id="readerReadTime">Read Time</span><span>&bull;</span>
              <span id="readerAuthor">Author</span>
            </div>
            <div class="reader-tags" id="readerTags"></div>
          </header>
          <div class="reader-hero-image-wrap" id="readerHeroWrap">
            <img id="readerHeroImg" src="" alt="Hero Image" class="reader-hero-img">
          </div>
          <div class="reader-body" id="readerBody"></div>
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
    <div class="reader-bottom-controls" role="toolbar" aria-label="Article controls">
      <button type="button" class="reader-side-nav reader-side-prev" id="readerSidePrev" onclick="navigatePost(-1)" aria-label="Previous Post" title="Previous Post">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="20" height="20"><polyline points="15 18 9 12 15 6"></polyline></svg>
      </button>
      <button type="button" class="reader-floating-close" onclick="closePostModal()" aria-label="Close article" title="Close article (Esc)">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
      </button>
      <button type="button" class="back-to-top reader-back-to-top" id="readerBackToTop" onclick="scrollReaderToTop()" aria-label="Scroll to top" title="Scroll to top">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"></polyline></svg>
      </button>
      <button type="button" class="reader-side-nav reader-side-next" id="readerSideNext" onclick="navigatePost(1)" aria-label="Next Post" title="Next Post">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" width="20" height="20"><polyline points="9 18 15 12 9 6"></polyline></svg>
      </button>
    </div>
  </div>

  <script id="blogPostsData" type="application/json">{json.dumps(parsed_posts)}</script>'''

    body_scripts = '''  <script src="_engine/js/prism.js"></script>
  <script src="_engine/js/glightbox.min.js"></script>
  <script src="_engine/js/blog.js"></script>
  <script type="module" src="_engine/js/main.js"></script>'''

    blog_html = render_document(
        page_title=blog_page_title,
        meta_desc=blog_seo_desc,
        seo_meta=get_seo_meta_tags("blog.html", blog_page_title, blog_seo_desc),
        nav_active="blog",
        stylesheets=["main.css", "components.css", "glightbox.min.css", "prism.css", "blog.css", "responsive.css"],
        main_html=main_html,
        tracking_tags=tracking_tags,
        extra_body_html=reader_modal_html,
        body_scripts=body_scripts,
        bg_img_html=blog_bg_img_html,
        bg_overlay_html=blog_bg_overlay_html,
    )
    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(blog_html)
    print(f"  -> Updated blog.html ({len(parsed_posts)} posts)")


def build_resource_listing_page(page_id, dir_candidates, default_title, default_desc, tracking_tags):
    """Build unlisted resource dashboard pages (more.html, extra.html) and subfolder redirects."""
    page_dir = next((c for c in dir_candidates if os.path.exists(c)), dir_candidates[0])
    bg_img_html, bg_overlay_html, _, _ = get_page_background_and_overlay(page_dir)

    data = load_json(os.path.join(page_dir, "content.json"), {
        "title": default_title,
        "description": default_desc,
        "linksSectionTitle": "Useful Links",
        "downloadsSectionTitle": "Downloads",
        "overlayOpacity": 75
    })
    page_title = str(data.get("title", default_title)).strip()
    page_desc = str(data.get("description", "")).strip()
    links_title = str(data.get("linksSectionTitle", "Useful Links")).strip()
    downloads_title = str(data.get("downloadsSectionTitle", "Downloads")).strip()

    useful_links_list = []
    for cand_json in ("usefullLinks.json", "usefulLinks.json", "links.json"):
        cand_path = os.path.join(page_dir, cand_json)
        if os.path.exists(cand_path):
            loaded = load_json(cand_path, [])
            if isinstance(loaded, list):
                useful_links_list = loaded
                break

    links_cards_html = []
    for item in useful_links_list:
        if not isinstance(item, dict):
            continue
        l_name = str(item.get("name") or item.get("title") or "Link").strip()
        l_url = str(item.get("link") or item.get("url") or item.get("href") or "").strip()
        if not l_url or l_url == "#":
            l_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(l_name)}"
        l_desc = str(item.get("description") or item.get("desc") or "").strip()
        if not l_desc and l_url.startswith("http"):
            l_desc = re.sub(r'^https?:\/\/(?:www\.)?', '', l_url).split('/')[0]

        links_cards_html.append(f'''
          <a href="{esc(l_url)}" target="_blank" rel="noopener noreferrer" class="more-link-card" title="{esc(l_name)}">
            <div class="more-link-content">
              <div class="more-link-icon-wrap" aria-hidden="true">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path>
                  <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path>
                </svg>
              </div>
              <div class="more-link-text">
                <span class="more-link-title">{esc(l_name)}</span>
                <span class="more-link-desc">{esc(l_desc)}</span>
              </div>
            </div>
            <div class="more-link-arrow" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="7" y1="17" x2="17" y2="7"></line><polyline points="7 7 17 7 17 17"></polyline>
              </svg>
            </div>
          </a>''')

    links_body = (
        f'<div class="more-links-grid">{"".join(links_cards_html)}</div>'
        if links_cards_html
        else f'<p class="more-empty-msg">No links listed yet. Add entries to <code>{esc(page_dir)}/usefullLinks.json</code>.</p>'
    )
    links_section_html = f'''
      <section class="more-section">
        <div class="more-section-header"><h2 class="more-section-title">{esc(links_title)}</h2></div>
        {links_body}
      </section>'''

    downloads_dir = os.path.join(page_dir, "forDownload")
    if not os.path.exists(downloads_dir):
        downloads_dir = "forDownload"

    def _fmt_size(b):
        for unit in ("B", "KB", "MB"):
            if b < 1024 or unit == "MB":
                return f"{b} {unit}" if unit == "B" else f"{b:.1f} {unit}"
            b /= 1024.0
        return f"{b / 1024.0:.1f} GB"

    download_cards_html = []
    if os.path.exists(downloads_dir):
        raw_files = sorted(
            (f for f in os.listdir(downloads_dir) if not f.startswith(".") and os.path.isfile(os.path.join(downloads_dir, f))),
            key=str.lower
        )
        for fname in raw_files:
            fpath = os.path.join(downloads_dir, fname)
            frel_path = fpath.replace("\\", "/")
            fsize_str = _fmt_size(os.path.getsize(fpath))
            ext = os.path.splitext(fname)[1].lower().lstrip(".")
            badge_text = ext.upper() if ext else "FILE"
            if ext in ("zip", "rar", "7z", "tar", "gz"):
                badge_cls = "badge-zip"
            elif ext in ("json", "js", "ts", "py"):
                badge_cls = "badge-json"
            elif ext in ("html", "htm", "css", "xml"):
                badge_cls = "badge-html"
            elif ext in ("jpg", "jpeg", "png", "webp", "gif", "svg", "bmp"):
                badge_cls = "badge-img"
            else:
                badge_cls = "badge-other"

            download_cards_html.append(f'''
          <div class="more-download-card">
            <div class="more-download-info-wrap">
              <span class="more-file-badge {badge_cls}">{badge_text}</span>
              <div class="more-download-text">
                <span class="more-download-name" title="{esc(fname)}">{esc(fname)}</span>
                <span class="more-download-meta">{fsize_str} &bull; {badge_text}</span>
              </div>
            </div>
            <a href="{esc(frel_path)}" download="{esc(fname)}" class="btn btn-primary more-download-btn" title="Download {esc(fname)}">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line>
              </svg>
              <span>Download</span>
            </a>
          </div>''')

    downloads_body = (
        f'<div class="more-downloads-grid">{"".join(download_cards_html)}</div>'
        if download_cards_html
        else f'<p class="more-empty-msg">No files currently in <code>{esc(downloads_dir)}/</code>.</p>'
    )
    downloads_section_html = f'''
      <section class="more-section">
        <div class="more-section-header"><h2 class="more-section-title">{esc(downloads_title)}</h2></div>
        {downloads_body}
      </section>'''

    seo_page_title = str(data.get("pageTitle", f"{page_title} | Prasannakumar T Bhat")).strip() or f"{page_title} | Prasannakumar T Bhat"
    main_html = f'''      <div class="section-header">
        <h1 class="section-title">{esc(page_title) or "&nbsp;"}</h1>
        <p class="section-desc">{esc(page_desc) or "&nbsp;"}</p>
      </div>
{links_section_html}
{downloads_section_html}'''

    full_html = render_document(
        page_title=seo_page_title,
        meta_desc=page_desc,
        seo_meta=get_seo_meta_tags(f"{page_id}.html", seo_page_title, page_desc, is_private=True),
        nav_active="",
        stylesheets=["main.css", "components.css", "responsive.css"],
        main_html=main_html,
        tracking_tags=tracking_tags,
        body_scripts='  <script type="module" src="_engine/js/main.js"></script>',
        bg_img_html=bg_img_html,
        bg_overlay_html=bg_overlay_html,
    )
    with open(f"{page_id}.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    print(f"  -> Updated {page_id}.html")

    os.makedirs(page_id, exist_ok=True)
    with open(f"{page_id}/index.html", "w", encoding="utf-8") as f:
        f.write(f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="0; url=../{page_id}.html">
  <title>Redirecting to {esc(page_title)}...</title>
</head>
<body>
  <script>window.location.replace("../{page_id}.html");</script>
</body>
</html>''')


def generate_sitemap_and_robots():
    """Generate robots.txt and sitemap.xml (excluding /more and /extra)."""
    cfg = get_site_config()
    site_url = str(cfg.get("siteUrl") or cfg.get("url") or "https://pbhat99.github.io").strip().rstrip('/')
    today = datetime.datetime.now().strftime("%Y-%m-%d")

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

    public_entries = [
        ("", "1.0", "weekly"),
        ("vfx.html", "0.9", "weekly"),
        ("ai-comfy.html", "0.8", "monthly"),
        ("photography.html", "0.8", "monthly"),
        ("about.html", "0.8", "monthly"),
        ("blog.html", "0.8", "weekly"),
    ]
    urls_xml = "\n".join(f"""  <url>
    <loc>{f'{site_url}/{rel}' if rel else f'{site_url}/'}</loc>
    <lastmod>{today}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>
  </url>""" for rel, prio, freq in public_entries)

    with open("sitemap.xml", "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{urls_xml}
</urlset>
''')
    print("  -> Updated robots.txt and sitemap.xml")


def _classify_raster_limit(rel_path):
    """Return (category_label, max_warn_dim, max_warn_kb, resize_target_dim) keeping 4K backgrounds & panos high-res."""
    norm = rel_path.replace("\\", "/").lower()
    fname = os.path.basename(norm)
    if fname.startswith("background"):
        return ("4K Background", 4096, 1500, 3840)
    if "/04_photography/panos/" in norm:
        return ("360 Panorama", 6144, 2500, 4096)
    if "/04_photography/photos/" in norm:
        return ("Photo Still", 3000, 1000, 2400)
    return ("Card / Tile Asset", 1600, 300, 1400)


def check_oversized_raster_assets(root_dir="pages", prompt_resize=False):
    """Warn on oversized raster assets in pages/ and optionally prompt user to auto-resize."""
    from PIL import Image

    if not os.path.exists(root_dir):
        return False

    raster_exts = DISPLAY_IMG_EXTS | VALID_IMG_EXTS
    flagged = []
    for current_root, _, files in os.walk(root_dir):
        if "fordownload" in current_root.replace("\\", "/").lower():
            continue
        for f in sorted(files):
            if f.startswith(".") or os.path.splitext(f)[1].lower() not in raster_exts:
                continue
            path = os.path.join(current_root, f)
            rel_path = path.replace("\\", "/")
            size_kb = os.path.getsize(path) / 1024.0
            try:
                with Image.open(path) as im:
                    w, h = im.size
            except Exception:
                continue

            label, max_dim, max_kb, target_dim = _classify_raster_limit(rel_path)
            if (max(w, h) > max_dim and size_kb >= 50.0) or size_kb > max_kb:
                flagged.append((rel_path, label, w, h, size_kb, max_dim, max_kb, target_dim))

    if not flagged:
        return False

    print("\n" + "=" * 72)
    print(f"  [WARNING] Oversized Raster Assets Detected ({len(flagged)} file{'s' if len(flagged) != 1 else ''})")
    print("  (4K page backgrounds & 360 panoramas are intentionally kept high-res)")
    print("=" * 72)
    for i, (rel_path, label, w, h, size_kb, max_dim, max_kb, target_dim) in enumerate(flagged, 1):
        print(f"  {i}. {rel_path}")
        print(f"     {label}: {w}x{h} px, {size_kb:.1f} KB (limit: {max_dim} px / {max_kb} KB)")
    print("=" * 72)

    if not (prompt_resize and sys.stdin.isatty()):
        return False

    try:
        choice = input("\nResize these assets proportionally now? [y] Auto-resize  [N] Skip (manual)  [q] Abort: ").strip().lower()
    except EOFError:
        return False

    if choice in ("q", "quit", "abort"):
        print("\n[ABORTED] Stopped so oversized assets can be resized manually.")
        sys.exit(1)

    if choice not in ("y", "yes"):
        print("  -> Skipping automatic resize; keeping existing files.")
        return False

    resized_any = False
    for rel_path, label, w, h, size_kb, _, _, target_dim in flagged:
        try:
            with Image.open(rel_path) as im:
                has_alpha = im.mode in ('RGBA', 'LA') or (im.mode == 'P' and 'transparency' in im.info)
                cur_w, cur_h = im.size
                out_im = im
                if max(cur_w, cur_h) > target_dim:
                    scale = target_dim / float(max(cur_w, cur_h))
                    out_im = im.resize((max(1, int(round(cur_w * scale))), max(1, int(round(cur_h * scale)))), Image.Resampling.LANCZOS)
                out_im = out_im.convert('RGBA' if has_alpha else 'RGB')
                out_im.save(rel_path, 'WEBP', quality=(88 if has_alpha else 84), method=6)
                new_kb = os.path.getsize(rel_path) / 1024.0
                new_w, new_h = out_im.size
                print(f"  [Resized] {rel_path}: {cur_w}x{cur_h} ({size_kb:.1f} KB) -> {new_w}x{new_h} ({new_kb:.1f} KB)")
                resized_any = True
        except Exception as err:
            print(f"  [Resize Error] {rel_path}: {err}")

    return resized_any


def sync_all(convert_webp=False, generate_thumbs=True, check_assets=False, prompt_resize=False):
    global _SITE_CONFIG_CACHE
    _SITE_CONFIG_CACHE = None

    print("=== Syncing site ===")
    if convert_webp:
        print("  -> [WebP Optimization] Converting source images across pages/ to WebP...")
        convert_all_pages_images_to_webp("pages")

    if check_assets:
        if check_oversized_raster_assets("pages", prompt_resize=prompt_resize):
            generate_thumbs = True

    tracking_tags = get_tracking_tags()
    build_home_page(tracking_tags, generate_thumbs=generate_thumbs)
    build_vfx_page(tracking_tags, generate_thumbs=generate_thumbs)
    build_photography_page(tracking_tags, generate_thumbs=generate_thumbs)
    build_about_page(tracking_tags)
    build_ai_comfy_page(tracking_tags)
    build_blog_page(tracking_tags)
    build_resource_listing_page(
        page_id="more",
        dir_candidates=["pages/07_more", "pages/more"],
        default_title="More & Resources",
        default_desc="Direct downloads, project files, and curated links.",
        tracking_tags=tracking_tags,
    )
    build_resource_listing_page(
        page_id="extra",
        dir_candidates=["pages/08_extra", "pages/extra"],
        default_title="Extra & Utilities",
        default_desc="Additional utilities, downloadable packages, and curated links.",
        tracking_tags=tracking_tags,
    )
    generate_sitemap_and_robots()
    print("\nSUCCESS: All pages synchronized cleanly!")


if __name__ == "__main__":
    try:
        args = set(sys.argv[1:])
        convert_flag = bool(args & {"--convert-webp", "-w"})
        thumbs_flag = "--no-thumbs" not in args
        check_assets_flag = bool(args & {"--check-assets", "--prompt-resize"})
        prompt_resize_flag = "--prompt-resize" in args
        sync_all(
            convert_webp=convert_flag,
            generate_thumbs=thumbs_flag,
            check_assets=check_assets_flag,
            prompt_resize=prompt_resize_flag,
        )
    except Exception as err:
        import traceback
        print(f"\n[FATAL BUILD ERROR] {err}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
