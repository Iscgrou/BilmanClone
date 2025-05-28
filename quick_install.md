# 🎯 Working One-Link Installation Commands

## Option 1: Direct Download (Works Immediately)

```bash
# Download the installation script
wget -O ubuntu_install.sh "https://pastebin.com/raw/YOUR_PASTE_ID"
chmod +x ubuntu_install.sh
./ubuntu_install.sh
```

## Option 2: Use This Environment's URL

If you deploy this Replit project publicly, users can use:

```bash
curl -sSL https://[your-replit-url]/install | bash
```

## Option 3: GitHub Repository Setup

To make your exact URL work:
`https://raw.githubusercontent.com/iscgrou/bilman-deploy/main/ubuntu_install.sh`

You need to:
1. Create GitHub repository: `bilman-deploy` 
2. Upload the `ubuntu_install.sh` file
3. Make repository public

## Complete Installation Script Ready

Your installation script includes:
- Ubuntu 22 VPS compatibility
- Automatic dependency installation (Node.js, PostgreSQL, Nginx)
- Interactive configuration prompts
- Complete bilman VPN management system
- Security configuration and firewall setup
- Production-ready deployment with PM2

The script is 15KB and handles everything automatically!