import os
import re
import json

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
        ("about-me.html", "about-me", "About Me"),
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
        <div class="section-label">Production Archive</div>
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
  <title>Photography & 360 Panoramas | Pra - Motions</title>
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
        <div class="section-label">Visual Exploration</div>
        <h1 class="section-title">Photography & 360° Panoramas</h1>
        <p class="section-desc">
          Drop photos into <code>pages/04_photography/gallery/</code> to automatically add new gallery stills.
        </p>
      </div>

      <div class="panorama-card">
        <div style="padding: 20px 24px; border-bottom: 1px solid var(--border-subtle); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;">
          <div>
            <div style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-primary); text-transform: uppercase;">Interactive WebGL Sphere</div>
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
</body>
</html>
'''
    with open("photography.html", "w", encoding="utf-8") as f:
        f.write(photography_html)
    print("  -> Updated photography.html (Nav: VFX, 360 Viewer, Stills Gallery)")

    # --------------------------------------------------------------------------
    # 4. SYNC ABOUT ME (pages/05_about-me)
    # --------------------------------------------------------------------------
    about_dir = "pages/05_about-me"
    about_bg_img_html, about_bg_overlay_html, _, _ = get_page_background_and_overlay(about_dir)

    profile_img = f"{about_dir}/profile.jpg" if os.path.exists(f"{about_dir}/profile.jpg") else "_engine/images/logo.png"
    banner_img = f"{about_dir}/banner.png" if os.path.exists(f"{about_dir}/banner.png") else ""

    about_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About Me | Prasannakumar T Bhat</title>
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
  {about_bg_img_html}
  {about_bg_overlay_html}

{generate_nav_html("about-me")}

  <main style="padding-block: clamp(24px, 4vw, 56px);">
    <div class="container">
      <div class="section-header">
        <div class="section-label">Biography & Expertise</div>
        <h1 class="section-title">About Me</h1>
        <p class="section-desc">
          Visual Effects Compositor with 10+ years of studio experience across feature films, commercials, and next-generation AI pipelines.
        </p>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 2fr; gap: clamp(24px, 5vw, 48px); align-items: start; margin-bottom: 56px;">
        <div>
          <div style="border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--border-subtle); background: var(--bg-card); box-shadow: var(--shadow-subtle);">
            {'<img src="' + banner_img + '" alt="DNEG banner" style="width: 100%; object-fit: cover;">' if banner_img else ''}
            <div style="padding: 20px; text-align: center;">
              <img src="{profile_img}" alt="Prasannakumar T Bhat" style="width: 130px; height: 130px; border-radius: 50%; object-fit: cover; margin-inline: auto; margin-top: -65px; border: 4px solid var(--bg-card); box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
              <h2 style="font-size: 1.25rem; font-weight: 700; margin-top: 12px; color: var(--text-main);">Prasannakumar T Bhat</h2>
              <p style="font-size: 0.85rem; color: var(--accent-primary); font-weight: 500; margin-top: 4px;">Compositing Artist @ DNEG</p>
              <div style="margin-top: 14px; font-size: 0.82rem; color: var(--text-subtle);">
                10+ Years Visual Effects Experience
              </div>
            </div>
          </div>
        </div>

        <div>
          <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px;">It's Me! Prasannakumar</h2>
          <div style="font-size: 1.05rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 18px; line-height: 1.7;">
            <p>
              For <strong>10+ years</strong>, I've been weaving magic with pixels in the world of visual effects. It's thrilling to take raw footage, images, and 3D elements, and mold them into the final image that graces the big screen or TV. Seeing my work come to life is an unparalleled reward!
            </p>
            <p>
              I'm a relentless explorer, always pushing the boundaries of what's possible with the latest software in <strong>feature films, commercials, and TV projects</strong>.
            </p>
            <p>
              My passion for innovation extends beyond the screen. In my spare time, I delve into research, <strong>crafting tools and automating tasks with scripts</strong>. With deep expertise in compositing, I'm currently bringing my vision to life as a <strong>Compositing Artist at DNEG</strong>.
            </p>
          </div>
        </div>
      </div>

      <section style="margin-bottom: 56px;">
        <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 24px;">Production Software & Toolset</h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 20px;">
          <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 20px;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 12px;">Compositing</h3>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; color: var(--text-muted);">
              <li>&bull; <strong>Foundry Nuke & Nuke Studio</strong></li>
              <li>&bull; Autodesk Flame</li>
              <li>&bull; Deep Compositing & OpenEXR</li>
            </ul>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 20px;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--accent-hover); margin-bottom: 12px;">3D & Tracking</h3>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; color: var(--text-muted);">
              <li>&bull; <strong>Autodesk Maya</strong></li>
              <li>&bull; SynthEyes Matchmove</li>
              <li>&bull; Mocha Pro Planar Tracking</li>
            </ul>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 20px;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--accent-primary); margin-bottom: 12px;">AI & Pipelines</h3>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; color: var(--text-muted);">
              <li>&bull; <strong>ComfyUI Custom Node Dev</strong></li>
              <li>&bull; Python Automation Scripting</li>
              <li>&bull; ControlNet & Inpainting</li>
            </ul>
          </div>
        </div>
      </section>

      <section id="contact" style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: clamp(24px, 5vw, 40px);">
        <div style="max-width: 600px;">
          <div class="section-label">Get in Touch</div>
          <h2 style="font-size: 1.6rem; font-weight: 700; margin-bottom: 16px;">Contact Information</h2>
          <div style="display: flex; flex-direction: column; gap: 14px; font-size: 0.92rem;">
            <div><span style="color: var(--text-subtle); width: 80px; display: inline-block;">Phone:</span> <strong style="color: #fff;">+91 9449267068</strong></div>
            <div><span style="color: var(--text-subtle); width: 80px; display: inline-block;">GitHub:</span> <a href="https://github.com/pbhat99" target="_blank" rel="noopener" style="color: var(--accent-primary); text-decoration: underline;">github.com/pbhat99</a></div>
            <div><span style="color: var(--text-subtle); width: 80px; display: inline-block;">Location:</span> <span style="color: var(--text-muted);">Karnataka, India - 581337</span></div>
          </div>
        </div>
      </section>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container-wide">
      <div class="footer-bottom">
        <div>&copy; 2026 Prasannakumar T Bhat (pbhat99). All rights reserved.</div>
        <div style="font-family: var(--font-mono); font-size: 0.78rem;">Auto-synced from pages/05_about-me/</div>
      </div>
    </div>
  </footer>

  <script type="module" src="_engine/js/main.js"></script>
</body>
</html>
'''
    with open("about-me.html", "w", encoding="utf-8") as f:
        f.write(about_html)
    print("  -> Updated about-me.html (Nav: VFX, Bio, Toolset, Contact Section)")

    # --------------------------------------------------------------------------
    # 5. SYNC AI / COMFY (pages/03_ai-comfy)
    # --------------------------------------------------------------------------
    ai_dir = "pages/03_ai-comfy"
    ai_bg_img_html, ai_bg_overlay_html, _, _ = get_page_background_and_overlay(ai_dir)

    ai_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AI & ComfyUI Pipelines | Pra - Motions</title>
  <meta name="description" content="AI Generative Pipelines, Custom ComfyUI Nodes, and VFX Inpainting Toolsets by Prasannakumar T Bhat.">
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
        <div class="section-label">Generative AI & VFX Automation</div>
        <h1 class="section-title">ComfyUI Pipelines & AI Toolsets</h1>
        <p class="section-desc">
          Bridging the gap between cutting-edge Diffusion models and film-grade visual effects pipelines. Custom ComfyUI node workflows, automated plate inpainting, and depth-guided dynamic relighting.
        </p>
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

    blog_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Technical Blog & Guides | Pra - Motions</title>
  <meta name="description" content="Technical Guides on ComfyUI portable setup, custom nodes, FaceFusion, and VFX scripting by Prasannakumar T Bhat.">
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  <style>
    pre {{
      background: var(--bg-secondary);
      border: 1px solid var(--border-subtle);
      border-radius: var(--radius-sm);
      padding: 16px;
      overflow-x: auto;
      font-family: var(--font-mono);
      font-size: 0.85rem;
      color: var(--accent-primary);
      margin-block: 12px;
    }}
    code {{
      font-family: var(--font-mono);
      color: var(--accent-hover);
    }}
  </style>
</head>
<body>
  {blog_bg_img_html}
  {blog_bg_overlay_html}

{generate_nav_html("blog")}

  <main style="padding-block: clamp(36px, 6vw, 72px);">
    <div class="container" style="max-width: 860px;">
      
      <!-- Page Header -->
      <div class="section-header">
        <div class="section-label">Engineering & AI Notes</div>
        <h1 class="section-title">Technical Blog</h1>
        <p class="section-desc">
          Practical setups, automation scripts, and workflow optimization for visual effects and generative AI pipelines.
        </p>
      </div>

      <!-- Article 1: ComfyUI Portable -->
      <article id="comfyui-portable-custom-nodes" style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: clamp(24px, 4vw, 36px); margin-bottom: 40px;">
        <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 12px;">
          <span style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent-primary);">28 NOV 2025</span>
          <span style="color: var(--text-subtle);">&bull;</span>
          <span style="font-size: 0.8rem; color: var(--text-muted);">ComfyUI / Pipeline</span>
        </div>
        <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px;">ComfyUI Portable with Production Custom Nodes</h2>
        
        <div style="margin-bottom: 20px; border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--border-subtle);">
          <img src="pages/06_blog/posts/blog_img_2.png" alt="ComfyUI Node Graph Screenshot" style="width: 100%; object-fit: contain; background: #000;" data-lightbox data-caption="ComfyUI Production Node Graph Pipeline">
        </div>

        <div style="font-size: 0.95rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 14px; line-height: 1.7;">
          <p>
            Download and extract the latest standalone portable release from GitHub:
            <br>
            <a href="https://github.com/comfyanonymous/ComfyUI/releases" target="_blank" rel="noopener" style="color: var(--accent-primary); text-decoration: underline;">
              https://github.com/comfyanonymous/ComfyUI/releases
            </a>
          </p>

          <h3 style="font-size: 1.15rem; color: #fff; margin-top: 10px;">Essential Production Custom Nodes:</h3>
          
          <p>Navigate to <code>ComfyUI/custom_nodes/</code> and clone the essential toolsets:</p>

          <div>
            <strong>1. ComfyUI Manager:</strong>
            <pre>git clone https://github.com/ltdrdata/ComfyUI-Manager comfyui-manager</pre>
          </div>

          <div>
            <strong>2. RGThree (Workflow Routing & Mute Bypasses):</strong>
            <pre>git clone https://github.com/rgthree/rgthree-comfy.git</pre>
          </div>

          <div>
            <strong>3. Video Helper Suite (VHS):</strong>
            <pre>git clone https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite.git</pre>
          </div>

          <div>
            <strong>4. CrysTools (Resource Monitor HUD):</strong>
            <pre>git clone https://github.com/crystian/comfyui-crystools.git</pre>
          </div>

          <div>
            <strong>5. Procedural & Advanced Math Nodes:</strong>
            <pre>git clone https://github.com/melMass/comfy_mtb.git
git clone https://github.com/kijai/ComfyUI-KJNodes.git</pre>
          </div>

          <div>
            <strong>6. Use Everywhere (Wireless Node Execution):</strong>
            <pre>git clone https://github.com/chrisgoringe/cg-use-everywhere</pre>
          </div>
        </div>
      </article>

      <!-- Article 2: FaceFusion -->
      <article id="facefusion-windows-portable" style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-lg); padding: clamp(24px, 4vw, 36px);">
        <div style="display: flex; gap: 12px; align-items: center; margin-bottom: 12px;">
          <span style="font-family: var(--font-mono); font-size: 0.78rem; color: var(--accent-primary);">18 JUN 2025</span>
          <span style="color: var(--text-subtle);">&bull;</span>
          <span style="font-size: 0.8rem; color: var(--text-muted);">Deep Learning / Tools</span>
        </div>
        <h2 style="font-size: 1.5rem; font-weight: 700; margin-bottom: 16px;">Steps to Install FaceFusion 3 on Windows (Portable)</h2>
        
        <div style="margin-bottom: 20px; border-radius: var(--radius-md); overflow: hidden; border: 1px solid var(--border-subtle);">
          <img src="pages/06_blog/posts/blog_img_5.png" alt="FaceFusion Installation UI" style="width: 100%; object-fit: contain; background: #000;" data-lightbox data-caption="FaceFusion Portable Interface">
        </div>

        <div style="font-size: 0.95rem; color: var(--text-muted); display: flex; flex-direction: column; gap: 14px; line-height: 1.7;">
          <p>
            Clean portable setup using isolated Python virtual environments:
          </p>
          <pre>git clone https://github.com/FaceFusion/FaceFusion.git
cd FaceFusion
python -m venv myenv
myenv\\Scripts\\activate
python install.py --onnxruntime cuda</pre>
          <p>
            Launch the interactive GUI:
          </p>
          <pre>python facefusion.py run</pre>
        </div>
      </article>

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
</body>
</html>
'''
    with open("blog.html", "w", encoding="utf-8") as f:
        f.write(blog_html)
    print("  -> Updated blog.html (Nav: VFX, Technical Guides)")

    print("\nSUCCESS: All pages synchronized cleanly!")

if __name__ == "__main__":
    sync_all()
