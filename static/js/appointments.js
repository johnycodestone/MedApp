// static/js/appointments.js
document.addEventListener("DOMContentLoaded", () => {
  console.log("Appointments module loaded");

  const appointmentForm = document.getElementById("appointment-form");
  const resultBox = document.getElementById("booking-result");

  if (appointmentForm) {
    appointmentForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const submitBtn = appointmentForm.querySelector("button[type='submit']");
      const formData = new FormData(appointmentForm);
      const slot = formData.get("scheduled_time");

      if (!slot) {
        if (resultBox) {
          resultBox.innerHTML = `
            <div class="alert alert-danger" role="alert">
              ❌ Please select a time slot before booking.
            </div>`;
        }
        return;
      }

      // Disable button + show loading state
      submitBtn.disabled = true;
      if (resultBox) {
        resultBox.innerHTML = `
          <div class="alert alert-info" role="alert">
            ⏳ Booking your appointment...
          </div>`;
      }

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

        if (resultBox) {
          resultBox.innerHTML = `
            <div class="alert alert-success" role="alert">
              ✅ Appointment booked for ${new Date(data.scheduled_time).toLocaleString()}.
            </div>
            <a href="/appointments/" class="btn btn-outline-primary btn-sm mt-2">
              Go to My Appointments
            </a>`;
        }
      } catch (err) {
        console.error("Booking error:", err);
        if (resultBox) {
          resultBox.innerHTML = `
            <div class="alert alert-danger" role="alert">
              ❌ Could not book appointment. Please try again.
            </div>`;
        }
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
});
