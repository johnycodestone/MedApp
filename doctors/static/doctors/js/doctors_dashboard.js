/*
  File: static/js/doctors_dashboard.js
  Purpose: small, unobtrusive behaviors for doctors dashboard.
  Patterns: Observer (listens for quick-action:click if needed).
*/

(function () {
  'use strict';

  document.addEventListener('DOMContentLoaded', function () {
    // Example: listen for quick-action clicks (frontend observer)
    document.addEventListener('quick-action:click', function (e) {
      // e.detail contains { label, href, timestamp }
      // Placeholder: you can send this to analytics endpoint
      // console.log('Quick action clicked:', e.detail);
    });
  });
})();
