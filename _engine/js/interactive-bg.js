/**
 * Interactive Mouse Pointer Canvas Background
 * Synchronized with #0e1733 background and #f98603 accent palette.
 */
export function initInteractiveBackground(canvasId = 'bg-canvas') {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width = window.innerWidth;
  let height = window.innerHeight;
  let dpr = Math.min(window.devicePixelRatio || 1, 2);

  // Mouse State
  const mouse = {
    x: width / 2,
    y: height / 2,
    targetX: width / 2,
    targetY: height / 2,
    radius: 220,
    active: true
  };

  function resize() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  const count = window.innerWidth < 768 ? 45 : 85;
  const particles = [];
  
  // Custom Color Palette: #f98603 and off-whites
  const palette = [
    { r: 249, g: 134, b: 3 },   // Vibrant Orange (#f98603)
    { r: 251, g: 175, b: 75 },  // Warm Amber
    { r: 248, g: 250, b: 252 }, // Off-white
    { r: 226, g: 232, b: 240 }  // Muted Off-white
  ];

  class Particle {
    constructor() {
      this.reset(true);
    }

    reset(randomPosition = false) {
      this.x = randomPosition ? Math.random() * width : (Math.random() > 0.5 ? 0 : width);
      this.y = randomPosition ? Math.random() * height : Math.random() * height;
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

      // Mouse Proximity Gravity & Swirl
      if (mouse.active) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < mouse.radius && dist > 1) {
          const force = (1 - dist / mouse.radius);
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
      if (this.x > width + 10) this.x = -10;
      if (this.y < -10) this.y = height + 10;
      if (this.y > height + 10) this.y = -10;
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
    particles.length = 0;
    for (let i = 0; i < count; i++) {
      particles.push(new Particle());
    }
  }

  function drawConnections() {
    const maxDist = 125;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i];
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDist) {
          const alpha = (1 - dist / maxDist) * 0.25;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(249, 134, 3, ${alpha})`;
          ctx.lineWidth = 0.85;
          ctx.stroke();
        }
      }

      // Connect to cursor
      if (mouse.active) {
        const dx = particles[i].x - mouse.x;
        const dy = particles[i].y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          const alpha = (1 - dist / mouse.radius) * 0.45;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
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

  let reqId;
  function render() {
    ctx.clearRect(0, 0, width, height);
    drawCursorGlow();
    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw();
    }
    drawConnections();
    reqId = requestAnimationFrame(render);
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

  window.addEventListener('pointermove', (e) => handlePointer(e.clientX, e.clientY));
  window.addEventListener('mousemove', (e) => handlePointer(e.clientX, e.clientY));
  window.addEventListener('touchmove', (e) => {
    if (e.touches && e.touches[0]) handlePointer(e.touches[0].clientX, e.touches[0].clientY);
  }, { passive: true });
  window.addEventListener('mouseleave', () => { mouse.active = false; });
  window.addEventListener('touchend', () => { mouse.active = false; });

  window.addEventListener('resize', () => {
    resize();
    initParticles();
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) cancelAnimationFrame(reqId);
    else render();
  });

  resize();
  initParticles();
  render();
}
