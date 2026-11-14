/**
 * Photography & 360 Panorama Interactive Controller
 * Tab Switching (Panos / Photos), Fullscreen Photo Viewer & Fullscreen 360 WebGL Panorama Viewer
 * with Bottom Filmstrips and Bulletproof Close Triggers
 */

(function () {
  'use strict';

  let photos = [];
  let panos = [];
  let currentPhotoIdx = 0;
  let currentPanoIdx = 0;
  let activePannellumViewer = null;

  function initPhotography() {
    // 1. Read JSON data embedded in page
    const photosEl = document.getElementById('photosData');
    if (photosEl) {
      try {
        photos = JSON.parse(photosEl.textContent);
      } catch (e) {
        console.error('Failed to parse photosData:', e);
      }
    }

    const panosEl = document.getElementById('panosData');
    if (panosEl) {
      try {
        panos = JSON.parse(panosEl.textContent);
      } catch (e) {
        console.error('Failed to parse panosData:', e);
      }
    }

    // 2. Build Filmstrips
    buildPhotoFilmstrip();
    buildPanoFilmstrip();

    // 3. Attach Direct Close Button Click Handlers
    const photoCloseBtn = document.getElementById('photoViewerCloseBtn');
    if (photoCloseBtn) {
      photoCloseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        closePhotoViewer();
      });
    }

    const panoCloseBtn = document.getElementById('panoViewerCloseBtn');
    if (panoCloseBtn) {
      panoCloseBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        closePanoViewer();
      });
    }

    // 4. Attach Global Keyboard Navigation (Esc, Left, Right)
    document.addEventListener('keydown', handleKeyNavigation);
  }

  // --------------------------------------------------------------------------
  // Tab Switching Controller (Pano 1st Tab, Photos 2nd Tab)
  // --------------------------------------------------------------------------
  window.switchGalleryTab = function (tab) {
    const panosSec = document.getElementById('panos-section');
    const photosSec = document.getElementById('photos-section');
    const tabPanos = document.getElementById('tabBtnPanos');
    const tabPhotos = document.getElementById('tabBtnPhotos');

    if (tab === 'panos') {
      if (panosSec) panosSec.style.display = 'block';
      if (photosSec) photosSec.style.display = 'none';
      if (tabPanos) tabPanos.classList.add('active');
      if (tabPhotos) tabPhotos.classList.remove('active');
    } else {
      if (panosSec) panosSec.style.display = 'none';
      if (photosSec) photosSec.style.display = 'block';
      if (tabPanos) tabPanos.classList.remove('active');
      if (tabPhotos) tabPhotos.classList.add('active');
    }
  };

  // --------------------------------------------------------------------------
  // Filmstrip Builders
  // --------------------------------------------------------------------------
  function buildPhotoFilmstrip() {
    const track = document.getElementById('photoFilmstripTrack');
    if (!track || !photos.length) return;

    track.innerHTML = photos.map((p, idx) => `
      <div class="filmstrip-item ${idx === 0 ? 'active' : ''}" data-idx="${idx}" onclick="switchPhoto(${idx})" title="${escapeHtml(p.title)}">
        <img src="${p.webp}" alt="${escapeHtml(p.title)}" loading="lazy">
      </div>
    `).join('');
  }

  function buildPanoFilmstrip() {
    const track = document.getElementById('panoFilmstripTrack');
    if (!track || !panos.length) return;

    track.innerHTML = panos.map((p, idx) => `
      <div class="filmstrip-pano-item ${idx === 0 ? 'active' : ''}" data-idx="${idx}" onclick="switchPano(${idx})" title="${escapeHtml(p.title)}">
        <img src="${p.webp}" alt="${escapeHtml(p.title)}" loading="lazy">
      </div>
    `).join('');
  }

  // --------------------------------------------------------------------------
  // 1. Fullscreen Photo Viewer Controller
  // --------------------------------------------------------------------------
  window.openPhotoViewer = function (idx) {
    if (!photos.length) return;
    currentPhotoIdx = Math.max(0, Math.min(photos.length - 1, idx));
    updatePhotoViewerDisplay();

    const modal = document.getElementById('photoViewerModal');
    if (modal) {
      modal.style.display = 'flex';
      requestAnimationFrame(() => {
        modal.classList.add('active');
      });
      document.body.style.overflow = 'hidden';
    }
  };

  window.closePhotoViewer = function () {
    const modal = document.getElementById('photoViewerModal');
    if (modal) {
      modal.classList.remove('active');
      setTimeout(() => {
        modal.style.display = 'none';
      }, 200);
      document.body.style.overflow = '';
    }
  };

  window.navPhotoViewer = function (delta) {
    if (!photos.length) return;
    const newIdx = currentPhotoIdx + delta;
    if (newIdx >= 0 && newIdx < photos.length) {
      currentPhotoIdx = newIdx;
      updatePhotoViewerDisplay();
    }
  };

  window.switchPhoto = function (idx) {
    if (idx >= 0 && idx < photos.length) {
      currentPhotoIdx = idx;
      updatePhotoViewerDisplay();
    }
  };

  function updatePhotoViewerDisplay() {
    const photo = photos[currentPhotoIdx];
    if (!photo) return;

    const img = document.getElementById('photoViewerImg');
    const title = document.getElementById('photoViewerTitle');
    const counter = document.getElementById('photoViewerCounter');
    const prevArrow = document.querySelector('#photoViewerModal .viewer-prev-arrow');
    const nextArrow = document.querySelector('#photoViewerModal .viewer-next-arrow');

    if (img) {
      img.style.opacity = '0.4';
      img.src = photo.webp;
      img.alt = photo.title;
      img.onload = () => { img.style.opacity = '1'; };
    }

    if (title) title.textContent = photo.title;
    if (counter) counter.textContent = `${currentPhotoIdx + 1} / ${photos.length}`;

    // Hide arrows at boundaries
    if (prevArrow) prevArrow.style.display = currentPhotoIdx > 0 ? 'flex' : 'none';
    if (nextArrow) nextArrow.style.display = currentPhotoIdx < photos.length - 1 ? 'flex' : 'none';

    // Update active thumbnail in filmstrip
    const track = document.getElementById('photoFilmstripTrack');
    if (track) {
      const items = track.querySelectorAll('.filmstrip-item');
      items.forEach((item, i) => {
        if (i === currentPhotoIdx) {
          item.classList.add('active');
          item.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        } else {
          item.classList.remove('active');
        }
      });
    }
  }

  // --------------------------------------------------------------------------
  // 2. Fullscreen 360 Panorama Viewer Controller
  // --------------------------------------------------------------------------
  window.openPanoViewer = function (idx) {
    if (!panos.length) return;
    currentPanoIdx = Math.max(0, Math.min(panos.length - 1, idx));

    const modal = document.getElementById('panoViewerModal');
    if (modal) {
      modal.style.display = 'flex';
      requestAnimationFrame(() => {
        modal.classList.add('active');
      });
      document.body.style.overflow = 'hidden';
    }

    updatePanoViewerDisplay();
  };

  window.closePanoViewer = function () {
    const modal = document.getElementById('panoViewerModal');
    if (modal) {
      modal.classList.remove('active');
      setTimeout(() => {
        modal.style.display = 'none';
      }, 200);
      document.body.style.overflow = '';
    }

    if (activePannellumViewer) {
      try {
        activePannellumViewer.destroy();
      } catch (e) {}
      activePannellumViewer = null;
    }
  };

  window.navPanoViewer = function (delta) {
    if (!panos.length) return;
    const newIdx = currentPanoIdx + delta;
    if (newIdx >= 0 && newIdx < panos.length) {
      currentPanoIdx = newIdx;
      updatePanoViewerDisplay();
    }
  };

  window.switchPano = function (idx) {
    if (idx >= 0 && idx < panos.length) {
      currentPanoIdx = idx;
      updatePanoViewerDisplay();
    }
  };

  function updatePanoViewerDisplay() {
    const pano = panos[currentPanoIdx];
    if (!pano) return;

    const title = document.getElementById('panoViewerTitle');
    const counter = document.getElementById('panoViewerCounter');
    const prevArrow = document.querySelector('#panoViewerModal .viewer-prev-arrow');
    const nextArrow = document.querySelector('#panoViewerModal .viewer-next-arrow');

    if (title) title.textContent = pano.title;
    if (counter) counter.textContent = `${currentPanoIdx + 1} / ${panos.length}`;

    if (prevArrow) prevArrow.style.display = currentPanoIdx > 0 ? 'flex' : 'none';
    if (nextArrow) nextArrow.style.display = currentPanoIdx < panos.length - 1 ? 'flex' : 'none';

    // Update filmstrip active state
    const track = document.getElementById('panoFilmstripTrack');
    if (track) {
      const items = track.querySelectorAll('.filmstrip-pano-item');
      items.forEach((item, i) => {
        if (i === currentPanoIdx) {
          item.classList.add('active');
          item.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
        } else {
          item.classList.remove('active');
        }
      });
    }

    // Load Pannellum Scene
    loadPannellumScene(pano.webp);
  }

  function loadPannellumScene(imageSrc) {
    const container = document.getElementById('fullscreenPanoContainer');
    if (!container) return;

    if (activePannellumViewer) {
      try {
        activePannellumViewer.destroy();
      } catch (e) {}
      activePannellumViewer = null;
    }

    // Clear container
    container.innerHTML = '';

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
    } else {
      console.warn('Pannellum library not loaded yet');
    }
  }

  // --------------------------------------------------------------------------
  // Keyboard Navigation
  // --------------------------------------------------------------------------
  function handleKeyNavigation(e) {
    const photoModal = document.getElementById('photoViewerModal');
    const panoModal = document.getElementById('panoViewerModal');

    const photoActive = photoModal && photoModal.classList.contains('active');
    const panoActive = panoModal && panoModal.classList.contains('active');

    if (!photoActive && !panoActive) return;

    if (e.key === 'Escape') {
      e.preventDefault();
      if (photoActive) closePhotoViewer();
      if (panoActive) closePanoViewer();
    } else if (e.key === 'ArrowLeft') {
      e.preventDefault();
      if (photoActive) navPhotoViewer(-1);
      if (panoActive) navPanoViewer(-1);
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      if (photoActive) navPhotoViewer(1);
      if (panoActive) navPanoViewer(1);
    }
  }

  function escapeHtml(str) {
    if (!str) return '';
    return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
  }

  // DOM ready init
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initPhotography);
  } else {
    initPhotography();
  }

})();
