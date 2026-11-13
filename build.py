import os
import re
import json

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

def generate_nav_html(active_page="home"):
    """
    Renders the unified transparent header with NO contact button.
    """
    nav_items = [
        ("index.html", "home", "Home"),
        ("vfx-works.html", "vfx-works", "VFX Works"),
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
    print("=== Syncing site (seamless background fallback, no stretch/squeeze, no contact in nav) ===")

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
    print("  -> Updated index.html (Clean Nav, No Contact Button, Proportional Background)")

    # --------------------------------------------------------------------------
    # 2. SYNC VFX WORKS (pages/02_vfx-works)
    # --------------------------------------------------------------------------
    vfx_dir = "pages/02_vfx-works"
    projects_dir = os.path.join(vfx_dir, "projects")
    projects_json_path = os.path.join(vfx_dir, "projects.json")

    vfx_bg_img_html, vfx_bg_overlay_html, _, _ = get_page_background_and_overlay(vfx_dir)

    existing_meta = {}
    if os.path.exists(projects_json_path):
        try:
            with open(projects_json_path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    existing_meta[os.path.basename(item.get('thumbnail', ''))] = item
                    existing_meta[item['id']] = item
        except Exception:
            pass

    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'}
    project_files = sorted([f for f in os.listdir(projects_dir) if os.path.splitext(f)[1].lower() in valid_exts]) if os.path.exists(projects_dir) else []
    
    updated_projects = []
    film_keywords = ['film', 'sandalwood', 'movie', 'anjani', 'kataka', 'samhara', 'ricky', 'badmaash', 'sihir', 'bengaluru', 'maruti', 'eradu', 'ajaramara', 'java', 'uddishya', 'mantram', 'double engine', 'patibeku', 'samyuktha', 'kamarottu', 'shankanaada', 'abhisaarike']
    music_keywords = ['chemical brothers', 'jay prince', 'music']

    for p_file in project_files:
        clean_name = format_title_from_filename(p_file)
        file_path = f"{projects_dir}/{p_file}".replace("\\", "/")
        meta = existing_meta.get(p_file) or existing_meta.get(clean_name.lower().replace(' ', '-'))
        
        category = "commercials"
        name_lower = clean_name.lower()
        if any(k in name_lower for k in film_keywords):
            category = "films"
        elif any(k in name_lower for k in music_keywords):
            category = "music-videos"

        if meta:
            item = {
                "id": meta.get("id", clean_name.lower().replace(' ', '-')),
                "title": meta.get("title", clean_name),
                "client": meta.get("client", "Production"),
                "category": meta.get("category", category),
                "year": meta.get("year", "2023"),
                "role": meta.get("role", "Compositor"),
                "thumbnail": file_path,
                "description": meta.get("description", f"Visual effects compositing and shot integration for {clean_name}."),
                "tools": meta.get("tools", ["Nuke", "Maya"]),
                "hasBeforeAfter": meta.get("hasBeforeAfter", False)
            }
        else:
            item = {
                "id": clean_name.lower().replace(' ', '-'),
                "title": clean_name,
                "client": "Production",
                "category": category,
                "year": "2023",
                "role": "Compositing Artist",
                "thumbnail": file_path,
                "description": f"Visual effects compositing and shot integration for {clean_name}.",
                "tools": ["Nuke", "Maya"],
                "hasBeforeAfter": False
            }
        updated_projects.append(item)

    with open(projects_json_path, "w", encoding="utf-8") as f:
        json.dump(updated_projects, f, indent=2)

    cards_html = []
    for p in updated_projects:
        cat_label = "Commercial"
        if p["category"] == "films": cat_label = "Feature Film"
        elif p["category"] == "music-videos": cat_label = "Music Video"
        
        tools_html = "".join([f'<span class="tool-tag">{t}</span>' for t in p.get('tools', ['Nuke', 'Maya'])])

        ba_html = ""
        if p.get("hasBeforeAfter", False):
            ba_html = f'''
            <div class="accordion-wrapper">
              <button class="accordion-trigger" aria-expanded="false">
                <span>Interactive Wipe Comparison</span>
                <span class="accordion-icon">&#9662;</span>
              </button>
              <div class="accordion-content">
                <div class="accordion-inner">
                  <div class="accordion-breakdown-box">
                    <div class="before-after-container" style="aspect-ratio: 16/9;">
                      <div class="ba-image-layer ba-before-layer">
                        <img src="{p['thumbnail']}" alt="Raw Plate">
                        <span class="ba-badge ba-badge-before">Raw Plate</span>
                      </div>
                      <div class="ba-image-layer ba-after-layer">
                        <img src="{p['thumbnail']}" alt="Final Comp">
                        <span class="ba-badge ba-badge-after">Final Comp</span>
                      </div>
                      <div class="ba-handle"><div class="ba-handle-circle"><div class="ba-handle-arrows"><span>&#9664;</span><span>&#9654;</span></div></div></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>'''

        cards_html.append(f'''
        <article class="project-card" data-category="{p['category']}">
          <div class="project-thumb-wrapper">
            <img src="{p['thumbnail']}" alt="{p['title']}" class="project-thumb" loading="lazy" data-lightbox data-caption="{p['title']} - {p.get('role', 'Compositor')}">
            <span class="card-overlay-badge">{cat_label}</span>
          </div>
          <div class="card-content">
            <div class="card-meta">
              <span class="card-client">{p.get('client', 'Production')}</span>
              <span>{p.get('year', '2023')}</span>
            </div>
            <h3 class="card-title">{p['title']}</h3>
            <p class="card-desc">{p.get('description', '')}</p>
            <div class="card-tools">{tools_html}</div>
            {ba_html}
          </div>
        </article>''')

    vfx_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>VFX Works | Pra - Motions</title>
  <link rel="icon" type="image/png" href="_engine/images/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
</head>
<body>
  {vfx_bg_img_html}
  {vfx_bg_overlay_html}

{generate_nav_html("vfx-works")}

  <main style="padding-block: clamp(24px, 4vw, 56px);">
    <div class="container-wide">
      <div class="section-header">
        <div class="section-label">Production Archive</div>
        <h1 class="section-title">Visual Effects & Compositing Works</h1>
        <p class="section-desc">
          Total of {len(updated_projects)} projects synced from <code>pages/02_vfx-works/projects/</code>.
        </p>
      </div>

      <div class="filter-bar">
        <button class="filter-btn active" data-filter="all">All ({len(updated_projects)})</button>
        <button class="filter-btn" data-filter="commercials">Commercials</button>
        <button class="filter-btn" data-filter="films">Feature Films</button>
        <button class="filter-btn" data-filter="music-videos">Music Videos</button>
      </div>

      <div class="portfolio-grid">
        {"".join(cards_html)}
      </div>
    </div>
  </main>

  <footer class="site-footer">
    <div class="container-wide">
      <div class="footer-bottom">
        <div>&copy; 2026 Prasannakumar T Bhat (pbhat99). All rights reserved.</div>
        <div style="font-family: var(--font-mono); font-size: 0.78rem;">Auto-synced from pages/02_vfx-works/</div>
      </div>
    </div>
  </footer>

  <script type="module" src="_engine/js/main.js"></script>
</body>
</html>
'''
    with open("vfx-works.html", "w", encoding="utf-8") as f:
        f.write(vfx_html)
    print(f"  -> Updated vfx-works.html ({len(updated_projects)} projects, seamless fallback background)")

    # --------------------------------------------------------------------------
    # 3. SYNC PHOTOGRAPHY (pages/04_photography)
    # --------------------------------------------------------------------------
    photo_dir = "pages/04_photography"
    gallery_dir = os.path.join(photo_dir, "gallery")
    photo_bg_img_html, photo_bg_overlay_html, _, _ = get_page_background_and_overlay(photo_dir)

    photo_files = sorted([f for f in os.listdir(gallery_dir) if os.path.splitext(f)[1].lower() in valid_exts]) if os.path.exists(gallery_dir) else []
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
    print("  -> Updated photography.html (360 Viewer, Stills Gallery, fallback background)")

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
          <div class="section-label">Biography & Expertise</div>
          <h1 class="section-title" style="margin-bottom: 20px;">It's Me! Prasannakumar</h1>
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
    print("  -> Updated about-me.html (Bio, Toolset, Contact Section, fallback background)")

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
              <img src="pages/02_vfx-works/projects/goatbusters.jpg" alt="Raw Live Plate with Markers">
              <span class="ba-badge ba-badge-before">Raw Plate + Tracking Markers</span>
            </div>
            <div class="ba-image-layer ba-after-layer">
              <img src="pages/02_vfx-works/projects/hummer-ev.jpg" alt="AI Inpainted Clean Plate">
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
    print("  -> Updated ai-comfy.html (ComfyUI Workflows, Inpaint Wipe Demo, fallback background)")

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
    print("  -> Updated blog.html (Technical Guides, fallback background)")

    print("\nSUCCESS: All 6 pages synchronized cleanly!")

if __name__ == "__main__":
    sync_all()
