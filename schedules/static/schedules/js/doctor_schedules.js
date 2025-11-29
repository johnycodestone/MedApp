// Doctor Schedules Page JavaScript

document.addEventListener("DOMContentLoaded", () => {
  console.log("Doctor Schedules Page Loaded 🚀");

  // Animate cards on scroll
  const animateOnScroll = () => {
    const cards = document.querySelectorAll('.duty-card, .slot-card, .leave-card, .override-card, .schedule-card, .stat-card');
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
          setTimeout(() => {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
          }, index * 50);
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

  // Add hover effects to cards
  const enhanceCardInteractions = () => {
    const cards = document.querySelectorAll('.duty-card, .slot-card, .leave-card, .override-card, .schedule-card');
    
    cards.forEach(card => {
      card.addEventListener('mouseenter', function() {
        this.style.zIndex = '10';
      });
      
      card.addEventListener('mouseleave', function() {
        this.style.zIndex = '1';
      });
    });
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

  // Add table row hover effects
  const enhanceTableRows = () => {
    const tableRows = document.querySelectorAll('.shifts-table tbody tr');
    
    tableRows.forEach(row => {
      row.addEventListener('mouseenter', function() {
        this.style.backgroundColor = '#f9fafb';
        this.style.cursor = 'pointer';
      });
      
      row.addEventListener('mouseleave', function() {
        this.style.backgroundColor = '';
      });
    });
  };

  // Add status badge animations
  const animateStatusBadges = () => {
    const badges = document.querySelectorAll('.duty-status, .shift-status, .leave-status, .override-status, .schedule-status');
    
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

  // Add click ripple effect to stat cards
  const addRippleEffect = () => {
    const statCards = document.querySelectorAll('.stat-card');
    
    statCards.forEach(card => {
      card.addEventListener('click', function(e) {
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
    enhanceCardInteractions();
    addSmoothScroll();
    enhanceTableRows();
    animateStatusBadges();
    addRippleEffect();
  };

  // Add CSS for dynamic effects
  const style = document.createElement('style');
  style.textContent = `
    .ripple-effect {
      position: absolute;
      border-radius: 50%;
      background: rgba(0, 102, 255, 0.3);
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
    
    .duty-card,
    .slot-card,
    .leave-card,
    .override-card,
    .schedule-card {
      will-change: transform;
    }
  `;
  document.head.appendChild(style);

  // Run initialization
  init();

  // Log completion
  console.log("✨ Doctor Schedules enhancements active!");
});

