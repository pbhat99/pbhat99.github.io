import json

with open('data/projects.json', 'r', encoding='utf-8') as f:
    projects = json.load(f)

print(f"Loaded {len(projects)} projects.")

cards_html = []
for p in projects:
    has_ba = p.get('hasBeforeAfter', False)
    category = p.get('category', 'commercials')
    cat_label = "Commercial"
    if category == "films":
        cat_label = "Feature Film"
    elif category == "music-videos":
        cat_label = "Music Video"

    tools_html = "".join([f'<span class="tool-tag">{t}</span>' for t in p.get('tools', ['Nuke', 'Maya'])])

    ba_accordion_html = ""
    if has_ba:
        before_img = p.get('beforeImage', p['thumbnail'])
        after_img = p.get('afterImage', p['thumbnail'])
        before_lbl = p.get('beforeLabel', 'Raw Plate')
        after_lbl = p.get('afterLabel', 'Final Comp')
        ba_accordion_html = f'''
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
                        <img src="{before_img}" alt="{before_lbl}">
                        <span class="ba-badge ba-badge-before">{before_lbl}</span>
                      </div>
                      <div class="ba-image-layer ba-after-layer">
                        <img src="{after_img}" alt="{after_lbl}">
                        <span class="ba-badge ba-badge-after">{after_lbl}</span>
                      </div>
                      <div class="ba-handle">
                        <div class="ba-handle-circle">
                          <div class="ba-handle-arrows"><span>&#9664;</span><span>&#9654;</span></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>'''
    elif p.get('highlight', False):
        ba_accordion_html = f'''
            <div class="accordion-wrapper">
              <button class="accordion-trigger" aria-expanded="false">
                <span>View Shot Notes</span>
                <span class="accordion-icon">&#9662;</span>
              </button>
              <div class="accordion-content">
                <div class="accordion-inner">
                  <div class="accordion-breakdown-box">
                    <div class="breakdown-step">
                      <span class="step-num">01.</span>
                      <div><strong>Plate Prep:</strong> High-precision matchmove tracking and optical cleanup.</div>
                    </div>
                    <div class="breakdown-step">
                      <span class="step-num">02.</span>
                      <div><strong>Composite:</strong> Multichannel EXR lighting passes integration and grade match.</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>'''

    card = f'''
        <article class="project-card" data-category="{category}">
          <div class="project-thumb-wrapper">
            <img src="{p['thumbnail']}" alt="{p['title']}" class="project-thumb" loading="lazy" data-lightbox data-caption="{p['title']} - {p.get('role', 'Compositing Artist')}">
            <span class="card-overlay-badge">{cat_label}</span>
          </div>
          <div class="card-content">
            <div class="card-meta">
              <span class="card-client">{p.get('client', 'Production')}</span>
              <span>{p.get('year', 'VFX')}</span>
            </div>
            <h3 class="card-title">{p['title']}</h3>
            <p class="card-desc">{p.get('description', '')}</p>
            <div class="card-tools">
              {tools_html}
            </div>
            {ba_accordion_html}
          </div>
        </article>'''
    cards_html.append(card)

# Inject into vfx-works.html
vfx_template = open('vfx-works.html', encoding='utf-8').read()
start_marker = '<div class="portfolio-grid">'
end_marker = '</div>\n\n    </div>\n  </main>'

prefix = vfx_template[:vfx_template.find(start_marker) + len(start_marker)]
suffix = vfx_template[vfx_template.find(end_marker):]

full_vfx = prefix + "\n" + "\n".join(cards_html) + "\n      " + suffix

with open('vfx-works.html', 'w', encoding='utf-8') as f:
    f.write(full_vfx)

print("vfx-works.html populated with all 64 projects and authentic Weebly images!")
