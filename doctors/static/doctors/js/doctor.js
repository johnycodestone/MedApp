// doctors/static/doctors/js/doctor.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("Doctor directory loaded");

  const bookingForm = document.getElementById("booking-form");
  const resultBox = document.getElementById("booking-result");

  if (bookingForm) {
    bookingForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const submitBtn = bookingForm.querySelector("button[type='submit']");
      const formData = new FormData(bookingForm);
      const slot = formData.get("scheduled_time");

      if (!slot) {
        resultBox.innerHTML = `
          <div class="alert alert-danger" role="alert">
            ❌ Please select a time slot before booking.
          </div>`;
        return;
      }

      // Disable button + show loading state
      submitBtn.disabled = true;
      resultBox.innerHTML = `
        <div class="alert alert-info" role="alert">
          ⏳ Booking your appointment...
        </div>`;

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
          <div class="alert alert-success" role="alert">
            ✅ Appointment booked for ${new Date(data.scheduled_time).toLocaleString()}.
          </div>
          <a href="/appointments/" class="btn btn-outline-primary btn-sm mt-2">
            Go to My Appointments
          </a>`;
      } catch (err) {
        console.error("Booking error:", err);
        resultBox.innerHTML = `
          <div class="alert alert-danger" role="alert">
            ❌ Could not book appointment. Please try again.
          </div>`;
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

  // Doctor filter form logging (optional enhancement)
  const filterForm = document.getElementById("doctor-filter-form");
  if (filterForm) {
    filterForm.addEventListener("submit", function () {
      const filters = Object.fromEntries(new FormData(filterForm));
      console.log("Submitting doctor filters:", filters);
      // You could enhance UX here (e.g., show spinner, AJAX filtering)
    });
  }
});
