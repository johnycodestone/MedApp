/* ============================================================================
   departments_detail.js
   Purpose:
     - App-level JavaScript for the Departments detail page.
     - Handles CTA bar interactions (e.g., book appointment, consult online).
     - Enhances doctor and hospital cards with dynamic behaviors.

   Usage:
     - Imported in departments detail page template.
     - Requires root-level scripts (cta_bar.js) to be loaded first.
   ============================================================================ */

document.addEventListener("DOMContentLoaded", () => {
  // CTA bar buttons (example: Book Appointment, Consult Online)
  const ctaButtons = document.querySelectorAll(".cta-bar .btn");
  ctaButtons.forEach((btn) => {
    btn.addEventListener("click", (e) => {
      e.preventDefault();
      const action = btn.dataset.action;
      console.log("CTA clicked:", action);

      // TODO: Implement actual CTA logic (modal, redirect, AJAX)
      // Example:
      // if (action === "book") {
      //   openBookingModal();
      // } else if (action === "consult") {
      //   redirectToConsultation();
      // }
    });
  });

  // Doctor card hover effect (optional enhancement)
  const doctorCards = document.querySelectorAll(".doctor-card");
  doctorCards.forEach((card) => {
    card.addEventListener("mouseenter", () => {
      card.classList.add("highlight");
    });
    card.addEventListener("mouseleave", () => {
      card.classList.remove("highlight");
    });
  });

  // Hospital card click → navigate to detail page
  const hospitalCards = document.querySelectorAll(".hospital-card");
  hospitalCards.forEach((card) => {
    card.addEventListener("click", () => {
      const link = card.querySelector("a.btn");
      if (link) window.location.href = link.href;
    });
  });
});
