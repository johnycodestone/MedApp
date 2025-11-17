document.addEventListener('DOMContentLoaded', () => {
  const cards = document.querySelectorAll('.dept-card');
  if (!('IntersectionObserver' in window)) {
    cards.forEach(c => c.classList.add('visible'));
    return;
  }

  const io = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const el = entry.target;
        const idx = Number(el.dataset.deptIndex || 0);
        setTimeout(() => el.classList.add('visible'), idx * 80);
        obs.unobserve(el);
      }
    });
  }, { threshold: 0.12 });

  cards.forEach(c => io.observe(c));
});
