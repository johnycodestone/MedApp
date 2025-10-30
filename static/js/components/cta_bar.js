/* cta_bar.js
   Purpose: Enhance CTA bar with optional analytics or dynamic behavior.
   Notes:
   - Currently logs clicks; can be extended to trigger modals or AJAX actions.
*/

document.addEventListener("DOMContentLoaded", () => {
  const ctaButtons = document.querySelectorAll(".cta-bar .btn");

  ctaButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      console.log(`CTA clicked: ${btn.textContent.trim()}`);
      // Extend: send analytics event, open modal, etc.
    });
  });
});
