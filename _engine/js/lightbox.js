/**
 * High-Performance Native Lightbox with 100% Zoom & Fullscreen Utilization
 * Touch-enabled, keyboard-accessible, smooth drag-to-pan, zero bloated dependencies
 */

let lightboxOverlay = null;
let currentItems = [];
let currentIndex = 0;
let isZoomed = false;

// DOM elements
let imgEl = null;
let imgWrapper = null;
let captionEl = null;
let closeBtn = null;
let prevBtn = null;
let nextBtn = null;
let zoomBtn = null;

// Drag-to-pan state
let isDragging = false;
let startX = 0;
let startY = 0;
let scrollStartLeft = 0;
let scrollStartTop = 0;
let dragMoved = false;

export function initLightbox() {
  if (lightboxOverlay) return;

  // Create Lightbox DOM structure
  lightboxOverlay = document.createElement('div');
  lightboxOverlay.className = 'lightbox-overlay';
  lightboxOverlay.innerHTML = `
    <div class="lightbox-dialog" role="dialog" aria-modal="true" aria-label="Image Preview">
      <div class="lightbox-controls">
        <button type="button" class="lightbox-btn lightbox-zoom" aria-label="Toggle 100% Zoom" title="Toggle 100% Zoom (Z)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            <line x1="11" y1="8" x2="11" y2="14"></line>
            <line x1="8" y1="11" x2="14" y2="11"></line>
          </svg>
          <span class="zoom-label">100%</span>
        </button>
        <button type="button" class="lightbox-btn lightbox-close" aria-label="Close Lightbox" title="Close (Esc)">&times;</button>
      </div>
      
      <button type="button" class="lightbox-btn lightbox-prev" aria-label="Previous Image" title="Previous Image">&#10094;</button>
      
      <div class="lightbox-img-wrapper" id="lightboxImgWrapper">
        <img class="lightbox-img" id="lightboxImg" src="" alt="Preview">
      </div>
      
      <button type="button" class="lightbox-btn lightbox-next" aria-label="Next Image" title="Next Image">&#10095;</button>
      
      <div class="lightbox-caption"></div>
    </div>
  `;
  document.body.appendChild(lightboxOverlay);

  imgEl = lightboxOverlay.querySelector('.lightbox-img');
  imgWrapper = lightboxOverlay.querySelector('.lightbox-img-wrapper');
  captionEl = lightboxOverlay.querySelector('.lightbox-caption');
  closeBtn = lightboxOverlay.querySelector('.lightbox-close');
  prevBtn = lightboxOverlay.querySelector('.lightbox-prev');
  nextBtn = lightboxOverlay.querySelector('.lightbox-next');
  zoomBtn = lightboxOverlay.querySelector('.lightbox-zoom');

  // Zoom Toggle Logic
  function toggleZoom(targetClientX, targetClientY) {
    if (!imgEl || !imgEl.src) return;

    if (!isZoomed) {
      // Switch to 100% native resolution
      isZoomed = true;
      imgWrapper.classList.add('is-zoomed');
      zoomBtn.classList.add('active');
      zoomBtn.querySelector('.zoom-label').textContent = 'Fit';

      // If user clicked a specific point on the image, center around it
      if (typeof targetClientX === 'number' && typeof targetClientY === 'number') {
        const rect = imgEl.getBoundingClientRect();
        const clickPercentX = Math.max(0, Math.min(1, (targetClientX - rect.left) / rect.width));
        const clickPercentY = Math.max(0, Math.min(1, (targetClientY - rect.top) / rect.height));

        requestAnimationFrame(() => {
          const natW = imgEl.naturalWidth || imgEl.offsetWidth;
          const natH = imgEl.naturalHeight || imgEl.offsetHeight;
          imgWrapper.scrollLeft = (clickPercentX * natW) - (imgWrapper.clientWidth / 2);
          imgWrapper.scrollTop = (clickPercentY * natH) - (imgWrapper.clientHeight / 2);
        });
      } else {
        // Center scroll
        requestAnimationFrame(() => {
          imgWrapper.scrollLeft = (imgWrapper.scrollWidth - imgWrapper.clientWidth) / 2;
          imgWrapper.scrollTop = (imgWrapper.scrollHeight - imgWrapper.clientHeight) / 2;
        });
      }
    } else {
      // Reset back to Fit-to-screen mode
      resetZoom();
    }
  }

  function resetZoom() {
    isZoomed = false;
    if (imgWrapper) {
      imgWrapper.classList.remove('is-zoomed');
      imgWrapper.scrollLeft = 0;
      imgWrapper.scrollTop = 0;
    }
    if (zoomBtn) {
      zoomBtn.classList.remove('active');
      zoomBtn.querySelector('.zoom-label').textContent = '100%';
    }
  }

  // Drag-to-pan in 100% Zoom mode
  imgWrapper.addEventListener('mousedown', (e) => {
    if (!isZoomed || e.button !== 0) return;
    isDragging = true;
    dragMoved = false;
    startX = e.pageX;
    startY = e.pageY;
    scrollStartLeft = imgWrapper.scrollLeft;
    scrollStartTop = imgWrapper.scrollTop;
    e.preventDefault();
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging || !isZoomed) return;
    const dx = e.pageX - startX;
    const dy = e.pageY - startY;
    if (Math.abs(dx) > 3 || Math.abs(dy) > 3) {
      dragMoved = true;
    }
    imgWrapper.scrollLeft = scrollStartLeft - dx;
    imgWrapper.scrollTop = scrollStartTop - dy;
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });

  // Clicking image toggles zoom (unless user just completed a drag)
  imgEl.addEventListener('click', (e) => {
    if (dragMoved) {
      dragMoved = false;
      return;
    }
    toggleZoom(e.clientX, e.clientY);
  });

  // Zoom Button Click
  zoomBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    toggleZoom();
  });

  function open(index) {
    currentIndex = index;
    resetZoom();
    updateContent();
    lightboxOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function close() {
    resetZoom();
    lightboxOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function updateContent() {
    const item = currentItems[currentIndex];
    if (!item) return;

    resetZoom();
    imgEl.src = item.src;
    imgEl.alt = item.caption || 'Image preview';
    captionEl.textContent = item.caption || '';

    // Show/hide prev/next buttons based on item count
    if (currentItems.length <= 1) {
      prevBtn.style.display = 'none';
      nextBtn.style.display = 'none';
    } else {
      prevBtn.style.display = 'flex';
      nextBtn.style.display = 'flex';
    }
  }

  function next() {
    if (currentItems.length <= 1) return;
    currentIndex = (currentIndex + 1) % currentItems.length;
    updateContent();
  }

  function prev() {
    if (currentItems.length <= 1) return;
    currentIndex = (currentIndex - 1 + currentItems.length) % currentItems.length;
    updateContent();
  }

  // Event Listeners
  closeBtn.addEventListener('click', close);
  prevBtn.addEventListener('click', prev);
  nextBtn.addEventListener('click', next);

  lightboxOverlay.addEventListener('click', (e) => {
    if (e.target === lightboxOverlay) close();
  });

  window.addEventListener('keydown', (e) => {
    if (!lightboxOverlay.classList.contains('active')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowRight') next();
    if (e.key === 'ArrowLeft') prev();
    if (e.key === 'z' || e.key === 'Z') toggleZoom();
  });

  // Touch Swipe for Mobile
  let touchStartX = 0;
  lightboxOverlay.addEventListener('touchstart', (e) => {
    if (isZoomed) return;
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  lightboxOverlay.addEventListener('touchend', (e) => {
    if (isZoomed) return;
    const touchEndX = e.changedTouches[0].screenX;
    if (touchEndX < touchStartX - 50) next();
    if (touchEndX > touchStartX + 50) prev();
  }, { passive: true });

  // Attach to all static elements with [data-lightbox]
  scanLightboxTriggers(open);

  // Global helper for opening custom list of images
  window.openLightbox = function (items, startIndex = 0) {
    if (!items || items.length === 0) return;
    currentItems = items.map(it => {
      if (typeof it === 'string') return { src: it, caption: '' };
      return { src: it.src || it.url, caption: it.caption || it.alt || '' };
    });
    open(startIndex);
  };

  window.scanLightboxTriggers = function () {
    scanLightboxTriggers(open);
  };
}

export function openLightboxItems(items, startIndex = 0) {
  if (!lightboxOverlay) initLightbox();
  if (window.openLightbox) {
    window.openLightbox(items, startIndex);
  }
}

export function scanLightboxTriggers(openFn) {
  const elements = document.querySelectorAll('[data-lightbox]');
  currentItems = [];

  elements.forEach((el, index) => {
    const src = el.getAttribute('data-src') || el.getAttribute('href') || el.src;
    const caption = el.getAttribute('data-caption') || el.getAttribute('alt') || '';
    currentItems.push({ src, caption });

    el.style.cursor = 'zoom-in';
    el.onclick = (e) => {
      e.preventDefault();
      if (openFn) {
        openFn(index);
      } else if (window.openLightbox) {
        window.openLightbox(currentItems, index);
      }
    };
  });
}
