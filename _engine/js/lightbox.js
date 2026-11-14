/**
 * Lightbox Module using GLightbox
 * Touch-enabled, keyboard-accessible, smooth drag-to-pan, 100% zoom
 */

let glightboxInstance = null;

export function initLightbox() {
  scanLightboxTriggers();
}

export function scanLightboxTriggers() {
  if (typeof GLightbox === 'undefined') return;

  // Scan all static elements with [data-lightbox]
  const elements = document.querySelectorAll('[data-lightbox]');
  elements.forEach((el) => {
    el.classList.add('glightbox');
    const src = el.getAttribute('data-src') || el.getAttribute('href') || el.src;
    if (src && !el.getAttribute('href')) {
      el.setAttribute('href', src);
    }
    const caption = el.getAttribute('data-caption') || el.getAttribute('alt') || '';
    if (caption) {
      el.setAttribute('data-title', caption);
    }
    el.style.cursor = 'zoom-in';
  });

  if (elements.length > 0) {
    try {
      GLightbox({
        selector: '.glightbox',
        touchNavigation: true,
        loop: true,
        zoomable: true,
        autoplayVideos: false
      });
    } catch (e) {
      console.error('Failed to init GLightbox on selector:', e);
    }
  }
}

export function openLightboxItems(items, startIndex = 0) {
  if (!items || items.length === 0) return;
  if (typeof GLightbox === 'undefined') {
    console.error('GLightbox library is not loaded');
    return;
  }

  const elements = items.map(it => {
    const href = typeof it === 'string' ? it : (it.src || it.url || it.href);
    const title = typeof it === 'string' ? '' : (it.caption || it.title || it.alt || '');
    return {
      href: href,
      type: 'image',
      title: title
    };
  });

  // Destroy previous dynamic instance if any
  if (glightboxInstance) {
    try { glightboxInstance.destroy(); } catch (e) {}
  }

  try {
    glightboxInstance = GLightbox({
      elements: elements,
      startAt: startIndex,
      loop: elements.length > 1,
      zoomable: true,
      touchNavigation: true,
      openEffect: 'zoom',
      closeEffect: 'zoom'
    });

    glightboxInstance.openAt(startIndex);
  } catch (err) {
    console.error('Error opening GLightbox:', err);
  }
}

// Immediate global exposure
if (typeof window !== 'undefined') {
  window.openLightbox = openLightboxItems;
  window.scanLightboxTriggers = scanLightboxTriggers;
  window.initLightbox = initLightbox;
}

// Auto-init on script load
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => initLightbox());
  } else {
    initLightbox();
  }
}
