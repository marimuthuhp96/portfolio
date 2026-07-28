/* ============================================================
   Mari Muthu Portfolio — animations.js
   Typing Effect, AOS Init, Counter Animation, Skill Rings
   ============================================================ */

'use strict';

/* ── AOS (Animate on Scroll) Init ─────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  if (typeof AOS !== 'undefined') {
    AOS.init({
      duration:   800,
      easing:     'cubic-bezier(0.16, 1, 0.3, 1)',
      once:       true,
      offset:     80,
      delay:      0,
    });
  }
});

/* ── Typing Animation ─────────────────────────────────────── */
(function initTyping() {
  const el = document.getElementById('hero-typed');
  if (!el) return;

  const roles = [
    'Data Analyst',
    'Business Intelligence Analyst',
    'Power BI Developer',
    'SQL Developer',
    'Junior Data Scientist',
  ];

  let roleIdx  = 0;
  let charIdx  = 0;
  let deleting = false;
  let timeout;

  const SPEEDS = { type: 70, delete: 40, pause: 2200, pauseAfterDelete: 400 };

  function tick() {
    const current = roles[roleIdx];

    if (!deleting) {
      el.textContent = current.slice(0, charIdx + 1);
      charIdx++;
      if (charIdx === current.length) {
        deleting = true;
        timeout = setTimeout(tick, SPEEDS.pause);
        return;
      }
    } else {
      el.textContent = current.slice(0, charIdx - 1);
      charIdx--;
      if (charIdx === 0) {
        deleting = false;
        roleIdx  = (roleIdx + 1) % roles.length;
        timeout  = setTimeout(tick, SPEEDS.pauseAfterDelete);
        return;
      }
    }

    timeout = setTimeout(tick, deleting ? SPEEDS.delete : SPEEDS.type);
  }

  tick();
})();

/* ── Animated Counter ─────────────────────────────────────── */
(function initCounters() {
  const counters = document.querySelectorAll('[data-count]');
  if (!counters.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const el     = entry.target;
      const target = parseInt(el.dataset.count, 10);
      const suffix = el.dataset.suffix || '';
      const dur    = parseInt(el.dataset.dur, 10) || 1800;
      const start  = performance.now();

      function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / dur, 1);
        /* Ease-out cubic */
        const eased = 1 - Math.pow(1 - progress, 3);
        el.textContent = Math.floor(eased * target) + suffix;
        if (progress < 1) requestAnimationFrame(update);
        else el.textContent = target + suffix;
      }

      requestAnimationFrame(update);
      io.unobserve(el);
    });
  }, { threshold: 0.5 });

  counters.forEach(c => io.observe(c));
})();

/* ── Progress Bars ────────────────────────────────────────── */
(function initProgressBars() {
  const bars = document.querySelectorAll('.progress-bar[data-width]');
  if (!bars.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const bar   = entry.target;
      const width = bar.dataset.width;
      setTimeout(() => { bar.style.width = width; }, 100);
      io.unobserve(bar);
    });
  }, { threshold: 0.3 });

  bars.forEach(b => io.observe(b));
})();

/* ── SVG Skill Rings ──────────────────────────────────────── */
(function initSkillRings() {
  const rings = document.querySelectorAll('.skill-ring-fill[data-pct]');
  if (!rings.length) return;

  const CIRC = 2 * Math.PI * 40; /* r=40 → circumference ≈ 251 */

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      const ring = entry.target;
      const pct  = parseFloat(ring.dataset.pct) / 100;
      const offset = CIRC * (1 - pct);
      ring.style.strokeDasharray  = CIRC;
      ring.style.strokeDashoffset = CIRC; /* start hidden */
      /* Trigger transition */
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          ring.style.strokeDashoffset = offset;
        });
      });
      io.unobserve(ring);
    });
  }, { threshold: 0.3 });

  rings.forEach(r => io.observe(r));
})();

/* ── Floating Badges Parallax ─────────────────────────────── */
(function initParallax() {
  const badges = document.querySelectorAll('.about-floating-badge');
  if (!badges.length) return;

  document.addEventListener('mousemove', (e) => {
    const cx = window.innerWidth  / 2;
    const cy = window.innerHeight / 2;
    const dx = (e.clientX - cx) / cx;
    const dy = (e.clientY - cy) / cy;

    badges.forEach((badge, i) => {
      const factor = (i + 1) * 6;
      badge.style.transform = `translate(${dx * factor}px, ${dy * factor}px)`;
    });
  });
})();

/* ── Section Counter Labels ───────────────────────────────── */
(function initSectionNumbers() {
  const sections = document.querySelectorAll('.numbered-section');
  sections.forEach((sec, i) => {
    const num = sec.querySelector('.section-number');
    if (num) num.textContent = String(i + 1).padStart(2, '0');
  });
})();

/* ── Glitch effect on hero name (subtle) ─────────────────── */
(function initGlitch() {
  const el = document.querySelector('.hero-name');
  if (!el) return;

  setInterval(() => {
    if (Math.random() > 0.97) {
      el.classList.add('glitch');
      setTimeout(() => el.classList.remove('glitch'), 150);
    }
  }, 2000);
})();
