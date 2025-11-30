// ==========================================
// Theme Management
// ==========================================
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.init();
    }

    init() {
        this.applyTheme(this.theme);
        this.setupToggle();
    }

    applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        this.theme = theme;
        localStorage.setItem('theme', theme);
    }

    toggle() {
        const newTheme = this.theme === 'light' ? 'dark' : 'light';
        this.applyTheme(newTheme);
    }

    setupToggle() {
        const toggleBtn = document.getElementById('themeToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }
}

// ==========================================
// Language Management
// ==========================================
class LanguageManager {
    constructor() {
        this.currentLang = localStorage.getItem('language') || 'en';
        this.init();
    }

    init() {
        this.applyLanguage(this.currentLang);
        this.setupToggle();
    }

    applyLanguage(lang) {
        const html = document.documentElement;
        const body = document.body;

        // Set language and direction
        html.setAttribute('lang', lang);
        html.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');

        // Update all translatable elements
        const elements = document.querySelectorAll('[data-en][data-ar]');
        elements.forEach(element => {
            const text = lang === 'ar' ? element.getAttribute('data-ar') : element.getAttribute('data-en');
            if (text) {
                element.textContent = text;
            }
        });

        // Update language toggle button text
        const langToggle = document.getElementById('langToggle');
        if (langToggle) {
            const langText = langToggle.querySelector('.lang-text');
            if (langText) {
                langText.textContent = lang === 'ar' ? 'English' : 'العربية';
            }
        }

        // Update form placeholders if needed
        this.updateFormPlaceholders(lang);

        this.currentLang = lang;
        localStorage.setItem('language', lang);
    }

    updateFormPlaceholders(lang) {
        const placeholders = {
            en: {
                name: 'Enter your name',
                email: 'Enter your email',
                company: 'Enter your company name',
                message: 'Enter your message'
            },
            ar: {
                name: 'أدخل اسمك',
                email: 'أدخل بريدك الإلكتروني',
                company: 'أدخل اسم شركتك',
                message: 'أدخل رسالتك'
            }
        };

        const inputs = {
            name: document.getElementById('name'),
            email: document.getElementById('email'),
            company: document.getElementById('company'),
            message: document.getElementById('message')
        };

        Object.keys(inputs).forEach(key => {
            if (inputs[key]) {
                inputs[key].placeholder = placeholders[lang][key];
            }
        });
    }

    toggle() {
        const newLang = this.currentLang === 'en' ? 'ar' : 'en';
        this.applyLanguage(newLang);
    }

    setupToggle() {
        const toggleBtn = document.getElementById('langToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }
}

// ==========================================
// Mobile Menu Management
// ==========================================
class MobileMenuManager {
    constructor() {
        this.isOpen = false;
        this.init();
    }

    init() {
        this.setupToggle();
        this.createMobileMenu();
    }

    createMobileMenu() {
        const navLinks = document.querySelector('.nav-links');
        if (!navLinks) return;

        // Clone nav links for mobile
        const mobileMenu = document.createElement('div');
        mobileMenu.className = 'mobile-menu';
        mobileMenu.innerHTML = navLinks.innerHTML;

        // Add to navbar
        const navbar = document.querySelector('.navbar .container');
        if (navbar) {
            navbar.appendChild(mobileMenu);
        }

        // Style mobile menu
        this.styleMobileMenu(mobileMenu);
    }

    styleMobileMenu(menu) {
        menu.style.cssText = `
            position: fixed;
            top: 70px;
            left: 0;
            right: 0;
            background: var(--bg-primary);
            border-bottom: 1px solid var(--border-color);
            padding: var(--spacing-lg);
            display: none;
            flex-direction: column;
            gap: var(--spacing-md);
            box-shadow: var(--shadow-lg);
            z-index: 999;
        `;
    }

    toggle() {
        const mobileMenu = document.querySelector('.mobile-menu');
        const toggleBtn = document.getElementById('mobileMenuToggle');

        if (!mobileMenu || !toggleBtn) return;

        this.isOpen = !this.isOpen;

        if (this.isOpen) {
            mobileMenu.style.display = 'flex';
            toggleBtn.classList.add('active');
        } else {
            mobileMenu.style.display = 'none';
            toggleBtn.classList.remove('active');
        }
    }

    setupToggle() {
        const toggleBtn = document.getElementById('mobileMenuToggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }

        // Close menu when clicking on a link
        document.addEventListener('click', (e) => {
            if (e.target.matches('.mobile-menu a')) {
                this.isOpen = true; // Set to true so toggle will close it
                this.toggle();
            }
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            const mobileMenu = document.querySelector('.mobile-menu');
            const toggleBtn = document.getElementById('mobileMenuToggle');

            if (this.isOpen && mobileMenu && toggleBtn) {
                if (!mobileMenu.contains(e.target) && !toggleBtn.contains(e.target)) {
                    this.toggle();
                }
            }
        });
    }
}

// ==========================================
// Smooth Scroll
// ==========================================
class SmoothScroll {
    constructor() {
        this.init();
    }

    init() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                const href = anchor.getAttribute('href');
                if (href === '#') return;

                e.preventDefault();
                const target = document.querySelector(href);

                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
}

// ==========================================
// Scroll Animations
// ==========================================
class ScrollAnimations {
    constructor() {
        this.observer = null;
        this.init();
    }

    init() {
        this.setupObserver();
        this.observeElements();
    }

    setupObserver() {
        const options = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                    this.observer.unobserve(entry.target);
                }
            });
        }, options);
    }

    observeElements() {
        const elements = document.querySelectorAll('.feature-card, .module-card, .about-feature, .contact-card');
        elements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            this.observer.observe(el);
        });

        // Add animation class styles
        const style = document.createElement('style');
        style.textContent = `
            .animate-in {
                opacity: 1 !important;
                transform: translateY(0) !important;
            }
        `;
        document.head.appendChild(style);
    }
}

// ==========================================
// Navbar Scroll Effect
// ==========================================
class NavbarScroll {
    constructor() {
        this.lastScroll = 0;
        this.init();
    }

    init() {
        window.addEventListener('scroll', () => {
            const navbar = document.querySelector('.navbar');
            if (!navbar) return;

            const currentScroll = window.pageYOffset;

            if (currentScroll > 100) {
                navbar.style.boxShadow = 'var(--shadow-md)';
            } else {
                navbar.style.boxShadow = 'none';
            }

            this.lastScroll = currentScroll;
        });
    }
}

// ==========================================
// Form Handler
// ==========================================
class FormHandler {
    constructor() {
        this.init();
    }

    init() {
        const form = document.querySelector('.contact-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleSubmit(e));
        }
    }

    async handleSubmit(e) {
        e.preventDefault();

        const form = e.target;
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);

        // Show loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        submitBtn.disabled = true;
        submitBtn.textContent = this.getLoadingText();

        try {
            // Send to ERPNext backend
            const response = await fetch('/api/method/correspondence.api.website.submit_contact_form', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (result.message && result.message.success) {
                // Show success message
                this.showMessage('success', this.getSuccessMessage());
                form.reset();
            } else {
                throw new Error(result.message || 'Submission failed');
            }
        } catch (error) {
            console.error('Form submission error:', error);
            // Show error message
            this.showMessage('error', this.getErrorMessage());
        } finally {
            // Restore button state
            submitBtn.disabled = false;
            submitBtn.textContent = originalText;
        }
    }

    getLoadingText() {
        const lang = localStorage.getItem('language') || 'en';
        return lang === 'ar' ? 'جاري الإرسال...' : 'Sending...';
    }

    getSuccessMessage() {
        const lang = localStorage.getItem('language') || 'en';
        return lang === 'ar'
            ? 'تم إرسال رسالتك بنجاح! سنتواصل معك قريباً.'
            : 'Message sent successfully! We\'ll get back to you soon.';
    }

    getErrorMessage() {
        const lang = localStorage.getItem('language') || 'en';
        return lang === 'ar'
            ? 'حدث خطأ أثناء إرسال الرسالة. يرجى المحاولة مرة أخرى.'
            : 'An error occurred while sending your message. Please try again.';
    }

    showMessage(type, message) {
        // Create message element
        const messageEl = document.createElement('div');
        messageEl.className = `form-message form-message-${type}`;
        messageEl.textContent = message;

        // Style the message
        messageEl.style.cssText = `
            padding: 1rem 1.5rem;
            border-radius: var(--radius-lg);
            margin-top: var(--spacing-md);
            font-weight: 600;
            text-align: center;
            animation: slideInFromTop 0.3s ease;
            background: ${type === 'success' ? '#d4edda' : '#f8d7da'};
            color: ${type === 'success' ? '#155724' : '#721c24'};
            border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};
        `;

        // Add animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInFromTop {
                from {
                    opacity: 0;
                    transform: translateY(-20px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        document.head.appendChild(style);

        // Insert message
        const form = document.querySelector('.contact-form');
        form.appendChild(messageEl);

        // Remove message after 5 seconds
        setTimeout(() => {
            messageEl.style.animation = 'slideOutToTop 0.3s ease';
            setTimeout(() => messageEl.remove(), 300);
        }, 5000);
    }
}

// ==========================================
// Stats Counter Animation
// ==========================================
class StatsCounter {
    constructor() {
        this.init();
    }

    init() {
        const stats = document.querySelectorAll('.stat-number');

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateValue(entry.target);
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });

        stats.forEach(stat => observer.observe(stat));
    }

    animateValue(element) {
        const text = element.textContent;
        const hasPercent = text.includes('%');
        const hasPlus = text.includes('+');
        const value = parseFloat(text);

        if (isNaN(value)) return;

        const duration = 2000;
        const steps = 60;
        const increment = value / steps;
        const stepDuration = duration / steps;
        let current = 0;

        const timer = setInterval(() => {
            current += increment;
            if (current >= value) {
                current = value;
                clearInterval(timer);
            }

            let displayValue = current.toFixed(hasPercent ? 1 : 0);
            if (hasPercent) displayValue += '%';
            if (hasPlus) displayValue += '+';

            element.textContent = displayValue;
        }, stepDuration);
    }
}

// ==========================================
// Parallax Effect
// ==========================================
class ParallaxEffect {
    constructor() {
        this.init();
    }

    init() {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const parallaxElements = document.querySelectorAll('.gradient-orb');

            parallaxElements.forEach((el, index) => {
                const speed = 0.5 + (index * 0.1);
                const yPos = -(scrolled * speed);
                el.style.transform = `translateY(${yPos}px)`;
            });
        });
    }
}

// ==========================================
// Initialize Everything
// ==========================================
class App {
    constructor() {
        this.init();
    }

    init() {
        // Wait for DOM to be ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initializeComponents());
        } else {
            this.initializeComponents();
        }
    }

    initializeComponents() {
        // Initialize all components
        new ThemeManager();
        new LanguageManager();
        new MobileMenuManager();
        new SmoothScroll();
        new ScrollAnimations();
        new NavbarScroll();
        new FormHandler();
        new StatsCounter();
        new ParallaxEffect();

        // Add loaded class to body
        document.body.classList.add('loaded');

        // Log initialization
        console.log('🚀 ERPNext Website initialized successfully!');
    }
}

// Start the application
new App();
