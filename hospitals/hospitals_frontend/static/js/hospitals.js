/*
  hospitals.js
  Purpose:
    - App-level interactions for the Hospitals pages (list and detail).
    - Search debounce, filter hooks, simple analytics tags.
  Safety:
    - Scoped to hospitals pages; does not affect other apps.
    - Defensive checks for selectors.
*/

(function () {
  /* Utility: Debounce function to limit frequent calls */
  function debounce(fn, delay) {
    let timer = null;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(this, args); }, delay);
    };
  }

  /* Search input debounce: auto-submits form after user stops typing */
  function initSearchDebounce() {
    const searchInput = document.querySelector('.hosp-search-input');
    if (!searchInput) return;

    const form = searchInput.closest('form');
    if (!form) return;

    searchInput.addEventListener('input', debounce(function () {
      form.submit();
    }, 400));
  }

  /* Example: add data attributes for analytics tracking */
  function tagCardImpressions() {
    const grid = document.querySelector('.hospital-grid');
    if (!grid) return;

    const cards = grid.querySelectorAll('.c-card');
    cards.forEach(function (card, index) {
      card.setAttribute('data-impression-index', String(index));
    });
  }

  /* Detail page: optional hook to highlight verified badge on load */
  function initDetailBadgeHighlight() {
    const badge = document.querySelector('.c-badge--success');
    if (!badge) return;

    // Subtle highlight effect on load
    badge.style.boxShadow = '0 0 0 0 rgba(16,185,129,0.5)';
    setTimeout(function () {
      badge.style.transition = 'box-shadow 600ms ease';
      badge.style.boxShadow = '0 0 0 8px rgba(16,185,129,0.2)';
      setTimeout(function () {
        badge.style.boxShadow = 'none';
      }, 650);
    }, 200);
  }

  /* Initialize app-level behaviors */
  function initHospitalsApp() {
    initSearchDebounce();
    tagCardImpressions();
    initDetailBadgeHighlight();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initHospitalsApp, { once: true });
  } else {
    initHospitalsApp();
  }
})();
