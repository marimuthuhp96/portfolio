/* ============================================================
   Mari Muthu Portfolio — timeline.js
   Animated vertical timeline for experience/education page
   ============================================================ */

'use strict';

(function initTimeline() {
  /* Animate timeline items on scroll */
  const items = document.querySelectorAll('.timeline-item');
  if (!items.length) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry, i) => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const delay = parseInt(el.dataset.delay, 10) || 0;
        setTimeout(() => {
          el.style.opacity   = '1';
          el.style.transform = 'translateY(0)';
        }, delay);
        io.unobserve(el);
      }
    });
  }, { threshold: 0.2 });

  items.forEach((item, i) => {
    item.style.opacity   = '0';
    item.style.transform = 'translateY(30px)';
    item.style.transition = `opacity 0.6s ease ${i * 100}ms, transform 0.6s cubic-bezier(0.16,1,0.3,1) ${i * 100}ms`;
    io.observe(item);
  });
})();

/* ── Journey Progress Line Animation ─────────────────────── */
(function initTimelineLine() {
  const line = document.querySelector('.timeline-progress-line');
  if (!line) return;

  const io = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        line.style.height = line.dataset.height || '100%';
      }
    });
  }, { threshold: 0.1 });

  line.style.height     = '0';
  line.style.transition = 'height 1.5s cubic-bezier(0.16,1,0.3,1)';
  io.observe(line);
})();
