function openModal() {
  document.getElementById("appointmentModal").style.display = "block";
}

function closeModal() {
  document.getElementById("appointmentModal").style.display = "none";
}

document.getElementById("appointmentForm")?.addEventListener("submit", function (e) {
  e.preventDefault();
  const date = document.getElementById("date").value;
  const time = document.getElementById("time").value;

  if (date && time) {
    alert(`Appointment booked on ${date} at ${time}`);
    closeModal();
  } else {
    alert("Please select both date and time.");
  }
});
