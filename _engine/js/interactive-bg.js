/**
 * Interactive Mouse Pointer Canvas Background
 * Synchronized with #0e1733 background and #f98603 accent palette.
 */
export function initInteractiveBackground(canvasId = 'bg-canvas') {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  if (!ctx) return;

  let width = window.innerWidth;
  let height = window.innerHeight;
  let dpr = Math.min(window.devicePixelRatio || 1, 2);
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const mouse = {
    x: width / 2,
    y: height / 2,
    targetX: width / 2,
    targetY: height / 2,
    radius: 220,
    radiusSq: 220 * 220,
    active: true
  };

  const palette = [
    { r: 249, g: 134, b: 3 },   // Vibrant Orange (#f98603)
    { r: 251, g: 175, b: 75 },  // Warm Amber
    { r: 248, g: 250, b: 252 }, // Off-white
    { r: 226, g: 232, b: 240 }  // Muted Off-white
  ];

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  const particles = [];

  class Particle {
    constructor() {
      this.x = Math.random() * width;
      this.y = Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.75;
      this.vy = (Math.random() - 0.5) * 0.75;
      this.baseRadius = Math.random() * 2 + 1.2;
      this.radius = this.baseRadius;
      this.baseAlpha = Math.random() * 0.45 + 0.35;
      this.alpha = this.baseAlpha;
      this.color = palette[Math.floor(Math.random() * palette.length)];
      this.pulseSpeed = Math.random() * 0.02 + 0.01;
      this.pulseAngle = Math.random() * Math.PI * 2;
    }

    update() {
      this.x += this.vx;
      this.y += this.vy;
      this.pulseAngle += this.pulseSpeed;
      this.alpha = this.baseAlpha + Math.sin(this.pulseAngle) * 0.15;

      if (mouse.active) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const distSq = dx * dx + dy * dy;

        if (distSq < mouse.radiusSq && distSq > 1) {
          const dist = Math.sqrt(distSq);
          const force = 1 - dist / mouse.radius;
          this.vx += (dx / dist) * force * 0.22;
          this.vy += (dy / dist) * force * 0.22;
          this.alpha = Math.min(1, this.alpha + force * 0.5);
          this.radius = this.baseRadius + force * 1.5;
        } else {
          this.radius = this.baseRadius;
        }
      }

      this.vx *= 0.98;
      this.vy *= 0.98;

      if (this.x < -10) this.x = width + 10;
      else if (this.x > width + 10) this.x = -10;
      if (this.y < -10) this.y = height + 10;
      else if (this.y > height + 10) this.y = -10;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, ${this.alpha})`;
      ctx.shadowBlur = 12;
      ctx.shadowColor = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0.8)`;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  function initParticles() {
    const count = width < 768 ? 45 : 85;
    particles.length = 0;
    for (let i = 0; i < count; i++) {
      particles.push(new Particle());
    }
  }

  function drawConnections() {
    const maxDist = 125;
    const maxDistSq = maxDist * maxDist;

    for (let i = 0; i < particles.length; i++) {
      const p1 = particles[i];
      for (let j = i + 1; j < particles.length; j++) {
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const distSq = dx * dx + dy * dy;

        if (distSq < maxDistSq) {
          const dist = Math.sqrt(distSq);
          const alpha = (1 - dist / maxDist) * 0.25;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(249, 134, 3, ${alpha})`;
          ctx.lineWidth = 0.85;
          ctx.stroke();
        }
      }

      if (mouse.active) {
        const dx = p1.x - mouse.x;
        const dy = p1.y - mouse.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < mouse.radiusSq) {
          const dist = Math.sqrt(distSq);
          const alpha = (1 - dist / mouse.radius) * 0.45;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(251, 175, 75, ${alpha})`;
          ctx.lineWidth = 1.1;
          ctx.stroke();
        }
      }
    }
  }

  function drawCursorGlow() {
    if (!mouse.active) return;
    mouse.x += (mouse.targetX - mouse.x) * 0.2;
    mouse.y += (mouse.targetY - mouse.y) * 0.2;

    const glow = ctx.createRadialGradient(
      mouse.x, mouse.y, 0,
      mouse.x, mouse.y, mouse.radius
    );
    glow.addColorStop(0, 'rgba(249, 134, 3, 0.25)');
    glow.addColorStop(0.35, 'rgba(249, 134, 3, 0.08)');
    glow.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(mouse.x, mouse.y, mouse.radius, 0, Math.PI * 2);
    ctx.fill();
  }

  let reqId = null;

  function drawFrame() {
    ctx.clearRect(0, 0, width, height);
    drawCursorGlow();
    for (let i = 0; i < particles.length; i++) {
      if (!reducedMotion) particles[i].update();
      particles[i].draw();
    }
    drawConnections();
  }

  function render() {
    drawFrame();
    if (!reducedMotion) {
      reqId = requestAnimationFrame(render);
    }
  }

  function handlePointer(x, y) {
    mouse.targetX = x;
    mouse.targetY = y;
    if (!mouse.active) {
      mouse.x = x;
      mouse.y = y;
      mouse.active = true;
    }
  }

  if (!reducedMotion) {
    window.addEventListener('pointermove', (e) => handlePointer(e.clientX, e.clientY), { passive: true });
    window.addEventListener('mousemove', (e) => handlePointer(e.clientX, e.clientY), { passive: true });
    window.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches[0]) handlePointer(e.touches[0].clientX, e.touches[0].clientY);
    }, { passive: true });
    window.addEventListener('mouseleave', () => { mouse.active = false; });
    window.addEventListener('touchend', () => { mouse.active = false; });

    document.addEventListener('visibilitychange', () => {
      if (document.hidden) {
        if (reqId) cancelAnimationFrame(reqId);
        reqId = null;
      } else if (!reqId) {
        render();
      }
    });
  } else {
    mouse.active = false;
  }

  let resizeTimer = null;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      resize();
      initParticles();
      if (reducedMotion) drawFrame();
    }, 100);
  }, { passive: true });

  resize();
  initParticles();
  render();
}
