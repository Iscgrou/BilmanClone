#!/usr/bin/env python3
"""
Simple HTTP server to host the Ubuntu installation script
Serves the installation script at a public URL for one-link installation
"""

import http.server
import socketserver
import os
import sys
from pathlib import Path

class InstallationHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/install' or self.path == '/ubuntu_install.sh':
            # Serve the installation script
            try:
                script_path = Path(__file__).parent / 'ubuntu_install.sh'
                with open(script_path, 'rb') as f:
                    content = f.read()
                
                self.send_response(200)
                self.send_header('Content-Type', 'text/plain')
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(content)
                
                print(f"✓ Served installation script to {self.client_address[0]}")
                
            except FileNotFoundError:
                self.send_error(404, "Installation script not found")
                
        elif self.path == '/' or self.path == '/status':
            # Serve status page
            html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Bilman VPN Installation Server</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        .header { background: #2563eb; color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .install-box { background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; margin: 20px 0; border-radius: 8px; }
        .command { background: #1e293b; color: #f1f5f9; padding: 15px; border-radius: 6px; font-family: monospace; overflow-x: auto; }
        .feature { background: #ecfdf5; border-left: 4px solid #10b981; padding: 15px; margin: 10px 0; }
        .warning { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Bilman VPN Management System</h1>
        <p>One-Link Installation Server for Ubuntu 22 VPS</p>
    </div>
    
    <div class="install-box">
        <h2>📋 Installation Command</h2>
        <p>Run this command on your Ubuntu 22 VPS to install everything:</p>
        <div class="command">curl -sSL http://""" + os.environ.get('REPL_SLUG', 'localhost') + """.replit.app/install | bash</div>
        <p><small>This will install Node.js, PostgreSQL, Nginx, and the complete VPN management system</small></p>
    </div>
    
    <div class="feature">
        <h3>✨ What Gets Installed</h3>
        <ul>
            <li><strong>Node.js 20</strong> - Latest LTS runtime</li>
            <li><strong>PostgreSQL 14</strong> - Database server</li>
            <li><strong>Nginx</strong> - Web server and reverse proxy</li>
            <li><strong>PM2</strong> - Process manager</li>
            <li><strong>Security tools</strong> - Firewall, Fail2ban protection</li>
            <li><strong>SSL support</strong> - Let's Encrypt ready</li>
        </ul>
    </div>
    
    <div class="feature">
        <h3>🔧 Interactive Setup</h3>
        <p>The installer will prompt you for:</p>
        <ul>
            <li>Domain name (e.g., vpn.example.com)</li>
            <li>Admin username (3-20 characters)</li>
            <li>Admin email address</li>
            <li>Secure password (validated)</li>
        </ul>
    </div>
    
    <div class="warning">
        <h3>⚠️ Requirements</h3>
        <ul>
            <li>Ubuntu 22.04 LTS VPS (or 20.04)</li>
            <li>Sudo access (don't run as root)</li>
            <li>Domain pointed to your server IP</li>
            <li>At least 1GB RAM, 20GB storage</li>
        </ul>
    </div>
    
    <div class="feature">
        <h3>🎯 Features You Get</h3>
        <ul>
            <li>Complete VPN management interface</li>
            <li>User authentication and roles</li>
            <li>Billing and payment tracking</li>
            <li>Analytics dashboard</li>
            <li>Telegram bot integration</li>
            <li>Multi-language support (Persian/English)</li>
        </ul>
    </div>
    
    <p style="text-align: center; margin-top: 40px; color: #6b7280;">
        <em>Installation takes 5-10 minutes. Your VPN management system will be ready to use!</em>
    </p>
</body>
</html>
            """
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', str(len(html_content)))
            self.end_headers()
            self.wfile.write(html_content.encode())
            
        else:
            self.send_error(404, "Not found")

def main():
    port = int(os.environ.get('PORT', 8000))
    
    print("🚀 Starting Bilman Installation Server")
    print(f"📡 Server running on port {port}")
    print(f"🌐 Installation URL: http://localhost:{port}/install")
    print(f"📊 Status page: http://localhost:{port}/")
    print("\n✅ Ready to serve installation script!")
    print("=" * 50)
    
    try:
        with socketserver.TCPServer(("0.0.0.0", port), InstallationHandler) as httpd:
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()