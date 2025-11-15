document.addEventListener("DOMContentLoaded", () => {
  console.log("Profile page loaded");

  const avatarInput = document.getElementById("avatar");
  avatarInput?.addEventListener("change", () => {
    alert("Avatar selected. Preview feature can be added here.");
  });
});
