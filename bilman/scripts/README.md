# VPN Management System Installation Scripts

This directory contains scripts for installing, updating, and backing up the VPN Management System on Ubuntu 22.04.

## Prerequisites

- Ubuntu 22.04 LTS
- Root access
- Domain name pointing to your server
- Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS)

## Scripts Overview

### 1. Installation Script (`install.sh`)

Installs and configures the complete VPN Management System.

```bash
sudo ./install.sh
```

The script will:
- Update system packages
- Install required dependencies (Node.js, Docker, Nginx, etc.)
- Set up SSL certificates
- Configure Nginx as reverse proxy
- Create admin user
- Set up the application

During installation, you'll need to provide:
- Domain name
- Admin username
- Admin password

### 2. Update Script (`update.sh`)

Updates the system and application to the latest version.

```bash
sudo ./update.sh
```

The script will:
- Create a backup before updating
- Update system packages
- Pull latest application changes
- Update dependencies
- Rebuild application
- Update Docker containers
- Renew SSL certificates

### 3. Backup Script (`backup.sh`)

Creates a complete backup of the system.

```bash
sudo ./backup.sh
```

The script will backup:
- Application files
- Database
- Environment variables
- Nginx configuration
- SSL certificates

Backups are stored in `/opt/vpn-manager/backups` with timestamp.
Keeps backups for the last 7 days.

## Automatic Backups

The backup script automatically sets up a daily cron job that runs at 2 AM.

## Monitoring

- Application logs: `journalctl -u vpn-manager`
- Nginx logs: `/var/log/nginx/`
- Docker logs: `docker-compose logs`

## Security Notes

1. Keep your admin credentials safe
2. Regularly update your system
3. Monitor system logs
4. Keep backups in a secure location
5. Use strong passwords

## Troubleshooting

If you encounter issues:

1. Check logs:
```bash
journalctl -u vpn-manager -n 100
docker-compose logs
```

2. Verify services are running:
```bash
systemctl status vpn-manager
systemctl status nginx
docker-compose ps
```

3. Check SSL certificate:
```bash
certbot certificates
```

## Recovery

To restore from backup:

1. Stop services:
```bash
systemctl stop vpn-manager
docker-compose down
```

2. Extract backup:
```bash
cd /opt/vpn-manager/backups
tar xzf vpn-manager-YYYYMMDD-HHMMSS.tar.gz
```

3. Restore configurations and restart:
```bash
systemctl start vpn-manager
docker-compose up -d
systemctl restart nginx

## Quick Installation

To install the complete system with a single command, run:

```bash
curl -sSL https://raw.githubusercontent.com/Iscgrou/billi/main/scripts/quick-install.sh | sudo bash
```

This will:
- Clone the repository
- Install all dependencies
- Set up SSL certificates
- Configure the system
- Create admin user
