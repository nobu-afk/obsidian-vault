// Mobile menu toggle
var menuToggle = document.querySelector(".menu-toggle");
var mobileNav = document.querySelector(".mobile-nav");

if (menuToggle && mobileNav) {
  function toggleMenu() {
    var isOpen = mobileNav.classList.toggle("open");
    menuToggle.classList.toggle("is-open", isOpen);
    menuToggle.setAttribute("aria-expanded", isOpen ? "true" : "false");
    menuToggle.setAttribute("aria-label", isOpen ? "メニューを閉じる" : "メニューを開く");
    mobileNav.setAttribute("aria-hidden", isOpen ? "false" : "true");
  }

  menuToggle.addEventListener("click", toggleMenu);
}

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(function(link) {
  link.addEventListener("click", function(event) {
    var targetId = link.getAttribute("href");
    if (!targetId) return;
    if (targetId === "#") {
      event.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }
    var target = document.querySelector(targetId);
    if (!target) return;
    event.preventDefault();
    target.scrollIntoView({ behavior: "smooth" });
    if (mobileNav && mobileNav.classList.contains("open")) {
      mobileNav.classList.remove("open");
      if (menuToggle) menuToggle.setAttribute("aria-expanded", "false");
      mobileNav.setAttribute("aria-hidden", "true");
    }
  });
});

// Scroll reveal
var observer = new IntersectionObserver(
  function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 }
);

document.querySelectorAll(".reveal").forEach(function(el) { observer.observe(el); });

// Form submission via hidden iframe
var coachingForm = document.getElementById("coaching-form");
if (coachingForm) {
  coachingForm.addEventListener("submit", function() {
    if (typeof fbq === "function") fbq("track", "Lead");
    var btn = coachingForm.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.textContent = "送信中...";
    }
    setTimeout(function() {
      coachingForm.reset();
      if (btn) {
        btn.disabled = false;
        btn.textContent = "送信しました ✓";
      }
      setTimeout(function() {
        if (btn) btn.innerHTML = '申し込む <i class="ri-arrow-right-s-line" aria-hidden="true"></i>';
      }, 3000);
    }, 1500);
  });
}
