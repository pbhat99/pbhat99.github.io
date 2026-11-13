/**
 * Interactive Mouse Pointer Canvas Background
 * High-performance, 60fps particle mesh with cursor gravity, glow, and organic physics.
 * Designed for Prasannakumar T Bhat (pbhat99) portfolio.
 */
export function initInteractiveBackground(canvasId = 'bg-canvas') {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const ctx = canvas.getContext('2d');
  let width, height;
  let dpr = Math.min(window.devicePixelRatio || 1, 2);

  // Mouse / Pointer State
  const mouse = {
    x: -1000,
    y: -1000,
    targetX: -1000,
    targetY: -1000,
    radius: 180,
    isHovered: false
  };

  // Particle configuration
  const particles = [];
  const baseCount = window.innerWidth < 768 ? 45 : 85;
  const colors = [
    { r: 56, g: 189, b: 248 },   // Cyan
    { r: 129, g: 140, b: 248 },  // Indigo
    { r: 168, g: 85, b: 247 },   // Violet
    { r: 255, g: 255, b: 255 }    // Crisp White
  ];

  function resize() {
    width = canvas.parentElement ? canvas.parentElement.offsetWidth : window.innerWidth;
    height = canvas.parentElement ? canvas.parentElement.offsetHeight : window.innerHeight;
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    canvas.style.width = width + 'px';
    canvas.style.height = height + 'px';
    ctx.scale(dpr, dpr);
  }

  class Particle {
    constructor() {
      this.reset(true);
    }

    reset(initial = false) {
      this.x = initial ? Math.random() * width : (Math.random() > 0.5 ? 0 : width);
      this.y = initial ? Math.random() * height : Math.random() * height;
      this.vx = (Math.random() - 0.5) * 0.7;
      this.vy = (Math.random() - 0.5) * 0.7;
      this.radius = Math.random() * 2 + 1;
      this.baseAlpha = Math.random() * 0.5 + 0.2;
      this.color = colors[Math.floor(Math.random() * colors.length)];
      this.pulseSpeed = Math.random() * 0.02 + 0.01;
      this.pulseAngle = Math.random() * Math.PI * 2;
    }

    update() {
      // Natural floating drift
      this.x += this.vx;
      this.y += this.vy;

      // Pulse alpha
      this.pulseAngle += this.pulseSpeed;
      this.currentAlpha = this.baseAlpha + Math.sin(this.pulseAngle) * 0.15;

      // Mouse interactive physics (gravity & subtle orbit)
      if (mouse.x > 0 && mouse.y > 0) {
        const dx = mouse.x - this.x;
        const dy = mouse.y - this.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < mouse.radius) {
          const force = (1 - dist / mouse.radius);
          // Gently attract towards cursor
          this.vx += (dx / dist) * force * 0.15;
          this.vy += (dy / dist) * force * 0.15;
          // Add extra brightness near mouse
          this.currentAlpha = Math.min(1, this.currentAlpha + force * 0.5);
        }
      }

      // Air friction / damping
      this.vx *= 0.985;
      this.vy *= 0.985;

      // Wrap boundaries
      if (this.x < -20) this.x = width + 20;
      if (this.x > width + 20) this.x = -20;
      if (this.y < -20) this.y = height + 20;
      if (this.y > height + 20) this.y = -20;
    }

    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, ${this.currentAlpha})`;
      ctx.shadowBlur = 10;
      ctx.shadowColor = `rgba(${this.color.r}, ${this.color.g}, ${this.color.b}, 0.6)`;
      ctx.fill();
      ctx.shadowBlur = 0;
    }
  }

  // Populate particles
  function initParticles() {
    particles.length = 0;
    for (let i = 0; i < baseCount; i++) {
      particles.push(new Particle());
    }
  }

  // Draw connecting constellation lines
  function drawConnections() {
    const maxDist = 130;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const p1 = particles[i];
        const p2 = particles[j];
        const dx = p1.x - p2.x;
        const dy = p1.y - p2.y;
        const dist = Math.sqrt(dx * dx + dy * dy);

        if (dist < maxDist) {
          const alpha = (1 - dist / maxDist) * 0.22;
          ctx.beginPath();
          ctx.moveTo(p1.x, p1.y);
          ctx.lineTo(p2.x, p2.y);
          ctx.strokeStyle = `rgba(56, 189, 248, ${alpha})`;
          ctx.lineWidth = 0.8;
          ctx.stroke();
        }
      }

      // Connect to mouse cursor
      if (mouse.x > 0 && mouse.y > 0) {
        const dx = particles[i].x - mouse.x;
        const dy = particles[i].y - mouse.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < mouse.radius) {
          const alpha = (1 - dist / mouse.radius) * 0.45;
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(mouse.x, mouse.y);
          ctx.strokeStyle = `rgba(168, 85, 247, ${alpha})`;
          ctx.lineWidth = 1;
          ctx.stroke();
        }
      }
    }
  }

  // Draw glowing cursor aura
  function drawMouseGlow() {
    if (mouse.x < 0 || mouse.y < 0) return;
    
    // Smooth mouse position interpolation
    mouse.x += (mouse.targetX - mouse.x) * 0.18;
    mouse.y += (mouse.targetY - mouse.y) * 0.18;

    const radial = ctx.createRadialGradient(
      mouse.x, mouse.y, 0,
      mouse.x, mouse.y, mouse.radius
    );
    radial.addColorStop(0, 'rgba(56, 189, 248, 0.18)');
    radial.addColorStop(0.4, 'rgba(129, 140, 248, 0.08)');
    radial.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.fillStyle = radial;
    ctx.beginPath();
    ctx.arc(mouse.x, mouse.y, mouse.radius, 0, Math.PI * 2);
    ctx.fill();
  }

  // Animation Loop
  let animId;
  function animate() {
    ctx.clearRect(0, 0, width, height);

    drawMouseGlow();

    for (let i = 0; i < particles.length; i++) {
      particles[i].update();
      particles[i].draw();
    }

    drawConnections();

    animId = requestAnimationFrame(animate);
  }

  // Pointer Listeners
  window.addEventListener('mousemove', (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.targetX = e.clientX - rect.left;
    mouse.targetY = e.clientY - rect.top;
    if (!mouse.isHovered) {
      mouse.x = mouse.targetX;
      mouse.y = mouse.targetY;
      mouse.isHovered = true;
    }
  });

  window.addEventListener('mouseleave', () => {
    mouse.targetX = -1000;
    mouse.targetY = -1000;
    mouse.isHovered = false;
  });

  // Touch listener for mobile devices
  window.addEventListener('touchmove', (e) => {
    if (e.touches && e.touches[0]) {
      const rect = canvas.getBoundingClientRect();
      mouse.targetX = e.touches[0].clientX - rect.left;
      mouse.targetY = e.touches[0].clientY - rect.top;
      mouse.x = mouse.targetX;
      mouse.y = mouse.targetY;
    }
  }, { passive: true });

  window.addEventListener('touchend', () => {
    mouse.targetX = -1000;
    mouse.targetY = -1000;
  });

  // Window Resize
  window.addEventListener('resize', () => {
    resize();
    initParticles();
  });

  // Pause when tab hidden to save battery
  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      cancelAnimationFrame(animId);
    } else {
      animate();
    }
  });

  resize();
  initParticles();
  animate();
}
