import { initAllBeforeAfter } from './before-after.js';
import { initLightbox } from './lightbox.js';
import { initAccordions } from './accordion.js';
import { initAllMultiPass } from './multi-pass.js';

document.addEventListener('DOMContentLoaded', () => {
  // Mobile Nav Toggle
  const mobileToggle = document.querySelector('.mobile-nav-toggle');
  const navLinks = document.querySelector('.nav-links');

  if (mobileToggle && navLinks) {
    mobileToggle.addEventListener('click', () => {
      navLinks.classList.toggle('active');
      const isOpen = navLinks.classList.contains('active');
      mobileToggle.setAttribute('aria-expanded', isOpen);
    });

    // Close on link click
    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('active');
        mobileToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // Portfolio & VFX Tag / Category Filtering
  let currentCategory = 'all';
  let currentTag = null;

  const filterBtns = document.querySelectorAll('.filter-bar .filter-btn');

  function updateCategoryButtons() {
    filterBtns.forEach(b => {
      if (b.getAttribute('data-filter') === currentCategory) {
        b.classList.add('active');
      } else {
        b.classList.remove('active');
      }
    });
  }

  function applyFilters() {
    const tiles = document.querySelectorAll('.project-tile, .project-card');
    const companySections = document.querySelectorAll('.company-section');

    tiles.forEach(tile => {
      const category = tile.getAttribute('data-category');
      const tagsAttr = tile.getAttribute('data-tags') || '';
      const tags = tagsAttr.split(',').map(t => t.trim().toLowerCase());

      const matchCategory = (currentCategory === 'all' || category === currentCategory);
      const matchTag = (!currentTag || tags.includes(currentTag.toLowerCase()));

      if (matchCategory && matchTag) {
        tile.style.display = 'block';
        setTimeout(() => { tile.style.opacity = '1'; }, 10);
      } else {
        tile.style.opacity = '0';
        setTimeout(() => { tile.style.display = 'none'; }, 200);
      }
    });

    // Highlight active tags
    document.querySelectorAll('.tile-tag').forEach(tagEl => {
      const tagVal = tagEl.getAttribute('data-tag');
      if (currentTag && tagVal && tagVal.toLowerCase() === currentTag.toLowerCase()) {
        tagEl.classList.add('active');
      } else {
        tagEl.classList.remove('active');
      }
    });

    // Update active tag banner
    const tagStatus = document.querySelector('.tag-filter-status');
    if (tagStatus) {
      if (currentTag) {
        tagStatus.innerHTML = `Filter: <strong>#${currentTag}</strong> <button class="tag-filter-clear" title="Clear tag filter">&times;</button>`;
        tagStatus.style.display = 'inline-flex';
      } else {
        tagStatus.style.display = 'none';
      }
    }

    // Update company sections visibility
    setTimeout(() => {
      companySections.forEach(section => {
        const visibleTiles = section.querySelectorAll('.project-tile:not([style*="display: none"]), .project-card:not([style*="display: none"])');
        if (visibleTiles.length === 0) {
          section.style.display = 'none';
        } else {
          section.style.display = 'block';
          section.style.opacity = '1';
        }
      });
    }, 220);
  }

  // Category Button Click (Delegated for dynamically generated pills)
  document.addEventListener('click', (e) => {
    const btn = e.target.closest('.filter-bar .filter-btn');
    if (btn) {
      e.preventDefault();
      currentCategory = btn.getAttribute('data-filter') || 'all';
      currentTag = null;
      updateCategoryButtons();
      applyFilters();
    }
  });

  // Delegated clicks for interactive Category Pills and Clickable Tags on Tiles
  document.addEventListener('click', (e) => {
    // Tag Click
    const tagBtn = e.target.closest('.tile-tag');
    if (tagBtn) {
      e.preventDefault();
      e.stopPropagation();
      const clickedTag = tagBtn.getAttribute('data-tag');
      if (currentTag && currentTag.toLowerCase() === clickedTag.toLowerCase()) {
        currentTag = null; // toggle off
      } else {
        currentTag = clickedTag;
      }
      applyFilters();
      return;
    }

    // Category Pill Click
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

    // Clear Tag Filter
    if (e.target.classList.contains('tag-filter-clear') || e.target.closest('.tag-filter-clear')) {
      e.preventDefault();
      currentTag = null;
      applyFilters();
      return;
    }
  });

  // Scroll to Top Floating Button (Show only when scrolled past one screen height)
  let backToTopBtn = document.getElementById('back-to-top');
  if (!backToTopBtn) {
    backToTopBtn = document.createElement('button');
    backToTopBtn.id = 'back-to-top';
    backToTopBtn.className = 'back-to-top';
    backToTopBtn.setAttribute('aria-label', 'Scroll to top');
    backToTopBtn.setAttribute('title', 'Scroll to top');
    backToTopBtn.innerHTML = `
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="18 15 12 9 6 15"></polyline>
      </svg>
    `;
    document.body.appendChild(backToTopBtn);
  }

  function handleScroll() {
    const scrollY = window.pageYOffset || document.documentElement.scrollTop;
    const screenHeight = window.innerHeight || document.documentElement.clientHeight;
    if (scrollY > screenHeight) {
      backToTopBtn.classList.add('visible');
    } else {
      backToTopBtn.classList.remove('visible');
    }
  }

  window.addEventListener('scroll', handleScroll, { passive: true });
  backToTopBtn.addEventListener('click', () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
  handleScroll();

  // Showreel Timestamp Jumpers
  const reelBadges = document.querySelectorAll('.reel-time-badge');
  const reelIframe = document.querySelector('.hero-reel-card iframe');

  reelBadges.forEach(badge => {
    badge.addEventListener('click', () => {
      const seconds = badge.getAttribute('data-seconds');
      if (reelIframe && seconds) {
        // Post message to Vimeo player or jump URL
        const currentSrc = reelIframe.src.split('#')[0];
        reelIframe.src = `${currentSrc}#t=${seconds}s`;
      }
    });
  });

  // Initialize all interactive modules
  initAllBeforeAfter();
  initLightbox();
  initAccordions();
  initAllMultiPass();
});

