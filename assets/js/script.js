// American Skyline Quality Standards - Custom JavaScript

document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize all functions
    initScrollToTop();
    initSmoothScrolling();
    initNavbarScroll();
    initCounterAnimation();
    initFadeInAnimation();
    initTypingAnimation();
    initMobileMenu();
    
    // Scroll to Top Button
    function initScrollToTop() {
        const scrollToTopBtn = document.getElementById('scrollToTop');
        
        if (scrollToTopBtn) {
            window.addEventListener('scroll', function() {
                if (window.pageYOffset > 300) {
                    scrollToTopBtn.classList.add('show');
                } else {
                    scrollToTopBtn.classList.remove('show');
                }
            });
            
            scrollToTopBtn.addEventListener('click', function() {
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
            });
        }
    }
    
    // Smooth Scrolling for Navigation Links
    function initSmoothScrolling() {
        const navLinks = document.querySelectorAll('a[href^="#"]');
        
        navLinks.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                
                const targetId = this.getAttribute('href');
                const targetSection = document.querySelector(targetId);
                
                if (targetSection) {
                    const headerHeight = document.querySelector('.header-section').offsetHeight;
                    const targetPosition = targetSection.offsetTop - headerHeight;
                    
                    window.scrollTo({
                        top: targetPosition,
                        behavior: 'smooth'
                    });
                    
                    // Close mobile menu if open
                    const navbarCollapse = document.querySelector('.navbar-collapse');
                    if (navbarCollapse.classList.contains('show')) {
                        const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                        bsCollapse.hide();
                    }
                }
            });
        });
    }
    
    // Navbar Active Link on Scroll
    function initNavbarScroll() {
        const sections = document.querySelectorAll('section[id]');
        const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
        
        window.addEventListener('scroll', function() {
            let current = '';
            const headerHeight = document.querySelector('.header-section').offsetHeight;
            
            sections.forEach(section => {
                const sectionTop = section.offsetTop - headerHeight - 100;
                const sectionHeight = section.offsetHeight;
                
                if (window.pageYOffset >= sectionTop && 
                    window.pageYOffset < sectionTop + sectionHeight) {
                    current = section.getAttribute('id');
                }
            });
            
            navLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                }
            });
        });
    }
    
    // Counter Animation
    function initCounterAnimation() {
        const counters = document.querySelectorAll('.stat-number');
        let animated = false;
        
        function animateCounters() {
            if (animated) return;
            
            const statisticsSection = document.querySelector('.statistics-section');
            const rect = statisticsSection.getBoundingClientRect();
            
            if (rect.top < window.innerHeight && rect.bottom > 0) {
                animated = true;
                
                counters.forEach(counter => {
                    const target = parseInt(counter.getAttribute('data-count'));
                    const duration = 2000; // 2 seconds
                    const increment = target / (duration / 16); // 60fps
                    let current = 0;
                    
                    const timer = setInterval(() => {
                        current += increment;
                        if (current >= target) {
                            current = target;
                            clearInterval(timer);
                        }
                        counter.textContent = Math.floor(current);
                    }, 16);
                });
            }
        }
        
        window.addEventListener('scroll', animateCounters);
        animateCounters(); // Check on load
    }
    
    // Fade In Animation on Scroll
    function initFadeInAnimation() {
        const fadeElements = document.querySelectorAll('.service-item, .about-section, .hero-section');
        
        fadeElements.forEach(element => {
            element.classList.add('fade-in');
        });
        
        function checkFadeIn() {
            fadeElements.forEach(element => {
                const rect = element.getBoundingClientRect();
                const isVisible = rect.top < window.innerHeight - 100;
                
                if (isVisible) {
                    element.classList.add('visible');
                }
            });
        }
        
        window.addEventListener('scroll', checkFadeIn);
        checkFadeIn(); // Check on load
    }
    
    // Typing Animation for Services Title
    function initTypingAnimation() {
        const animatedText = document.querySelector('.animated-text');
        if (!animatedText) return;
        
        const text = 'Our Services';
        let index = 0;
        
        function typeText() {
            if (index < text.length) {
                animatedText.textContent = text.slice(0, index + 1);
                index++;
                setTimeout(typeText, 100);
            } else {
                setTimeout(() => {
                    index = 0;
                    animatedText.textContent = '';
                    setTimeout(typeText, 500);
                }, 2000);
            }
        }
        
        // Start typing animation when section is visible
        const servicesTitle = document.querySelector('.services-title-section');
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    typeText();
                    observer.unobserve(entry.target);
                }
            });
        });
        
        if (servicesTitle) {
            observer.observe(servicesTitle);
        }
    }
    
    // Mobile Menu Enhancement
    function initMobileMenu() {
        const navbarToggler = document.querySelector('.navbar-toggler');
        const navbarCollapse = document.querySelector('.navbar-collapse');
        
        if (navbarToggler && navbarCollapse) {
            navbarToggler.addEventListener('click', function() {
                this.classList.toggle('active');
            });
            
            // Close menu when clicking outside
            document.addEventListener('click', function(e) {
                if (!navbarCollapse.contains(e.target) && 
                    !navbarToggler.contains(e.target) && 
                    navbarCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(navbarCollapse);
                    bsCollapse.hide();
                    navbarToggler.classList.remove('active');
                }
            });
        }
    }
    
    // Parallax Effect for Hero Section
    function initParallaxEffect() {
        const heroSection = document.querySelector('.hero-section');
        
        if (heroSection) {
            window.addEventListener('scroll', function() {
                const scrolled = window.pageYOffset;
                const rate = scrolled * -0.5;
                heroSection.style.transform = `translateY(${rate}px)`;
            });
        }
    }
    
    // Initialize parallax effect
    initParallaxEffect();
    
    // Preloader (if needed)
    function hidePreloader() {
        const preloader = document.querySelector('.preloader');
        if (preloader) {
            preloader.style.opacity = '0';
            setTimeout(() => {
                preloader.style.display = 'none';
            }, 300);
        }
    }
    
    // Hide preloader when page is loaded
    window.addEventListener('load', hidePreloader);
    
    // Form Validation (if contact form exists)
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }
                form.classList.add('was-validated');
            });
        });
    }
    
    initFormValidation();
    
    // Lazy Loading for Images
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
    
    initLazyLoading();
    
    // WhatsApp Chat Button Animation
    function initWhatsAppAnimation() {
        const whatsappBtn = document.querySelector('.whatsapp-btn');
        
        if (whatsappBtn) {
            // Pulse animation every 5 seconds
            setInterval(() => {
                whatsappBtn.style.animation = 'pulse 0.5s ease-in-out';
                setTimeout(() => {
                    whatsappBtn.style.animation = '';
                }, 500);
            }, 5000);
        }
    }
    
    initWhatsAppAnimation();
    
    // Add CSS for pulse animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.1); }
            100% { transform: scale(1); }
        }
        
        .navbar-toggler.active .navbar-toggler-icon {
            transform: rotate(45deg);
        }
        
        .preloader {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: #fff;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            transition: opacity 0.3s ease;
        }
        
        .lazy {
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .lazy.loaded {
            opacity: 1;
        }
    `;
    document.head.appendChild(style);
});

// Additional utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Performance optimization for scroll events
const optimizedScrollHandler = throttle(function() {
    // Scroll-based animations can be added here
}, 16); // 60fps

window.addEventListener('scroll', optimizedScrollHandler);
