document.addEventListener("DOMContentLoaded", () => {
  console.log("Doctor directory loaded");

  const bookingForm = document.getElementById("booking-form");
  if (bookingForm) {
    bookingForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(bookingForm);
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
          <p class="success">✅ Appointment booked for ${new Date(data.scheduled_time).toLocaleString()}.</p>
          <a href="/appointments/">Go to My Appointments</a>
        `;
      } catch (err) {
        resultBox.innerHTML = `<p class="error">❌ Could not book appointment. Please try again.</p>`;
      }
    });
  }

  // Existing filter logic
  document.getElementById("doctor-filter-form")?.addEventListener("submit", function (e) {
    e.preventDefault();
    const name = document.getElementById("search-name").value;
    const specialization = document.getElementById("specialization").value;
    console.log("Filtering doctors:", { name, specialization });
  });
});
