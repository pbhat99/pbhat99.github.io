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
├── assets/
│   ├── css/
│   │   ├── main.css          # Design system & dark mode cinematic theme
│   │   ├── components.css    # Wipe slider, lightbox, accordions, 360 viewer
│   │   └── responsive.css    # Fluid scaling, auto-alignment for mobile/desktop
│   ├── js/
│   │   ├── main.js           # Core router, filtering, and event coordinator
│   │   ├── before-after.js   # Touch & drag wipe comparison slider
│   │   ├── accordion.js      # Accessible expandable shot breakdowns
│   │   ├── lightbox.js       # High-res image modal with gesture support
│   │   ├── multi-pass.js     # VFX layer composite pass switcher
│   │   └── panorama-360.js   # 360 photosphere WebGL viewer
│   └── images/
│       ├── branding/         # Logos & banners
│       └── portfolio/        # Project thumbnails & composite passes
├── data/
│   ├── projects.json         # Master VFX project database
│   ├── comfy_workflows.json  # ComfyUI nodes & AI generative pipelines
│   ├── photography.json      # Photographs & 360 photospheres
│   └── blog.json             # Technical tutorial articles
├── index.html                # Home page with hero reel & live dynamic showcases
├── vfx-works.html            # Complete categorized VFX portfolio
├── ai-comfy.html             # AI / ComfyUI pipelines & custom node guides
├── photography.html          # Photography & interactive 360 panorama
├── about-me.html             # Bio, DNEG compositing role, software matrix, contact
├── blog.html                 # Technical guides (ComfyUI portable, FaceFusion)
├── package.json              # Development scripts
└── README.md
```

---

## Easy Maintenance Process

Adding a new VFX project or blog post takes **less than 60 seconds**:

### 1. Adding a New VFX Project
Open `data/projects.json` and append your project:
```json
{
  "id": "my-new-project",
  "title": "Client Name - Spot Title",
  "client": "Client",
  "category": "commercials",
  "year": "2026",
  "role": "Lead Compositor",
  "thumbnail": "assets/images/portfolio/my-shot.jpg",
  "description": "Shot summary...",
  "tools": ["Nuke", "Maya"],
  "hasBeforeAfter": true,
  "beforeImage": "assets/images/portfolio/my-plate.jpg",
  "afterImage": "assets/images/portfolio/my-comp.jpg"
}
```

### 2. Deploying to GitHub
Any commit pushed to `main` is automatically built and deployed live via the included GitHub Action (`.github/workflows/deploy.yml`):
```bash
git add .
git commit -m "Add new project"
git push origin main
```

---

## Local Development Preview

To test locally:
```bash
# Using Node / npx:
npm run dev

# Or using Python:
python -m http.server 3000
```
Then open `http://localhost:3000` in your browser.
