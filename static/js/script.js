// Mobile Menu Toggle
const menuToggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");

menuToggle.addEventListener("click", () => {
  navLinks.classList.toggle("show");
});

// Transparent Navbar on Scroll
const navbar = document.getElementById("navbar");

window.addEventListener("scroll", () => {
  if (window.scrollY > 10) {
    navbar.classList.add("scrolled");
  } else {
    navbar.classList.remove("scrolled");
  }
});

const toggleBtn = document.getElementById("theme-toggle");
const body = document.body;

// Load saved preference
const storedTheme = localStorage.getItem("theme");
if (storedTheme === "dark") {
  body.classList.add("dark-mode");
  toggleBtn.textContent = "☀️";
}

// Toggle dark/light mode
toggleBtn.addEventListener("click", () => {
  body.classList.toggle("dark-mode");
  const isDark = body.classList.contains("dark-mode");
  toggleBtn.textContent = isDark ? "☀️" : "🌙";
  localStorage.setItem("theme", isDark ? "dark" : "light");
});

const contactForm = document.getElementById("contact-form");
const responseMsg = document.getElementById("form-response");

contactForm.addEventListener("submit", (e) => {
  e.preventDefault();

  // Basic feedback (you can replace this with real backend/API later)
  responseMsg.textContent = "Thank you! Your message has been sent.";

  // Clear form
  contactForm.reset();

  // Hide message after 5 seconds
  setTimeout(() => {
    responseMsg.textContent = "";
  }, 5000);
});

contactForm.addEventListener("submit", (e) => {
  e.preventDefault();
  responseMsg.textContent = "Thank you! Your message has been sent.";
  contactForm.reset();
  setTimeout(() => {
    responseMsg.textContent = "";
  }, 5000);
});
