document.addEventListener("DOMContentLoaded", () => {
  console.log("History page loaded");

  // Example: collapsible sections
  const headers = document.querySelectorAll(".history-container h3");
  headers.forEach(header => {
    header.addEventListener("click", () => {
      const nextUl = header.nextElementSibling;
      if (nextUl && nextUl.tagName === "UL") {
        nextUl.classList.toggle("hidden");
      }
    });
  });
});
