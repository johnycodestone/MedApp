/*
  Card Component JS
  - Enhances cards with reveal-on-scroll
  - Leverages IntersectionObserver for performance
  - No global side effects; opt-in via .c-card
*/

(function () {
  function reveal(el) {
    el.style.opacity = '1';
    el.style.transform = 'translateY(0)';
  }

  function prepare(el) {
    el.style.opacity = '0';
    el.style.transform = 'translateY(6px)';
    el.style.transition = 'opacity 240ms ease, transform 240ms ease';
  }

  function init() {
    const cards = document.querySelectorAll('.c-card');
    if (!('IntersectionObserver' in window)) {
      // Graceful fallback: reveal immediately
      cards.forEach(reveal);
      return;
    }

    cards.forEach(prepare);

    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          reveal(entry.target);
          io.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -5% 0px', threshold: 0.1 });

    cards.forEach((card) => io.observe(card));
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
