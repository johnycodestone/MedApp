/* ============================================================================
   filters.js
   Purpose: Initialize and manage filter chips for UI-based filtering.
   Usage: Designed for reusable integration across MedApp modules (e.g., departments, doctors).
   ============================================================================ */

/**
 * Initializes filter chips within a given container and binds click events.
 * @param {string} containerSelector - CSS selector for the filter chip container.
 * @param {function} onFilterSelect - Optional callback to handle filter selection logic.
 */
export function initFilterChips(containerSelector, onFilterSelect) {
  // Locate the container element using the provided selector
  const container = document.querySelector(containerSelector);
  if (!container) {
    console.warn(`Filter container not found: ${containerSelector}`);
    return;
  }

  // Select all chip elements within the container
  const chips = container.querySelectorAll(".chip");

  // Attach click event to each chip
  chips.forEach(chip => {
    chip.addEventListener("click", (e) => {
      e.preventDefault(); // Prevent default navigation if using AJAX filtering

      // Extract filter value from data attribute or href query param
      const filterValue =
        chip.dataset.filter || chip.getAttribute("href").split("=")[1];

      // Optional: visually mark chip as active (can be styled via CSS)
      chips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");

      // Trigger callback if provided
      if (typeof onFilterSelect === "function") {
        onFilterSelect(filterValue);
      } else {
        // Default behavior: navigate using query param
        window.location.href = `?filter=${filterValue}`;
      }
    });
  });
}

/* ============================================================================
   Notes for developers:
   - To use this module, import it in your app-level JS and call initFilterChips.
   - You can pass a custom callback to handle dynamic filtering (e.g., AJAX reload).
   - Ensure your HTML uses .chip elements with either data-filter or href="?filter=value".
   - Styling for active chips should be handled in filters.css.
   ============================================================================ */
