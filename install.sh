#!/bin/bash

# Bilman One-Link Installation Script
# This script provides automated installation with domain and credential configuration

set -e  # Exit on any error

echo "🚀 Bilman One-Link Installation"
echo "==============================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Function to prompt for user input
prompt_user() {
    local prompt="$1"
    local var_name="$2"
    local is_password="$3"
    
    if [ "$is_password" = "true" ]; then
        echo -n "$prompt: "
        read -s user_input
        echo  # New line after password input
    else
        echo -n "$prompt: "
        read user_input
    fi
    
    export $var_name="$user_input"
}

# Function to validate domain format
validate_domain() {
    local domain="$1"
    if [[ $domain =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate username
validate_username() {
    local username="$1"
    if [[ $username =~ ^[a-zA-Z0-9_]{3,20}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Function to validate password strength
validate_password() {
    local password="$1"
    if [[ ${#password} -ge 8 ]]; then
        return 0
    else
        return 1
    fi
}

# Main installation function
main() {
    print_header "Starting Bilman Installation Process"
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check if Git is available
    if ! command -v git &> /dev/null; then
        print_error "Git is required but not installed"
        exit 1
    fi
    
    print_status "Prerequisites check passed"
    
    # Collect configuration from user
    print_header "Configuration Setup"
    echo "Please provide the following configuration details:"
    echo
    
    # Domain configuration
    while true; do
        prompt_user "Enter your domain (e.g., example.com)" "USER_DOMAIN" "false"
        if validate_domain "$USER_DOMAIN"; then
            break
        else
            print_error "Invalid domain format. Please enter a valid domain (e.g., example.com)"
        fi
    done
    
    # Username configuration
    while true; do
        prompt_user "Enter username (3-20 alphanumeric characters)" "USER_USERNAME" "false"
        if validate_username "$USER_USERNAME"; then
            break
        else
            print_error "Invalid username. Must be 3-20 characters, alphanumeric and underscore only"
        fi
    done
    
    # Password configuration
    while true; do
        prompt_user "Enter password (minimum 8 characters)" "USER_PASSWORD" "true"
        if validate_password "$USER_PASSWORD"; then
            prompt_user "Confirm password" "CONFIRM_PASSWORD" "true"
            if [ "$USER_PASSWORD" = "$CONFIRM_PASSWORD" ]; then
                break
            else
                print_error "Passwords do not match. Please try again."
            fi
        else
            print_error "Password must be at least 8 characters long"
        fi
    done
    
    print_status "Configuration collected successfully"
    
    # Export configuration as environment variables
    export BILMAN_DOMAIN="$USER_DOMAIN"
    export BILMAN_USERNAME="$USER_USERNAME"
    export BILMAN_PASSWORD="$USER_PASSWORD"
    
    # Save configuration to file for Python script
    cat > config.env << EOF
BILMAN_DOMAIN=$USER_DOMAIN
BILMAN_USERNAME=$USER_USERNAME
BILMAN_PASSWORD=$USER_PASSWORD
EOF
    
    print_status "Configuration saved to config.env"
    
    # Install Python dependencies if requirements exist
    if [ -f "requirements.txt" ]; then
        print_header "Installing Python Dependencies"
        pip install -r requirements.txt || {
            print_warning "Failed to install some dependencies, continuing..."
        }
    fi
    
    # Run the deployment script
    print_header "Running Deployment Process"
    python3 deploy.py || {
        print_error "Deployment script failed"
        exit 1
    }
    
    # Start the web interface for final configuration
    print_header "Starting Configuration Web Interface"
    python3 web_interface.py &
    WEB_PID=$!
    
    print_status "Web interface started on http://localhost:5000"
    print_status "Complete the configuration in your browser"
    
    # Wait for user to complete web configuration
    echo
    echo "Press Enter after completing web configuration to continue..."
    read
    
    # Stop web interface
    kill $WEB_PID 2>/dev/null || true
    
    print_header "Installation Complete"
    print_status "Bilman has been successfully installed and configured"
    print_status "Domain: $USER_DOMAIN"
    print_status "Username: $USER_USERNAME"
    print_status "Check deployment_report.json for detailed information"
    
    # Clean up sensitive files
    rm -f config.env
    
    echo
    echo "🎉 Installation completed successfully!"
    echo "📋 Check the deployment logs for any additional information"
}

# Trap to clean up on exit
trap 'print_warning "Installation interrupted"; exit 1' INT TERM

# Run main function
main "$@"
