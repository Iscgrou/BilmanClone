#!/bin/bash

# Bilman One-Link Installation Script
# Complete automated installation with domain and credential configuration
# Usage: curl -sSL https://your-repo.com/install.sh | bash

set -e

echo "🚀 Bilman VPN Management System - One-Link Installation"
echo "======================================================="

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}[STEP]${NC} $1"; }

prompt_user() {
    local prompt="$1"
    local var_name="$2"
    local is_password="$3"
    
    if [ "$is_password" = "true" ]; then
        echo -n "$prompt: "
        read -s user_input
        echo
    else
        echo -n "$prompt: "
        read user_input
    fi
    export $var_name="$user_input"
}

validate_domain() {
    [[ $1 =~ ^[a-zA-Z0-9][a-zA-Z0-9-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]
}

validate_username() {
    [[ $1 =~ ^[a-zA-Z0-9_]{3,20}$ ]]
}

validate_password() {
    [[ ${#1} -ge 8 ]]
}

main() {
    print_header "Checking Prerequisites"
    
    # Check for required tools
    for cmd in git node npm python3; do
        if ! command -v $cmd &> /dev/null; then
            print_error "$cmd is required but not installed"
            exit 1
        fi
    done
    print_status "All prerequisites found"
    
    # Clone repository if not exists
    if [ ! -d "bilman" ]; then
        print_header "Cloning Bilman Repository"
        git clone https://github.com/Iscgrou/bilman.git
        print_status "Repository cloned successfully"
    else
        print_status "Bilman repository already exists"
    fi
    
    # Install Node.js dependencies
    print_header "Installing Dependencies"
    cd bilman
    npm install
    print_status "Dependencies installed"
    
    # Configuration setup
    print_header "Configuration Setup"
    echo "Please provide your deployment configuration:"
    echo
    
    # Domain configuration
    while true; do
        prompt_user "Enter your domain (e.g., vpn.example.com)" "USER_DOMAIN" "false"
        if validate_domain "$USER_DOMAIN"; then
            break
        else
            print_error "Invalid domain format"
        fi
    done
    
    # Username configuration  
    while true; do
        prompt_user "Enter admin username (3-20 characters)" "USER_USERNAME" "false"
        if validate_username "$USER_USERNAME"; then
            break
        else
            print_error "Invalid username format"
        fi
    done
    
    # Password configuration
    while true; do
        prompt_user "Enter admin password (min 8 characters)" "USER_PASSWORD" "true"
        if validate_password "$USER_PASSWORD"; then
            prompt_user "Confirm password" "CONFIRM_PASSWORD" "true"
            if [ "$USER_PASSWORD" = "$CONFIRM_PASSWORD" ]; then
                break
            else
                print_error "Passwords do not match"
            fi
        else
            print_error "Password too short"
        fi
    done
    
    print_status "Configuration collected"
    
    # Create environment file
    print_header "Setting up Environment"
    cat > .env << EOF
NODE_ENV=production
PORT=3000
NEXT_PUBLIC_DOMAIN=${USER_DOMAIN}

# Database (PostgreSQL required)
DATABASE_URL="postgresql://localhost:5432/bilman"

# Authentication
JWT_SECRET=bilman-jwt-secret-$(date +%s)
JWT_EXPIRES_IN=7d

# Admin Account
ADMIN_USERNAME=${USER_USERNAME}
ADMIN_PASSWORD=${USER_PASSWORD}

# Deployment Info
BILMAN_DOMAIN=${USER_DOMAIN}
BILMAN_USERNAME=${USER_USERNAME}
BILMAN_PASSWORD=${USER_PASSWORD}
DEPLOYMENT_DATE=$(date)

# Optional Services
TELEGRAM_BOT_TOKEN=
REDIS_URL=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
EOF
    
    print_status "Environment configured"
    
    # Setup database if available
    print_header "Database Setup"
    if command -v npx &> /dev/null; then
        npx prisma generate 2>/dev/null || print_warning "Prisma setup pending"
        npx prisma db push 2>/dev/null || print_warning "Database connection needed"
    fi
    
    # Create deployment summary
    cat > DEPLOYMENT_INFO.md << EOF
# Bilman VPN Management System - Deployment Complete

## Configuration
- **Domain**: ${USER_DOMAIN}
- **Admin Username**: ${USER_USERNAME}
- **Deployment Date**: $(date)

## Access
- **Application**: http://localhost:3000
- **Admin Panel**: Login with your credentials
- **Configuration**: Available in web interface

## Next Steps
1. Start the application: \`npm run dev\`
2. Access at: http://localhost:3000
3. Login with admin credentials
4. Configure additional services as needed

## Features Available
- User Management & Authentication
- VPN Service Management  
- Billing & Payment Tracking
- Analytics Dashboard
- Telegram Integration (configurable)
- Multi-language Support

## Support
Check application logs and documentation for troubleshooting.
EOF
    
    print_header "🎉 Installation Complete!"
    print_status "Bilman VPN Management System configured successfully"
    print_status "Domain: ${USER_DOMAIN}"
    print_status "Admin: ${USER_USERNAME}"
    
    echo
    echo "📋 Quick Start:"
    echo "  cd bilman"
    echo "  npm run dev"
    echo "  Open: http://localhost:3000"
    echo
    echo "🎉 Ready to deploy! Check DEPLOYMENT_INFO.md for details."
}

main "$@"