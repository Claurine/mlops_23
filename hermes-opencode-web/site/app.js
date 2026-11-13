const ctaButton = document.querySelector("#ctaButton");
const steps = [...document.querySelectorAll("[data-step]")];
const clock = document.querySelector("#clock");

function updateClock() {
  clock.textContent = new Intl.DateTimeFormat("id-ID", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date());
}

updateClock();
setInterval(updateClock, 30000);

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener("click", function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute("href"));
    if (target) {
      target.scrollIntoView({ behavior: "smooth" });
    }
  });
});

// Highlight active section on scroll
const sections = document.querySelectorAll("section");
window.addEventListener("scroll", () => {
  let current = "";
  sections.forEach(section => {
    const sectionTop = section.offsetTop;
    const sectionHeight = section.clientHeight;
    if (pageYOffset >= sectionTop - sectionHeight / 3) {
      current = section.getAttribute("id");
    }
  });
  const navLinks = document.querySelectorAll(".topbar .text-link, .topbar .brand");
  navLinks.forEach(link => {
    link.classList.remove("active");
    if (link.getAttribute("href") === `#${current}`) {
      link.classList.add("active");
    }
  });
});

// Theme toggle
const themeButton = document.querySelector("#themeButton");
themeButton.addEventListener("click", () => {
  document.body.classList.toggle("light");
});

// CTA button ripple effect
if (ctaButton) {
  ctaButton.addEventListener("click", function(e) {
    const rect = this.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const ripple = document.createElement("span");
    ripple.style.left = `${x}px`;
    ripple.style.top = `${y}px`;
    ripple.className = "ripple";
    this.appendChild(ripple);
    setTimeout(() => ripple.remove(), 600);
  });
}
