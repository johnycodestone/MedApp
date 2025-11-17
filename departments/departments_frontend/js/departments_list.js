/* ============================================================================
   departments_list.js
   Purpose:
     - App-level JavaScript for the Departments list page.
     - Integrates root-level components: filters.js, pagination.js, breadcrumbs.
     - Handles dynamic filtering, search, and pagination (AJAX-ready).

   Usage:
     - Imported in departments list page template.
     - Requires root-level scripts (filters.js, pagination.js) to be loaded first.
   ============================================================================ */

import { initFilterChips } from "/static/js/components/filters.js";

document.addEventListener("DOMContentLoaded", () => {
  // Initialize filter chips with callback for AJAX filtering
  initFilterChips(".filter-chips", (filterValue) => {
    // Example AJAX handler (replace with real API call)
    console.log("Filter selected:", filterValue);

    // TODO: Implement AJAX fetch → update department list
    // fetch(`/departments/?filter=${filterValue}`)
    //   .then(res => res.text())
    //   .then(html => {
    //     document.querySelector(".department-list").innerHTML = html;
    //   });
  });

  // Pagination enhancement is already handled globally by pagination.js
  // Breadcrumbs are static (rendered via template), so no JS needed here.

  // Optional: Search bar live update (AJAX-ready)
  const searchForm = document.querySelector(".filter-search");
  if (searchForm) {
    searchForm.addEventListener("submit", (e) => {
      e.preventDefault();
      const query = searchForm.querySelector("input[name='q']").value;
      console.log("Search query:", query);

      // TODO: Implement AJAX search → update department list
    });
  }
});
