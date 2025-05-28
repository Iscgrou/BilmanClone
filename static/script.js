// Bilman Deployment Configuration JavaScript

class BilmanConfig {
    constructor() {
        this.init();
        this.loadInitialData();
    }

    init() {
        // Bind event listeners
        document.getElementById('configForm').addEventListener('submit', (e) => this.handleFormSubmit(e));
        document.getElementById('testBtn').addEventListener('click', () => this.testConnection());
        
        // Real-time validation
        document.getElementById('domain').addEventListener('input', () => this.validateDomain());
        document.getElementById('username').addEventListener('input', () => this.validateUsername());
        document.getElementById('password').addEventListener('input', () => this.validatePassword());
        document.getElementById('confirmPassword').addEventListener('input', () => this.validatePasswordConfirm());
        
        // Auto-refresh status and logs
        setInterval(() => this.refreshStatus(), 5000); // Every 5 seconds
        setInterval(() => this.refreshLogs(), 10000); // Every 10 seconds
    }

    async loadInitialData() {
        await this.refreshStatus();
        await this.refreshLogs();
        await this.loadExistingConfig();
    }

    async loadExistingConfig() {
        try {
            const response = await fetch('/api/config');
            const data = await response.json();
            
            if (data.success && data.config) {
                // Populate form with existing config (except password)
                if (data.config.domain) {
                    document.getElementById('domain').value = data.config.domain;
                }
                if (data.config.username) {
                    document.getElementById('username').value = data.config.username;
                }
                
                this.showAlert('info', 'Existing configuration loaded');
                this.updateProgressStep(4, 'completed');
            }
        } catch (error) {
            console.error('Failed to load existing config:', error);
        }
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        // Validate form
        if (!this.validateForm()) {
            return;
        }
        
        const formData = this.getFormData();
        const saveBtn = document.getElementById('saveBtn');
        
        // Show loading state
        saveBtn.disabled = true;
        saveBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Saving...';
        
        try {
            const response = await fetch('/api/config', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('success', 'Configuration saved successfully!');
                this.updateProgressStep(4, 'completed');
                this.updateProgressStep(5, 'active');
                
                // Clear password fields for security
                document.getElementById('password').value = '';
                document.getElementById('confirmPassword').value = '';
            } else {
                this.showAlert('danger', data.error || 'Failed to save configuration');
            }
        } catch (error) {
            this.showAlert('danger', 'Network error: ' + error.message);
        } finally {
            // Reset button state
            saveBtn.disabled = false;
            saveBtn.innerHTML = '<i class="fas fa-save"></i> Save Configuration';
        }
    }

    async testConnection() {
        const formData = this.getFormData();
        const testBtn = document.getElementById('testBtn');
        
        // Validate required fields
        if (!formData.domain || !formData.username || !formData.password) {
            this.showAlert('warning', 'Please fill in all fields before testing');
            return;
        }
        
        // Show loading state
        testBtn.disabled = true;
        testBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Testing...';
        
        try {
            const response = await fetch('/api/test-connection', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showAlert('success', 'Connection test successful!');
            } else {
                this.showAlert('danger', data.error || 'Connection test failed');
            }
        } catch (error) {
            this.showAlert('danger', 'Network error: ' + error.message);
        } finally {
            // Reset button state
            testBtn.disabled = false;
            testBtn.innerHTML = '<i class="fas fa-plug"></i> Test Connection';
        }
    }

    async refreshStatus() {
        try {
            const response = await fetch('/api/status');
            const data = await response.json();
            
            if (data.success) {
                this.updateStatusDisplay(data.status);
                this.updateProgressSteps(data.status);
            }
        } catch (error) {
            console.error('Failed to refresh status:', error);
        }
    }

    async refreshLogs() {
        try {
            const response = await fetch('/api/logs');
            const data = await response.json();
            
            if (data.success) {
                this.updateLogsDisplay(data.logs);
            }
        } catch (error) {
            console.error('Failed to refresh logs:', error);
        }
    }

    updateStatusDisplay(status) {
        const container = document.getElementById('statusContent');
        
        let html = '<div class="row">';
        
        // Bilman Directory Status
        html += '<div class="col-md-6 mb-3">';
        html += '<div class="status-indicator ' + (status.bilman_directory_exists ? 'success' : 'error') + '">';
        html += '<i class="fas fa-' + (status.bilman_directory_exists ? 'check-circle' : 'times-circle') + '"></i>';
        html += 'Bilman Directory';
        html += '</div>';
        html += '</div>';
        
        // Config Files Status
        html += '<div class="col-md-6 mb-3">';
        html += '<div class="status-indicator ' + (status.config_files_exist ? 'success' : 'warning') + '">';
        html += '<i class="fas fa-' + (status.config_files_exist ? 'check-circle' : 'exclamation-triangle') + '"></i>';
        html += 'Configuration Files';
        html += '</div>';
        html += '</div>';
        
        // Deployment Log Status
        html += '<div class="col-md-6 mb-3">';
        html += '<div class="status-indicator ' + (status.deployment_log_exists ? 'success' : 'warning') + '">';
        html += '<i class="fas fa-' + (status.deployment_log_exists ? 'check-circle' : 'exclamation-triangle') + '"></i>';
        html += 'Deployment Log';
        html += '</div>';
        html += '</div>';
        
        // Analysis Report Status
        html += '<div class="col-md-6 mb-3">';
        html += '<div class="status-indicator ' + (status.analysis_report_exists ? 'success' : 'warning') + '">';
        html += '<i class="fas fa-' + (status.analysis_report_exists ? 'check-circle' : 'exclamation-triangle') + '"></i>';
        html += 'Analysis Report';
        html += '</div>';
        html += '</div>';
        
        html += '</div>';
        
        // Add analysis summary if available
        if (status.analysis_report) {
            html += '<div class="mt-3">';
            html += '<h6><i class="fas fa-chart-bar"></i> Project Analysis Summary</h6>';
            html += '<div class="row">';
            html += '<div class="col-md-4">';
            html += '<small class="text-muted">Project Type:</small><br>';
            html += '<strong>' + (status.analysis_report.project_type?.primary || 'Unknown') + '</strong>';
            html += '</div>';
            html += '<div class="col-md-4">';
            html += '<small class="text-muted">Total Files:</small><br>';
            html += '<strong>' + (status.analysis_report.structure?.total_files || 0) + '</strong>';
            html += '</div>';
            html += '<div class="col-md-4">';
            html += '<small class="text-muted">Issues Found:</small><br>';
            html += '<strong>' + (status.analysis_report.potential_issues?.length || 0) + '</strong>';
            html += '</div>';
            html += '</div>';
            html += '</div>';
        }
        
        container.innerHTML = html;
    }

    updateProgressSteps(status) {
        // Update progress based on status
        if (status.bilman_directory_exists) {
            this.updateProgressStep(1, 'completed');
        }
        
        if (status.analysis_report_exists) {
            this.updateProgressStep(2, 'completed');
            this.updateProgressStep(3, 'completed');
        }
        
        if (status.config_files_exist) {
            this.updateProgressStep(4, 'completed');
        }
        
        // Set current active step
        if (!status.bilman_directory_exists) {
            this.updateProgressStep(1, 'active');
        } else if (!status.analysis_report_exists) {
            this.updateProgressStep(2, 'active');
        } else if (!status.config_files_exist) {
            this.updateProgressStep(4, 'active');
        } else {
            this.updateProgressStep(5, 'active');
        }
    }

    updateProgressStep(stepNumber, status) {
        const step = document.getElementById(`step${stepNumber}`);
        if (step) {
            step.className = 'progress-step ' + status;
        }
    }

    updateLogsDisplay(logs) {
        const container = document.getElementById('logsContent');
        
        if (!logs || logs.length === 0) {
            container.innerHTML = `
                <div class="text-center">
                    <i class="fas fa-file-alt fa-2x text-muted"></i>
                    <p class="text-muted">No logs available</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        logs.forEach(log => {
            const logClass = this.getLogClass(log);
            html += `<div class="log-entry ${logClass}">${this.escapeHtml(log.trim())}</div>`;
        });
        
        container.innerHTML = html;
        container.scrollTop = container.scrollHeight; // Auto-scroll to bottom
    }

    getLogClass(logEntry) {
        const lower = logEntry.toLowerCase();
        if (lower.includes('error') || lower.includes('failed')) {
            return 'error';
        } else if (lower.includes('warning') || lower.includes('warn')) {
            return 'warning';
        } else if (lower.includes('info') || lower.includes('starting')) {
            return 'info';
        }
        return '';
    }

    validateForm() {
        let isValid = true;
        
        isValid = this.validateDomain() && isValid;
        isValid = this.validateUsername() && isValid;
        isValid = this.validatePassword() && isValid;
        isValid = this.validatePasswordConfirm() && isValid;
        
        return isValid;
    }

    validateDomain() {
        const domain = document.getElementById('domain').value.trim();
        const domainPattern = /^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$/;
        
        return this.validateField('domain', domainPattern.test(domain), 'Please enter a valid domain (e.g., example.com)');
    }

    validateUsername() {
        const username = document.getElementById('username').value.trim();
        const usernamePattern = /^[a-zA-Z0-9_]{3,20}$/;
        
        return this.validateField('username', usernamePattern.test(username), 'Username must be 3-20 characters, alphanumeric and underscores only');
    }

    validatePassword() {
        const password = document.getElementById('password').value;
        
        return this.validateField('password', password.length >= 8, 'Password must be at least 8 characters long');
    }

    validatePasswordConfirm() {
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;
        
        return this.validateField('confirmPassword', password === confirmPassword, 'Passwords do not match');
    }

    validateField(fieldId, isValid, errorMessage) {
        const field = document.getElementById(fieldId);
        const feedback = field.parentElement.querySelector('.invalid-feedback') || 
                        this.createFeedbackElement(field.parentElement);
        
        if (isValid) {
            field.classList.remove('is-invalid');
            field.classList.add('is-valid');
            feedback.style.display = 'none';
        } else {
            field.classList.remove('is-valid');
            field.classList.add('is-invalid');
            feedback.textContent = errorMessage;
            feedback.style.display = 'block';
        }
        
        return isValid;
    }

    createFeedbackElement(parent) {
        const feedback = document.createElement('div');
        feedback.className = 'invalid-feedback';
        parent.appendChild(feedback);
        return feedback;
    }

    getFormData() {
        return {
            domain: document.getElementById('domain').value.trim(),
            username: document.getElementById('username').value.trim(),
            password: document.getElementById('password').value
        };
    }

    showAlert(type, message) {
        const alertContainer = document.getElementById('alertContainer');
        const alertId = 'alert-' + Date.now();
        
        const alertHtml = `
            <div class="alert alert-${type} alert-dismissible fade show fade-in" id="${alertId}" role="alert">
                <i class="fas fa-${this.getAlertIcon(type)}"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        `;
        
        alertContainer.insertAdjacentHTML('beforeend', alertHtml);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            const alert = document.getElementById(alertId);
            if (alert) {
                alert.remove();
            }
        }, 5000);
    }

    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            danger: 'exclamation-triangle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new BilmanConfig();
});
