/* filters.js
   Purpose: Enhance filter chips with toggle behavior and query parameter syncing.
   Notes:
   - This script assumes chips are anchor tags with ?filter=value.
   - Can be extended to support multi-select filters.
*/

document.addEventListener("DOMContentLoaded", () => {
  const chips = document.querySelectorAll(".filter-chips .chip");

  chips.forEach(chip => {
    chip.addEventListener("click", (e) => {
      // Optional: prevent default and handle via JS if you want AJAX filtering
      // e.preventDefault();
      // For now, let it navigate with query params.
    });
  });
});
