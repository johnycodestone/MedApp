/* ============================================================================
   accounts.js
   Purpose:
     - JavaScript for accounts app
     - Form validation, password toggle, password strength checker
   
   Usage:
     - Loaded in accounts templates
   ============================================================================ */

(function() {
  'use strict';

  // =========================================================================
  // Password Toggle Functionality
  // =========================================================================
  
  function initPasswordToggles() {
    document.querySelectorAll('.password-toggle').forEach(toggle => {
      toggle.addEventListener('click', function() {
        const targetId = this.dataset.target || this.closest('.password-field').querySelector('input').id;
        const input = document.getElementById(targetId);
        
        if (input.type === 'password') {
          input.type = 'text';
          this.querySelector('.password-icon').textContent = '🙈';
        } else {
          input.type = 'password';
          this.querySelector('.password-icon').textContent = '👁️';
        }
      });
    });
  }

  // =========================================================================
  // Password Strength Checker
  // =========================================================================
  
  function checkPasswordStrength(password) {
    const checks = {
      length: password.length >= 8,
      letter: /[a-zA-Z]/.test(password),
      number: /[0-9]/.test(password),
      special: /[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?]/.test(password)
    };

    const score = Object.values(checks).filter(Boolean).length;
    
    return {
      score,
      checks,
      strength: score <= 1 ? 'weak' : score <= 2 ? 'fair' : score <= 3 ? 'good' : 'strong'
    };
  }

  // =========================================================================
  // Password Requirements Validation (for password change page)
  // =========================================================================
  
  function initPasswordRequirements() {
    const newPassword = document.getElementById('id_new_password1');
    const confirmPassword = document.getElementById('id_new_password2');
    
    if (!newPassword) return;

    function updateRequirements() {
      const password = newPassword.value;
      const confirm = confirmPassword ? confirmPassword.value : '';

      // Length check
      const lengthReq = document.getElementById('req-length');
      if (lengthReq) {
        lengthReq.classList.toggle('valid', password.length >= 8);
      }

      // Letter check
      const letterReq = document.getElementById('req-letter');
      if (letterReq) {
        letterReq.classList.toggle('valid', /[a-zA-Z]/.test(password));
      }

      // Number check
      const numberReq = document.getElementById('req-number');
      if (numberReq) {
        numberReq.classList.toggle('valid', /[0-9]/.test(password));
      }

      // Match check
      const matchReq = document.getElementById('req-match');
      if (matchReq && confirmPassword) {
        matchReq.classList.toggle('valid', password === confirm && password.length > 0);
      }
    }

    newPassword.addEventListener('input', updateRequirements);
    if (confirmPassword) {
      confirmPassword.addEventListener('input', updateRequirements);
    }
  }

  // =========================================================================
  // Login Form Validation
  // =========================================================================
  
  function initLoginForm() {
    const form = document.getElementById('loginForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
      const username = document.getElementById('id_username');
      const password = document.getElementById('id_password');
      let valid = true;

      // Clear previous errors
      MedApp.clearFormErrors(form);

      // Validate username
      if (!username.value.trim()) {
        MedApp.showFieldError(username, 'Please enter your username or email');
        valid = false;
      }

      // Validate password
      if (!password.value) {
        MedApp.showFieldError(password, 'Please enter your password');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
      }
    });
  }

  // =========================================================================
  // Registration Form Validation
  // =========================================================================
  
  function initRegisterForm() {
    const form = document.getElementById('registerForm');
    if (!form) return;

    // Real-time email validation
    const emailInput = document.getElementById('id_email');
    if (emailInput) {
      emailInput.addEventListener('blur', function() {
        if (this.value && !MedApp.isValidEmail(this.value)) {
          MedApp.showFieldError(this, 'Please enter a valid email address');
        } else {
          MedApp.clearFieldError(this);
        }
      });
    }

    // Real-time phone validation
    const phoneInput = document.getElementById('id_phone');
    if (phoneInput) {
      phoneInput.addEventListener('blur', function() {
        if (this.value && !MedApp.isValidPhone(this.value)) {
          MedApp.showFieldError(this, 'Please enter a valid phone number');
        } else {
          MedApp.clearFieldError(this);
        }
      });
    }

    // Password match validation
    const password1 = document.getElementById('id_password1');
    const password2 = document.getElementById('id_password2');
    
    if (password2) {
      password2.addEventListener('input', function() {
        if (this.value && password1.value !== this.value) {
          MedApp.showFieldError(this, 'Passwords do not match');
        } else {
          MedApp.clearFieldError(this);
        }
      });
    }

    // Form submission validation
    form.addEventListener('submit', function(e) {
      let valid = true;

      // Clear previous errors
      MedApp.clearFormErrors(form);

      // Required fields
      const requiredFields = [
        'first_name',
        'last_name',
        'username',
        'email',
        'role',
        'password1',
        'password2'
      ];

      requiredFields.forEach(fieldName => {
        const field = document.getElementById(`id_${fieldName}`);
        if (field && !field.value.trim()) {
          MedApp.showFieldError(field, 'This field is required');
          valid = false;
        }
      });

      // Email validation
      if (emailInput && emailInput.value && !MedApp.isValidEmail(emailInput.value)) {
        MedApp.showFieldError(emailInput, 'Please enter a valid email address');
        valid = false;
      }

      // Password strength
      if (password1 && password1.value) {
        const strength = checkPasswordStrength(password1.value);
        if (strength.score < 2) {
          MedApp.showFieldError(password1, 'Password is too weak. Use at least 8 characters with letters and numbers.');
          valid = false;
        }
      }

      // Password match
      if (password1 && password2 && password1.value !== password2.value) {
        MedApp.showFieldError(password2, 'Passwords do not match');
        valid = false;
      }

      // Terms checkbox
      const termsCheckbox = form.querySelector('input[name="terms"]');
      if (termsCheckbox && !termsCheckbox.checked) {
        MedApp.showToast('Please accept the Terms & Conditions', 'error');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
        // Scroll to first error
        const firstError = form.querySelector('.is-invalid');
        if (firstError) {
          firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    });
  }

  // =========================================================================
  // Profile Edit Form Validation
  // =========================================================================
  
  function initProfileEditForm() {
    const form = document.getElementById('profileEditForm');
    if (!form) return;

    // Real-time email validation
    const emailInput = document.getElementById('id_email');
    if (emailInput) {
      emailInput.addEventListener('blur', function() {
        if (this.value && !MedApp.isValidEmail(this.value)) {
          MedApp.showFieldError(this, 'Please enter a valid email address');
        } else {
          MedApp.clearFieldError(this);
        }
      });
    }

    // Form submission validation
    form.addEventListener('submit', function(e) {
      let valid = true;

      // Clear previous errors
      MedApp.clearFormErrors(form);

      // Required fields
      const requiredFields = ['first_name', 'last_name', 'email'];

      requiredFields.forEach(fieldName => {
        const field = document.getElementById(`id_${fieldName}`);
        if (field && !field.value.trim()) {
          MedApp.showFieldError(field, 'This field is required');
          valid = false;
        }
      });

      // Email validation
      if (emailInput && emailInput.value && !MedApp.isValidEmail(emailInput.value)) {
        MedApp.showFieldError(emailInput, 'Please enter a valid email address');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
      }
    });
  }

  // =========================================================================
  // Password Change Form Validation
  // =========================================================================
  
  function initPasswordChangeForm() {
    const form = document.getElementById('passwordChangeForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
      let valid = true;

      // Clear previous errors
      MedApp.clearFormErrors(form);

      const oldPassword = document.getElementById('id_old_password');
      const newPassword1 = document.getElementById('id_new_password1');
      const newPassword2 = document.getElementById('id_new_password2');

      // Validate old password
      if (!oldPassword.value) {
        MedApp.showFieldError(oldPassword, 'Please enter your current password');
        valid = false;
      }

      // Validate new password
      if (!newPassword1.value) {
        MedApp.showFieldError(newPassword1, 'Please enter a new password');
        valid = false;
      } else {
        const strength = checkPasswordStrength(newPassword1.value);
        if (strength.score < 2) {
          MedApp.showFieldError(newPassword1, 'Password is too weak. Use at least 8 characters with letters and numbers.');
          valid = false;
        }
      }

      // Validate password match
      if (!newPassword2.value) {
        MedApp.showFieldError(newPassword2, 'Please confirm your new password');
        valid = false;
      } else if (newPassword1.value !== newPassword2.value) {
        MedApp.showFieldError(newPassword2, 'Passwords do not match');
        valid = false;
      }

      // Check if new password is same as old
      if (oldPassword.value && newPassword1.value && oldPassword.value === newPassword1.value) {
        MedApp.showFieldError(newPassword1, 'New password must be different from current password');
        valid = false;
      }

      if (!valid) {
        e.preventDefault();
      }
    });
  }

  // =========================================================================
  // Auto-dismiss Success Messages
  // =========================================================================
  
  function initAutoDismissAlerts() {
    const alerts = document.querySelectorAll('.alert-success');
    alerts.forEach(alert => {
      setTimeout(() => {
        alert.style.transition = 'opacity 0.3s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 300);
      }, 5000);
    });
  }

  // =========================================================================
  // Initialize on Page Load
  // =========================================================================
  
  document.addEventListener('DOMContentLoaded', function() {
    initPasswordToggles();
    initPasswordRequirements();
    initLoginForm();
    initRegisterForm();
    initProfileEditForm();
    initPasswordChangeForm();
    initAutoDismissAlerts();

    console.log('Accounts module initialized');
  });

})();
