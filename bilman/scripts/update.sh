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

# Stop the application
log "Stopping VPN Manager service..."
systemctl stop vpn-manager

# Backup current version
log "Creating backup before update..."
./backup.sh

# Update system packages
log "Updating system packages..."
apt-get update && apt-get upgrade -y

# Update application
cd /opt/vpn-manager

# Store current version
CURRENT_VERSION=$(git rev-parse HEAD)

# Pull latest changes
log "Pulling latest changes from repository..."
git fetch origin
git reset --hard origin/main

# Check if there are changes
NEW_VERSION=$(git rev-parse HEAD)
if [ "$CURRENT_VERSION" == "$NEW_VERSION" ]; then
    log "Already up to date!"
else
    log "Updating dependencies..."
    npm install

    log "Rebuilding application..."
    npm run build

    log "Updating Docker containers..."
    docker-compose down
    docker-compose pull
    docker-compose up -d
fi

# Restart services
log "Restarting services..."
systemctl restart nginx
systemctl start vpn-manager

# Renew SSL certificate
log "Checking SSL certificate..."
certbot renew --quiet

log "Update completed successfully!"
warning "Please check the application logs for any potential issues"
