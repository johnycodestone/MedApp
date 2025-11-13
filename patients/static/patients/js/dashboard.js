// Enhanced Patient Dashboard JavaScript
document.addEventListener("DOMContentLoaded", () => {
  console.log("Enhanced Patient Dashboard Loaded 🚀");

  // Animate cards on scroll
  const animateOnScroll = () => {
    const cards = document.querySelectorAll('.card, .btn');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }, index * 100);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    cards.forEach(card => {
      card.style.opacity = '0';
      card.style.transform = 'translateY(20px)';
      card.style.transition = 'all 0.5s ease-out';
      observer.observe(card);
    });
  };

  // Add loading states to quick action buttons
  const addButtonLoadingStates = () => {
    const buttons = document.querySelectorAll('.quick-actions .btn');
    
    buttons.forEach(btn => {
      btn.addEventListener('click', function(e) {
        if (!this.classList.contains('loading')) {
          this.classList.add('loading');
          
          // Create spinner
          const spinner = document.createElement('span');
          spinner.className = 'btn-spinner';
          spinner.innerHTML = '⟳';
          spinner.style.display = 'inline-block';
          spinner.style.animation = 'spin 0.8s linear infinite';
          
          const originalContent = this.innerHTML;
          this.innerHTML = '';
          this.appendChild(spinner);
          
          // Simulate loading (remove after navigation starts)
          setTimeout(() => {
            this.innerHTML = originalContent;
            this.classList.remove('loading');
          }, 1000);
        }
      });
    });
  };

  // Add hover effects to cards
  const enhanceCardInteractions = () => {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.zIndex = '10';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.zIndex = '1';
      });
    });
  };

  // Add status badge animations
  const animateStatusBadges = () => {
    const badges = document.querySelectorAll('.card-status');
    
    badges.forEach((badge, index) => {
      setTimeout(() => {
        badge.style.opacity = '1';
        badge.style.transform = 'scale(1)';
      }, 300 + (index * 50));
      
      badge.style.opacity = '0';
      badge.style.transform = 'scale(0.8)';
      badge.style.transition = 'all 0.3s ease-out';
    });
  };

  // Trust strip animation
  const animateTrustStrip = () => {
    const trustStrip = document.querySelector('.trust-strip');
    if (!trustStrip) return;
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.style.opacity = '1';
          entry.target.style.transform = 'translateY(0)';
        }
      });
    }, { threshold: 0.5 });
    
    trustStrip.style.opacity = '0';
    trustStrip.style.transform = 'translateY(30px)';
    trustStrip.style.transition = 'all 0.6s ease-out';
    observer.observe(trustStrip);
  };

  // Add smooth scroll to sections
  const addSmoothScroll = () => {
    const sections = document.querySelectorAll('.section');
    sections.forEach((section, index) => {
      section.style.opacity = '0';
      section.style.transform = 'translateY(20px)';
      section.style.transition = 'all 0.5s ease-out';
      
      setTimeout(() => {
        section.style.opacity = '1';
        section.style.transform = 'translateY(0)';
      }, 200 + (index * 100));
    });
  };

  // Add click ripple effect to buttons
  const addRippleEffect = () => {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
      button.addEventListener('click', function(e) {
        const ripple = document.createElement('span');
        const rect = this.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.className = 'ripple-effect';
        
        this.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
      });
    });
  };

  // Initialize all enhancements
  const init = () => {
    animateOnScroll();
    addButtonLoadingStates();
    enhanceCardInteractions();
    animateStatusBadges();
    animateTrustStrip();
    addSmoothScroll();
    addRippleEffect();
  };

  // Add CSS for dynamic effects
  const style = document.createElement('style');
  style.textContent = `
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    
    .btn-spinner {
      display: inline-block;
      margin-right: 0.5rem;
    }
    
    .ripple-effect {
      position: absolute;
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.6);
      transform: scale(0);
      animation: ripple 0.6s ease-out;
      pointer-events: none;
    }
    
    @keyframes ripple {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
    
    .card {
      will-change: transform;
    }
  `;
  document.head.appendChild(style);

  // Run initialization
  init();

  // Log completion
  console.log("✨ Dashboard enhancements active!");
});