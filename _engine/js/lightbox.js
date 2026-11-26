/**
 * Lightbox Module using GLightbox
 * Touch-enabled, keyboard-accessible, smooth zoom & gallery navigation
 */

let glightboxInstance = null;

export function initLightbox() {
  if (typeof GLightbox === 'undefined') return;

  const elements = document.querySelectorAll('[data-lightbox]');
  if (elements.length === 0) return;

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

  try {
    GLightbox({
      selector: '.glightbox',
      touchNavigation: true,
      loop: true,
      zoomable: true,
      openEffect: 'fade',
      closeEffect: 'fade',
      slideEffect: 'fade',
      autoplayVideos: false
    });
  } catch (e) {
    console.error('Failed to init GLightbox on selector:', e);
  }
}

export function openLightbox(items, startIndex = 0) {
  if (!items || items.length === 0) return;
  if (typeof GLightbox === 'undefined') {
    console.error('GLightbox library is not loaded');
    return;
  }

  const elements = items.map((it) => {
    const href = typeof it === 'string' ? it : (it.src || it.url || it.href);
    const title = typeof it === 'string' ? '' : (it.caption || it.title || it.alt || '');
    return {
      href,
      type: 'image',
      title: title || ''
    };
  });

  if (glightboxInstance) {
    try { glightboxInstance.destroy(); } catch (e) {}
    glightboxInstance = null;
  }

  try {
    glightboxInstance = GLightbox({
      elements,
      startAt: startIndex,
      loop: elements.length > 1,
      zoomable: true,
      touchNavigation: true,
      openEffect: 'fade',
      closeEffect: 'fade',
      slideEffect: 'fade'
    });

    glightboxInstance.on('open', () => {
      document.body.classList.add('lightbox-active');
    });

    glightboxInstance.on('close', () => {
      document.body.classList.remove('lightbox-active');
      if (glightboxInstance) {
        try { glightboxInstance.destroy(); } catch (e) {}
        glightboxInstance = null;
      }
    });

    glightboxInstance.open();
  } catch (err) {
    console.error('Error opening GLightbox:', err);
  }
}

if (typeof window !== 'undefined') {
  window.openLightbox = openLightbox;
  window.initLightbox = initLightbox;
}
