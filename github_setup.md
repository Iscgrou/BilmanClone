# GitHub Repository Setup for One-Link Installation

## Create Your Repository

1. Go to: https://github.com/iscgrou
2. Click "New repository"
3. Repository name: `bilman-deploy`
4. Description: "One-link installation for Bilman VPN Management System"
5. Make it **Public**
6. Check "Add a README file"
7. Click "Create repository"

## Upload Installation Script

After creating the repository:

1. Click "uploading an existing file" or "Add file" → "Upload files"
2. Upload the `ubuntu_install.sh` file from this project
3. Commit with message: "Add Ubuntu 22 VPS installation script"

## Your Working Installation URL

Once uploaded, users can install with:

```bash
curl -sSL https://raw.githubusercontent.com/iscgrou/bilman-deploy/main/ubuntu_install.sh | bash
```

## Alternative: Clone and Push

If you prefer using git commands:

```bash
git clone https://github.com/iscgrou/bilman-deploy.git
cd bilman-deploy
cp /path/to/ubuntu_install.sh .
git add ubuntu_install.sh
git commit -m "Add Ubuntu installation script"
git push origin main
```

Your one-link installation will work immediately after upload!