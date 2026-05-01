// GRAVITY LP：スムーススクロール
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('a[href^="#"]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            var targetId = this.getAttribute('href');
            if (targetId === '#') {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: 'smooth' });
                return;
            }
            var target = document.querySelector(targetId);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Mobile hamburger menu
    var hamburger = document.querySelector('.b-hamburger');
    var headerNav = document.querySelector('.b-header-nav');
    if (hamburger && headerNav) {
        hamburger.addEventListener('click', function() {
            var isOpen = hamburger.classList.toggle('is-open');
            headerNav.classList.toggle('is-open');
            hamburger.setAttribute('aria-expanded', isOpen);
            hamburger.setAttribute('aria-label', isOpen ? 'メニューを閉じる' : 'メニューを開く');
        });
        headerNav.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                hamburger.classList.remove('is-open');
                headerNav.classList.remove('is-open');
                hamburger.setAttribute('aria-expanded', 'false');
                hamburger.setAttribute('aria-label', 'メニューを開く');
            });
        });
    }

    // Scroll reveal
    var observer = new IntersectionObserver(
        function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.15 }
    );
    document.querySelectorAll('.reveal').forEach(function(el) { observer.observe(el); });

    // Roadmap modal
    var openBtn = document.getElementById('open-roadmap');
    var modal = document.getElementById('roadmap-modal');
    if (openBtn && modal) {
        var overlay = modal.querySelector('.b-roadmap-modal-overlay');
        var closeBtn = modal.querySelector('.b-roadmap-modal-close');

        function openModal() {
            modal.classList.add('is-open');
            modal.setAttribute('aria-hidden', 'false');
            document.body.style.overflow = 'hidden';
        }
        function closeModal() {
            modal.classList.remove('is-open');
            modal.setAttribute('aria-hidden', 'true');
            document.body.style.overflow = '';
        }

        openBtn.addEventListener('click', openModal);
        if (closeBtn) closeBtn.addEventListener('click', closeModal);
        if (overlay) overlay.addEventListener('click', closeModal);
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && modal.classList.contains('is-open')) closeModal();
        });
    }

    // Form submission via hidden iframe
    var trialForm = document.getElementById('trial-form');
    if (trialForm) {
        trialForm.addEventListener('submit', function() {
            if (typeof fbq === 'function') fbq('track', 'Lead');
            var btn = trialForm.querySelector('button[type="submit"]');
            if (btn) {
                btn.disabled = true;
                btn.textContent = '送信中...';
            }
            setTimeout(function() {
                trialForm.reset();
                if (btn) {
                    btn.disabled = false;
                    btn.textContent = '送信しました ✓';
                }
                setTimeout(function() {
                    if (btn) btn.innerHTML = '体験セッションを申し込む（無料・60分） <i class="ri-arrow-right-line" aria-hidden="true"></i>';
                }, 3000);
            }, 1500);
        });
    }
});
