document.getElementById("doctor-filter-form")?.addEventListener("submit", function (e) {
  e.preventDefault();
  const name = document.getElementById("search-name").value;
  const specialization = document.getElementById("specialization").value;

  console.log("Filtering doctors:", { name, specialization });
  // TODO: Add AJAX filter logic here if needed
});

function viewDoctor(id) {
  window.location.href = `/doctor/${id}/`;
}
