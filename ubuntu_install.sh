#!/bin/bash

# Bilman VPN Management System - Ubuntu 22 VPS One-Link Installation
# Complete automated installation with all dependencies and requirements
# Usage: curl -sSL https://raw.githubusercontent.com/your-repo/bilman-deploy/main/ubuntu_install.sh | bash

set -e

echo "🚀 Bilman VPN Management System - Ubuntu 22 VPS Installation"
echo "============================================================="
echo "This script will install and configure everything needed for your VPN management system"
echo

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }
print_header() { echo -e "${BLUE}[STEP]${NC} $1"; }
print_info() { echo -e "${PURPLE}[INFO]${NC} $1"; }

# Function to prompt for user input with validation
prompt_user() {
    local prompt="$1"
    local var_name="$2"
    local is_password="$3"
    local validation_func="$4"
    
    while true; do
        if [ "$is_password" = "true" ]; then
            echo -n "$prompt: "
            read -s user_input
            echo
        else
            echo -n "$prompt: "
            read user_input
        fi
        
        if [ -n "$validation_func" ]; then
            if $validation_func "$user_input"; then
                break
            else
                print_error "Invalid input. Please try again."
                continue
            fi
        else
            break
        fi
    done
    
    export $var_name="$user_input"
}

# Validation functions
validate_domain() {
    local domain="$1"
    if [[ $domain =~ ^[a-zA-Z0-9][a-zA-Z0-9.-]{1,61}[a-zA-Z0-9]\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        print_error "Domain must be valid format (e.g., vpn.example.com)"
        return 1
    fi
}

validate_username() {
    local username="$1"
    if [[ $username =~ ^[a-zA-Z0-9_]{3,20}$ ]]; then
        return 0
    else
        print_error "Username must be 3-20 characters, alphanumeric and underscore only"
        return 1
    fi
}

validate_password() {
    local password="$1"
    if [[ ${#password} -ge 8 ]]; then
        if [[ $password =~ [A-Z] && $password =~ [a-z] && $password =~ [0-9] ]]; then
            return 0
        else
            print_error "Password must contain uppercase, lowercase, and numbers"
            return 1
        fi
    else
        print_error "Password must be at least 8 characters"
        return 1
    fi
}

validate_email() {
    local email="$1"
    if [[ $email =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        print_error "Please enter a valid email address"
        return 1
    fi
}

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Please don't run this script as root. Run as a regular user with sudo access."
        exit 1
    fi
    
    if ! sudo -n true 2>/dev/null; then
        print_error "This script requires sudo access. Please ensure your user has sudo privileges."
        exit 1
    fi
}

# Check Ubuntu version
check_ubuntu() {
    if [ ! -f /etc/os-release ]; then
        print_error "Cannot detect OS version"
        exit 1
    fi
    
    . /etc/os-release
    if [ "$ID" != "ubuntu" ]; then
        print_error "This script is designed for Ubuntu. Detected: $ID"
        exit 1
    fi
    
    if [ "$VERSION_ID" != "22.04" ] && [ "$VERSION_ID" != "20.04" ]; then
        print_warning "This script is optimized for Ubuntu 22.04. Detected: $VERSION_ID"
        echo -n "Continue anyway? (y/N): "
        read -r response
        if [[ ! $response =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

# Install system dependencies
install_system_deps() {
    print_header "Installing System Dependencies"
    
    # Update package list
    print_info "Updating package lists..."
    sudo apt update -qq
    
    # Install essential packages
    print_info "Installing essential packages..."
    sudo apt install -y \
        curl \
        wget \
        git \
        build-essential \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release \
        ufw \
        fail2ban \
        htop \
        unzip \
        openssl \
        libssl-dev \
        pkg-config \
        postgresql-client \
        nginx
    
    print_success "System dependencies installed"
}

# Install Node.js
install_nodejs() {
    print_header "Installing Node.js 20"
    
    # Add NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
    
    # Verify installation
    node_version=$(node --version)
    npm_version=$(npm --version)
    
    print_success "Node.js installed: $node_version"
    print_success "NPM installed: $npm_version"
}

# Install PostgreSQL
install_postgresql() {
    print_header "Installing PostgreSQL 14"
    
    sudo apt install -y postgresql postgresql-contrib
    sudo systemctl start postgresql
    sudo systemctl enable postgresql
    
    print_success "PostgreSQL installed and started"
}

# Setup PostgreSQL database
setup_database() {
    print_header "Setting up Database"
    
    # Create database and user
    sudo -u postgres psql << EOF
CREATE DATABASE bilman_vpn;
CREATE USER bilman_user WITH ENCRYPTED PASSWORD '$DB_PASSWORD';
GRANT ALL PRIVILEGES ON DATABASE bilman_vpn TO bilman_user;
GRANT ALL ON SCHEMA public TO bilman_user;
\q
EOF
    
    export DATABASE_URL="postgresql://bilman_user:$DB_PASSWORD@localhost:5432/bilman_vpn"
    print_success "Database created and configured"
}

# Install PM2 for process management
install_pm2() {
    print_header "Installing PM2 Process Manager"
    
    sudo npm install -g pm2
    pm2 startup | grep -E '^sudo' | sh || true
    
    print_success "PM2 installed"
}

# Setup firewall
setup_firewall() {
    print_header "Configuring Firewall"
    
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 3000/tcp  # Bilman app
    sudo ufw --force enable
    
    print_success "Firewall configured"
}

# Clone and setup Bilman
setup_bilman() {
    print_header "Setting up Bilman VPN Management System"
    
    # Clone repository
    if [ -d "bilman" ]; then
        print_info "Removing existing bilman directory..."
        rm -rf bilman
    fi
    
    git clone https://github.com/Iscgrou/bilman.git
    cd bilman
    
    # Install dependencies
    print_info "Installing Node.js dependencies..."
    npm install
    
    # Create environment file
    cat > .env << EOF
# Application Configuration
NODE_ENV=production
PORT=3000
NEXT_PUBLIC_DOMAIN=$USER_DOMAIN

# Database Configuration
DATABASE_URL=$DATABASE_URL
DIRECT_URL=$DATABASE_URL

# Authentication Configuration
JWT_SECRET=bilman-jwt-secret-$(date +%s)-$(openssl rand -hex 16)
JWT_EXPIRES_IN=7d
NEXTAUTH_SECRET=$(openssl rand -base64 32)
NEXTAUTH_URL=https://$USER_DOMAIN

# Admin Account Configuration
ADMIN_USERNAME=$USER_USERNAME
ADMIN_PASSWORD=$USER_PASSWORD
ADMIN_EMAIL=$USER_EMAIL

# Deployment Configuration
BILMAN_DOMAIN=$USER_DOMAIN
BILMAN_USERNAME=$USER_USERNAME
BILMAN_PASSWORD=$USER_PASSWORD
DEPLOYMENT_DATE=$(date)

# Optional Services (configure later)
TELEGRAM_BOT_TOKEN=
REDIS_URL=
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=

# Security Configuration
CSRF_SECRET=$(openssl rand -base64 32)
RATE_LIMIT_MAX=100
RATE_LIMIT_WINDOW=15
EOF
    
    # Setup database schema
    print_info "Setting up database schema..."
    npx prisma generate
    npx prisma db push
    
    # Build application
    print_info "Building application..."
    npm run build
    
    print_success "Bilman application setup complete"
}

# Setup Nginx reverse proxy
setup_nginx() {
    print_header "Configuring Nginx Reverse Proxy"
    
    # Remove default site
    sudo rm -f /etc/nginx/sites-enabled/default
    
    # Create Bilman site configuration
    sudo tee /etc/nginx/sites-available/bilman << EOF
server {
    listen 80;
    server_name $USER_DOMAIN;
    
    # Redirect HTTP to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name $USER_DOMAIN;
    
    # SSL configuration (you'll need to add your certificates)
    # ssl_certificate /path/to/your/certificate.crt;
    # ssl_certificate_key /path/to/your/private.key;
    
    # For now, we'll set up HTTP only
    listen 80;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_cache_bypass \$http_upgrade;
        proxy_read_timeout 86400;
    }
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/bilman /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    print_success "Nginx configured and started"
}

# Setup PM2 to run Bilman
setup_pm2_app() {
    print_header "Setting up Application Service"
    
    # Create PM2 ecosystem file
    cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'bilman-vpn',
    script: 'npm',
    args: 'start',
    cwd: '$(pwd)',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    }
  }]
};
EOF
    
    # Start application with PM2
    pm2 start ecosystem.config.js
    pm2 save
    
    print_success "Application service configured"
}

# Setup SSL with Let's Encrypt (optional)
setup_ssl() {
    print_header "SSL Certificate Setup"
    
    echo "Would you like to set up SSL certificate with Let's Encrypt? (y/N): "
    read -r ssl_response
    
    if [[ $ssl_response =~ ^[Yy]$ ]]; then
        # Install Certbot
        sudo apt install -y certbot python3-certbot-nginx
        
        # Get certificate
        sudo certbot --nginx -d $USER_DOMAIN --non-interactive --agree-tos --email $USER_EMAIL
        
        print_success "SSL certificate installed"
    else
        print_warning "Skipping SSL setup. You can run 'sudo certbot --nginx -d $USER_DOMAIN' later"
    fi
}

# Create startup script
create_startup_script() {
    print_header "Creating Management Scripts"
    
    # Create start script
    cat > bilman-start.sh << 'EOF'
#!/bin/bash
cd /home/$(whoami)/bilman
pm2 start ecosystem.config.js
echo "Bilman VPN Management System started"
EOF
    
    # Create stop script
    cat > bilman-stop.sh << 'EOF'
#!/bin/bash
pm2 stop bilman-vpn
echo "Bilman VPN Management System stopped"
EOF
    
    # Create status script
    cat > bilman-status.sh << 'EOF'
#!/bin/bash
echo "=== Bilman VPN Management System Status ==="
pm2 status bilman-vpn
echo
echo "=== System Resources ==="
df -h /
free -h
echo
echo "=== Recent Logs ==="
pm2 logs bilman-vpn --lines 10
EOF
    
    chmod +x bilman-*.sh
    
    print_success "Management scripts created"
}

# Generate installation summary
generate_summary() {
    print_header "Generating Installation Summary"
    
    cat > INSTALLATION_SUMMARY.md << EOF
# Bilman VPN Management System - Installation Complete

## 🎉 Installation Summary
- **Installation Date**: $(date)
- **Server**: Ubuntu $(lsb_release -rs)
- **Domain**: $USER_DOMAIN
- **Admin Username**: $USER_USERNAME
- **Admin Email**: $USER_EMAIL

## 🌐 Access Information
- **Web Interface**: http://$USER_DOMAIN (or https if SSL configured)
- **Local Access**: http://localhost:3000
- **Admin Panel**: Login with your credentials

## 🔧 System Configuration
- **Node.js**: $(node --version)
- **PostgreSQL**: $(sudo -u postgres psql -c "SELECT version();" | head -3 | tail -1)
- **PM2**: $(pm2 --version)
- **Nginx**: $(nginx -v 2>&1)

## 📋 Management Commands
\`\`\`bash
# Start the application
./bilman-start.sh

# Stop the application
./bilman-stop.sh

# Check status and logs
./bilman-status.sh

# PM2 commands
pm2 status
pm2 logs bilman-vpn
pm2 restart bilman-vpn
\`\`\`

## 🔐 Security Features Enabled
- Firewall (UFW) configured
- Fail2ban protection active
- CSRF protection enabled
- Rate limiting implemented
- Secure JWT authentication

## 🚀 Next Steps
1. Access your domain: http://$USER_DOMAIN
2. Login with admin credentials
3. Configure VPN services as needed
4. Set up Telegram bot (optional)
5. Configure email notifications (optional)

## 📞 Support
- Check logs: \`pm2 logs bilman-vpn\`
- Monitor status: \`pm2 status\`
- System resources: \`htop\`

## 🎯 Features Available
- User Management & Authentication
- VPN Server Management
- Billing & Payment Tracking
- Analytics Dashboard
- Telegram Integration
- Multi-language Support (Persian/English)

Installation completed successfully! 🎉
EOF
    
    print_success "Installation summary created: INSTALLATION_SUMMARY.md"
}

# Main installation function
main() {
    echo "Starting Bilman VPN Management System installation..."
    echo "This will install and configure everything needed on your Ubuntu 22 VPS"
    echo
    
    # Preliminary checks
    check_root
    check_ubuntu
    
    # Collect configuration information
    print_header "Configuration Setup"
    echo "Please provide the following information for your VPN management system:"
    echo
    
    prompt_user "Enter your domain name (e.g., vpn.example.com)" "USER_DOMAIN" "false" "validate_domain"
    prompt_user "Enter admin username (3-20 characters)" "USER_USERNAME" "false" "validate_username"
    prompt_user "Enter admin email address" "USER_EMAIL" "false" "validate_email"
    prompt_user "Enter admin password (min 8 chars, mixed case + numbers)" "USER_PASSWORD" "true" "validate_password"
    
    # Confirm password
    prompt_user "Confirm admin password" "CONFIRM_PASSWORD" "true"
    if [ "$USER_PASSWORD" != "$CONFIRM_PASSWORD" ]; then
        print_error "Passwords do not match!"
        exit 1
    fi
    
    # Generate database password
    DB_PASSWORD=$(openssl rand -base64 32)
    
    print_success "Configuration collected successfully"
    echo
    print_info "Domain: $USER_DOMAIN"
    print_info "Admin: $USER_USERNAME"
    print_info "Email: $USER_EMAIL"
    echo
    
    echo "Starting installation in 5 seconds... (Ctrl+C to cancel)"
    sleep 5
    
    # Installation steps
    install_system_deps
    install_nodejs
    install_postgresql
    setup_database
    install_pm2
    setup_firewall
    setup_bilman
    setup_nginx
    setup_pm2_app
    setup_ssl
    create_startup_script
    generate_summary
    
    # Final success message
    print_header "🎉 Installation Complete!"
    print_success "Bilman VPN Management System has been successfully installed!"
    echo
    print_info "Access your system at: http://$USER_DOMAIN"
    print_info "Admin username: $USER_USERNAME"
    print_info "Check INSTALLATION_SUMMARY.md for detailed information"
    echo
    print_success "Your VPN management system is ready to use!"
}

# Run main function
main "$@"