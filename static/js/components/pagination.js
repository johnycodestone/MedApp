/* ============================================================================
   pagination.js
   Purpose:
     - Enhance pagination links with better UX and optional AJAX hooks.
     - Prevent double-clicks, preserve non-page query params, scroll to top on navigation.
     - Provide a pluggable handler for AJAX pagination without changing templates.

   How it works:
     - Finds .pagination containers and their links.
     - For normal navigation: ensures only one click is processed, sets aria-busy,
       and scrolls to top (progressive enhancement).
     - For AJAX mode: if window.MedAppPagination.loadPage is defined, it will
       intercept clicks and call that function with the target page number and
       current query parameters (excluding 'page').

   Integration:
     - Include this script globally via base.html or on pages that use pagination.
     - To enable AJAX:
         window.MedAppPagination = {
           loadPage: function (page, params) {
             // Implement your fetch → render → update logic here.
           }
         };
   ============================================================================ */

(function () {
  /**
   * Utility: Parse current location's query params into a Map
   * @returns {Map} key-value pairs of query parameters
   */
  function parseQueryParams() {
    const params = new URLSearchParams(window.location.search);
    const map = new Map();
    params.forEach((value, key) => map.set(key, value));
    return map;
  }

  /**
   * Utility: Build a query string preserving all params except 'page'
   * @param {number} page - target page number
   * @param {Map} paramsMap - existing query parameters
   * @returns {string} query string with updated page
   */
  function buildQueryStringWithPage(page, paramsMap) {
    const next = new URLSearchParams();
    paramsMap.forEach((value, key) => {
      if (key !== 'page') next.append(key, value);
    });
    next.set('page', String(page));
    return `?${next.toString()}`;
  }

  /**
   * Utility: Extract page number from a pagination link's href safely
   * @param {string} href - link href
   * @returns {number|null} page number or null if not found
   */
  function getPageFromHref(href) {
    try {
      const url = new URL(href, window.location.origin);
      const p = url.searchParams.get('page');
      return p ? parseInt(p, 10) : null;
    } catch {
      return null;
    }
  }

  /**
   * Utility: Smoothly scroll to top (progressive enhancement)
   */
  function scrollToTop() {
    try {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch {
      window.scrollTo(0, 0);
    }
  }

  // Optional global AJAX hook namespace
  window.MedAppPagination = window.MedAppPagination || {};

  // Initialize enhancement on DOM ready
  document.addEventListener('DOMContentLoaded', () => {
    const paginations = document.querySelectorAll('nav[aria-label="Page navigation"] .pagination');
    if (!paginations.length) return;

    const currentParams = parseQueryParams();
    let isNavigating = false; // prevent double activations

    paginations.forEach((ul) => {
      ul.setAttribute('aria-live', 'polite'); // accessibility: announce updates

      const links = ul.querySelectorAll('.page-link');

      links.forEach((link) => {
        link.addEventListener('click', (evt) => {
          const li = link.closest('.page-item');
          if (!li || li.classList.contains('disabled') || li.classList.contains('active')) {
            evt.preventDefault(); // ignore disabled/active clicks
            return;
          }

          const targetPage = getPageFromHref(link.href);
          if (!targetPage) return; // fallback to default navigation if parsing fails

          // AJAX mode: intercept and delegate to custom loader
          if (typeof window.MedAppPagination.loadPage === 'function') {
            evt.preventDefault();
            if (isNavigating) return;

            isNavigating = true;
            ul.setAttribute('aria-busy', 'true');

            const paramsObj = {};
            currentParams.forEach((value, key) => {
              if (key !== 'page') paramsObj[key] = value;
            });

            Promise.resolve()
              .then(() => window.MedAppPagination.loadPage(targetPage, paramsObj))
              .catch((err) => {
                console.error('MedAppPagination.loadPage error:', err);
                window.location.assign(buildQueryStringWithPage(targetPage, currentParams));
              })
              .finally(() => {
                isNavigating = false;
                ul.removeAttribute('aria-busy');
                scrollToTop();
              });

            return;
          }

          // Default navigation mode
          if (isNavigating) {
            evt.preventDefault();
            return;
          }
          isNavigating = true;

          ul.setAttribute('aria-busy', 'true');
          evt.preventDefault();

          const target = buildQueryStringWithPage(targetPage, currentParams);
          scrollToTop();
          window.location.assign(target);
        });
      });
    });
  });
})();
