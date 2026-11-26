import { initLightbox } from './lightbox.js';

function initMainApp() {
  // 1. Mobile Navigation Drawer
  const mobileToggle = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (mobileToggle && navLinks) {
    function toggleNav(forceState) {
      const willOpen = typeof forceState === 'boolean' ? forceState : !navLinks.classList.contains('active');
      navLinks.classList.toggle('active', willOpen);
      mobileToggle.classList.toggle('active', willOpen);
      mobileToggle.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
      document.documentElement.classList.toggle('mobile-nav-open', willOpen);
      document.body.classList.toggle('mobile-nav-open', willOpen);
    }

    mobileToggle.addEventListener('pointerup', () => {
      setTimeout(() => mobileToggle.blur(), 0);
    });

    mobileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      toggleNav();
    });

    document.addEventListener('click', (e) => {
      if (navLinks.classList.contains('active') && !navLinks.contains(e.target) && !mobileToggle.contains(e.target)) {
        toggleNav(false);
      }
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && navLinks.classList.contains('active')) {
        toggleNav(false);
      }
    });

    navLinks.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', () => toggleNav(false));
    });
  }

  // 2. VFX Portfolio Category & Tag Filtering
  const isVfxPage = Boolean(document.querySelector('.company-section'));
  if (isVfxPage) {
    let currentCategory = 'all';
    let currentTag = null;
    let sectionHideTimer = null;

    function updateCategoryButtons() {
      document.querySelectorAll('.filter-bar .filter-btn[data-filter]').forEach((btn) => {
        btn.classList.toggle('active', btn.getAttribute('data-filter') === currentCategory);
      });
    }

    function applyFilters() {
      const tiles = document.querySelectorAll('.project-tile');
      const companySections = document.querySelectorAll('.company-section');

      clearTimeout(sectionHideTimer);

      tiles.forEach((tile) => {
        clearTimeout(tile._hideTimer);
        clearTimeout(tile._fadeTimer);

        const category = tile.getAttribute('data-category');
        const tagsAttr = tile.getAttribute('data-tags') || '';
        const tags = tagsAttr.split(',').map((t) => t.trim().toLowerCase());

        const matchCategory = currentCategory === 'all' || category === currentCategory;
        const matchTag = !currentTag || tags.includes(currentTag.toLowerCase());

        if (matchCategory && matchTag) {
          tile.style.display = 'block';
          tile._fadeTimer = setTimeout(() => { tile.style.opacity = '1'; }, 10);
        } else {
          tile.style.opacity = '0';
          tile._hideTimer = setTimeout(() => { tile.style.display = 'none'; }, 200);
        }
      });

      document.querySelectorAll('.tile-tag').forEach((tagEl) => {
        const tagVal = tagEl.getAttribute('data-tag');
        tagEl.classList.toggle('active', Boolean(currentTag && tagVal && tagVal.toLowerCase() === currentTag.toLowerCase()));
      });

      const tagStatus = document.querySelector('.tag-filter-status');
      if (tagStatus) {
        if (currentTag) {
          tagStatus.textContent = '';
          const label = document.createElement('span');
          label.innerHTML = 'Filter: ';
          const strong = document.createElement('strong');
          strong.textContent = `#${currentTag}`;
          const clearBtn = document.createElement('button');
          clearBtn.type = 'button';
          clearBtn.className = 'tag-filter-clear';
          clearBtn.title = 'Clear tag filter';
          clearBtn.setAttribute('aria-label', 'Clear tag filter');
          clearBtn.innerHTML = '&times;';
          tagStatus.append(label, strong, clearBtn);
          tagStatus.style.display = 'inline-flex';
        } else {
          tagStatus.style.display = 'none';
        }
      }

      sectionHideTimer = setTimeout(() => {
        companySections.forEach((section) => {
          const hasVisible = Array.from(section.querySelectorAll('.project-tile'))
            .some((t) => t.style.display !== 'none');
          section.style.display = hasVisible ? 'block' : 'none';
          if (hasVisible) section.style.opacity = '1';
        });
      }, 220);
    }

    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.filter-bar .filter-btn[data-filter]');
      if (btn) {
        e.preventDefault();
        currentCategory = btn.getAttribute('data-filter') || 'all';
        currentTag = null;
        updateCategoryButtons();
        applyFilters();
        return;
      }

      const tagBtn = e.target.closest('.tile-tag');
      if (tagBtn) {
        e.preventDefault();
        e.stopPropagation();
        const clickedTag = tagBtn.getAttribute('data-tag');
        currentTag = (currentTag && currentTag.toLowerCase() === clickedTag.toLowerCase()) ? null : clickedTag;
        applyFilters();
        return;
      }

      const catPill = e.target.closest('.tile-category-pill');
      if (catPill) {
        e.preventDefault();
        e.stopPropagation();
        currentCategory = catPill.getAttribute('data-filter-category') || 'all';
        currentTag = null;
        updateCategoryButtons();
        applyFilters();
        return;
      }

      if (e.target.closest('.tag-filter-clear')) {
        e.preventDefault();
        currentTag = null;
        applyFilters();
      }
    });
  }

  // 3. Scroll-to-Top Floating Button
  const backToTopBtn = document.getElementById('back-to-top');
  if (backToTopBtn) {
    const handleScroll = () => {
      const scrollY = window.scrollY || document.documentElement.scrollTop || 0;
      const threshold = Math.min(280, (window.innerHeight || 600) * 0.5);
      backToTopBtn.classList.toggle('visible', scrollY > threshold);
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    backToTopBtn.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    handleScroll();
  }

  // 4. Initialize GLightbox when present on page
  initLightbox();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initMainApp);
} else {
  initMainApp();
}
