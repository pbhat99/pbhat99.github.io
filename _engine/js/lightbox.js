/**
 * Lightbox Module using GLightbox
 * Touch-enabled, keyboard-accessible, smooth drag-to-pan, 100% zoom
 */

(function () {
  'use strict';

  let glightboxInstance = null;

  function initLightbox() {
    scanLightboxTriggers();
  }

  function scanLightboxTriggers() {
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
          openEffect: 'fade',
          closeEffect: 'fade',
          slideEffect: 'fade',
          autoplayVideos: false
        });
      } catch (e) {
        console.error('Failed to init GLightbox on selector:', e);
      }
    }
  }

  function openLightboxItems(items, startIndex = 0) {
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
        title: title || ''
      };
    });

    // Destroy previous dynamic instance if any
    if (glightboxInstance) {
      try { glightboxInstance.destroy(); } catch (e) {}
      glightboxInstance = null;
    }

    try {
      glightboxInstance = GLightbox({
        elements: elements,
        startAt: startIndex,
        loop: elements.length > 1,
        zoomable: true,
        touchNavigation: true,
        openEffect: 'fade',
        closeEffect: 'fade',
        slideEffect: 'fade'
      });

      // Hide blog reader floating buttons while lightbox is open to eliminate any overlap
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

      // open() directly displays the slide specified by startAt without race condition
      glightboxInstance.open();
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

  // Auto-init on script load or DOM ready
  if (typeof document !== 'undefined') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', () => initLightbox());
    } else {
      initLightbox();
    }
  }

  if (typeof window !== 'undefined') {
    window.__lightboxExports = { initLightbox, scanLightboxTriggers, openLightboxItems };
  }
})();

export const initLightbox = typeof window !== 'undefined' && window.__lightboxExports ? window.__lightboxExports.initLightbox : function(){};
export const scanLightboxTriggers = typeof window !== 'undefined' && window.__lightboxExports ? window.__lightboxExports.scanLightboxTriggers : function(){};
export const openLightboxItems = typeof window !== 'undefined' && window.__lightboxExports ? window.__lightboxExports.openLightboxItems : function(){};

