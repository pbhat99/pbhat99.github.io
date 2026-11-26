/**
 * Pra - Motions: Home Page Multi-Background Parallax Wipe Slider
 * - Direct interactive scroll-driven wipe scrub matching scroll speed
 * - Arbitrary angle diagonal polygon clipping
 * - Non-priority progressive lazy loading for images & videos
 * - Desktop-only auto-hiding header (stays static/visible on mobile <= 860px)
 */

const MOBILE_MQ = '(max-width: 860px)';

export function initHomeHeaderScroll() {
  const header = document.querySelector('.site-header');
  if (!header) return;

  const isMobile = () => window.matchMedia(MOBILE_MQ).matches;
  if (isMobile()) {
    header.classList.remove('header-hidden');
    return;
  }

  let isHeaderHidden = false;

  function setHeaderVisibility(show) {
    if (isMobile()) {
      header.classList.remove('header-hidden');
      isHeaderHidden = false;
      return;
    }

    if (show && isHeaderHidden) {
      header.classList.remove('header-hidden');
      isHeaderHidden = false;
    } else if (!show && !isHeaderHidden) {
      const navLinks = document.querySelector('.nav-links');
      if (navLinks && navLinks.classList.contains('active')) return;
      header.classList.add('header-hidden');
      isHeaderHidden = true;
    }
  }

  // Hide strictly on scroll down; do NOT unhide on scroll up (ArrowUp / PageUp / wheel up)
  window.addEventListener('wheel', (e) => {
    if (e.deltaY > 3) setHeaderVisibility(false);
  }, { passive: true });

  window.addEventListener('keydown', (e) => {
    if (['ArrowDown', 'PageDown', ' '].includes(e.key)) {
      setHeaderVisibility(false);
    }
  });

  // Unhide on mouse movement anywhere across the full viewport
  let lastMouseX = -1;
  let lastMouseY = -1;
  window.addEventListener('mousemove', (e) => {
    if (lastMouseX === e.clientX && lastMouseY === e.clientY) return;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
    setHeaderVisibility(true);
  }, { passive: true });

  window.addEventListener('resize', () => {
    if (isMobile()) {
      header.classList.remove('header-hidden');
      isHeaderHidden = false;
    }
  }, { passive: true });
}

export function initHomeBackgroundSlider(containerId = 'home-bg-slider') {
  initHomeHeaderScroll();

  const container = document.getElementById(containerId);
  if (!container) return;

  const slides = Array.from(container.querySelectorAll('.home-bg-slide'));
  const totalSlides = slides.length;
  if (totalSlides <= 1) return;

  if (window.matchMedia(MOBILE_MQ).matches) {
    ensureSlideMediaLoaded(slides[0]);
    slides[0].style.visibility = 'visible';
    slides[0].style.zIndex = '1';
    slides[0].style.clipPath = 'none';
    slides[0].classList.add('is-active');

    slides.forEach((s, idx) => {
      const v = s.querySelector('video');
      if (v) v.pause();
      if (idx > 0) {
        s.style.display = 'none';
        s.style.visibility = 'hidden';
      }
    });
    return;
  }

  const globalWipeAngle = (container.getAttribute('data-wipe-angle') || container.getAttribute('data-wipe-from') || '45').toLowerCase().trim();
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

  function resolveAngleDegrees(directionOrAngle) {
    const raw = (directionOrAngle !== undefined && directionOrAngle !== null
      ? String(directionOrAngle)
      : globalWipeAngle || '45'
    ).toLowerCase().trim();

    let angle = 45;
    if (Object.prototype.hasOwnProperty.call(namedAngles, raw)) {
      angle = namedAngles[raw];
    } else {
      const parsed = parseFloat(raw);
      if (!Number.isNaN(parsed)) angle = parsed;
    }
    return ((angle % 360) + 360) % 360;
  }

  function getClipPath(directionOrAngle, progress) {
    const p = Math.max(0, Math.min(1, progress));
    if (p <= 0.0001) return 'polygon(0% 0%, 0% 0%, 0% 0%)';
    if (p >= 0.9999) return 'polygon(0% 0%, 100% 0%, 100% 100%, 0% 100%)';

    const rad = (resolveAngleDegrees(directionOrAngle) * Math.PI) / 180;
    const dx = Math.sin(rad);
    const dy = -Math.cos(rad);

    const corners = [[0.0, 0.0], [1.0, 0.0], [1.0, 1.0], [0.0, 1.0]];
    const dots = corners.map(([x, y]) => x * dx + y * dy);
    const vMin = Math.min(...dots);
    const vMax = Math.max(...dots);
    const thresh = vMin + p * (vMax - vMin);

    const out = [];
    const len = corners.length;
    for (let i = 0; i < len; i++) {
      const curr = corners[i];
      const prev = corners[(i - 1 + len) % len];
      const currIn = (curr[0] * dx + curr[1] * dy) <= thresh + 1e-7;
      const prevIn = (prev[0] * dx + prev[1] * dy) <= thresh + 1e-7;

      if (currIn !== prevIn) {
        const denom = (curr[0] - prev[0]) * dx + (curr[1] - prev[1]) * dy;
        const t = Math.abs(denom) < 1e-9 ? 0 : (thresh - (prev[0] * dx + prev[1] * dy)) / denom;
        out.push([
          prev[0] + t * (curr[0] - prev[0]),
          prev[1] + t * (curr[1] - prev[1])
        ]);
      }
      if (currIn) out.push(curr);
    }

    if (out.length === 0) return 'polygon(0% 0%, 0% 0%, 0% 0%)';
    return `polygon(${out.map(([x, y]) => `${(x * 100).toFixed(2)}% ${(y * 100).toFixed(2)}%`).join(', ')})`;
  }

  function scheduleIdle(fn, timeoutMs, fallbackMs) {
    if ('requestIdleCallback' in window) {
      requestIdleCallback(fn, { timeout: timeoutMs });
    } else {
      setTimeout(fn, fallbackMs);
    }
  }

  function ensureSlideMediaLoaded(slide) {
    if (!slide || slide.getAttribute('data-loaded') === 'true') return;
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
      const slide = slides[queueIdx];
      if (!slide || slide.getAttribute('data-loaded') === 'true') {
        queueIdx++;
        scheduleIdle(loadNext, 2500, 200);
        return;
      }

      const mediaType = slide.getAttribute('data-type') || 'image';
      if (mediaType === 'video') {
        ensureSlideMediaLoaded(slide);
        queueIdx++;
        scheduleIdle(loadNext, 3500, 350);
      } else {
        const bgUrl = slide.getAttribute('data-bg');
        if (!bgUrl) {
          queueIdx++;
          scheduleIdle(loadNext, 2000, 150);
          return;
        }
        const img = new Image();
        // Lowest network priority so page resources & background_00.webp always finish first
        if ('fetchPriority' in img) img.fetchPriority = 'low';
        img.decoding = 'async';
        img.onload = () => {
          ensureSlideMediaLoaded(slide);
          queueIdx++;
          scheduleIdle(loadNext, 3000, 250);
        };
        img.onerror = () => {
          queueIdx++;
          scheduleIdle(loadNext, 3000, 250);
        };
        img.src = bgUrl;
      }
    }

    const beginLastPriorityPrefetch = () => {
      // Wait for post-load settle (fonts, scripts, canvas) before queuing lowest-priority slides
      setTimeout(() => scheduleIdle(loadNext, 4000, 500), 1500);
    };

    if (document.readyState === 'complete') {
      beginLastPriorityPrefetch();
    } else {
      window.addEventListener('load', beginLastPriorityPrefetch, { once: true });
    }
  }

  let targetScroll = 0;
  let currentScroll = 0;
  let isRunning = false;

  function renderWipe(s) {
    const normalized = ((s % totalSlides) + totalSlides) % totalSlides;
    const baseIndex = Math.floor(normalized);
    const incomingIndex = (baseIndex + 1) % totalSlides;
    const progress = normalized - baseIndex;

    const baseSlide = slides[baseIndex];
    const incomingSlide = slides[incomingIndex];

    // Load only the visible slide immediately; incoming slide loads on demand once wiping starts
    ensureSlideMediaLoaded(baseSlide);

    baseSlide.style.visibility = 'visible';
    baseSlide.style.zIndex = '1';
    baseSlide.style.clipPath = 'none';
    baseSlide.classList.add('is-active');

    const baseVideo = baseSlide.querySelector('video');
    if (baseVideo && baseVideo.paused && !document.hidden) {
      baseVideo.play().catch(() => {});
    }

    if (progress < 0.0005) {
      incomingSlide.style.visibility = 'hidden';
      incomingSlide.style.zIndex = '0';
      incomingSlide.style.clipPath = 'none';
      incomingSlide.classList.remove('is-active');
    } else {
      ensureSlideMediaLoaded(incomingSlide);
      const wipeAngle = incomingSlide.getAttribute('data-wipe-angle') || incomingSlide.getAttribute('data-wipe-from') || globalWipeAngle;
      incomingSlide.style.visibility = 'visible';
      incomingSlide.style.zIndex = '2';
      incomingSlide.style.clipPath = getClipPath(wipeAngle, progress);
      incomingSlide.classList.add('is-active');

      const incomingVideo = incomingSlide.querySelector('video');
      if (incomingVideo && incomingVideo.paused && !document.hidden) {
        incomingVideo.play().catch(() => {});
      }
    }

    for (let i = 0; i < totalSlides; i++) {
      if (i !== baseIndex && i !== incomingIndex) {
        const other = slides[i];
        other.style.visibility = 'hidden';
        other.style.zIndex = '0';
        other.style.clipPath = 'none';
        other.classList.remove('is-active');

        const otherVideo = other.querySelector('video');
        if (otherVideo && !otherVideo.paused) {
          otherVideo.pause();
        }
      }
    }
  }

  function updateLoop() {
    const diff = targetScroll - currentScroll;
    if (Math.abs(diff) > 0.0003) {
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

  window.addEventListener('wheel', (e) => {
    e.preventDefault();
    const scrollDistance = Math.max(500, window.innerHeight * 0.85);
    targetScroll += e.deltaY / scrollDistance;
    startAnimation();
  }, { passive: false });

  // Touch scrubbing (uses resolved angle to choose horizontal vs vertical drag)
  let lastTouchY = 0;
  let lastTouchX = 0;
  let isTouching = false;
  const resolvedBaseDeg = resolveAngleDegrees(globalWipeAngle);
  const isHorizontalWipe = (resolvedBaseDeg >= 45 && resolvedBaseDeg <= 135) || (resolvedBaseDeg >= 225 && resolvedBaseDeg <= 315);

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
    const deltaY = lastTouchY - currentY;
    const deltaX = lastTouchX - currentX;
    lastTouchY = currentY;
    lastTouchX = currentX;

    const primaryDelta = isHorizontalWipe && Math.abs(deltaX) > Math.abs(deltaY) ? deltaX : deltaY;
    const scrollDistance = Math.max(380, window.innerHeight * 0.8);
    targetScroll += primaryDelta / scrollDistance;
    startAnimation();
  }, { passive: true });

  window.addEventListener('touchend', () => { isTouching = false; }, { passive: true });

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

  document.addEventListener('visibilitychange', () => {
    slides.forEach((s) => {
      const v = s.querySelector('video');
      if (!v) return;
      if (document.hidden) v.pause();
      else if (s.classList.contains('is-active')) v.play().catch(() => {});
    });
  });

  renderWipe(0);
  startLazyProgressiveLoading();
}
