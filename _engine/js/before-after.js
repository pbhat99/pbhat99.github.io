/**
 * Ultra-fast Native Before & After Wipe Slider
 * Zero third-party dependencies, touch-friendly, keyboard accessible
 */
export function initBeforeAfter(container) {
  if (!container) return;

  const afterLayer = container.querySelector('.ba-after-layer');
  const handle = container.querySelector('.ba-handle');
  if (!afterLayer || !handle) return;

  let isDragging = false;

  function updatePosition(xPos) {
    const rect = container.getBoundingClientRect();
    let percentage = ((xPos - rect.left) / rect.width) * 100;
    
    // Clamp between 0% and 100%
    percentage = Math.max(0, Math.min(100, percentage));
    
    afterLayer.style.width = `${percentage}%`;
    handle.style.left = `${percentage}%`;
  }

  // Pointer & Touch events
  function onPointerDown(e) {
    isDragging = true;
    container.classList.add('is-dragging');
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    updatePosition(clientX);
  }

  function onPointerMove(e) {
    if (!isDragging) return;
    const clientX = e.touches ? e.touches[0].clientX : e.clientX;
    updatePosition(clientX);
  }

  function onPointerUp() {
    isDragging = false;
    container.classList.remove('is-dragging');
  }

  // Event Listeners
  handle.addEventListener('mousedown', onPointerDown);
  container.addEventListener('mousedown', onPointerDown);
  window.addEventListener('mousemove', onPointerMove);
  window.addEventListener('mouseup', onPointerUp);

  handle.addEventListener('touchstart', onPointerDown, { passive: true });
  container.addEventListener('touchstart', onPointerDown, { passive: true });
  window.addEventListener('touchmove', onPointerMove, { passive: true });
  window.addEventListener('touchend', onPointerUp);

  // Keyboard accessibility
  handle.setAttribute('tabindex', '0');
  handle.setAttribute('role', 'slider');
  handle.setAttribute('aria-label', 'Before and After Image Comparison');
  handle.addEventListener('keydown', (e) => {
    const currentPercent = parseFloat(handle.style.left) || 50;
    if (e.key === 'ArrowLeft') {
      updatePositionWithPercent(Math.max(0, currentPercent - 5));
    } else if (e.key === 'ArrowRight') {
      updatePositionWithPercent(Math.min(100, currentPercent + 5));
    }
  });

  function updatePositionWithPercent(percentage) {
    afterLayer.style.width = `${percentage}%`;
    handle.style.left = `${percentage}%`;
  }

  // Make sure after image width matches container width
  function syncImageWidth() {
    const afterImg = afterLayer.querySelector('img');
    if (afterImg) {
      afterImg.style.width = `${container.offsetWidth}px`;
    }
  }

  window.addEventListener('resize', syncImageWidth);
  syncImageWidth();
}

export function initAllBeforeAfter() {
  document.querySelectorAll('.before-after-container').forEach(el => initBeforeAfter(el));
}

