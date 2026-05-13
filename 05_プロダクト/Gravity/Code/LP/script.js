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
      if (menuToggle) {
        menuToggle.classList.remove("is-open");
        menuToggle.setAttribute("aria-expanded", "false");
        menuToggle.setAttribute("aria-label", "メニューを開く");
      }
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

// Close mobile nav when clicking outside
document.addEventListener("click", function(event) {
  if (mobileNav && mobileNav.classList.contains("open")) {
    if (!mobileNav.contains(event.target) && !menuToggle.contains(event.target)) {
      mobileNav.classList.remove("open");
      menuToggle.classList.remove("is-open");
      menuToggle.setAttribute("aria-expanded", "false");
      menuToggle.setAttribute("aria-label", "メニューを開く");
      mobileNav.setAttribute("aria-hidden", "true");
    }
  }
});

// Mobile CTA visibility (hide near form section)
var mobileCta = document.querySelector(".mobile-cta");
if (mobileCta) {
  var applySection = document.getElementById("apply");
  window.addEventListener("scroll", function() {
    var scrollY = window.scrollY;
    var showAfter = 600;
    var hideNearForm = applySection ? applySection.offsetTop - window.innerHeight + 100 : Infinity;
    if (scrollY > showAfter && scrollY < hideNearForm) {
      mobileCta.classList.add("is-visible");
      mobileCta.setAttribute("aria-hidden", "false");
    } else {
      mobileCta.classList.remove("is-visible");
      mobileCta.setAttribute("aria-hidden", "true");
    }
  }, { passive: true });
}

// Form submission via hidden iframe
var codeForm = document.getElementById("code-form");
if (codeForm) {
  codeForm.addEventListener("submit", function() {
    if (typeof fbq === "function") fbq("track", "Lead");
    var btn = codeForm.querySelector('button[type="submit"]');
    if (btn) {
      btn.disabled = true;
      btn.textContent = "送信中...";
    }
    setTimeout(function() {
      codeForm.reset();
      if (btn) {
        btn.disabled = false;
        btn.textContent = "送信しました ✓";
        btn.style.background = "#16a34a";
      }
      setTimeout(function() {
        if (btn) {
          btn.innerHTML = '自分の取扱説明書を手に入れる <i class="ri-arrow-right-s-line" aria-hidden="true"></i>';
          btn.style.background = "";
        }
      }, 3000);
    }, 1500);
  });
}
