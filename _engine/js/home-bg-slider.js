/**
 * Pra - Motions: Home Page Multi-Background Parallax Wipe Slider
 * Features:
 * - Direct interactive scroll-driven wipe scrub matching scroll speed exactly
 * - Controlled forward and backward with mouse wheel, trackpad, and mobile touch
 * - Allows stopping halfway at any point with zero snapping
 * - True diagonal mask (clean 45° diagonal dividing line, not a box/square mask)
 * - Supports image (webp, jfif, jpg, png) and video (mp4, webm) backgrounds
 * - Configurable wipe direction via json key wipeFrom (bottom, left, right, top, bottom-left, top-left, etc.)
 * - Non-priority progressive lazy loading
 */

export function initHomeBackgroundSlider(containerId = 'home-bg-slider') {
  const container = document.getElementById(containerId);
  if (!container) return;

  const slides = Array.from(container.querySelectorAll('.home-bg-slide'));
  const totalSlides = slides.length;
  if (totalSlides <= 1) return;

  // On mobile screens: keep single static background image (no wipe or video background)
  const isMobile = window.matchMedia('(max-width: 860px)').matches;
  if (isMobile) {
    ensureSlideMediaLoaded(slides[0]);
    slides[0].style.visibility = 'visible';
    slides[0].style.zIndex = '1';
    slides[0].style.clipPath = 'none';
    slides[0].classList.add('is-active');

    // Pause and hide any videos
    slides.forEach((s, idx) => {
      const v = s.querySelector('video');
      if (v) v.pause();
      if (idx > 0) {
        s.style.display = 'none';
        s.style.visibility = 'hidden';
      }
    });
    return; // Exit without attaching wheel/touch wipe scrubbing listeners on mobile
  }

  // Global wipe angle/direction from container data attribute or default '45'
  const globalWipeAngle = (container.getAttribute('data-wipe-angle') || container.getAttribute('data-wipe-from') || '45').toLowerCase().trim();

  // Scroll tracking: targetScroll is driven by wheel/touch, currentScroll smoothly catches up
  let targetScroll = 0;
  let currentScroll = 0;
  let isRunning = false;

  // --------------------------------------------------------------------------
  // 1. Precise Arbitrary Angle (0-360 deg) Wipe Geometry via Polygon Clipping
  // --------------------------------------------------------------------------
  function getClipPath(directionOrAngle, progress) {
    const p = Math.max(0, Math.min(1, progress));
    if (p <= 0.0001) return 'polygon(0% 0%, 0% 0%, 0% 0%)';
    if (p >= 0.9999) return 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)';

    let raw = (directionOrAngle !== undefined && directionOrAngle !== null ? String(directionOrAngle) : (globalWipeAngle || '45')).toLowerCase().trim();
    let angle = 45;

    const namedAngles = {
      'bottom': 0,
      'bottom-left': 45,
      'bottomleft': 45,
      'left': 90,
      'top-left': 135,
      'topleft': 135,
      'top': 180,
      'top-right': 225,
      'topright': 225,
      'right': 270,
      'bottom-right': 315,
      'bottomright': 315
    };

    if (Object.prototype.hasOwnProperty.call(namedAngles, raw)) {
      angle = namedAngles[raw];
    } else {
      const parsed = parseFloat(raw);
      if (!isNaN(parsed)) {
        angle = parsed;
      }
    }

    // Normalize angle to [0, 360)
    angle = ((angle % 360) + 360) % 360;

    // Direction vector in screen space (x: right, y: down)
    const rad = (angle * Math.PI) / 180;
    const dx = Math.sin(rad);
    const dy = -Math.cos(rad);

    const corners = [
      [0.0, 0.0],
      [1.0, 0.0],
      [1.0, 1.0],
      [0.0, 1.0]
    ];

    const dots = corners.map(pt => pt[0] * dx + pt[1] * dy);
    const vMin = Math.min(...dots);
    const vMax = Math.max(...dots);
    const thresh = vMin + p * (vMax - vMin);

    const out = [];
    const len = corners.length;
    for (let i = 0; i < len; i++) {
      const currPt = corners[i];
      const prevPt = corners[(i - 1 + len) % len];
      const currIn = (currPt[0] * dx + currPt[1] * dy) <= thresh + 1e-7;
      const prevIn = (prevPt[0] * dx + prevPt[1] * dy) <= thresh + 1e-7;

      if (currIn) {
        if (!prevIn) {
          const denom = (currPt[0] - prevPt[0]) * dx + (currPt[1] - prevPt[1]) * dy;
          const t = Math.abs(denom) < 1e-9 ? 0 : (thresh - (prevPt[0] * dx + prevPt[1] * dy)) / denom;
          out.push([
            prevPt[0] + t * (currPt[0] - prevPt[0]),
            prevPt[1] + t * (currPt[1] - prevPt[1])
          ]);
        }
        out.push(currPt);
      } else if (prevIn) {
        const denom = (currPt[0] - prevPt[0]) * dx + (currPt[1] - prevPt[1]) * dy;
        const t = Math.abs(denom) < 1e-9 ? 0 : (thresh - (prevPt[0] * dx + prevPt[1] * dy)) / denom;
        out.push([
          prevPt[0] + t * (currPt[0] - prevPt[0]),
          prevPt[1] + t * (currPt[1] - prevPt[1])
        ]);
      }
    }

    if (out.length === 0) return 'polygon(0% 0%, 0% 0%, 0% 0%)';
    const ptsStr = out.map(pt => `${(pt[0] * 100).toFixed(2)}% ${(pt[1] * 100).toFixed(2)}%`).join(', ');
    return `polygon(${ptsStr})`;
  }

  // --------------------------------------------------------------------------
  // 2. Non-Priority / Lazy Media Loader (Images & Videos)
  // --------------------------------------------------------------------------
  function ensureSlideMediaLoaded(slide) {
    if (!slide) return;
    const mediaType = slide.getAttribute('data-type') || 'image';

    if (mediaType === 'video') {
      const video = slide.querySelector('video');
      const videoSrc = slide.getAttribute('data-video-src');
      const videoType = slide.getAttribute('data-video-type') || 'video/mp4';

      if (video && videoSrc && !video.querySelector('source')) {
        const source = document.createElement('source');
        source.src = videoSrc;
        source.type = videoType;
        video.appendChild(source);
        video.load();
        slide.removeAttribute('data-video-src');
      }
    } else {
      const bgUrl = slide.getAttribute('data-bg');
      if (bgUrl) {
        const inner = slide.querySelector('.home-bg-slide-inner');
        if (inner && (!inner.style.backgroundImage || inner.style.backgroundImage === 'none')) {
          inner.style.backgroundImage = `url('${bgUrl}')`;
        }
        slide.removeAttribute('data-bg');
      }
    }
    slide.setAttribute('data-loaded', 'true');
  }

  function startLazyProgressiveLoading() {
    let queueIdx = 1;
    function loadNext() {
      if (queueIdx >= totalSlides) return;
      const s = slides[queueIdx];
      const mediaType = s.getAttribute('data-type') || 'image';

      if (mediaType === 'video') {
        ensureSlideMediaLoaded(s);
        queueIdx++;
        if ('requestIdleCallback' in window) {
          requestIdleCallback(loadNext, { timeout: 2500 });
        } else {
          setTimeout(loadNext, 180);
        }
      } else {
        const bgUrl = s.getAttribute('data-bg');
        if (!bgUrl) {
          queueIdx++;
          loadNext();
          return;
        }
        const img = new Image();
        img.onload = () => {
          ensureSlideMediaLoaded(s);
          queueIdx++;
          if ('requestIdleCallback' in window) {
            requestIdleCallback(loadNext, { timeout: 2000 });
          } else {
            setTimeout(loadNext, 120);
          }
        };
        img.onerror = () => {
          queueIdx++;
          loadNext();
        };
        img.src = bgUrl;
      }
    }

    if (document.readyState === 'complete') {
      if ('requestIdleCallback' in window) {
        requestIdleCallback(loadNext, { timeout: 3000 });
      } else {
        setTimeout(loadNext, 400);
      }
    } else {
      window.addEventListener('load', () => {
        if ('requestIdleCallback' in window) {
          requestIdleCallback(loadNext, { timeout: 3000 });
        } else {
          setTimeout(loadNext, 400);
        }
      });
    }
  }

  // --------------------------------------------------------------------------
  // 3. Continuous Scroll Scrubbing & Wipe Renderer (No Snapping, Direct Speed Match)
  // --------------------------------------------------------------------------
  function renderWipe(s) {
    // Map continuous float s to cyclic [0, totalSlides)
    const normalized = ((s % totalSlides) + totalSlides) % totalSlides;
    const baseIndex = Math.floor(normalized);
    const incomingIndex = (baseIndex + 1) % totalSlides;
    const progress = normalized - baseIndex; // [0, 1)

    const baseSlide = slides[baseIndex];
    const incomingSlide = slides[incomingIndex];

    // Ensure immediate and adjacent slide media are loaded
    ensureSlideMediaLoaded(baseSlide);
    ensureSlideMediaLoaded(incomingSlide);
    // Preload next and previous in background
    ensureSlideMediaLoaded(slides[(incomingIndex + 1) % totalSlides]);
    ensureSlideMediaLoaded(slides[(baseIndex - 1 + totalSlides) % totalSlides]);

    // Handle base slide (underneath)
    baseSlide.style.visibility = 'visible';
    baseSlide.style.zIndex = '1';
    baseSlide.style.clipPath = 'none';
    baseSlide.classList.add('is-active');

    const baseVideo = baseSlide.querySelector('video');
    if (baseVideo && baseVideo.paused) {
      baseVideo.play().catch(() => {});
    }

    if (progress < 0.0005) {
      // Exactly on base slide, incoming slide not revealed
      incomingSlide.style.visibility = 'hidden';
      incomingSlide.style.zIndex = '0';
      incomingSlide.style.clipPath = 'none';
      incomingSlide.classList.remove('is-active');
    } else {
      // Incoming slide is wiping on top
      const wipeAngle = incomingSlide.getAttribute('data-wipe-angle') || incomingSlide.getAttribute('data-wipe-from') || globalWipeAngle;
      incomingSlide.style.visibility = 'visible';
      incomingSlide.style.zIndex = '2';
      incomingSlide.style.clipPath = getClipPath(wipeAngle, progress);
      incomingSlide.classList.add('is-active');

      const incomingVideo = incomingSlide.querySelector('video');
      if (incomingVideo && incomingVideo.paused) {
        incomingVideo.play().catch(() => {});
      }
    }

    // Hide all other slides and pause their videos to conserve resources
    for (let i = 0; i < totalSlides; i++) {
      if (i !== baseIndex && i !== incomingIndex) {
        const otherSlide = slides[i];
        otherSlide.style.visibility = 'hidden';
        otherSlide.style.zIndex = '0';
        otherSlide.style.clipPath = 'none';
        otherSlide.classList.remove('is-active');

        const otherVideo = otherSlide.querySelector('video');
        if (otherVideo && !otherVideo.paused) {
          otherVideo.pause();
        }
      }
    }
  }

  // --------------------------------------------------------------------------
  // 4. Animation Loop (Silky Smooth rAF Dampening, Zero Snap)
  // --------------------------------------------------------------------------
  function updateLoop() {
    const diff = targetScroll - currentScroll;

    if (Math.abs(diff) > 0.0003) {
      // Responsive easing factor: tracks hand movement closely while absorbing discrete notches
      currentScroll += diff * 0.22;
      renderWipe(currentScroll);
      requestAnimationFrame(updateLoop);
    } else {
      currentScroll = targetScroll;
      renderWipe(currentScroll);
      isRunning = false;
    }
  }

  function startAnimation() {
    if (!isRunning) {
      isRunning = true;
      requestAnimationFrame(updateLoop);
    }
  }

  // --------------------------------------------------------------------------
  // 5. Wheel Event Handler (Matches Scroll Speed, Direct Bi-Directional Scrub)
  // --------------------------------------------------------------------------
  window.addEventListener('wheel', (e) => {
    // Prevent default body bouncing
    e.preventDefault();

    // Scroll distance required to wipe 1 full background:
    // Scaled to viewport height (~750-900px) for 1:1 physical feel
    const scrollDistance = Math.max(500, window.innerHeight * 0.85);

    // Delta directly adds to target scroll (positive = forward, negative = backwards)
    targetScroll += (e.deltaY / scrollDistance);
    startAnimation();
  }, { passive: false });

  // --------------------------------------------------------------------------
  // 6. Mobile & Touch Screen Swipe Navigation (1:1 Finger Tracking & Scrubbing)
  // --------------------------------------------------------------------------
  let lastTouchY = 0;
  let lastTouchX = 0;
  let isTouching = false;

  window.addEventListener('touchstart', (e) => {
    if (e.touches && e.touches.length > 0) {
      lastTouchY = e.touches[0].clientY;
      lastTouchX = e.touches[0].clientX;
      isTouching = true;
    }
  }, { passive: true });

  window.addEventListener('touchmove', (e) => {
    if (!isTouching || !e.touches || e.touches.length === 0) return;
    const currentY = e.touches[0].clientY;
    const currentX = e.touches[0].clientX;

    const deltaY = lastTouchY - currentY; // Drag up -> forward scrub
    const deltaX = lastTouchX - currentX; // Drag left -> forward scrub

    lastTouchY = currentY;
    lastTouchX = currentX;

    const isHorizontal = ['left', 'right'].includes(globalWipeFrom);
    const primaryDelta = isHorizontal ? deltaX : deltaY;

    const scrollDistance = Math.max(380, window.innerHeight * 0.8);
    targetScroll += (primaryDelta / scrollDistance);
    startAnimation();
  }, { passive: true });

  window.addEventListener('touchend', () => {
    isTouching = false;
  }, { passive: true });

  // --------------------------------------------------------------------------
  // 7. Keyboard Navigation (Smooth 1-Slide Glides)
  // --------------------------------------------------------------------------
  window.addEventListener('keydown', (e) => {
    if (e.target && ['input', 'textarea', 'select'].includes(e.target.tagName.toLowerCase())) return;

    if (e.key === 'ArrowDown' || e.key === 'PageDown' || (e.key === ' ' && !e.shiftKey)) {
      e.preventDefault();
      targetScroll = Math.floor(targetScroll + 1);
      startAnimation();
    } else if (e.key === 'ArrowUp' || e.key === 'PageUp' || (e.key === ' ' && e.shiftKey)) {
      e.preventDefault();
      targetScroll = Math.ceil(targetScroll - 1);
      startAnimation();
    }
  });

  // Initial render at position 0
  renderWipe(0);

  // Progressive lazy load remaining backgrounds
  startLazyProgressiveLoading();
}
