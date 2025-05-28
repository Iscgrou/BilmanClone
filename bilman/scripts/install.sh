#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Log function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root"
   exit 1
fi

# Get domain name
read -p "Enter your domain name (e.g., vpn.example.com): " DOMAIN_NAME
if [ -z "$DOMAIN_NAME" ]; then
    error "Domain name is required"
    exit 1
fi

# Get admin credentials
read -p "Enter admin username: " ADMIN_USER
read -s -p "Enter admin password: " ADMIN_PASS
echo
read -s -p "Confirm admin password: " ADMIN_PASS_CONFIRM
echo

if [ "$ADMIN_PASS" != "$ADMIN_PASS_CONFIRM" ]; then
    error "Passwords do not match"
    exit 1
fi

# Update system
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# Install required packages
log "Installing required packages..."
apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release \
    git \
    nginx \
    certbot \
    python3-certbot-nginx \
    ufw

# Install Node.js 18.x
log "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt-get install -y nodejs

# Install Docker
log "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
log "Installing Docker Compose..."
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Configure firewall
log "Configuring firewall..."
ufw allow 22
ufw allow 80
ufw allow 443
ufw --force enable

# Create application directory
log "Setting up application directory..."
mkdir -p /opt/vpn-manager
cd /opt/vpn-manager

# Clone repository
log "Cloning repository..."
git clone https://github.com/Iscgrou/billi.git .

# Create environment file
log "Creating environment file..."
cat > .env << EOL
DOMAIN=${DOMAIN_NAME}
ADMIN_USER=${ADMIN_USER}
ADMIN_PASS=$(echo -n ${ADMIN_PASS} | sha256sum | cut -d' ' -f1)
NODE_ENV=production
EOL

# Install dependencies
log "Installing Node.js dependencies..."
npm install

# Build application
log "Building application..."
npm run build

# Setup Docker Compose
log "Setting up Docker containers..."
docker-compose up -d

# Configure Nginx
log "Configuring Nginx..."
cat > /etc/nginx/sites-available/${DOMAIN_NAME} << EOL
server {
    listen 80;
    server_name ${DOMAIN_NAME};
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOL

ln -s /etc/nginx/sites-available/${DOMAIN_NAME} /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# Setup SSL
log "Setting up SSL certificate..."
certbot --nginx -d ${DOMAIN_NAME} --non-interactive --agree-tos --email admin@${DOMAIN_NAME} --redirect

# Create systemd service
log "Creating systemd service..."
cat > /etc/systemd/system/vpn-manager.service << EOL
[Unit]
Description=VPN Manager
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/vpn-manager
ExecStart=/usr/bin/npm start
Restart=always
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOL

systemctl daemon-reload
systemctl enable vpn-manager
systemctl start vpn-manager

# Final steps
log "Installation completed successfully!"
log "Your VPN management system is now available at: https://${DOMAIN_NAME}"
log "Admin username: ${ADMIN_USER}"
warning "Please make sure to:"
warning "1. Configure your domain's DNS to point to this server"
warning "2. Keep your admin credentials safe"
warning "3. Regularly update your system and backup your data"
