/*
  File: static/js/dashboard.js

  Purpose:
    - Lightweight behaviors for the hospitals dashboard.
    - Non-invasive: progressive enhancement only (works fine without JS).
    - Adds focus management, panel collapse (optional), and a simple analytics hook for quick actions.

  Notes:
    - Avoids framework dependencies. Plain, readable JavaScript.
    - All selectors are scoped to dashboard contexts to prevent cross-app interference.
*/

(function () {
  'use strict';

  /**
   * Utility: safe query selector
   */
  function $(selector, root = document) {
    return root.querySelector(selector);
  }

  function $all(selector, root = document) {
    return Array.from(root.querySelectorAll(selector));
  }

  /**
   * Panel collapse behavior (optional):
   * - If a panel header has a data-collapsible attribute, clicking its title toggles the body.
   * - Gracefully degrades: panels remain open if JS is disabled.
   */
  function initPanelCollapse() {
    const panels = $all('.panel');

    panels.forEach((panel) => {
      const header = $('.panel-header', panel);
      const body = $('.panel-body', panel);
      if (!header || !body) return;

      const isCollapsible = header.getAttribute('data-collapsible') === 'true';
      if (!isCollapsible) return;

      // Make the title focusable for accessibility
      const title = $('.panel-title', header);
      if (title) {
        title.setAttribute('tabindex', '0');
        title.setAttribute('role', 'button');
        title.setAttribute('aria-expanded', 'true');
      }

      function toggle() {
        const isHidden = body.hasAttribute('hidden');
        if (isHidden) {
          body.removeAttribute('hidden');
          if (title) title.setAttribute('aria-expanded', 'true');
        } else {
          body.setAttribute('hidden', '');
          if (title) title.setAttribute('aria-expanded', 'false');
        }
      }

      header.addEventListener('click', (e) => {
        // Allow clicking anywhere in header to toggle
        if (e.target.closest('.panel-title')) {
          toggle();
        }
      });

      header.addEventListener('keydown', (e) => {
        if ((e.key === 'Enter' || e.key === ' ') && e.target.closest('.panel-title')) {
          e.preventDefault();
          toggle();
        }
      });
    });
  }

  /**
   * Quick actions analytics hook:
   * - Emits a CustomEvent 'quick-action:click' with details (label, href) when a quick action is clicked.
   * - Apps can listen for this event and integrate their own analytics without editing root/app templates.
   */
  function initQuickActionsAnalytics() {
    const qaRoot = document.querySelector('.hosp-quick-actions') || document.querySelector('.qa-panel');
    if (!qaRoot) return;

    qaRoot.addEventListener('click', (e) => {
      const btn = e.target.closest('.qa-button, .btn');
      if (!btn) return;

      const detail = {
        label: btn.querySelector('.qa-label')?.textContent?.trim() || btn.textContent.trim(),
        href: btn.getAttribute('href') || null,
        timestamp: Date.now()
      };

      const event = new CustomEvent('quick-action:click', { detail });
      document.dispatchEvent(event);
    });
  }

  /**
   * Focus management for accessibility:
   * - If the page has a main title in the dashboard, move focus there on load.
   */
  function initFocusManagement() {
    const main = document.getElementById('main-content');
    if (!main) return;
    const heading = main.querySelector('h1, h2.panel-title') || document.title;
    if (heading && typeof heading.focus === 'function') {
      heading.setAttribute('tabindex', '-1');
      heading.focus();
    }
  }

  /**
   * Initialize all features on DOM ready
   */
  document.addEventListener('DOMContentLoaded', () => {
    initPanelCollapse();
    initQuickActionsAnalytics();
    initFocusManagement();

    // Example: external listeners can hook into quick-action clicks
    document.addEventListener('quick-action:click', (e) => {
      // Placeholder for analytics integration (e.g., send to backend)
      // console.log('Quick action clicked:', e.detail);
    });
  });
})();
