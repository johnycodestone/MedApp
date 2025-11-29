// ========================================
// ADMIN PANEL JAVASCRIPT
// ========================================

// Global admin utilities
const AdminPanel = {
  // Make AJAX requests
  ajax: async function(url, method = 'GET', data = null) {
    const options = {
      method: method,
      headers: {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
      }
    };

    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
      options.headers['X-CSRFToken'] = csrfToken.value;
    }

    if (data && method !== 'GET') {
      options.body = JSON.stringify(data);
    }

    try {
      const response = await fetch(url, options);
      return await response.json();
    } catch (error) {
      console.error('AJAX Error:', error);
      throw error;
    }
  },

  // Show toast notification
  showToast: function(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
      color: white;
      border-radius: 0.5rem;
      box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
      z-index: 9999;
      animation: slideIn 0.3s ease;
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3000);
  },

  // Debounce function
  debounce: function(func, wait) {
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
};

// ========================================
// DASHBOARD INITIALIZATION
// ========================================
function initDashboard() {
  console.log('Initializing dashboard...');
  
  // Load user statistics
  loadUserStats();
  
  // Initialize charts
  initCharts();
  
  // Setup sidebar toggle
  setupSidebarToggle();
  
  // Setup quick actions
  setupQuickActions();
}

// ========================================
// USER STATISTICS
// ========================================
async function loadUserStats() {
  try {
    const response = await AdminPanel.ajax('/adminpanel/api/system/user-stats/');
    console.log('User stats loaded:', response);
    // Update dashboard stats if needed
  } catch (error) {
    console.error('Failed to load user stats:', error);
  }
}

// ========================================
// CHARTS INITIALIZATION
// ========================================
function initCharts() {
  // Check if Chart.js is loaded
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js not loaded');
    return;
  }

  // User Growth Chart
  const userGrowthCanvas = document.getElementById('userGrowthChart');
  if (userGrowthCanvas) {
    const ctx = userGrowthCanvas.getContext('2d');
    
    // Sample data - replace with actual data from API
    const dates = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    }
    
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: dates,
        datasets: [{
          label: 'New Users',
          data: [12, 19, 15, 25, 22, 30, 28],
          borderColor: '#2563eb',
          backgroundColor: 'rgba(37, 99, 235, 0.1)',
          tension: 0.4,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            display: false
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0
            }
          }
        }
      }
    });
  }

  // User Distribution Chart
  const userDistCanvas = document.getElementById('userDistributionChart');
  if (userDistCanvas) {
    const ctx = userDistCanvas.getContext('2d');
    
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Patients', 'Doctors', 'Hospitals', 'Admins'],
        datasets: [{
          data: [45, 30, 20, 5],
          backgroundColor: [
            '#3b82f6',
            '#10b981',
            '#f59e0b',
            '#ef4444'
          ]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom'
          }
        }
      }
    });
  }
}

// ========================================
// SIDEBAR TOGGLE
// ========================================
function setupSidebarToggle() {
  const toggle = document.getElementById('sidebarToggle');
  const sidebar = document.getElementById('adminSidebar');
  
  if (toggle && sidebar) {
    toggle.addEventListener('click', () => {
      sidebar.classList.toggle('active');
    });

    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
      if (window.innerWidth <= 1024) {
        if (!sidebar.contains(e.target) && !toggle.contains(e.target)) {
          sidebar.classList.remove('active');
        }
      }
    });
  }
}

// ========================================
// QUICK ACTIONS
// ========================================
function setupQuickActions() {
  // Create Backup
  const createBackupBtn = document.querySelector('[data-action="create-backup"]');
  if (createBackupBtn) {
    createBackupBtn.addEventListener('click', createBackup);
  }

  // View Audit Logs
  const viewAuditBtn = document.querySelector('[data-action="view-audit"]');
  if (viewAuditBtn) {
    viewAuditBtn.addEventListener('click', () => {
      window.location.href = '/adminpanel/audit/';
    });
  }

  // Manage Configs
  const manageConfigsBtn = document.querySelector('[data-action="manage-configs"]');
  if (manageConfigsBtn) {
    manageConfigsBtn.addEventListener('click', () => {
      window.location.href = '/adminpanel/configs/';
    });
  }

  // Export Data
  const exportDataBtn = document.querySelector('[data-action="export-data"]');
  if (exportDataBtn) {
    exportDataBtn.addEventListener('click', exportData);
  }
}

// ========================================
// TABLE UTILITIES
// ========================================
function initDataTable(tableId) {
  const table = document.getElementById(tableId);
  if (!table) return;

  // Add search functionality
  const searchInput = table.closest('.table-card').querySelector('.table-search');
  if (searchInput) {
    searchInput.addEventListener('input', AdminPanel.debounce((e) => {
      filterTable(table, e.target.value);
    }, 300));
  }
}

function filterTable(table, searchTerm) {
  const rows = table.querySelectorAll('tbody tr');
  const term = searchTerm.toLowerCase();

  rows.forEach(row => {
    const text = row.textContent.toLowerCase();
    row.style.display = text.includes(term) ? '' : 'none';
  });
}

// ========================================
// USER MANAGEMENT
// ========================================
function toggleUserStatus(userId) {
  AdminPanel.ajax(`/adminpanel/api/users/${userId}/toggle-status/`, 'POST')
    .then(response => {
      AdminPanel.showToast('User status updated', 'success');
      location.reload();
    })
    .catch(error => {
      AdminPanel.showToast('Failed to update user status', 'error');
    });
}

function deleteUser(userId) {
  if (!confirm('Are you sure you want to delete this user?')) return;

  AdminPanel.ajax(`/adminpanel/api/users/${userId}/`, 'DELETE')
    .then(response => {
      AdminPanel.showToast('User deleted successfully', 'success');
      location.reload();
    })
    .catch(error => {
      AdminPanel.showToast('Failed to delete user', 'error');
    });
}

// ========================================
// BACKUP MANAGEMENT
// ========================================
function initiateBackup(backupType = 'database') {
  const button = event.target;
  button.disabled = true;
  button.textContent = 'Creating backup...';

  AdminPanel.ajax('/adminpanel/api/backups/initiate/', 'POST', { type: backupType })
    .then(response => {
      AdminPanel.showToast('Backup initiated successfully', 'success');
      setTimeout(() => location.reload(), 2000);
    })
    .catch(error => {
      AdminPanel.showToast('Failed to initiate backup', 'error');
      button.disabled = false;
      button.textContent = 'Create Backup';
    });
}

function createBackup() {
  initiateBackup('database');
}

// ========================================
// CONFIGURATION MANAGEMENT
// ========================================
function updateConfig(configId, newValue) {
  AdminPanel.ajax(`/adminpanel/api/configs/${configId}/`, 'PATCH', { value: newValue })
    .then(response => {
      AdminPanel.showToast('Configuration updated', 'success');
    })
    .catch(error => {
      AdminPanel.showToast('Failed to update configuration', 'error');
    });
}

function toggleConfig(configId) {
  AdminPanel.ajax(`/adminpanel/api/configs/${configId}/toggle/`, 'POST')
    .then(response => {
      AdminPanel.showToast('Configuration toggled', 'success');
    })
    .catch(error => {
      AdminPanel.showToast('Failed to toggle configuration', 'error');
    });
}

// ========================================
// CATEGORY TABS
// ========================================
function setupCategoryTabs() {
  const tabs = document.querySelectorAll('.category-tab');
  
  tabs.forEach(tab => {
    tab.addEventListener('click', function() {
      // Remove active class from all tabs
      tabs.forEach(t => t.classList.remove('active'));
      
      // Add active class to clicked tab
      this.classList.add('active');
      
      // Filter items based on category
      const category = this.dataset.category;
      filterByCategory(category);
    });
  });
}

function filterByCategory(category) {
  const items = document.querySelectorAll('[data-category]');
  
  items.forEach(item => {
    if (category === 'all' || item.dataset.category === category) {
      item.style.display = '';
    } else {
      item.style.display = 'none';
    }
  });
}

// ========================================
// LOG ENTRY EXPANSION
// ========================================
function setupLogExpansion() {
  const logEntries = document.querySelectorAll('.log-entry');
  
  logEntries.forEach(entry => {
    entry.addEventListener('click', function() {
      this.classList.toggle('expanded');
    });
  });
}

// ========================================
// MODAL UTILITIES
// ========================================
function showModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

function hideModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}

// Close modal when clicking outside
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
});

// ========================================
// EXPORT FUNCTIONALITY
// ========================================
function exportData() {
  AdminPanel.showToast('Exporting data...', 'info');
  
  // Implement actual export logic here
  setTimeout(() => {
    AdminPanel.showToast('Data exported successfully', 'success');
  }, 2000);
}

function exportTable(tableId, filename = 'export.csv') {
  const table = document.getElementById(tableId);
  if (!table) return;

  let csv = [];
  const rows = table.querySelectorAll('tr');

  rows.forEach(row => {
    const cols = row.querySelectorAll('td, th');
    const rowData = [];
    cols.forEach(col => rowData.push(col.textContent));
    csv.push(rowData.join(','));
  });

  const csvContent = csv.join('\n');
  const blob = new Blob([csvContent], { type: 'text/csv' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  window.URL.revokeObjectURL(url);
}

// ========================================
// SEARCH FUNCTIONALITY
// ========================================
function setupSearch() {
  const searchInputs = document.querySelectorAll('[data-search]');
  
  searchInputs.forEach(input => {
    input.addEventListener('input', AdminPanel.debounce((e) => {
      const target = e.target.dataset.search;
      const term = e.target.value.toLowerCase();
      const items = document.querySelectorAll(`[data-searchable="${target}"]`);
      
      items.forEach(item => {
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(term) ? '' : 'none';
      });
    }, 300));
  });
}

// ========================================
// AUTO-REFRESH
// ========================================
function setupAutoRefresh() {
  const toggle = document.getElementById('autoRefreshToggle');
  if (!toggle) return;

  let interval = null;

  toggle.addEventListener('change', function() {
    if (this.checked) {
      interval = setInterval(() => {
        location.reload();
      }, 5000);
      AdminPanel.showToast('Auto-refresh enabled', 'info');
    } else {
      clearInterval(interval);
      AdminPanel.showToast('Auto-refresh disabled', 'info');
    }
  });
}

// ========================================
// FORM VALIDATION
// ========================================
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return false;

  const requiredFields = form.querySelectorAll('[required]');
  let isValid = true;

  requiredFields.forEach(field => {
    if (!field.value.trim()) {
      field.classList.add('error');
      isValid = false;
    } else {
      field.classList.remove('error');
    }
  });

  return isValid;
}

// ========================================
// INITIALIZE ON DOM LOAD
// ========================================
document.addEventListener('DOMContentLoaded', function() {
  console.log('Admin Panel JS loaded');

  // Check if we're on dashboard
  if (document.getElementById('userGrowthChart')) {
    initDashboard();
  }

  // Setup category tabs
  if (document.querySelector('.category-tab')) {
    setupCategoryTabs();
  }

  // Setup log expansion
  if (document.querySelector('.log-entry')) {
    setupLogExpansion();
  }

  // Setup search
  setupSearch();

  // Setup auto-refresh
  setupAutoRefresh();

  // Setup sidebar toggle
  setupSidebarToggle();
});

// ========================================
// CSS ANIMATIONS
// ========================================
const style = document.createElement('style');
style.textContent = `
  @keyframes slideIn {
    from {
      transform: translateX(100%);
      opacity: 0;
    }
    to {
      transform: translateX(0);
      opacity: 1;
    }
  }

  @keyframes slideOut {
    from {
      transform: translateX(0);
      opacity: 1;
    }
    to {
      transform: translateX(100%);
      opacity: 0;
    }
  }
`;
document.head.appendChild(style);

// Export for global use
window.AdminPanel = AdminPanel;
