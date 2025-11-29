/* ============================================================================
   prescriptions.js
   Purpose:
     - JavaScript for prescriptions app
     - Dynamic medication form, filtering, search, download functionality
   
   Usage:
     - Loaded in prescriptions templates
   ============================================================================ */

(function() {
  'use strict';

  // =========================================================================
  // Global Variables
  // =========================================================================
  
  let medicationCount = 1;

  // =========================================================================
  // Medication Form Management (Create Page)
  // =========================================================================
  
  function initMedicationForm() {
    const addBtn = document.getElementById('addMedicationBtn');
    if (!addBtn) return;

    addBtn.addEventListener('click', addMedicationField);
  }

  function addMedicationField() {
    const container = document.getElementById('medicationsContainer');
    const template = document.getElementById('medicationTemplate');
    
    if (!container || !template) return;

    // Clone template
    const clone = template.content.cloneNode(true);
    const medicationItem = clone.querySelector('.medication-form-item');
    
    // Update index
    medicationItem.dataset.index = medicationCount;
    
    // Update medication number
    const numberSpan = clone.querySelector('.medication-number');
    if (numberSpan) {
      numberSpan.textContent = medicationCount + 1;
    }

    // Update input names and IDs
    const inputs = clone.querySelectorAll('input, select');
    inputs.forEach(input => {
      const name = input.getAttribute('name');
      if (name) {
        input.setAttribute('name', name.replace('[]', `[${medicationCount}]`));
      }
      
      const id = input.getAttribute('id');
      if (id) {
        input.setAttribute('id', id + '_' + medicationCount);
      }
    });

    // Update labels
    const labels = clone.querySelectorAll('label');
    labels.forEach(label => {
      const forAttr = label.getAttribute('for');
      if (forAttr) {
        label.setAttribute('for', forAttr + '_' + medicationCount);
      }
    });

    // Update remove button
    const removeBtn = clone.querySelector('.btn-remove');
    if (removeBtn) {
      removeBtn.onclick = function() {
        removeMedication(medicationCount);
      };
    }

    container.appendChild(clone);
    medicationCount++;

    // Show remove buttons if more than one medication
    updateRemoveButtons();

    // Show success toast
    MedApp.showToast('Medication field added', 'success');
  }

  function removeMedication(index) {
    const item = document.querySelector(`.medication-form-item[data-index="${index}"]`);
    if (!item) return;

    // Confirm removal
    MedApp.confirm('Remove this medication?', () => {
      item.remove();
      updateRemoveButtons();
      MedApp.showToast('Medication removed', 'info');
    });
  }

  // Make removeMedication available globally
  window.removeMedication = removeMedication;

  function updateRemoveButtons() {
    const items = document.querySelectorAll('.medication-form-item');
    const removeButtons = document.querySelectorAll('.btn-remove');

    removeButtons.forEach((btn, index) => {
      if (items.length > 1) {
        btn.style.display = 'flex';
      } else {
        btn.style.display = 'none';
      }
    });
  }

  // =========================================================================
  // Prescription List Filtering
  // =========================================================================
  
  function initFilterTabs() {
    const tabs = document.querySelectorAll('.filter-tab');
    if (tabs.length === 0) return;

    tabs.forEach(tab => {
      tab.addEventListener('click', function() {
        // Remove active from all tabs
        tabs.forEach(t => t.classList.remove('active'));
        
        // Add active to clicked tab
        this.classList.add('active');

        // Get filter value
        const filter = this.dataset.filter;
        
        // Filter prescriptions
        filterPrescriptions(filter);
      });
    });
  }

  function filterPrescriptions(filter) {
    const cards = document.querySelectorAll('.prescription-card');
    
    cards.forEach(card => {
      // In real implementation, check prescription data
      // For now, just show all
      if (filter === 'all') {
        card.style.display = 'block';
      } else if (filter === 'recent') {
        // Show prescriptions from last 30 days
        // This would check the date in real implementation
        card.style.display = 'block';
      } else if (filter === 'active') {
        // Show only active prescriptions
        card.style.display = 'block';
      }
    });

    MedApp.showToast(`Showing ${filter} prescriptions`, 'info');
  }

  // =========================================================================
  // Search Functionality
  // =========================================================================
  
  function initSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;

    // Debounced search
    const debouncedSearch = MedApp.debounce(performSearch, 300);
    
    searchInput.addEventListener('input', function() {
      debouncedSearch(this.value);
    });
  }

  function performSearch(query) {
    const cards = document.querySelectorAll('.prescription-card');
    const lowerQuery = query.toLowerCase();

    if (!query) {
      // Show all if search is empty
      cards.forEach(card => {
        card.style.display = 'block';
      });
      return;
    }

    let visibleCount = 0;

    cards.forEach(card => {
      // Get card text content
      const text = card.textContent.toLowerCase();
      
      if (text.includes(lowerQuery)) {
        card.style.display = 'block';
        visibleCount++;
      } else {
        card.style.display = 'none';
      }
    });

    // Show message if no results
    const grid = document.getElementById('prescriptionsGrid');
    if (grid) {
      let noResultsMsg = grid.querySelector('.no-results-message');
      
      if (visibleCount === 0) {
        if (!noResultsMsg) {
          noResultsMsg = document.createElement('div');
          noResultsMsg.className = 'empty-state no-results-message';
          noResultsMsg.innerHTML = `
            <div class="empty-icon">🔍</div>
            <h3>No Results Found</h3>
            <p>No prescriptions match your search "${query}"</p>
          `;
          grid.appendChild(noResultsMsg);
        }
      } else {
        if (noResultsMsg) {
          noResultsMsg.remove();
        }
      }
    }
  }

  // =========================================================================
  // Download Prescription
  // =========================================================================
  
  function downloadPrescription(prescriptionId) {
    // Show loading
    const spinner = MedApp.showLoading();

    // In real implementation, make API call to generate PDF
    setTimeout(() => {
      MedApp.hideLoading(spinner);
      MedApp.showToast('Prescription downloaded successfully', 'success');
      
      // Simulate download
      // In real implementation:
      // window.location.href = `/prescriptions/${prescriptionId}/download/`;
    }, 1500);
  }

  // Make downloadPrescription available globally
  window.downloadPrescription = downloadPrescription;

  // =========================================================================
  // Form Validation (Create Page)
  // =========================================================================
  
  function initCreateForm() {
    const form = document.getElementById('createPrescriptionForm');
    if (!form) return;

    form.addEventListener('submit', function(e) {
      let valid = true;

      // Clear previous errors
      MedApp.clearFormErrors(form);

      // Validate patient selection
      const patientSelect = document.getElementById('id_patient');
      if (patientSelect && !patientSelect.value) {
        MedApp.showFieldError(patientSelect, 'Please select a patient');
        valid = false;
      }

      // Validate medications
      const medicationItems = document.querySelectorAll('.medication-form-item');
      if (medicationItems.length === 0) {
        MedApp.showToast('Please add at least one medication', 'error');
        valid = false;
      }

      // Validate each medication
      medicationItems.forEach((item, index) => {
        const nameInput = item.querySelector('input[name*="[name]"]');
        const dosageInput = item.querySelector('input[name*="[dosage]"]');
        const frequencySelect = item.querySelector('select[name*="[frequency]"]');
        const durationInput = item.querySelector('input[name*="[duration]"]');

        if (nameInput && !nameInput.value.trim()) {
          MedApp.showFieldError(nameInput, 'Medication name is required');
          valid = false;
        }

        if (dosageInput && !dosageInput.value.trim()) {
          MedApp.showFieldError(dosageInput, 'Dosage is required');
          valid = false;
        }

        if (frequencySelect && !frequencySelect.value) {
          MedApp.showFieldError(frequencySelect, 'Frequency is required');
          valid = false;
        }

        if (durationInput && !durationInput.value.trim()) {
          MedApp.showFieldError(durationInput, 'Duration is required');
          valid = false;
        }
      });

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
  // Print Functionality
  // =========================================================================
  
  function initPrintButton() {
    // Print button is handled inline in template
    // But we can add custom print styles here if needed
  }

  // =========================================================================
  // Keyboard Shortcuts
  // =========================================================================
  
  function initKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
      // Ctrl/Cmd + P to print (on detail page)
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        if (document.querySelector('.prescription-detail-container')) {
          e.preventDefault();
          window.print();
        }
      }

      // Escape to clear search
      if (e.key === 'Escape') {
        const searchInput = document.getElementById('searchInput');
        if (searchInput && searchInput.value) {
          searchInput.value = '';
          performSearch('');
        }
      }
    });
  }

  // =========================================================================
  // Auto-save Draft (Create Page)
  // =========================================================================
  
  function initAutoSave() {
    const form = document.getElementById('createPrescriptionForm');
    if (!form) return;

    // Save draft to localStorage every 30 seconds
    setInterval(() => {
      const formData = new FormData(form);
      const draft = {};
      
      for (let [key, value] of formData.entries()) {
        draft[key] = value;
      }

      localStorage.setItem('prescriptionDraft', JSON.stringify(draft));
      console.log('Draft saved');
    }, 30000);
  }

  function loadDraft() {
    const form = document.getElementById('createPrescriptionForm');
    if (!form) return;

    const draftJson = localStorage.getItem('prescriptionDraft');
    if (!draftJson) return;

    try {
      const draft = JSON.parse(draftJson);
      
      // Ask user if they want to load draft
      MedApp.confirm('Load saved draft?', () => {
        // Load draft into form
        for (let key in draft) {
          const input = form.querySelector(`[name="${key}"]`);
          if (input) {
            input.value = draft[key];
          }
        }
        
        MedApp.showToast('Draft loaded', 'success');
      }, () => {
        // Clear draft if user says no
        localStorage.removeItem('prescriptionDraft');
      });
    } catch (e) {
      console.error('Error loading draft:', e);
    }
  }

  // =========================================================================
  // Initialize on Page Load
  // =========================================================================
  
  document.addEventListener('DOMContentLoaded', function() {
    initMedicationForm();
    initFilterTabs();
    initSearch();
    initCreateForm();
    initPrintButton();
    initKeyboardShortcuts();
    
    // Load draft on create page
    if (document.getElementById('createPrescriptionForm')) {
      initAutoSave();
      loadDraft();
    }

    console.log('Prescriptions module initialized');
  });

})();
