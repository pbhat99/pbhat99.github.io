/**
 * Interactive 360° Photosphere Panorama Viewer
 * Loads Pannellum WebGL viewer on demand or handles interactive spherical pan
 */
export function initPanoramaViewer(containerId, imageSrc) {
  const container = document.getElementById(containerId);
  if (!container) return;

  // Dynamically load Pannellum if not already loaded
  if (!window.pannellum) {
    const css = document.createElement('link');
    css.rel = 'stylesheet';
    css.href = 'https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.css';
    document.head.appendChild(css);

    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/pannellum@2.5.6/build/pannellum.js';
    script.onload = () => {
      createViewer(containerId, imageSrc);
    };
    document.body.appendChild(script);
  } else {
    createViewer(containerId, imageSrc);
  }
}

function createViewer(containerId, imageSrc) {
  if (window.pannellum) {
    window.pannellum.viewer(containerId, {
      type: 'equirectangular',
      panorama: imageSrc,
      autoLoad: true,
      autoRotate: -2,
      compass: false,
      showZoomCtrl: true,
      showFullscreenCtrl: true,
      mouseZoom: true
    });
  }
}
