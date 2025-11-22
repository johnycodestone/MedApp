/*
  Interaction Utilities (JS)
  - Attach ripple effect to elements with .js-card-link or .u-ripple
  - Ensure keyboard accessibility for Enter/Space on links or buttons
  Scope:
    Non-intrusive and safe: only binds to elements that opt-in via classes.
*/

(function () {
  // Ripple effect on click/tap
  function attachRipple(el) {
    el.addEventListener('click', function (e) {
      // Ignore modified clicks (Ctrl, Meta for new tabs)
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;

      const rect = el.getBoundingClientRect();
      const ripple = document.createElement('span');

      // Position ripple
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const size = Math.max(rect.width, rect.height);

      ripple.style.position = 'absolute';
      ripple.style.left = `${x - size / 2}px`;
      ripple.style.top = `${y - size / 2}px`;
      ripple.style.width = `${size}px`;
      ripple.style.height = `${size}px`;
      ripple.style.borderRadius = '50%';
      ripple.style.background = 'rgba(59,130,246,0.25)';
      ripple.style.transform = 'scale(0)';
      ripple.style.pointerEvents = 'none';
      ripple.style.animation = 'ripple 600ms ease forwards';

      el.appendChild(ripple);
      setTimeout(() => ripple.remove(), 650);
    }, { passive: true });
  }

  // Keyboard accessibility: trigger click on Enter/Space for focusable elements
  function attachKeyboardActivation(el) {
    el.addEventListener('keydown', function (e) {
      const isEnter = e.key === 'Enter';
      const isSpace = e.key === ' ';
      if (isEnter || isSpace) {
        el.click();
        e.preventDefault();
      }
    });
  }

  // Initialize on DOM ready
  function init() {
    const clickable = document.querySelectorAll('.js-card-link, .u-ripple');
    clickable.forEach(function (el) {
      attachRipple(el);
      attachKeyboardActivation(el);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init, { once: true });
  } else {
    init();
  }
})();
