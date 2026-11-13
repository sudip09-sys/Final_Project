/* Portfolio-style presentation only. Attendance simulation remains in script.js. */
(() => {
  'use strict';
  const root = document.documentElement;
  const reducedMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const finePointer = matchMedia('(pointer: fine)');
  const themeButton = document.querySelector('#theme-toggle');
  const motionButton = document.querySelector('#motion-toggle');
  const canvas = document.querySelector('#embers');
  let painter = null;
  try { painter = canvas.getContext('2d'); } catch { /* Content works without canvas. */ }
  const read = key => { try { return localStorage.getItem(key); } catch { return null; } };
  const save = (key, value) => { try { localStorage.setItem(key, value); } catch { /* Optional preferences. */ } };
  let theme = read('attendly-project-theme') === 'light' ? 'light' : 'dark';
  let motionRequested = read('attendly-project-motion') !== 'off';
  let motionEnabled = false;
  let width = innerWidth, height = innerHeight, particles = [];
  let animation = 0, lastPaint = 0, scrollFrame = 0;
  let pointer = { x: 0, y: 0 };

  function applyTheme() {
    root.dataset.theme = theme;
    themeButton.textContent = theme === 'dark' ? 'Light mode' : 'Dark mode';
    themeButton.setAttribute('aria-pressed', String(theme === 'light'));
    document.querySelector('meta[name="theme-color"]').content = theme === 'dark' ? '#09090c' : '#f6f0ec';
    paintEmbers(0);
  }

  function resizeCanvas() {
    width = innerWidth;
    height = innerHeight;
    if (!painter) return;
    const ratio = Math.min(devicePixelRatio || 1, 1.5);
    canvas.width = Math.round(width * ratio);
    canvas.height = Math.round(height * ratio);
    painter.setTransform(ratio, 0, 0, ratio, 0, 0);
    particles = Array.from({ length: width < 700 ? 22 : 48 }, () => ({
      x: Math.random() * width, y: Math.random() * height,
      radius: .5 + Math.random() * 1.4, speed: .12 + Math.random() * .32,
      drift: Math.random() * .14 - .07, opacity: .15 + Math.random() * .6
    }));
    paintEmbers(0);
    updateProgress();
  }

  function paintEmbers(delta) {
    if (!painter) return;
    painter.clearRect(0, 0, width, height);
    particles.forEach((particle, index) => {
      if (delta) {
        particle.y -= particle.speed * delta;
        particle.x += particle.drift * delta;
        if (particle.y < -10) { particle.y = height + 10; particle.x = Math.random() * width; }
      }
      painter.globalAlpha = particle.opacity * (motionEnabled ? 1 : .5);
      painter.fillStyle = theme === 'dark' ? (index % 4 ? '#f33748' : '#ff9653') : '#bb1630';
      painter.shadowColor = '#ef263c';
      painter.shadowBlur = index % 4 ? 5 : 10;
      const x = particle.x + (motionEnabled ? pointer.x * (index % 3 + 1) : 0);
      const y = particle.y + (motionEnabled ? pointer.y * (index % 3 + 1) : 0);
      painter.beginPath();
      painter.ellipse(x, y, particle.radius, particle.radius * 1.6, .65, 0, Math.PI * 2);
      painter.fill();
    });
    painter.globalAlpha = 1;
    painter.shadowBlur = 0;
  }

  function animate(now) {
    animation = 0;
    if (!motionEnabled || document.hidden || !painter) return;
    if (now - lastPaint >= 32) {
      paintEmbers(Math.min((now - (lastPaint || now - 32)) / 16.67, 3));
      lastPaint = now;
    }
    animation = requestAnimationFrame(animate);
  }

  const art = document.querySelector('.hero-visual');
  function resetTilt() {
    art.style.removeProperty('--tilt-x');
    art.style.removeProperty('--tilt-y');
  }

  function applyMotion() {
    motionEnabled = motionRequested && !reducedMotion.matches;
    root.dataset.motion = motionEnabled ? 'on' : 'off';
    motionButton.disabled = reducedMotion.matches;
    motionButton.querySelector('span:last-child').textContent = reducedMotion.matches ? 'Reduced motion' : motionEnabled ? 'Pause motion' : 'Resume motion';
    motionButton.setAttribute('aria-pressed', String(!motionEnabled));
    cancelAnimationFrame(animation);
    animation = 0;
    lastPaint = 0;
    resetTilt();
    if (motionEnabled && !document.hidden && painter) animation = requestAnimationFrame(animate);
    else paintEmbers(0);
  }

  function updateProgress() {
    scrollFrame = 0;
    const distance = root.scrollHeight - innerHeight;
    const progress = distance > 0 ? Math.min(1, Math.max(0, scrollY / distance)) : 0;
    document.querySelector('.reading-progress').style.transform = `scaleX(${progress})`;
  }

  themeButton.hidden = false;
  motionButton.hidden = false;
  themeButton.addEventListener('click', () => {
    theme = theme === 'dark' ? 'light' : 'dark';
    applyTheme();
    save('attendly-project-theme', theme);
  });
  motionButton.addEventListener('click', () => {
    motionRequested = !motionRequested;
    save('attendly-project-motion', motionRequested ? 'on' : 'off');
    applyMotion();
  });
  reducedMotion.addEventListener('change', applyMotion);
  document.addEventListener('visibilitychange', applyMotion);
  window.addEventListener('resize', resizeCanvas, { passive: true });
  window.addEventListener('pointermove', event => {
    if (motionEnabled && finePointer.matches) pointer = { x: (event.clientX / width - .5) * 3, y: (event.clientY / height - .5) * 3 };
  }, { passive: true });
  art.addEventListener('pointermove', event => {
    if (!motionEnabled || !finePointer.matches) return;
    const bounds = art.getBoundingClientRect();
    art.style.setProperty('--tilt-x', `${(event.clientY - bounds.top - bounds.height / 2) / bounds.height * -4}deg`);
    art.style.setProperty('--tilt-y', `${(event.clientX - bounds.left - bounds.width / 2) / bounds.width * 5}deg`);
  }, { passive: true });
  art.addEventListener('pointerleave', resetTilt);
  window.addEventListener('scroll', () => {
    if (!scrollFrame) scrollFrame = requestAnimationFrame(updateProgress);
  }, { passive: true });

  if ('IntersectionObserver' in window) {
    const reveal = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      if (motionEnabled) entry.target.classList.add('reveal-enter');
      reveal.unobserve(entry.target);
    }), { threshold: .08 });
    document.querySelectorAll('.section-heading,.steps article,.principle-list article,.resource-card').forEach(target => reveal.observe(target));
    const nav = document.querySelector('.nav-wrap nav');
    const sectionObserver = new IntersectionObserver(entries => entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      nav.querySelectorAll('a').forEach(link => {
        if (link.hash === '#' + entry.target.id) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }), { rootMargin: '-10% 0px -40% 0px', threshold: 0 });
    document.querySelectorAll('#workflow,#explore,#resources').forEach(section => sectionObserver.observe(section));
  }

  resizeCanvas();
  applyTheme();
  applyMotion();
  updateProgress();
})();
