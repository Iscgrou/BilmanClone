#!/bin/bash

# GitHub Repository Creation Script
# This will create the bilman-deploy repository with your installation script

echo "🚀 Setting up GitHub repository for one-link installation"
echo "========================================================="

# Check if GitHub CLI is available
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
    sudo apt update
    sudo apt install gh -y
fi

# Create repository directory
mkdir -p bilman-deploy
cd bilman-deploy

# Copy installation script
cp ../ubuntu_install.sh .

# Create README
cat > README.md << 'EOF'
# 🚀 Bilman VPN Management System - One-Link Installation

Complete automated installation for Ubuntu 22 VPS with all dependencies and requirements.

## Quick Installation

```bash
curl -sSL https://raw.githubusercontent.com/iscgrou/bilman-deploy/main/ubuntu_install.sh | bash
```

## What Gets Installed

- **Node.js 20** - Latest LTS runtime
- **PostgreSQL 14** - Database server  
- **Nginx** - Web server and reverse proxy
- **PM2** - Process manager
- **Security tools** - Firewall, Fail2ban protection
- **SSL support** - Let's Encrypt ready

## Interactive Setup

The installer prompts for:
- Domain name (e.g., vpn.example.com)
- Admin username (3-20 characters)
- Admin email address
- Secure password (validated)

## Features

- Complete VPN management interface
- User authentication and roles
- Billing and payment tracking
- Analytics dashboard
- Telegram bot integration
- Multi-language support (Persian/English)

## Requirements

- Ubuntu 22.04 LTS VPS (or 20.04)
- Sudo access (don't run as root)
- Domain pointed to server IP
- At least 1GB RAM, 20GB storage

Installation takes 5-10 minutes and results in a fully functional VPN management system!
EOF

# Initialize git repository
git init
git add .
git commit -m "Initial commit: Ubuntu 22 VPS installation script for Bilman VPN Management System"

echo "✅ Repository created locally!"
echo "📋 Next steps:"
echo "1. Authenticate with GitHub: gh auth login"
echo "2. Create repository: gh repo create iscgrou/bilman-deploy --public --source=. --remote=origin --push"
echo "3. Your installation URL will be ready!"
echo ""
echo "🎯 Final URL: https://raw.githubusercontent.com/iscgrou/bilman-deploy/main/ubuntu_install.sh"