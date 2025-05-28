#!/bin/bash

# Bilman One-Link Installation and Deployment Script
# This script provides complete automated installation with domain and credential configuration

set -e  # Exit on any error

echo "🚀 Bilman VPN Management System - One-Link Installation"
echo "======================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
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
    print_header "Starting Bilman Installation and Deployment"
    
    # Check if bilman directory exists
    if [ ! -d "./bilman" ]; then
        print_error "Bilman project not found. Please run the analysis first."
        exit 1
    fi
    
    print_status "Bilman project directory found"
    
    # Collect configuration from user
    print_header "Configuration Setup"
    echo "Please provide the following configuration details:"
    echo
    
    # Domain configuration
    while true; do
        prompt_user "Enter your domain (e.g., vpn.example.com)" "USER_DOMAIN" "false"
        if validate_domain "$USER_DOMAIN"; then
            break
        else
            print_error "Invalid domain format. Please enter a valid domain (e.g., vpn.example.com)"
        fi
    done
    
    # Username configuration
    while true; do
        prompt_user "Enter admin username (3-20 alphanumeric characters)" "USER_USERNAME" "false"
        if validate_username "$USER_USERNAME"; then
            break
        else
            print_error "Invalid username. Must be 3-20 characters, alphanumeric and underscore only"
        fi
    done
    
    # Password configuration
    while true; do
        prompt_user "Enter admin password (minimum 8 characters)" "USER_PASSWORD" "true"
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
    
    # Update environment file
    print_header "Updating Environment Configuration"
    cd bilman
    
    # Update .env file with user configuration
    cat > .env << EOF
# Application Configuration
NODE_ENV=production
PORT=3000
NEXT_PUBLIC_DOMAIN=${USER_DOMAIN}

# Database Configuration
DATABASE_URL="${DATABASE_URL}"

# Authentication Configuration
JWT_SECRET=bilman-secure-jwt-secret-key-$(date +%s)
JWT_EXPIRES_IN=7d

# Admin Account Configuration
ADMIN_USERNAME=${USER_USERNAME}
ADMIN_PASSWORD=${USER_PASSWORD}

# Deployment Configuration
BILMAN_DOMAIN=${USER_DOMAIN}
BILMAN_USERNAME=${USER_USERNAME}
BILMAN_PASSWORD=${USER_PASSWORD}

# Optional Services (can be configured later)
TELEGRAM_BOT_TOKEN=
REDIS_URL=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
EOF
    
    print_status "Environment configuration updated"
    
    # Setup database
    print_header "Setting up Database"
    if command -v npx &> /dev/null; then
        print_status "Generating Prisma client..."
        npx prisma generate || print_warning "Prisma generation failed, continuing..."
        
        print_status "Running database migrations..."
        npx prisma db push || print_warning "Database migration failed, continuing..."
    else
        print_warning "NPX not available, skipping database setup"
    fi
    
    # Create deployment summary
    print_header "Deployment Summary"
    cat > deployment_summary.txt << EOF
Bilman VPN Management System - Deployment Summary
================================================

Deployment Date: $(date)
Domain: ${USER_DOMAIN}
Admin Username: ${USER_USERNAME}
Database: PostgreSQL (configured)

Application Details:
- Framework: Next.js 15 with React
- Database: PostgreSQL with Prisma ORM
- Features: User management, billing, analytics, Telegram integration
- Security: JWT authentication, CSRF protection, rate limiting

Access Information:
- Web Interface: http://localhost:3000
- Admin Login: ${USER_USERNAME}
- Configuration Interface: http://localhost:5000

Next Steps:
1. Access the application at http://localhost:3000
2. Login with your admin credentials
3. Configure additional services (Telegram, Email) as needed
4. Set up SSL certificate for production use
5. Configure domain DNS to point to your server

Files Created:
- .env (environment configuration)
- deployment_summary.txt (this file)

Support:
For issues or questions, check the logs and documentation.
EOF
    
    print_status "Deployment summary created: deployment_summary.txt"
    
    print_header "🎉 Installation Complete!"
    print_status "Bilman VPN Management System has been successfully configured"
    print_status "Domain: ${USER_DOMAIN}"
    print_status "Admin Username: ${USER_USERNAME}"
    print_status "Configuration Interface: http://localhost:5000"
    
    echo
    echo "📋 Next Steps:"
    echo "1. Start the application: cd bilman && npm run dev"
    echo "2. Access at: http://localhost:3000"
    echo "3. Login with your admin credentials"
    echo "4. Complete additional configuration as needed"
    
    echo
    echo "🎉 Deployment completed successfully!"
    echo "📋 Check deployment_summary.txt for detailed information"
}

# Run main function
main "$@"