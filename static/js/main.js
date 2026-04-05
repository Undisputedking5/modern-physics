// static/js/main.js
document.addEventListener('DOMContentLoaded', () => {

    // Mobile Menu Toggle
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navbarMenu = document.querySelector('.navbar-menu');

    if (mobileMenuBtn && navbarMenu) {
        mobileMenuBtn.addEventListener('click', () => {
            navbarMenu.classList.toggle('active');
            mobileMenuBtn.innerHTML = navbarMenu.classList.contains('active') 
                ? '<i class="fas fa-times"></i>' 
                : '<i class="fas fa-bars"></i>';
        });

        // Close menu when a link is clicked
        document.querySelectorAll('.navbar-menu a').forEach(link => {
            link.addEventListener('click', () => {
                navbarMenu.classList.remove('active');
                mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            });
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('header')) {
                navbarMenu.classList.remove('active');
                mobileMenuBtn.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
    }

    // Scroll Reveal Animation
    const revealElements = document.querySelectorAll('.fade-up, .hero-content > *');

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animation = 'fadeUp 0.8s forwards';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });

    revealElements.forEach(el => observer.observe(el));

    // Button shine effect
    document.querySelectorAll('.btn-primary').forEach(btn => {
        btn.addEventListener('mousemove', (e) => {
            const rect = btn.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            btn.style.setProperty('--mouse-x', `${x}px`);
            btn.style.setProperty('--mouse-y', `${y}px`);
        });
    });
});

// ================== RESOURCES PAGE LOGIC ==================

// Run only when page is loaded
document.addEventListener('DOMContentLoaded', () => {

    const buttons = document.querySelectorAll('.tab-btn');
    const cards = document.querySelectorAll('.resource-card');

    // Only run if resources page exists (prevents errors on other pages)
    if (buttons.length > 0 && cards.length > 0) {

        buttons.forEach(btn => {
            btn.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                const type = btn.dataset.tab;

                cards.forEach(card => {
                    if (type === 'all') {
                        card.style.display = 'block';
                    } else {
                        card.style.display = card.dataset.type === type ? 'block' : 'none';
                    }
                });
            });
        });

        // AUTO FILTER FROM NAVBAR (?type=...)
        const params = new URLSearchParams(window.location.search);
        const type = params.get('type');

        if (type) {
            const targetBtn = document.querySelector(`.tab-btn[data-tab="${type}"]`);
            if (targetBtn) targetBtn.click();
        }
    }
});