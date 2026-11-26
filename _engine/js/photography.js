/**
 * Photography & 360 Panorama Interactive Controller
 * Dynamic Flex Waterfall (3 cols for All/Photos, 2 cols for Panoramas),
 * Unified Photo & 360 WebGL Panorama Viewers with Filmstrips
 */

(function () {
  'use strict';

  let photos = [];
  let panos = [];
  let activePannellumViewer = null;
  let currentGalleryTab = 'all';
  let allWaterfallItems = [];

  const viewers = {
    photos: {
      items: () => photos,
      index: 0,
      modalId: 'photoViewerModal',
      titleId: 'photoViewerTitle',
      counterId: 'photoViewerCounter',
      trackId: 'photoFilmstripTrack',
      itemClass: 'filmstrip-item',
      onDisplay(item) {
        const img = document.getElementById('photoViewerImg');
        if (img) {
          img.style.opacity = '0.4';
          img.src = item.webp;
          img.alt = item.title;
          img.onload = () => { img.style.opacity = '1'; };
        }
      },
      onClose() {}
    },
    panos: {
      items: () => panos,
      index: 0,
      modalId: 'panoViewerModal',
      titleId: 'panoViewerTitle',
      counterId: 'panoViewerCounter',
      trackId: 'panoFilmstripTrack',
      itemClass: 'filmstrip-pano-item',
      onDisplay(item) {
        loadPannellumScene(item.webp);
      },
      onClose() {
        destroyPannellumViewer();
      }
    }
  };

  function escapeHtml(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function parseJsonScript(id) {
    const el = document.getElementById(id);
    if (!el) return [];
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      console.error(`Failed to parse ${id}:`, e);
      return [];
    }
  }

  function getTargetColumnCount(tab) {
    const w = window.innerWidth;
    if (tab === 'panos') return w <= 600 ? 1 : 2;
    return w <= 640 ? 2 : 3;
  }

  function renderWaterfall(tab) {
    currentGalleryTab = tab || currentGalleryTab;
    const container = document.getElementById('photoWaterfallContainer');
    if (!container || !allWaterfallItems.length) return;

    const items = allWaterfallItems.filter((item) => currentGalleryTab === 'all' || item.type === currentGalleryTab);
    const numCols = getTargetColumnCount(currentGalleryTab);
    const cols = Array.from({ length: numCols }, () => []);
    const colHeights = new Array(numCols).fill(0);

    items.forEach((item) => {
      let minCol = 0;
      for (let c = 1; c < numCols; c++) {
        if (colHeights[c] < colHeights[minCol]) minCol = c;
      }
      cols[minCol].push(item.element);
      colHeights[minCol] += 1 / (item.aspect || 1.778);
    });

    container.textContent = '';
    container.className = `waterfall-container waterfall-${numCols}-col`;
    cols.forEach((colItems) => {
      const colDiv = document.createElement('div');
      colDiv.className = 'waterfall-col';
      colItems.forEach((el) => {
        el.style.display = '';
        colDiv.appendChild(el);
      });
      container.appendChild(colDiv);
    });
  }

  function buildFilmstrip(key) {
    const cfg = viewers[key];
    const items = cfg.items();
    const track = document.getElementById(cfg.trackId);
    if (!track || !items.length) return;

    track.innerHTML = items.map((item, idx) => `
      <div class="${cfg.itemClass} ${idx === 0 ? 'active' : ''}" data-viewer="${key}" data-idx="${idx}" title="${escapeHtml(item.title)}">
        <img src="${item.thumb || item.webp}" alt="${escapeHtml(item.title)}" loading="lazy" decoding="async">
      </div>
    `).join('');
  }

  function updateViewerDisplay(key) {
    const cfg = viewers[key];
    const list = cfg.items();
    const item = list[cfg.index];
    if (!item) return;

    const titleEl = document.getElementById(cfg.titleId);
    const counterEl = document.getElementById(cfg.counterId);
    const prevArrow = document.querySelector(`#${cfg.modalId} .viewer-prev-arrow`);
    const nextArrow = document.querySelector(`#${cfg.modalId} .viewer-next-arrow`);

    if (titleEl) titleEl.textContent = item.title;
    if (counterEl) counterEl.textContent = `${cfg.index + 1} / ${list.length}`;
    if (prevArrow) prevArrow.style.display = cfg.index > 0 ? 'flex' : 'none';
    if (nextArrow) nextArrow.style.display = cfg.index < list.length - 1 ? 'flex' : 'none';

    const track = document.getElementById(cfg.trackId);
    if (track) {
      track.querySelectorAll(`.${cfg.itemClass}`).forEach((thumb, i) => {
        const isCurrent = i === cfg.index;
        thumb.classList.toggle('active', isCurrent);
        if (isCurrent) {
          thumb.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        }
      });
    }

    cfg.onDisplay(item);
  }

  function openViewer(key, idx) {
    const cfg = viewers[key];
    const list = cfg.items();
    if (!list.length) return;

    cfg.index = Math.max(0, Math.min(list.length - 1, idx));
    const modal = document.getElementById(cfg.modalId);
    if (modal) {
      clearTimeout(modal._closeTimer);
      modal.style.display = 'flex';
      modal.setAttribute('aria-hidden', 'false');
      requestAnimationFrame(() => modal.classList.add('active'));
      document.body.style.overflow = 'hidden';
    }
    updateViewerDisplay(key);
  }

  function closeViewer(key) {
    const cfg = viewers[key];
    const modal = document.getElementById(cfg.modalId);
    if (modal) {
      clearTimeout(modal._closeTimer);
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
      modal._closeTimer = setTimeout(() => { modal.style.display = 'none'; }, 200);
      document.body.style.overflow = '';
    }
    cfg.onClose();
  }

  function navViewer(key, delta) {
    const cfg = viewers[key];
    const list = cfg.items();
    const nextIdx = cfg.index + delta;
    if (nextIdx >= 0 && nextIdx < list.length) {
      cfg.index = nextIdx;
      updateViewerDisplay(key);
    }
  }

  function switchViewerItem(key, idx) {
    const cfg = viewers[key];
    const list = cfg.items();
    if (idx >= 0 && idx < list.length) {
      cfg.index = idx;
      updateViewerDisplay(key);
    }
  }

  function destroyPannellumViewer() {
    if (activePannellumViewer) {
      try { activePannellumViewer.destroy(); } catch (e) {}
      activePannellumViewer = null;
    }
  }

  function loadPannellumScene(imageSrc) {
    const container = document.getElementById('fullscreenPanoContainer');
    if (!container) return;

    destroyPannellumViewer();
    container.textContent = '';

    if (window.pannellum) {
      try {
        activePannellumViewer = window.pannellum.viewer('fullscreenPanoContainer', {
          type: 'equirectangular',
          panorama: imageSrc,
          autoLoad: true,
          autoRotate: -2,
          compass: false,
          showZoomCtrl: false,
          showFullscreenCtrl: false,
          mouseZoom: true
        });
      } catch (err) {
        console.error('Error starting Pannellum viewer:', err);
      }
    }
  }

  window.switchGalleryTab = function (tab, e) {
    if (e && e.stopPropagation) e.stopPropagation();

    document.querySelectorAll('.filter-bar [data-tab]').forEach((btn) => {
      btn.classList.toggle('active', btn.getAttribute('data-tab') === tab);
    });

    renderWaterfall(tab);
  };

  window.openPhotoViewer = (idx) => openViewer('photos', idx);
  window.closePhotoViewer = () => closeViewer('photos');
  window.navPhotoViewer = (delta) => navViewer('photos', delta);
  window.switchPhoto = (idx) => switchViewerItem('photos', idx);

  window.openPanoViewer = (idx) => openViewer('panos', idx);
  window.closePanoViewer = () => closeViewer('panos');
  window.navPanoViewer = (delta) => navViewer('panos', delta);
  window.switchPano = (idx) => switchViewerItem('panos', idx);

  function getActiveViewerKey() {
    for (const key of ['photos', 'panos']) {
      const modal = document.getElementById(viewers[key].modalId);
      if (modal && modal.classList.contains('active')) return key;
    }
    return null;
  }

  function initPhotography() {
    photos = parseJsonScript('photosData');
    panos = parseJsonScript('panosData');

    buildFilmstrip('photos');
    buildFilmstrip('panos');

    // Cache waterfall items from static HTML
    allWaterfallItems = Array.from(document.querySelectorAll('.waterfall-item')).map((el) => ({
      element: el,
      type: el.getAttribute('data-type') || 'photos',
      aspect: parseFloat(el.getAttribute('data-aspect') || el.style.getPropertyValue('--aspect') || '1.778')
    }));

    // Ensure mobile viewports start with responsive column count immediately
    if (getTargetColumnCount('all') !== 3) {
      renderWaterfall('all');
    }

    // Filter pill click delegation
    const filterBar = document.querySelector('.filter-bar');
    if (filterBar) {
      filterBar.addEventListener('click', (e) => {
        const btn = e.target.closest('[data-tab]');
        if (!btn) return;
        e.preventDefault();
        e.stopPropagation();
        window.switchGalleryTab(btn.getAttribute('data-tab'), e);
      });
    }

    // Waterfall tile click & keyboard activation delegation
    const container = document.getElementById('photoWaterfallContainer');
    if (container) {
      const activateTile = (tile) => {
        if (!tile) return;
        const photoIdx = tile.getAttribute('data-photo-idx');
        const panoIdx = tile.getAttribute('data-pano-idx');
        if (photoIdx !== null) openViewer('photos', parseInt(photoIdx, 10));
        else if (panoIdx !== null) openViewer('panos', parseInt(panoIdx, 10));
      };

      container.addEventListener('click', (e) => {
        activateTile(e.target.closest('[data-photo-idx], [data-pano-idx]'));
      });

      container.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          const tile = e.target.closest('[data-photo-idx], [data-pano-idx]');
          if (tile) {
            e.preventDefault();
            activateTile(tile);
          }
        }
      });
    }

    // Filmstrip click delegation
    document.addEventListener('click', (e) => {
      const thumb = e.target.closest('[data-viewer][data-idx]');
      if (!thumb) return;
      switchViewerItem(thumb.getAttribute('data-viewer'), parseInt(thumb.getAttribute('data-idx'), 10));
    });

    // Modal backdrop click on photo stage closes viewer
    const photoStage = document.getElementById('photoViewerStage');
    if (photoStage) {
      photoStage.addEventListener('click', (e) => {
        if (e.target === photoStage) closeViewer('photos');
      });
    }

    // Debounced resize redistribution (only when column count changes)
    let lastCols = getTargetColumnCount(currentGalleryTab);
    let resizeTimer = null;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {
        const nextCols = getTargetColumnCount(currentGalleryTab);
        if (nextCols !== lastCols) {
          lastCols = nextCols;
          renderWaterfall(currentGalleryTab);
        }
      }, 100);
    }, { passive: true });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      const activeKey = getActiveViewerKey();
      if (!activeKey) return;

      if (e.key === 'Escape') {
        e.preventDefault();
        closeViewer(activeKey);
      } else if (e.key === 'ArrowLeft') {
        e.preventDefault();
        navViewer(activeKey, -1);
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        navViewer(activeKey, 1);
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPhotography);
  } else {
    initPhotography();
  }
})();
