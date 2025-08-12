const contactForm = document.getElementById("contact-form");
const responseMsg = document.getElementById("form-response");

contactForm.addEventListener("submit", (e) => {
  e.preventDefault();
  responseMsg.textContent = "Thank you! Your message has been sent.";
  contactForm.reset();
  setTimeout(() => {
    responseMsg.textContent = "";
  }, 5000);
});
