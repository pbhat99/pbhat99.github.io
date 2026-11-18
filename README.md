# Pra - Motions | Prasannakumar T Bhat Portfolio

Modern, high-performance Visual Effects (VFX) & AI pipeline portfolio engineered for GitHub Pages: **[pbhat99.github.io](https://pbhat99.github.io)**.

Replaces the legacy Weebly site (`pramotions.weebly.com`) with a dark cinematic visual aesthetic, zero-bloat architecture, and interactive showcase dynamics:
- **Interactive Before & After Wipe Slider** (native touch/swipe and keyboard accessible)
- **Fluid Lightbox Image Viewer** (touch pinch-to-zoom, swipe, keyboard navigation)
- **Animated Accordion Galleries** (expandable shot breakdowns with technical software badges)
- **Interactive 360° Photosphere Panorama Viewer** (pure client-side WebGL replacing slow Google Maps iframes)
- **Multi-Pass VFX Layer Inspector** (scrub through plate, 3D CG pass, atmospheric lighting, and final grade)
- **Showreel Timestamp Jumper** (click project badges to instantly seek to that shot in the reel)

---

## Architecture & Project Structure

```
pbhat99.github.io/
├── .github/workflows/
│   └── deploy.yml            # Automated GitHub Pages CI/CD deployment
├── _engine/
│   ├── css/                  # Design system & dark mode cinematic theme
│   ├── js/                   # Slider, lightbox, accordions, 360 viewer, routing
│   └── images/               # Branding and core engine icons
├── pages/                    # Source content and raw high-res images
├── tools/                    # Developer build, preview, and deployment tools
│   ├── preview.bat           # 1-click local test server launcher (localhost:8080)
│   ├── deploy.bat            # 1-click build, verify, commit & deploy to GitHub
│   ├── build.py              # Site compiler (WebP generator, sitemap, HTML builder)
│   ├── watcher.py            # Live hot-reloading development server
│   ├── verify_site.py        # Static asset and link validator
│   ├── preview.ps1           # PowerShell browser & port orchestrator
│   └── siteConfig.json       # Central tracking & domain configuration
├── index.html                # Home page with hero reel & dynamic showcases
├── vfx.html                  # Complete categorized VFX portfolio
├── ai-comfy.html             # AI / ComfyUI pipelines & custom node guides
├── photography.html          # Photography & interactive 360 panorama
├── about.html                # Bio, showreel, software matrix, contact
├── blog.html                 # Technical articles & guides
├── more.html                 # Private download vault & curated links
├── extra.html                # Private utilities & additional resources
├── robots.txt                # Search engine crawler policies
├── sitemap.xml               # Search engine index sitemap
└── README.md
```

---

## Easy Maintenance & Developer Workflow

### 1. Local Preview & Testing
Run the preview tool:
```bash
tools\preview.bat
```
This automatically converts any new images in `pages/` to WebP, clears caches, and launches a live server at `http://localhost:8080`.

### 2. Deploying to GitHub
When ready to publish updates live:
```bash
tools\deploy.bat
```
This automatically runs WebP optimization, validates site links, commits changes to `dev`, and mirrors directly to `main` for GitHub Pages.

