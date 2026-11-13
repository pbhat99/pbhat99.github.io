import os
import re
import json

def format_title_from_filename(filename):
    name = os.path.splitext(filename)[0]
    name = re.sub(r'^[0-9]+[-_]', '', name)
    name = name.replace('_orig', '').replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()

def sync_all():
    print("=== Syncing site with pages/ folder structure & Ubuntu typography ===")

    # --------------------------------------------------------------------------
    # 1. SYNC HOME PAGE (pages/01_home)
    # --------------------------------------------------------------------------
    home_dir = "pages/01_home"
    content_file = os.path.join(home_dir, "content.json")
    home_data = {
        "name": "Prasannakumar T Bhat",
        "tagline": "CG is not just faking, its adding beautiful layers of lie on the ugly truth."
    }
    if os.path.exists(content_file):
        try:
            with open(content_file, "r", encoding="utf-8") as f:
                home_data.update(json.load(f))
        except Exception as e:
            print(f"Notice reading {content_file}: {e}")

    has_bg_image = os.path.exists(os.path.join(home_dir, "background.jpg"))
    bg_style = f"background-image: linear-gradient(to bottom, rgba(9, 12, 19, 0.75), rgba(9, 12, 19, 0.9)), url('{home_dir}/background.jpg');" if has_bg_image else ""

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{home_data['name']}</title>
  <meta name="description" content="{home_data['name']} - {home_data['tagline']}">
  <link rel="icon" type="image/png" href="assets/images/branding/logo.png">
  
  <!-- Ubuntu Typography -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  
  <style>
    /* Fixed Full-Screen Non-Scrollable Viewport */
    html, body {{
      margin: 0;
      padding: 0;
      width: 100vw;
      height: 100vh;
      overflow: hidden;
      position: fixed;
      inset: 0;
      font-family: 'Ubuntu', sans-serif;
    }}

    /* Transparent Navigation - Seamless, No Border or Background */
    .site-header {{
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      z-index: 100;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
      backdrop-filter: none !important;
      -webkit-backdrop-filter: none !important;
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
      background-size: cover;
      background-position: center;
      background-repeat: no-repeat;
      padding-inline: 24px;
      {bg_style}
    }}

    #bg-canvas {{
      position: fixed;
      inset: 0;
      width: 100vw;
      height: 100vh;
      pointer-events: none;
      z-index: 1;
    }}

    .home-center-stage {{
      position: relative;
      z-index: 10;
      max-width: 95vw;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}

    /* Name and Tagline in a Single Horizontal Line */
    .name-tagline-row {{
      display: inline-flex;
      align-items: baseline;
      justify-content: center;
      gap: clamp(10px, 1.8vw, 22px);
      white-space: nowrap;
      flex-wrap: nowrap;
      max-width: 95vw;
    }}

    .hero-name-inline {{
      font-family: 'Ubuntu', sans-serif;
      font-size: clamp(1.4rem, 2.6vw, 2.5rem);
      font-weight: 700;
      color: #ffffff;
      letter-spacing: -0.02em;
      margin: 0;
      line-height: 1.2;
      text-shadow: 0 0 40px rgba(56, 189, 248, 0.45);
    }}

    .row-separator {{
      color: var(--accent-cyan);
      font-weight: 300;
      font-size: clamp(1.2rem, 2.2vw, 2.1rem);
      opacity: 0.85;
    }}

    .hero-tagline-inline {{
      font-family: 'Ubuntu', sans-serif;
      font-size: clamp(0.95rem, 1.6vw, 1.4rem);
      font-weight: 400;
      font-style: italic;
      color: rgba(241, 245, 249, 0.88);
      margin: 0;
      line-height: 1.2;
    }}

    .about-action-wrap {{
      margin-top: 36px;
    }}

    .btn-about {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      padding: 11px 36px;
      font-size: 0.95rem;
      font-weight: 500;
      font-family: 'Ubuntu', sans-serif;
      border-radius: var(--radius-full);
      background: linear-gradient(135deg, #0284c7, #2563eb);
      color: #ffffff;
      box-shadow: 0 4px 18px rgba(37, 99, 235, 0.4);
      transition: all var(--transition-fast);
      letter-spacing: 0.02em;
    }}

    .btn-about:hover {{
      background: linear-gradient(135deg, #38bdf8, #3b82f6);
      transform: translateY(-2px);
      box-shadow: 0 6px 25px rgba(56, 189, 248, 0.55);
    }}

    @media (max-width: 768px) {{
      .name-tagline-row {{
        flex-direction: column;
        align-items: center;
        gap: 8px;
        white-space: normal;
      }}
      .row-separator {{
        display: none;
      }}
    }}
  </style>
</head>
<body>

  <!-- Navigation Bar (Seamless & Transparent) -->
  <header class="site-header">
    <div class="container-wide nav-wrapper">
      <a href="index.html" class="brand-logo">
        <img src="assets/images/branding/logo.png" alt="Pra Motions Logo" width="34" height="34" style="border-radius: 6px;">
        <span>Pra - <span class="brand-badge">Motions</span></span>
        <span class="brand-tag">VFX</span>
      </a>

      <button class="mobile-nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>

      <ul class="nav-links">
        <li><a href="index.html" class="active">Home</a></li>
        <li><a href="vfx-works.html">VFX Works</a></li>
        <li><a href="ai-comfy.html">AI / Comfy</a></li>
        <li><a href="photography.html">Photography</a></li>
        <li><a href="about-me.html">About Me</a></li>
        <li><a href="blog.html">Blog</a></li>
        <li><a href="about-me.html#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem; font-weight: 500;">Contact</a></li>
      </ul>
    </div>
  </header>

  <!-- Full-Screen Interactive Viewport -->
  <main class="home-fullscreen-container">
    <!-- 60fps Interactive Mouse Pointer Canvas Background -->
    <canvas id="bg-canvas"></canvas>

    <!-- Center Stage: Name and Tagline in a Single Line + About Button -->
    <div class="home-center-stage">
      <div class="name-tagline-row">
        <h1 class="hero-name-inline">{home_data['name']}</h1>
        <span class="row-separator">—</span>
        <p class="hero-tagline-inline">"{home_data['tagline']}"</p>
      </div>

      <div class="about-action-wrap">
        <a href="about-me.html" class="btn-about">About</a>
      </div>
    </div>
  </main>

  <!-- Interactive Background Engine -->
  <script type="module">
    import {{ initInteractiveBackground }} from './_engine/js/interactive-bg.js';
    import './_engine/js/main.js';
    initInteractiveBackground('bg-canvas');
  </script>
</body>
</html>
'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("  -> Updated index.html (Single-line Name & Tagline, only About button, full-page fixed, interactive canvas)")

    # --------------------------------------------------------------------------
    # 2. SYNC VFX WORKS (pages/02_vfx-works/projects)
    # --------------------------------------------------------------------------
    projects_dir = "pages/02_vfx-works/projects"
    projects_json_path = "pages/02_vfx-works/projects.json"

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
    project_files = sorted([f for f in os.listdir(projects_dir) if os.path.splitext(f)[1].lower() in valid_exts])
    
    updated_projects = []
    film_keywords = ['film', 'sandalwood', 'movie', 'anjani', 'kataka', 'samhara', 'ricky', 'badmaash', 'sihir', 'bengaluru', 'maruti', 'eradu', 'ajaramara', 'java', 'uddishya', 'mantram', 'double engine', 'patibeku', 'samyuktha', 'kamarottu', 'shankanaada', 'abhisaarike']
    music_keywords = ['chemical brothers', 'jay prince', 'music']

    for p_file in project_files:
        clean_name = format_title_from_filename(p_file)
        file_path = f"{projects_dir}/{p_file}"
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
  <link rel="icon" type="image/png" href="assets/images/branding/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  <style>
    .site-header {{
      position: relative;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container-wide nav-wrapper">
      <a href="index.html" class="brand-logo">
        <img src="assets/images/branding/logo.png" alt="Pra Motions Logo" width="34" height="34" style="border-radius: 6px;">
        <span>Pra - <span class="brand-badge">Motions</span></span>
        <span class="brand-tag">VFX</span>
      </a>
      <button class="mobile-nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="vfx-works.html" class="active">VFX Works</a></li>
        <li><a href="ai-comfy.html">AI / Comfy</a></li>
        <li><a href="photography.html">Photography</a></li>
        <li><a href="about-me.html">About Me</a></li>
        <li><a href="blog.html">Blog</a></li>
        <li><a href="about-me.html#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem; font-weight: 500;">Contact</a></li>
      </ul>
    </div>
  </header>

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
    print(f"  -> Updated vfx-works.html with {len(updated_projects)} project cards and Ubuntu font")

    # --------------------------------------------------------------------------
    # 3. SYNC PHOTOGRAPHY (pages/04_photography/gallery)
    # --------------------------------------------------------------------------
    photo_dir = "pages/04_photography/gallery"
    photo_files = sorted([f for f in os.listdir(photo_dir) if os.path.splitext(f)[1].lower() in valid_exts]) if os.path.exists(photo_dir) else []
    
    photo_cards_html = []
    for pf in photo_files:
        title = format_title_from_filename(pf)
        photo_cards_html.append(f'''
        <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); overflow: hidden;">
          <img src="{photo_dir}/{pf}" alt="{title}" style="width: 100%; aspect-ratio: 4/3; object-fit: cover;" data-lightbox data-caption="{title}">
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
  <link rel="icon" type="image/png" href="assets/images/branding/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  <style>
    .site-header {{
      position: relative;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container-wide nav-wrapper">
      <a href="index.html" class="brand-logo">
        <img src="assets/images/branding/logo.png" alt="Pra Motions Logo" width="34" height="34" style="border-radius: 6px;">
        <span>Pra - <span class="brand-badge">Motions</span></span>
        <span class="brand-tag">VFX</span>
      </a>
      <button class="mobile-nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="vfx-works.html">VFX Works</a></li>
        <li><a href="ai-comfy.html">AI / Comfy</a></li>
        <li><a href="photography.html" class="active">Photography</a></li>
        <li><a href="about-me.html">About Me</a></li>
        <li><a href="blog.html">Blog</a></li>
        <li><a href="about-me.html#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem; font-weight: 500;">Contact</a></li>
      </ul>
    </div>
  </header>

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
            <div style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-cyan); text-transform: uppercase;">Interactive WebGL Sphere</div>
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
    print(f"  -> Updated photography.html with {len(photo_files)} photos and Ubuntu font")

    # --------------------------------------------------------------------------
    # 4. SYNC ABOUT ME (pages/05_about-me)
    # --------------------------------------------------------------------------
    about_dir = "pages/05_about-me"
    profile_img = f"{about_dir}/profile.jpg" if os.path.exists(f"{about_dir}/profile.jpg") else "assets/images/branding/about_me_2.jpg"
    banner_img = f"{about_dir}/banner.png" if os.path.exists(f"{about_dir}/banner.png") else "assets/images/branding/dneg-banner.png"

    about_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>About Me | Prasannakumar T Bhat</title>
  <link rel="icon" type="image/png" href="assets/images/branding/logo.png">
  <link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  <style>
    .site-header {{
      position: relative;
      background: transparent !important;
      border: none !important;
      box-shadow: none !important;
    }}
  </style>
</head>
<body>
  <header class="site-header">
    <div class="container-wide nav-wrapper">
      <a href="index.html" class="brand-logo">
        <img src="assets/images/branding/logo.png" alt="Pra Motions Logo" width="34" height="34" style="border-radius: 6px;">
        <span>Pra - <span class="brand-badge">Motions</span></span>
        <span class="brand-tag">VFX</span>
      </a>
      <button class="mobile-nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span><span></span><span></span>
      </button>
      <ul class="nav-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="vfx-works.html">VFX Works</a></li>
        <li><a href="ai-comfy.html">AI / Comfy</a></li>
        <li><a href="photography.html">Photography</a></li>
        <li><a href="about-me.html" class="active">About Me</a></li>
        <li><a href="blog.html">Blog</a></li>
        <li><a href="#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem; font-weight: 500;">Contact</a></li>
      </ul>
    </div>
  </header>

  <main style="padding-block: clamp(24px, 4vw, 56px);">
    <div class="container">
      <div style="display: grid; grid-template-columns: 1fr 2fr; gap: clamp(24px, 5vw, 48px); align-items: start; margin-bottom: 56px;">
        <div>
          <div style="border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--border-subtle); background: var(--bg-card); box-shadow: var(--shadow-subtle);">
            <img src="{banner_img}" alt="DNEG banner" style="width: 100%; object-fit: cover;">
            <div style="padding: 20px; text-align: center;">
              <img src="{profile_img}" alt="Prasannakumar T Bhat" style="width: 130px; height: 130px; border-radius: 50%; object-fit: cover; margin-inline: auto; margin-top: -65px; border: 4px solid var(--bg-card); box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
              <h2 style="font-size: 1.25rem; font-weight: 700; margin-top: 12px;">Prasannakumar T Bhat</h2>
              <p style="font-size: 0.85rem; color: var(--accent-cyan); font-weight: 500; margin-top: 4px;">Compositing Artist @ DNEG</p>
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
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--accent-cyan); margin-bottom: 12px;">Compositing</h3>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; color: var(--text-muted);">
              <li>&bull; <strong>Foundry Nuke & Nuke Studio</strong></li>
              <li>&bull; Autodesk Flame</li>
              <li>&bull; Deep Compositing & OpenEXR</li>
            </ul>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 20px;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--accent-violet); margin-bottom: 12px;">3D & Tracking</h3>
            <ul style="list-style: none; display: flex; flex-direction: column; gap: 8px; font-size: 0.9rem; color: var(--text-muted);">
              <li>&bull; <strong>Autodesk Maya</strong></li>
              <li>&bull; SynthEyes Matchmove</li>
              <li>&bull; Mocha Pro Planar Tracking</li>
            </ul>
          </div>
          <div style="background: var(--bg-card); border: 1px solid var(--border-subtle); border-radius: var(--radius-md); padding: 20px;">
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--accent-emerald); margin-bottom: 12px;">AI & Pipelines</h3>
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
            <div><span style="color: var(--text-subtle); width: 80px; display: inline-block;">GitHub:</span> <a href="https://github.com/pbhat99" target="_blank" rel="noopener" style="color: var(--accent-cyan); text-decoration: underline;">github.com/pbhat99</a></div>
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
    print("  -> Updated about-me.html (synced with profile.jpg, banner.png, and Ubuntu font)")

    # --------------------------------------------------------------------------
    # 5. SYNC AI / COMFY & BLOG
    # --------------------------------------------------------------------------
    for f_name in ["ai-comfy.html", "blog.html"]:
        if os.path.exists(f_name):
            content = open(f_name, "r", encoding="utf-8").read()
            # Replace Inter with Ubuntu font link
            content = re.sub(r'<link href="https://fonts\.googleapis\.com/css2\?family=Inter[^"]+" rel="stylesheet">',
                             '<link href="https://fonts.googleapis.com/css2?family=Ubuntu:ital,wght@0,300;0,400;0,500;0,700;1,300;1,400;1,700&family=Ubuntu+Mono:wght@400;700&display=swap" rel="stylesheet">',
                             content)
            # Seamless header
            if ".site-header {" not in content:
                content = content.replace("</head>", "  <style>\n    .site-header { position: relative; background: transparent !important; border: none !important; box-shadow: none !important; }\n  </style>\n</head>")
            open(f_name, "w", encoding="utf-8").write(content)
    print("  -> Updated ai-comfy.html and blog.html with Ubuntu font and seamless header")

    print("\nSUCCESS: All pages updated with single-line home, seamless header, and Ubuntu font!")

if __name__ == "__main__":
    sync_all()
