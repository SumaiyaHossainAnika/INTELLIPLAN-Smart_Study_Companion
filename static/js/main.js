// Main JavaScript file for Intelliplan
// Common functions and utilities used across the application

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize common components
    initializeTooltips();
    initializeAlerts();
    initializeTheme();
    setupGlobalEventListeners();
    initializeMobileNavigation(); // Add mobile navigation
    initializeMobile(); // Add mobile-specific features
    
    // Check for notifications permission
    requestNotificationPermission();
}

// Tooltip initialization
function initializeTooltips() {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(tooltip => {
        new bootstrap.Tooltip(tooltip);
    });
}

// Alert system
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        if (!alert.querySelector('.btn-close')) {
            setTimeout(() => {
                if (alert.parentNode) {
                    alert.remove();
                }
            }, 5000);
        }
    });
}

// Theme management
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    applyTheme(savedTheme);
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update theme toggle button if it exists
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    applyTheme(newTheme);
}

// Global event listeners
function setupGlobalEventListeners() {
    // Theme toggle
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Navigation active state
    updateActiveNavigation();
    
    // Auto-save functionality
    setupAutoSave();
    
    // Keyboard shortcuts
    setupKeyboardShortcuts();
}

// Navigation helpers
function updateActiveNavigation() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.navbar-nav .nav-link');
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
}

// Auto-save functionality
function setupAutoSave() {
    const autoSaveElements = document.querySelectorAll('[data-autosave]');
    autoSaveElements.forEach(element => {
        let timeout;
        element.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                autoSaveData(element);
            }, 2000); // Auto-save after 2 seconds of inactivity
        });
    });
}

function autoSaveData(element) {
    const endpoint = element.getAttribute('data-autosave');
    const data = {
        field: element.name || element.id,
        value: element.value
    };
    
    fetch(endpoint, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Auto-saved', 'success');
        }
    })
    .catch(error => {
        console.error('Auto-save error:', error);
    });
}

// Keyboard shortcuts
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S for save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveButton = document.querySelector('[data-save]');
            if (saveButton) {
                saveButton.click();
            }
        }
        
        // Ctrl/Cmd + / for search
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            const searchInput = document.querySelector('#searchInput');
            if (searchInput) {
                searchInput.focus();
            }
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                const modal = bootstrap.Modal.getInstance(openModal);
                if (modal) modal.hide();
            }
        }
    });
}

// Notification system
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

function showNotification(title, options = {}) {
    if ('Notification' in window && Notification.permission === 'granted') {
        const defaultOptions = {
            icon: '/static/images/logo.png',
            badge: '/static/images/logo.png',
            ...options
        };
        
        return new Notification(title, defaultOptions);
    }
}

// Toast notifications
function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = getOrCreateToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.innerHTML = `
        <div class="toast-header">
            <i class="fas fa-${getToastIcon(type)} me-2"></i>
            <strong class="me-auto">Intelliplan</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">${message}</div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, duration);
    
    // Handle manual close
    const closeBtn = toast.querySelector('.btn-close');
    closeBtn.addEventListener('click', () => {
        toast.remove();
    });
}

function getOrCreateToastContainer() {
    let container = document.getElementById('toastContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
    }
    return container;
}

function getToastIcon(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-circle',
        warning: 'exclamation-triangle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Modal helpers
function showModal(modalId, data = {}) {
    const modal = document.getElementById(modalId);
    if (modal) {
        // Populate modal with data if provided
        Object.keys(data).forEach(key => {
            const element = modal.querySelector(`[data-field="${key}"]`);
            if (element) {
                element.textContent = data[key];
            }
        });
        
        const modalInstance = new bootstrap.Modal(modal);
        modalInstance.show();
        return modalInstance;
    }
}

// Form helpers
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.reset();
        // Clear any validation messages
        const invalidElements = form.querySelectorAll('.is-invalid');
        invalidElements.forEach(el => el.classList.remove('is-invalid'));
        
        const feedbackElements = form.querySelectorAll('.invalid-feedback');
        feedbackElements.forEach(el => el.textContent = '');
    }
}

function validateForm(formId, rules) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    let isValid = true;
    
    Object.keys(rules).forEach(fieldName => {
        const field = form.querySelector(`[name="${fieldName}"]`);
        const rule = rules[fieldName];
        
        if (field) {
            const value = field.value.trim();
            let fieldValid = true;
            let errorMessage = '';
            
            // Required validation
            if (rule.required && !value) {
                fieldValid = false;
                errorMessage = rule.requiredMessage || 'This field is required';
            }
            
            // Min length validation
            if (fieldValid && rule.minLength && value.length < rule.minLength) {
                fieldValid = false;
                errorMessage = rule.minLengthMessage || `Minimum ${rule.minLength} characters required`;
            }
            
            // Pattern validation
            if (fieldValid && rule.pattern && !rule.pattern.test(value)) {
                fieldValid = false;
                errorMessage = rule.patternMessage || 'Invalid format';
            }
            
            // Custom validation
            if (fieldValid && rule.custom) {
                const customResult = rule.custom(value);
                if (customResult !== true) {
                    fieldValid = false;
                    errorMessage = customResult;
                }
            }
            
            // Update field appearance
            if (fieldValid) {
                field.classList.remove('is-invalid');
                field.classList.add('is-valid');
            } else {
                field.classList.remove('is-valid');
                field.classList.add('is-invalid');
                isValid = false;
            }
            
            // Show error message
            const feedback = field.parentNode.querySelector('.invalid-feedback');
            if (feedback) {
                feedback.textContent = errorMessage;
            }
        }
    });
    
    return isValid;
}

// API helpers
function apiRequest(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        ...options
    };
    
    return fetch(url, defaultOptions)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('API request failed:', error);
            showToast('Request failed. Please try again.', 'error');
            throw error;
        });
}

// Utility functions
function formatDate(date, format = 'short') {
    const options = {
        short: { month: 'short', day: 'numeric' },
        long: { year: 'numeric', month: 'long', day: 'numeric' },
        time: { hour: '2-digit', minute: '2-digit' },
        datetime: { 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric',
            hour: '2-digit', 
            minute: '2-digit' 
        }
    };
    
    return new Date(date).toLocaleDateString('en-US', options[format]);
}

function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}h ${minutes}m`;
    } else if (minutes > 0) {
        return `${minutes}m ${secs}s`;
    } else {
        return `${secs}s`;
    }
}

function formatFileSize(bytes) {
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    if (bytes === 0) return '0 Bytes';
    const i = Math.floor(Math.log(bytes) / Math.log(1024));
    return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
}

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

// Progress bar helper
function updateProgressBar(elementId, percentage, animated = true) {
    const progressBar = document.getElementById(elementId);
    if (progressBar) {
        progressBar.style.width = `${percentage}%`;
        progressBar.setAttribute('aria-valuenow', percentage);
        
        if (animated) {
            progressBar.classList.add('progress-bar-animated');
        }
        
        // Add color classes based on percentage
        progressBar.classList.remove('bg-danger', 'bg-warning', 'bg-success');
        if (percentage < 30) {
            progressBar.classList.add('bg-danger');
        } else if (percentage < 70) {
            progressBar.classList.add('bg-warning');
        } else {
            progressBar.classList.add('bg-success');
        }
    }
}

// Chart helpers (if using Chart.js)
function createChart(canvasId, type, data, options = {}) {
    const ctx = document.getElementById(canvasId);
    if (ctx && typeof Chart !== 'undefined') {
        return new Chart(ctx, {
            type: type,
            data: data,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                ...options
            }
        });
    }
}

// Storage helpers
function saveToLocalStorage(key, data) {
    try {
        localStorage.setItem(key, JSON.stringify(data));
        return true;
    } catch (error) {
        console.error('Failed to save to localStorage:', error);
        return false;
    }
}

function loadFromLocalStorage(key, defaultValue = null) {
    try {
        const data = localStorage.getItem(key);
        return data ? JSON.parse(data) : defaultValue;
    } catch (error) {
        console.error('Failed to load from localStorage:', error);
        return defaultValue;
    }
}

// Mobile Navigation Functions
function initializeMobileNavigation() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');
    const body = document.body;
    
    if (!hamburgerMenu || !navLinks) return;
    
    // Create mobile overlay
    const mobileOverlay = document.createElement('div');
    mobileOverlay.className = 'mobile-overlay';
    body.appendChild(mobileOverlay);
    
    // Hamburger menu click event
    hamburgerMenu.addEventListener('click', function(e) {
        e.preventDefault();
        toggleMobileMenu();
    });
    
    // Overlay click event
    mobileOverlay.addEventListener('click', function() {
        closeMobileMenu();
    });
    
    // Close menu when nav link is clicked
    const navLinkItems = navLinks.querySelectorAll('a');
    navLinkItems.forEach(link => {
        link.addEventListener('click', function() {
            // Small delay to allow navigation before closing menu
            setTimeout(() => {
                closeMobileMenu();
            }, 100);
        });
    });
    
    // Close menu on escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeMobileMenu();
        }
    });
    
    // Handle window resize
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeMobileMenu();
        }
    });
}

function toggleMobileMenu() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');
    const mobileOverlay = document.querySelector('.mobile-overlay');
    const body = document.body;
    
    if (!hamburgerMenu || !navLinks || !mobileOverlay) return;
    
    const isActive = navLinks.classList.contains('active');
    
    if (isActive) {
        closeMobileMenu();
    } else {
        openMobileMenu();
    }
}

function openMobileMenu() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');
    const mobileOverlay = document.querySelector('.mobile-overlay');
    const body = document.body;
    
    if (!hamburgerMenu || !navLinks || !mobileOverlay) return;
    
    hamburgerMenu.classList.add('active');
    navLinks.classList.add('active');
    mobileOverlay.classList.add('active');
    body.style.overflow = 'hidden'; // Prevent scrolling when menu is open
}

function closeMobileMenu() {
    const hamburgerMenu = document.querySelector('.hamburger-menu');
    const navLinks = document.querySelector('.nav-links');
    const mobileOverlay = document.querySelector('.mobile-overlay');
    const body = document.body;
    
    if (!hamburgerMenu || !navLinks || !mobileOverlay) return;
    
    hamburgerMenu.classList.remove('active');
    navLinks.classList.remove('active');
    mobileOverlay.classList.remove('active');
    body.style.overflow = ''; // Restore scrolling
}

// Mobile Touch Enhancements
function setupMobileTouchEnhancements() {
    // Only run on mobile devices
    if (window.innerWidth <= 768) {
        setupSwipeGestures();
        setupTouchFeedback();
        improveFormExperience();
    }
}

// Swipe gesture for closing mobile menu
function setupSwipeGestures() {
    let startX = null;
    let startY = null;
    
    const navLinks = document.querySelector('.nav-links');
    if (!navLinks) return;
    
    navLinks.addEventListener('touchstart', function(e) {
        startX = e.touches[0].clientX;
        startY = e.touches[0].clientY;
    });
    
    navLinks.addEventListener('touchend', function(e) {
        if (!startX || !startY) return;
        
        const endX = e.changedTouches[0].clientX;
        const endY = e.changedTouches[0].clientY;
        
        const diffX = startX - endX;
        const diffY = startY - endY;
        
        // Swipe right to close menu (when menu is open)
        if (Math.abs(diffX) > Math.abs(diffY) && diffX < -50 && navLinks.classList.contains('active')) {
            closeMobileMenu();
        }
        
        startX = null;
        startY = null;
    });
}

// Add touch feedback for buttons
function setupTouchFeedback() {
    const interactiveElements = document.querySelectorAll('button, .btn, a, input[type="submit"], input[type="button"]');
    
    interactiveElements.forEach(element => {
        element.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.98)';
            this.style.transition = 'transform 0.1s ease';
        });
        
        element.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
        
        element.addEventListener('touchcancel', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

// Improve form experience on mobile
function improveFormExperience() {
    const inputs = document.querySelectorAll('input, textarea, select');
    
    inputs.forEach(input => {
        // Prevent zoom on focus for iOS
        if (input.type !== 'file') {
            const currentFontSize = window.getComputedStyle(input).fontSize;
            if (parseInt(currentFontSize) < 16) {
                input.style.fontSize = '16px';
            }
        }
        
        // Auto-scroll to input when focused
        input.addEventListener('focus', function() {
            setTimeout(() => {
                this.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }, 300);
        });
    });
}

// Mobile-specific initialization
function initializeMobile() {
    if (window.innerWidth <= 768) {
        setupMobileTouchEnhancements();
        
        // Update on orientation change
        window.addEventListener('orientationchange', function() {
            setTimeout(() => {
                closeMobileMenu();
                setupMobileTouchEnhancements();
            }, 500);
        });
    }
}

// Export functions for use in other files
window.Intelliplan = {
    showToast,
    showNotification,
    showModal,
    resetForm,
    validateForm,
    apiRequest,
    formatDate,
    formatDuration,
    formatFileSize,
    debounce,
    throttle,
    updateProgressBar,
    createChart,
    saveToLocalStorage,
    loadFromLocalStorage,
    toggleTheme,
    applyTheme
};

// Settings Section Management
function showSection(sectionId) {
    // Hide main options
    const mainOptions = document.getElementById('main-options');
    if (mainOptions) {
        mainOptions.style.display = 'none';
    }
    
    // Hide all sections
    const allSections = document.querySelectorAll('.settings-section');
    allSections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.style.display = 'block';
    }
}

function showMainOptions() {
    // Hide all sections
    const allSections = document.querySelectorAll('.settings-section');
    allSections.forEach(section => {
        section.style.display = 'none';
    });
    
    // Show main options
    const mainOptions = document.getElementById('main-options');
    if (mainOptions) {
        mainOptions.style.display = 'flex';
    }
}

// Make functions globally available
window.showSection = showSection;
window.showMainOptions = showMainOptions;
