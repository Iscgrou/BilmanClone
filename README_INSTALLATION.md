# 🚀 Bilman VPN Management System - One-Link Installation

## Quick Installation for Ubuntu 22 VPS

### One-Line Installation Command

```bash
curl -sSL https://raw.githubusercontent.com/YourUsername/bilman-deploy/main/ubuntu_install.sh | bash
```

Or download and run:

```bash
wget https://raw.githubusercontent.com/YourUsername/bilman-deploy/main/ubuntu_install.sh
chmod +x ubuntu_install.sh
./ubuntu_install.sh
```

## What This Installation Does

### 🔧 System Requirements Installation
- **Node.js 20** - Latest LTS version
- **PostgreSQL 14** - Database server
- **Nginx** - Reverse proxy and web server
- **PM2** - Process manager for production
- **SSL Support** - Let's Encrypt certificate (optional)
- **Firewall** - UFW configuration with security rules
- **Fail2ban** - Intrusion prevention

### 📝 Interactive Configuration
The script will prompt you for:

1. **Domain Name** (e.g., `vpn.example.com`)
   - Must be a valid domain format
   - Will be used for web access and SSL certificate

2. **Admin Username** (3-20 characters)
   - Alphanumeric and underscore only
   - Your main admin account

3. **Admin Email** 
   - Valid email format required
   - Used for SSL certificate and notifications

4. **Admin Password**
   - Minimum 8 characters
   - Must contain uppercase, lowercase, and numbers
   - Confirmed with re-entry

### 🏗️ Complete Setup Process

1. **System Update** - Updates all packages
2. **Dependencies** - Installs all required software
3. **Database Setup** - Creates PostgreSQL database and user
4. **Application** - Clones and configures Bilman VPN system
5. **Web Server** - Configures Nginx reverse proxy
6. **Security** - Sets up firewall and protection
7. **SSL Certificate** - Optional Let's Encrypt setup
8. **Service Management** - PM2 process management
9. **Startup Scripts** - Management commands

## 🎯 What You Get

### VPN Management Features
- **User Management** - Role-based access control
- **VPN Services** - Complete server management
- **Billing System** - Invoice and payment tracking  
- **Analytics** - Usage statistics and reporting
- **Telegram Integration** - Bot notifications
- **Multi-language** - Persian/English support

### Production Ready Setup
- **Auto-restart** - PM2 keeps application running
- **Reverse Proxy** - Nginx handles web traffic
- **Security** - Firewall, fail2ban, rate limiting
- **SSL Ready** - HTTPS certificate support
- **Monitoring** - Built-in status and logging

## 📱 Access Your System

After installation completes:

- **Web Interface**: `http://your-domain.com`
- **Admin Login**: Use your configured credentials
- **Local Access**: `http://localhost:3000`

## 🛠️ Management Commands

```bash
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
```

## 🔐 Security Features

- **Firewall** configured with essential ports only
- **Fail2ban** protection against brute force
- **CSRF** protection enabled
- **Rate limiting** on API endpoints
- **JWT** secure authentication
- **Password hashing** with bcrypt

## 📋 System Requirements

- **OS**: Ubuntu 22.04 LTS (or 20.04)
- **RAM**: Minimum 1GB (2GB recommended)
- **Storage**: Minimum 20GB available space
- **Network**: Public IP with domain pointed to server
- **Access**: Sudo privileges required

## 🚀 Installation Time

Total installation time: **5-10 minutes**
- System updates: 2-3 minutes
- Dependencies: 2-3 minutes  
- Application setup: 2-3 minutes
- Configuration: 1-2 minutes

## 🎉 Post-Installation

1. **Access your domain** in a web browser
2. **Login** with your admin credentials
3. **Configure VPN settings** as needed
4. **Add users** and manage permissions
5. **Set up billing** if using paid services
6. **Configure Telegram bot** for notifications (optional)

Your complete VPN management system is ready to use!