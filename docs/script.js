// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Mobile navigation toggle
const hamburger = document.querySelector('.hamburger');
const navMenu = document.querySelector('.nav-menu');

if (hamburger && navMenu) {
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navMenu.classList.toggle('active');
    });

    // Close mobile menu when clicking on a link
    document.querySelectorAll('.nav-link').forEach(n => n.addEventListener('click', () => {
        hamburger.classList.remove('active');
        navMenu.classList.remove('active');
    }));
}

// Navbar scroll effect
window.addEventListener('scroll', () => {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 100) {
        navbar.style.background = 'rgba(255, 255, 255, 0.98)';
        navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
    } else {
        navbar.style.background = 'rgba(255, 255, 255, 0.95)';
        navbar.style.boxShadow = 'none';
    }
});

// Animate elements on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe elements for animation
document.addEventListener('DOMContentLoaded', () => {
    const animateElements = document.querySelectorAll('.feature-card, .step, .cta-content');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Copy code snippets to clipboard
document.querySelectorAll('code').forEach(codeBlock => {
    codeBlock.addEventListener('click', async () => {
        try {
            await navigator.clipboard.writeText(codeBlock.textContent);
            
            // Show feedback
            const originalText = codeBlock.textContent;
            codeBlock.textContent = 'Copied!';
            codeBlock.style.background = '#10b981';
            
            setTimeout(() => {
                codeBlock.textContent = originalText;
                codeBlock.style.background = '#1f2937';
            }, 1000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    });
    
    // Add cursor pointer to indicate clickable
    codeBlock.style.cursor = 'pointer';
    codeBlock.title = 'Click to copy';
});

// Animate trading card price
function animatePrice() {
    const priceElement = document.querySelector('.price');
    if (priceElement) {
        const basePrice = 185420;
        const variation = Math.random() * 1000 - 500; // Random variation
        const newPrice = basePrice + variation;
        
        priceElement.textContent = `RM ${newPrice.toLocaleString()}`;
        
        // Update change indicator
        const changeElement = document.querySelector('.change');
        if (changeElement) {
            const changePercent = (variation / basePrice * 100).toFixed(2);
            changeElement.textContent = `${changePercent >= 0 ? '+' : ''}${changePercent}%`;
            changeElement.className = `change ${changePercent >= 0 ? 'positive' : 'negative'}`;
        }
    }
}

// Animate mini chart
function animateChart() {
    const chartLine = document.querySelector('.mini-chart polyline');
    if (chartLine) {
        const points = chartLine.getAttribute('points').split(' ');
        const newPoints = points.map(point => {
            const [x, y] = point.split(',');
            const newY = Math.max(5, Math.min(55, parseFloat(y) + (Math.random() - 0.5) * 10));
            return `${x},${newY}`;
        });
        chartLine.setAttribute('points', newPoints.join(' '));
    }
}

// Start animations
setInterval(() => {
    animatePrice();
    animateChart();
}, 3000);

// Add loading animation for buttons
document.querySelectorAll('.btn').forEach(btn => {
    btn.addEventListener('click', function(e) {
        // Don't prevent default for external links
        if (this.getAttribute('href').startsWith('http')) {
            return;
        }
        
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple');
        
        this.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    });
});

// Add ripple effect CSS
const style = document.createElement('style');
style.textContent = `
    .btn {
        position: relative;
        overflow: hidden;
    }
    
    .ripple {
        position: absolute;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.3);
        transform: scale(0);
        animation: ripple-animation 0.6s linear;
        pointer-events: none;
    }
    
    @keyframes ripple-animation {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .change.negative {
        color: #ef4444;
    }
    
    @media (max-width: 768px) {
        .nav-menu {
            position: fixed;
            left: -100%;
            top: 70px;
            flex-direction: column;
            background-color: rgba(255, 255, 255, 0.98);
            width: 100%;
            text-align: center;
            transition: 0.3s;
            box-shadow: 0 10px 27px rgba(0, 0, 0, 0.05);
            padding: 2rem 0;
        }
        
        .nav-menu.active {
            left: 0;
        }
        
        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }
        
        .hamburger.active span:nth-child(1) {
            transform: translateY(8px) rotate(45deg);
        }
        
        .hamburger.active span:nth-child(3) {
            transform: translateY(-8px) rotate(-45deg);
        }
    }
`;
document.head.appendChild(style);
