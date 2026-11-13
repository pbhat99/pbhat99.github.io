import os
import re
import json

def format_title_from_filename(filename):
    name = os.path.splitext(filename)[0]
    # Remove numbers, hashes, hashes from IMDb
    name = re.sub(r'^[0-9]+[-_]', '', name)
    name = name.replace('_orig', '').replace('_', ' ').replace('-', ' ')
    name = re.sub(r'\s+', ' ', name).strip()
    return name.title()

def sync_all():
    print("=== Syncing site with pages/ folder structure ===")

    # --------------------------------------------------------------------------
    # 1. SYNC HOME PAGE (pages/01_home)
    # --------------------------------------------------------------------------
    home_dir = "pages/01_home"
    content_file = os.path.join(home_dir, "content.json")
    home_data = {
        "name": "Prasannakumar T Bhat",
        "designation": "Senior Visual Effects Compositor @ DNEG",
        "tagline": "CG is not just faking, its adding beautiful layers of lie on the ugly truth."
    }
    if os.path.exists(content_file):
        try:
            with open(content_file, "r", encoding="utf-8") as f:
                home_data.update(json.load(f))
        except Exception as e:
            print(f"Notice reading {content_file}: {e}")

    has_bg_image = os.path.exists(os.path.join(home_dir, "background.jpg"))

    # Generate Minimalist, Ethereal, Cinematic Home Page
    bg_style = f"background-image: linear-gradient(to bottom, rgba(9, 12, 19, 0.82), rgba(9, 12, 19, 0.96)), url('{home_dir}/background.jpg');" if has_bg_image else ""

    index_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{home_data['name']} | Portfolio</title>
  <meta name="description" content="{home_data['name']} - {home_data['designation']}">
  <link rel="icon" type="image/png" href="assets/images/branding/logo.png">
  
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
  
  <style>
    /* Full-screen Minimalist Home Viewport */
    .home-hero-fullscreen {{
      position: relative;
      min-height: calc(100vh - 72px);
      display: flex;
      align-items: center;
      justify-content: center;
      text-align: center;
      padding: clamp(24px, 5vw, 60px) 20px;
      overflow: hidden;
      background-size: cover;
      background-position: center;
      {bg_style}
    }}

    #bg-canvas {{
      position: absolute;
      inset: 0;
      width: 100%;
      height: 100%;
      pointer-events: auto;
      z-index: 1;
    }}

    .home-content-box {{
      position: relative;
      z-index: 10;
      max-width: 860px;
      margin-inline: auto;
      pointer-events: none; /* Allows mouse to seamlessly interact with canvas below */
    }}

    .home-content-box * {{
      pointer-events: auto; /* Re-enable buttons and links */
    }}

    .hero-name {{
      font-size: clamp(2.8rem, 7vw, 5.5rem);
      font-weight: 800;
      letter-spacing: -0.035em;
      line-height: 1.05;
      margin-bottom: 18px;
      background: linear-gradient(135deg, #ffffff 40%, rgba(255, 255, 255, 0.65) 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      text-shadow: 0 0 50px rgba(56, 189, 248, 0.25);
    }}

    .hero-designation {{
      font-family: var(--font-mono);
      font-size: clamp(0.9rem, 2vw, 1.25rem);
      color: var(--accent-cyan);
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-weight: 600;
      margin-bottom: 24px;
      display: inline-flex;
      align-items: center;
      gap: 10px;
      background: rgba(56, 189, 248, 0.08);
      padding: 6px 18px;
      border-radius: var(--radius-full);
      border: 1px solid rgba(56, 189, 248, 0.25);
      backdrop-filter: blur(8px);
    }}

    .hero-tagline-clean {{
      font-size: clamp(1.15rem, 2.5vw, 1.55rem);
      color: var(--text-muted);
      font-weight: 300;
      line-height: 1.5;
      max-width: 720px;
      margin-inline: auto;
      margin-bottom: 36px;
      font-style: italic;
    }}

    .home-quick-actions {{
      display: flex;
      justify-content: center;
      gap: 16px;
      flex-wrap: wrap;
    }}

    .mouse-hint {{
      position: absolute;
      bottom: 24px;
      left: 50%;
      transform: translateX(-50%);
      font-family: var(--font-mono);
      font-size: 0.72rem;
      color: var(--text-subtle);
      letter-spacing: 0.1em;
      text-transform: uppercase;
      z-index: 10;
      pointer-events: none;
      display: flex;
      align-items: center;
      gap: 8px;
      opacity: 0.75;
    }}
  </style>
</head>
<body style="overflow-x: hidden;">

  <!-- Site Navigation -->
  <header class="site-header">
    <div class="container-wide nav-wrapper">
      <a href="index.html" class="brand-logo">
        <img src="assets/images/branding/logo.png" alt="Pra Motions Logo" width="34" height="34" style="border-radius: 6px;">
        <span>Pra - <span class="brand-badge">Motions</span></span>
        <span class="brand-tag">VFX</span>
      </a>

      <button class="mobile-nav-toggle" aria-label="Toggle navigation" aria-expanded="false">
        <span></span>
        <span></span>
        <span></span>
      </button>

      <ul class="nav-links">
        <li><a href="index.html" class="active">Home</a></li>
        <li><a href="vfx-works.html">VFX Works</a></li>
        <li><a href="ai-comfy.html">AI / Comfy</a></li>
        <li><a href="photography.html">Photography</a></li>
        <li><a href="about-me.html">About Me</a></li>
        <li><a href="blog.html">Blog</a></li>
        <li><a href="about-me.html#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem;">Contact</a></li>
      </ul>
    </div>
  </header>

  <main>
    <section class="home-hero-fullscreen">
      <!-- Interactive Mouse Pointer Background Canvas -->
      <canvas id="bg-canvas"></canvas>

      <!-- Center Minimalist Content: Name, Designation & Tagline -->
      <div class="home-content-box">
        <div class="hero-designation">
          <span>{home_data['designation']}</span>
        </div>
        <h1 class="hero-name">{home_data['name']}</h1>
        <p class="hero-tagline-clean">
          "{home_data['tagline']}"
        </p>
        <div class="home-quick-actions">
          <a href="vfx-works.html" class="btn btn-primary" style="padding: 12px 28px; font-size: 1rem;">
            <span>Explore Works</span>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
          </a>
          <a href="about-me.html" class="btn btn-secondary" style="padding: 12px 24px; font-size: 1rem;">
            <span>About Me</span>
          </a>
        </div>
      </div>

      <!-- Mouse interaction guide indicator -->
      <div class="mouse-hint">
        <span>&#10022;</span> Move cursor to interact with fluid particle field
      </div>
    </section>
  </main>

  <!-- Interactive Background Script -->
  <script type="module">
    import {{ initInteractiveBackground }} from './_engine/js/interactive-bg.js';
    import './_engine/js/main.js';
    document.addEventListener('DOMContentLoaded', () => {{
      initInteractiveBackground('bg-canvas');
    }});
  </script>
</body>
</html>
'''
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
    print("  -> Updated index.html (Minimalist, Name, Designation, Tagline, Interactive Canvas)")

    # --------------------------------------------------------------------------
    # 2. SYNC VFX WORKS (pages/02_vfx-works/projects)
    # --------------------------------------------------------------------------
    projects_dir = "pages/02_vfx-works/projects"
    projects_json_path = "pages/02_vfx-works/projects.json"

    # Load existing metadata if available
    existing_meta = {}
    if os.path.exists(projects_json_path):
        try:
            with open(projects_json_path, "r", encoding="utf-8") as f:
                for item in json.load(f):
                    existing_meta[os.path.basename(item.get('thumbnail', ''))] = item
                    existing_meta[item['id']] = item
        except Exception as e:
            print(f"Notice reading projects.json: {e}")

    # Read all files in projects/ folder
    valid_exts = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif'}
    project_files = sorted([f for f in os.listdir(projects_dir) if os.path.splitext(f)[1].lower() in valid_exts])
    
    updated_projects = []
    film_keywords = ['film', 'sandalwood', 'movie', 'anjani', 'kataka', 'samhara', 'ricky', 'badmaash', 'sihir', 'bengaluru', 'maruti', 'eradu', 'ajaramara', 'java', 'uddishya', 'mantram', 'double engine', 'patibeku', 'samyuktha', 'kamarottu', 'shankanaada', 'abhisaarike']
    music_keywords = ['chemical brothers', 'jay prince', 'music']

    for p_file in project_files:
        clean_name = format_title_from_filename(p_file)
        file_path = f"{projects_dir}/{p_file}"
        
        # Check if already has curated metadata
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

    # Save updated projects.json
    with open(projects_json_path, "w", encoding="utf-8") as f:
        json.dump(updated_projects, f, indent=2)

    # Update vfx-works.html
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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
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
        <li><a href="about-me.html#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem;">Contact</a></li>
      </ul>
    </div>
  </header>

  <main style="padding-block: clamp(36px, 6vw, 72px);">
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
    print(f"  -> Updated vfx-works.html with {len(updated_projects)} project cards")

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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
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
        <li><a href="about-me.html#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem;">Contact</a></li>
      </ul>
    </div>
  </header>

  <main style="padding-block: clamp(36px, 6vw, 72px);">
    <div class="container-wide">
      <div class="section-header">
        <div class="section-label">Visual Exploration</div>
        <h1 class="section-title">Photography & 360° Panoramas</h1>
        <p class="section-desc">
          Drop photos into <code>pages/04_photography/gallery/</code> to automatically add new gallery stills.
        </p>
      </div>

      <!-- Interactive 360° Panorama Viewer -->
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
        <div id="panorama-viewer" class="panorama-viewport">
          <div class="panorama-overlay-hint">
            <span>&#10022;</span> Interactive 360° Space: Click & Drag to explore
          </div>
        </div>
      </div>

      <!-- Photo Gallery Grid -->
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
    print(f"  -> Updated photography.html with {len(photo_files)} photos")

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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="_engine/css/main.css">
  <link rel="stylesheet" href="_engine/css/components.css">
  <link rel="stylesheet" href="_engine/css/responsive.css">
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
        <li><a href="#contact" class="btn btn-primary" style="padding: 6px 16px; font-size: 0.82rem;">Contact</a></li>
      </ul>
    </div>
  </header>

  <main style="padding-block: clamp(36px, 6vw, 72px);">
    <div class="container">
      <div style="display: grid; grid-template-columns: 1fr 2fr; gap: clamp(24px, 5vw, 48px); align-items: start; margin-bottom: 56px;">
        <div>
          <div style="border-radius: var(--radius-lg); overflow: hidden; border: 1px solid var(--border-subtle); background: var(--bg-card); box-shadow: var(--shadow-subtle);">
            <img src="{banner_img}" alt="DNEG banner" style="width: 100%; object-fit: cover;">
            <div style="padding: 20px; text-align: center;">
              <img src="{profile_img}" alt="Prasannakumar T Bhat" style="width: 130px; height: 130px; border-radius: 50%; object-fit: cover; margin-inline: auto; margin-top: -65px; border: 4px solid var(--bg-card); box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
              <h2 style="font-size: 1.25rem; font-weight: 700; margin-top: 12px;">Prasannakumar T Bhat</h2>
              <p style="font-size: 0.85rem; color: var(--accent-cyan); font-weight: 600; margin-top: 4px;">Compositing Artist @ DNEG</p>
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
    print("  -> Updated about-me.html (synced with profile.jpg and banner.png)")

    # --------------------------------------------------------------------------
    # 5. SYNC AI / COMFY (pages/03_ai-comfy) & BLOG (pages/06_blog)
    # --------------------------------------------------------------------------
    # Ensure they link to _engine/css and _engine/js
    for f_name in ["ai-comfy.html", "blog.html"]:
        if os.path.exists(f_name):
            content = open(f_name, "r", encoding="utf-8").read()
            content = content.replace("assets/css/", "_engine/css/")
            content = content.replace("assets/js/", "_engine/js/")
            open(f_name, "w", encoding="utf-8").write(content)
    print("  -> Updated ai-comfy.html and blog.html engine paths")

    print("\nSUCCESS: All pages and structures are synchronized perfectly!")

if __name__ == "__main__":
    sync_all()
