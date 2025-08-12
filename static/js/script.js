const menuToggle = document.getElementById("menu-toggle");
const navLinks = document.getElementById("nav-links");
const navbar = document.getElementById("navbar");
const toggleBtn = document.getElementById("theme-toggle");
const body = document.body;

menuToggle.addEventListener("click", () => {
  navLinks.classList.toggle("show");
});

window.addEventListener("scroll", () => {
  if (window.scrollY > 10) {
    navbar.classList.add("scrolled");
  } else {
    navbar.classList.remove("scrolled");
  }
});

const storedTheme = localStorage.getItem("theme");
if (storedTheme === "dark") {
  body.classList.add("dark-mode");
  toggleBtn.textContent = "☀️";
}

toggleBtn.addEventListener("click", () => {
  body.classList.toggle("dark-mode");
  const isDark = body.classList.contains("dark-mode");
  toggleBtn.textContent = isDark ? "☀️" : "🌙";
  localStorage.setItem("theme", isDark ? "dark" : "light");
});
