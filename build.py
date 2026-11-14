import os
import re
import json
import html
import yaml
import markdown

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
    bg_candidates = ["background.jpg", "background.jpeg", "background.png", "background.webp"]
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

    bg_img_html = f'<div class="site-bg-image" style="background-image: url(\'{resolved_bg}\');"></div>' if resolved_bg else ''
    bg_overlay_html = f'<div class="site-bg-overlay" style="opacity: {overlay_alpha};"></div>' if resolved_bg else ''

    return bg_img_html, bg_overlay_html, resolved_bg, overlay_alpha

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
    <div class="container-wide nav-wrapper">
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

def sync_all():
    print("=== Syncing site (02_VFX company structure, vfx.html, proportional background fallback) ===")

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

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{fixed_name}</title>
  <meta name="description" content="{fixed_name} - {designation}">
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  
  <!-- Ubuntu Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
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

    vfx_bg_img_html, vfx_bg_overlay_html, _, _ = get_page_background_and_overlay(vfx_dir)

    company_subdirs = sorted([d for d in os.listdir(vfx_dir) if os.path.isdir(os.path.join(vfx_dir, d)) and not d.startswith('.')]) if os.path.exists(vfx_dir) else []
    
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
            "cardBgOpacity": 85
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
        logo_html = f'''
        <div class="company-banner-logo-wrap">
          <img src="{banner_path}" alt="{company_name} Logo" class="company-banner-logo-img">
        </div>''' if banner_path else ''

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

    vfx_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VFX | Pra - Motions</title>
  <meta name="description" content="Visual Effects & Compositing portfolio of Prasannakumar T Bhat across DNEG, The Mill, and feature film productions.">
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
  {vfx_bg_img_html}
  {vfx_bg_overlay_html}

{generate_nav_html("vfx")}

  <main style="padding-block: clamp(24px, 4vw, 56px);">
    <div class="container-wide">
      <div class="section-header">
        <h1 class="section-title">{vfx_content.get('title', 'Visual Effects & Compositing')}</h1>
        <p class="section-desc">
          {vfx_content.get('description', 'Production shots, feature film breakdowns, and commercials across world-class visual effects studios.')}
        </p>
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

  <footer class="site-footer">
    <div class="container-wide">
      <div class="footer-bottom">
        <div>&copy; 2026 Prasannakumar T Bhat (pbhat99). All rights reserved.</div>
        <div style="font-family: var(--font-mono); font-size: 0.78rem;">Auto-synced from pages/02_VFX/</div>
      </div>
    </div>
  </footer>

  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("vfx.html", "w", encoding="utf-8") as f:
        f.write(vfx_html)
    print(f"  -> Updated vfx.html ({len(company_subdirs)} companies, {total_projects_count} projects, auto-sorted descending)")

    # --------------------------------------------------------------------------
    # 3. SYNC PHOTOGRAPHY (pages/04_photography)
    # --------------------------------------------------------------------------
    photo_dir = "pages/04_photography"
    gallery_dir = os.path.join(photo_dir, "gallery")
    photo_bg_img_html, photo_bg_overlay_html, _, _ = get_page_background_and_overlay(photo_dir)

    # Read Photography content.json if present
    photo_page_info = {
        "title": "Photography & 360° Panoramas",
        "description": "Drop photos into <code>pages/04_photography/gallery/</code> to automatically add new gallery stills."
    }
    photo_content_json = os.path.join(photo_dir, "content.json")
    if os.path.exists(photo_content_json):
        try:
            with open(photo_content_json, "r", encoding="utf-8") as f:
                photo_page_info.update(json.load(f))
        except Exception:
            pass

    photo_title = photo_page_info.get("title", "Photography & 360° Panoramas")
    photo_desc = photo_page_info.get("description", "")
    photo_title_inner = photo_title if photo_title else '&nbsp;'
    photo_desc_inner = photo_desc if photo_desc else ''

    photo_files = sorted([f for f in os.listdir(gallery_dir) if os.path.splitext(f)[1].lower() in valid_img_exts]) if os.path.exists(gallery_dir) else []
    photo_cards_html = []
    for pf in photo_files:
        title = format_title_from_filename(pf)
        photo_cards_html.append(f'''
        <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); overflow: hidden;">
          <img src="{gallery_dir}/{pf}" alt="{title}" style="width: 100%; aspect-ratio: 4/3; object-fit: cover;" data-lightbox data-caption="{title}">
          <div style="padding: 14px;">
            <h3 style="font-size: 1rem; font-weight: 700;">{title}</h3>
            <span style="font-size: 0.8rem; color: var(--text-subtle);">Photography Still</span>
          </div>
        </div>''')

    photography_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{photo_title} | Pra - Motions</title>
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
  {photo_bg_img_html}
  {photo_bg_overlay_html}

{generate_nav_html("photography")}

  <main style="padding-block: clamp(24px, 4vw, 56px);">
    <div class="container-wide">
      <div class="section-header">
        <h1 class="section-title">{photo_title_inner}</h1>
        <p class="section-desc">{photo_desc_inner}</p>
      </div>

      <div class="panorama-card">
        <div style="padding: 20px 24px; border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
          <div>
            <h2 style="font-size: 1.3rem; font-weight: 700; margin-top: 4px;">360° Photosphere Panorama Viewer</h2>
          </div>
          <span style="font-size: 0.8rem; color: var(--text-muted); background: var(--bg-secondary); padding: 4px 10px; border-radius: 4px;">
            Drag to Look Around &bull; Pinch to Zoom
          </span>
        </div>
        <div id="panorama-viewer" class="panorama-viewport"></div>
      </div>

      <h2 style="font-size: 1.5rem; font-weight: 700; margin-top: 48px; margin-bottom: 24px;">Still Photography Gallery ({len(photo_files)} Stills)</h2>
      <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(min(100%, 320px), 1fr)); gap: 24px;">
        {"".join(photo_cards_html)}
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container-wide">
      <div class="footer-bottom">
        <div>&copy; 2026 Prasannakumar T Bhat (pbhat99). All rights reserved.</div>
        <div style="font-family: var(--font-mono); font-size: 0.78rem;">Auto-synced from pages/04_photography/</div>
      </div>
    </div>
  </footer>

  <script type="module">
    import {{ initPanoramaViewer }} from './_engine/js/panorama-360.js';
    import './_engine/js/main.js';
    document.addEventListener('DOMContentLoaded', () => {{
      initPanoramaViewer('panorama-viewer', 'https://pannellum.org/images/alma.jpg');
    }});
  </script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("photography.html", "w", encoding="utf-8") as f:
        f.write(photography_html)
    print("  -> Updated photography.html (Nav: VFX, 360 Viewer, Stills Gallery)")

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

    # Find profile picture (profilePic.jpg or fallback)
    profile_img = "_engine/images/logo.png"
    for cand_img in ["profilePic.jpg", "profilePic.png", "profilePic.webp", "profile.jpg", "profile.png"]:
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
        tools_section_html = f'''
      <section class="known-tools-section">
        <div class="known-tools-strip">
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
            showreel_section_html = f'''
      <section class="about-video-card">
        <div class="about-video-container">
          <iframe src="{embed_src}"
                  allow="{allow_attr}" allowfullscreen
                  title="VFX Showreel - {name}"></iframe>
        </div>
      </section>'''

    meta_role = f'{designation}'
    if experience:
        meta_role += f' &bull; {experience}'

    page_title = about_data.get("title", "About Me")
    page_desc = about_data.get("description", "")
    title_inner = page_title if page_title else '&nbsp;'
    desc_inner = page_desc if page_desc else ''

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
    for cand in ["contact.jpg", "contact.png", "contact.webp", "contact.jpeg"]:
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
                            
                            s_img_path = f"{social_folder}/{img_name}".replace("\\", "/")
                            if os.path.exists(os.path.join(social_folder, img_name)):
                                social_tiles_html.append(f'''
            <a href="{s_link}" target="_blank" rel="noopener noreferrer" class="social-tile" title="{s_name}">
              <div class="tile-circling-border" aria-hidden="true"></div>
              <div class="tile-inner">
                <img src="{s_img_path}" alt="{s_name}" class="social-icon-img" loading="lazy">
              </div>
            </a>''')
            except Exception as e:
                print("Notice reading social.json:", e)

    social_section_html = ""
    if social_tiles_html:
        social_section_html = f'''
          <div class="about-social-row">
            {"".join(social_tiles_html)}
          </div>'''

    about_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About | {name}</title>
  <meta name="description" content="{name} - {designation}. {experience}.">
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
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

        <div class="about-bio-col">
          <h1 class="about-name">{name}</h1>
          <div class="about-role-strip">{meta_role}</div>
          <div class="about-paragraphs">
            {paragraphs_html}
          </div>
          {social_section_html}
          <div class="about-actions-wrap">
            <a href="{resume_link}" class="btn btn-primary" download>Resume</a>
            <a href="{cover_letter_link}" class="btn btn-primary" download>Cover Letter</a>
          </div>
        </div>
      </div>

      <!-- Known Tools Strip (Single Row Auto-Fitted Across Full Width) -->
      {tools_section_html}

      <!-- Showreel Video Embed (Vimeo or YouTube) -->
      {showreel_section_html}

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

  <footer class="site-footer">
    <div class="container-wide">
      <div class="footer-bottom">
        <div>&copy; 2026 {name} (pbhat99). All rights reserved.</div>
        <div style="font-family: var(--font-mono); font-size: 0.78rem;">Auto-synced from {about_dir}/</div>
      </div>
    </div>
  </footer>

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
    ai_title_inner = ai_title if ai_title else '&nbsp;'
    ai_desc_inner = ai_desc if ai_desc else ''

    ai_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{ai_title} | Pra - Motions</title>
  <meta name="description" content="{ai_desc}">
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
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
          <img src="pages/03_ai-comfy/workflows/comfyui-production-pipeline.png" alt="ComfyUI Production Pipeline Architecture" style="width: 100%; object-fit: contain; cursor: zoom-in;" data-lightbox data-caption="ComfyUI Master VFX Production Workflow Architecture">
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
              <img src="pages/02_VFX/01_DNEG/02_goatbusters/projectImage.jpg" alt="Raw Live Plate with Markers">
              <span class="ba-badge ba-badge-before">Raw Plate + Tracking Markers</span>
            </div>
            <div class="ba-image-layer ba-after-layer">
              <img src="pages/02_VFX/01_DNEG/03_gmc-hummer-ev-quiet-revolution/projectImage.jpg" alt="AI Inpainted Clean Plate">
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

  <footer class="site-footer">
    <div class="container-wide">
      <div class="footer-bottom">
        <div>&copy; 2026 Prasannakumar T Bhat (pbhat99). All rights reserved.</div>
        <div style="font-family: var(--font-mono); font-size: 0.78rem;">Hosted on GitHub Pages &bull; pbhat99.github.io</div>
      </div>
    </div>
  </footer>

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
    blog_bg_img_html, blog_bg_overlay_html, _, _ = get_page_background_and_overlay(blog_dir)

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
    blog_title_inner = blog_title if blog_title else '&nbsp;'
    blog_desc_inner = blog_desc if blog_desc else ''

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

            # Date extraction from folder name: YYYY-MM-DD...
            date_match = re.match(r'^(\d{4})-(\d{2})-(\d{2})', folder_name)
            if date_match:
                post_meta["date"] = f"{date_match.group(1)}-{date_match.group(2)}-{date_match.group(3)}"

            # Load post.json if present
            post_json_path = os.path.join(folder_path, "post.json")
            if os.path.exists(post_json_path):
                try:
                    with open(post_json_path, "r", encoding="utf-8") as f:
                        post_meta.update(json.load(f))
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
                            post_meta.update(frontmatter)
                            md_content = parts[2].strip()
                    except Exception:
                        pass

            # Resolve thumbnail image
            thumbnail_path = ""
            if post_meta.get("thumbnail"):
                cand_thumb = os.path.join(folder_path, post_meta["thumbnail"])
                if os.path.exists(cand_thumb):
                    thumbnail_path = cand_thumb.replace("\\", "/")
                elif os.path.exists(post_meta["thumbnail"]):
                    thumbnail_path = post_meta["thumbnail"].replace("\\", "/")

            if not thumbnail_path:
                for img_cand in ["cover.jpg", "cover.png", "cover.webp", "thumbnail.jpg", "thumbnail.png"]:
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
                # 1. Process relative image paths: e.g. src="image.png" -> src="pages/06_blog/posts/.../image.png"
                def fix_md_img(m):
                    alt, src = m.group(1), m.group(2)
                    if not src.startswith("http") and not src.startswith("/") and not src.startswith("pages/"):
                        src = f"{folder_path}/{src}".replace("\\", "/")
                    return f'![{alt}]({src})'
                fixed_md = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', fix_md_img, md_content)

                # Process code blocks into collapsible cards with copy button
                def process_markdown_code_blocks(md_text):
                    code_pattern = re.compile(r'```([a-zA-Z0-9_-]*)\r?\n(.*?)```', re.DOTALL)
                    def code_repl(m):
                        lang = m.group(1).strip() or 'text'
                        code_esc = html.escape(m.group(2).rstrip())
                        return f'''<div class="code-block-card">
  <div class="code-block-header">
    <span class="code-lang-badge">{lang}</span>
    <div class="code-actions">
      <button type="button" class="btn-code-toggle" onclick="toggleCodeBlock(this)">Collapse</button>
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
          <li class="tree-item tree-year open" data-year="{y}">
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

    categories_pills = ['<button type="button" class="filter-pill active" onclick="filterByCategory(\'all\')">All</button>']
    for cat in sorted(categories_set):
        categories_pills.append(f'<button type="button" class="filter-pill" onclick="filterByCategory(\'{cat}\')">{cat}</button>')

    posts_json_str = json.dumps(parsed_posts)

    blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{blog_title} | Pra - Motions</title>
  <meta name="description" content="{blog_desc}">
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  <link rel="stylesheet" href="_engine/css/prism.css">
  <link rel="stylesheet" href="_engine/css/blog.css">
</head>
<body>
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
        
        <!-- Left Tree View Archive Sidebar -->
        <aside class="blog-sidebar">
          <div class="blog-tree-card">
            <div class="tree-header">
              <h3 class="tree-title">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                Archive
              </h3>
              <button type="button" class="tree-reset-btn" onclick="resetBlogFilter()">Reset</button>
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

            <div class="tree-section-divider"></div>

            <div class="tree-categories-wrap">
              <h4 class="tree-subtitle">Categories</h4>
              <div class="tree-pill-list">
                {"".join(categories_pills)}
              </div>
            </div>
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
    <div class="blog-reader-dialog" role="dialog" aria-modal="true">
      
      <div class="blog-reader-topbar">
        <span class="reader-category-pill" id="readerCategory">Category</span>
        <button type="button" class="reader-close-btn" onclick="closePostModal()" title="Close (Esc)">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
        </button>
      </div>

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

        <!-- Bottom Post Navigation: Move to Previous & Next Post -->
        <nav class="reader-footer-nav">
          <button type="button" class="reader-nav-btn prev-post-btn" id="readerPrevBtn" onclick="navigatePost(-1)">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 18 9 12 15 6"></polyline></svg>
            <div class="btn-text-wrap">
              <span class="nav-sub">Previous Post</span>
              <span class="nav-title" id="readerPrevTitle">Prev Title</span>
            </div>
          </button>

          <button type="button" class="reader-close-bottom-btn" onclick="closePostModal()">
            Back to All Posts
          </button>

          <button type="button" class="reader-nav-btn next-post-btn" id="readerNextBtn" onclick="navigatePost(1)">
            <div class="btn-text-wrap">
              <span class="nav-sub">Next Post</span>
              <span class="nav-title" id="readerNextTitle">Next Title</span>
            </div>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"></polyline></svg>
          </button>
        </nav>

      </article>

    </div>
  </div>

  <script id="blogPostsData" type="application/json">
{posts_json_str}
  </script>

  <script src="_engine/js/prism.js"></script>
  <script src="_engine/js/blog.js"></script>
  <script type="module" src="_engine/js/main.js"></script>

{BACK_TO_TOP_HTML}
</body>
</html>
'''
    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(blog_html)
    print("  -> Updated blog.html (Nav: Blog, 3-Tile Grid, Archive Tree, Modal Reader, Code Highlights)")

    print("\nSUCCESS: All pages synchronized cleanly!")

if __name__ == "__main__":
    sync_all()
