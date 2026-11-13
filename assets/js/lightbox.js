/**
 * High-Performance Native Lightbox
 * Touch-enabled, keyboard-accessible, zero bloated dependencies
 */
let lightboxOverlay = null;
let currentItems = [];
let currentIndex = 0;

export function initLightbox() {
  if (lightboxOverlay) return;

  // Create Lightbox DOM structure
  lightboxOverlay = document.createElement('div');
  lightboxOverlay.className = 'lightbox-overlay';
  lightboxOverlay.innerHTML = `
    <div class="lightbox-dialog" role="dialog" aria-modal="true" aria-label="Image Preview">
      <button class="lightbox-btn lightbox-close" aria-label="Close Lightbox">&times;</button>
      <button class="lightbox-btn lightbox-prev" aria-label="Previous Image">&#10094;</button>
      <div class="lightbox-img-wrapper">
        <img class="lightbox-img" src="" alt="Preview">
      </div>
      <button class="lightbox-btn lightbox-next" aria-label="Next Image">&#10095;</button>
      <div class="lightbox-caption"></div>
    </div>
  `;
  document.body.appendChild(lightboxOverlay);

  const imgEl = lightboxOverlay.querySelector('.lightbox-img');
  const captionEl = lightboxOverlay.querySelector('.lightbox-caption');
  const closeBtn = lightboxOverlay.querySelector('.lightbox-close');
  const prevBtn = lightboxOverlay.querySelector('.lightbox-prev');
  const nextBtn = lightboxOverlay.querySelector('.lightbox-next');

  function open(index) {
    currentIndex = index;
    updateContent();
    lightboxOverlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function close() {
    lightboxOverlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  function updateContent() {
    const item = currentItems[currentIndex];
    if (!item) return;
    imgEl.src = item.src;
    imgEl.alt = item.caption || 'Image preview';
    captionEl.textContent = item.caption || '';
  }

  function next() {
    currentIndex = (currentIndex + 1) % currentItems.length;
    updateContent();
  }

  function prev() {
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
  });

  // Touch Swipe for Mobile
  let touchStartX = 0;
  lightboxOverlay.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, { passive: true });

  lightboxOverlay.addEventListener('touchend', (e) => {
    const touchEndX = e.changedTouches[0].screenX;
    if (touchEndX < touchStartX - 50) next();
    if (touchEndX > touchStartX + 50) prev();
  }, { passive: true });

  // Attach to all elements with [data-lightbox]
  scanLightboxTriggers(open);
}

export function scanLightboxTriggers(openFn) {
  const elements = document.querySelectorAll('[data-lightbox]');
  currentItems = [];

  elements.forEach((el, index) => {
    const src = el.getAttribute('data-src') || el.getAttribute('href') || el.src;
    const caption = el.getAttribute('data-caption') || el.getAttribute('alt') || '';
    currentItems.push({ src, caption });

    el.style.cursor = 'zoom-in';
    el.addEventListener('click', (e) => {
      e.preventDefault();
      if (openFn) openFn(index);
    });
  });
}
