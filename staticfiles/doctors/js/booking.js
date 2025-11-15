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

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("booking-form");
  form?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(form);
    const resultBox = document.getElementById("booking-result");

    try {
      const response = await fetch("/appointments/api/", {
        method: "POST",
        headers: {
          "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
        },
        body: formData,
      });

      if (!response.ok) throw new Error("Booking failed");

      const data = await response.json();
      resultBox.innerHTML = `
        <p class="success">Appointment booked for ${new Date(data.scheduled_time).toLocaleString()}.</p>
        <a href="/appointments/">Go to My Appointments</a>
      `;
    } catch (err) {
      resultBox.innerHTML = `<p class="error">Could not book appointment. Please try again.</p>`;
    }
  });
});
