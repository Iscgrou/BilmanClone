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

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
   error "This script must be run as root"
   exit 1
fi

# Load environment variables
if [ -f /opt/vpn-manager/.env ]; then
    source /opt/vpn-manager/.env
else
    error "Environment file not found"
    exit 1
fi

# Create backup directory
BACKUP_DIR="/opt/vpn-manager/backups"
BACKUP_NAME="vpn-manager-$(date +%Y%m%d-%H%M%S)"
mkdir -p ${BACKUP_DIR}

# Create temporary directory
TEMP_DIR=$(mktemp -d)
log "Creating backup in ${TEMP_DIR}..."

# Backup application files
log "Backing up application files..."
cp -r /opt/vpn-manager/* ${TEMP_DIR}/ 2>/dev/null || true

# Backup database
log "Backing up database..."
if [ -f /opt/vpn-manager/docker-compose.yml ]; then
    docker-compose -f /opt/vpn-manager/docker-compose.yml exec -T db mysqldump -u root -p"${DB_ROOT_PASSWORD}" --all-databases > ${TEMP_DIR}/database.sql
fi

# Backup environment variables
log "Backing up environment variables..."
cp /opt/vpn-manager/.env ${TEMP_DIR}/ 2>/dev/null || true

# Backup Nginx configuration
log "Backing up Nginx configuration..."
cp -r /etc/nginx/sites-available ${TEMP_DIR}/nginx-sites-available
cp -r /etc/nginx/sites-enabled ${TEMP_DIR}/nginx-sites-enabled

# Backup SSL certificates
log "Backing up SSL certificates..."
cp -r /etc/letsencrypt ${TEMP_DIR}/letsencrypt

# Create archive
log "Creating backup archive..."
cd ${TEMP_DIR}
tar czf ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz ./*

# Cleanup
log "Cleaning up..."
rm -rf ${TEMP_DIR}

# Remove old backups (keep last 7 days)
find ${BACKUP_DIR} -type f -mtime +7 -name '*.tar.gz' -delete

log "Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"

# Create backup info file
cat > ${BACKUP_DIR}/${BACKUP_NAME}.info << EOL
Backup created on: $(date)
System information:
$(uname -a)
Disk usage:
$(df -h)
Docker containers:
$(docker ps -a)
EOL

# Optional: Upload backup to remote storage (uncomment and configure as needed)
# if [ ! -z "$BACKUP_REMOTE_PATH" ]; then
#     log "Uploading backup to remote storage..."
#     rclone copy "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" "$BACKUP_REMOTE_PATH"
#     rclone copy "${BACKUP_DIR}/${BACKUP_NAME}.info" "$BACKUP_REMOTE_PATH"
# fi

log "Backup info saved to: ${BACKUP_DIR}/${BACKUP_NAME}.info"

# Setup daily cron job if it doesn't exist
if ! crontab -l | grep -q "backup.sh"; then
    log "Setting up daily backup cron job..."
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/vpn-manager/scripts/backup.sh") | crontab -
fi
