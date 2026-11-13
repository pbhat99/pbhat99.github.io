/**
 * Multi-Pass VFX Layer Switcher Component
 * Allows clients & directors to scrub through plate, 3d, lighting, and comp passes
 */
export function initMultiPass(container) {
  if (!container) return;
  const tabs = container.querySelectorAll('.multipass-tab-btn');
  const img = container.querySelector('.multipass-viewport img');

  tabs.forEach(tab => {
    tab.addEventListener('click', () => {
      tabs.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');

      const passSrc = tab.getAttribute('data-pass-src');
      if (passSrc && img) {
        img.style.opacity = '0';
        setTimeout(() => {
          img.src = passSrc;
          img.style.opacity = '1';
        }, 150);
      }
    });
  });
}

export function initAllMultiPass() {
  document.querySelectorAll('.multipass-container').forEach(el => initMultiPass(el));
}

