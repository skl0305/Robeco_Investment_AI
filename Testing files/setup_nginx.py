#!/usr/bin/env python3
"""
NGINX + Fixed IP Setup for Robeco Professional System
Professional deployment with permanent URL
"""

import os
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def check_nginx_installed():
    """Check if nginx is installed"""
    try:
        result = subprocess.run(['nginx', '-v'], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_nginx():
    """Install nginx using homebrew"""
    logger.info("📦 Installing nginx...")
    try:
        subprocess.run(['brew', 'install', 'nginx'], check=True)
        logger.info("✅ nginx installed successfully")
        return True
    except subprocess.CalledProcessError:
        logger.error("❌ Failed to install nginx")
        return False

def create_nginx_config():
    """Create nginx configuration for Robeco"""
    
    config_content = """
# Robeco Professional System - NGINX Configuration
# Replace 'yourdomain.com' with your actual domain

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (Replace with your certificates)
    ssl_certificate /usr/local/etc/nginx/ssl/yourdomain.crt;
    ssl_certificate_key /usr/local/etc/nginx/ssl/yourdomain.key;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Proxy Settings for Robeco App
    location / {
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # WebSocket Support
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Timeout Settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Static Files Optimization
    location /static/ {
        proxy_pass http://127.0.0.1:8005;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    # API Endpoints
    location /api/ {
        proxy_pass http://127.0.0.1:8005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # WebSocket Endpoint
    location /ws/ {
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
"""
    
    # Create nginx config directory if it doesn't exist
    config_dir = Path("/usr/local/etc/nginx/servers")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "robeco.conf"
    
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logger.info(f"✅ nginx configuration created: {config_file}")
        return str(config_file)
    except Exception as e:
        logger.error(f"❌ Failed to create nginx config: {e}")
        return None

def setup_ssl_directory():
    """Create SSL certificate directory"""
    ssl_dir = Path("/usr/local/etc/nginx/ssl")
    ssl_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"📁 SSL directory created: {ssl_dir}")
    return ssl_dir

def display_setup_instructions():
    """Display complete setup instructions"""
    
    logger.info("🔧 COMPLETE NGINX SETUP INSTRUCTIONS")
    logger.info("=" * 80)
    logger.info("")
    
    logger.info("📋 STEP 1: Domain Setup")
    logger.info("   • Purchase domain: namecheap.com, godaddy.com (~$15/year)")
    logger.info("   • OR use free subdomain: duckdns.org, noip.com")
    logger.info("   • Point domain to your public IP: 138.199.60.185")
    logger.info("")
    
    logger.info("📋 STEP 2: Router Configuration")
    logger.info("   • Login to router: http://192.168.1.1")
    logger.info("   • Port forwarding: 80 → 10.7.7.2:80")
    logger.info("   • Port forwarding: 443 → 10.7.7.2:443")
    logger.info("")
    
    logger.info("📋 STEP 3: SSL Certificate")
    logger.info("   • Free SSL: certbot --nginx")
    logger.info("   • OR: openssl req -x509 -nodes -days 365 -newkey rsa:2048")
    logger.info("        -keyout /usr/local/etc/nginx/ssl/yourdomain.key")
    logger.info("        -out /usr/local/etc/nginx/ssl/yourdomain.crt")
    logger.info("")
    
    logger.info("📋 STEP 4: Start Services")
    logger.info("   • Start nginx: sudo nginx")
    logger.info("   • Start Robeco: python run_professional_system.py")
    logger.info("   • Test: https://yourdomain.com")
    logger.info("")
    
    logger.info("🎯 FINAL RESULT:")
    logger.info("   ✅ Fixed URL: https://yourdomain.com")
    logger.info("   ✅ Professional setup")
    logger.info("   ✅ SSL encrypted")
    logger.info("   ✅ Your own infrastructure")
    logger.info("   ✅ No monthly fees")
    logger.info("=" * 80)

def main():
    """Main setup function"""
    
    logger.info("🌐 NGINX + Fixed IP Setup for Robeco Professional System")
    logger.info("=" * 70)
    logger.info("")
    
    # Check if nginx is installed
    if not check_nginx_installed():
        logger.info("📦 nginx not found. Installing...")
        if not install_nginx():
            logger.error("❌ Failed to install nginx. Please install manually:")
            logger.error("   brew install nginx")
            return
    else:
        logger.info("✅ nginx is already installed")
    
    # Create nginx configuration
    logger.info("🔧 Creating nginx configuration...")
    config_file = create_nginx_config()
    
    if not config_file:
        logger.error("❌ Failed to create nginx configuration")
        return
    
    # Setup SSL directory
    ssl_dir = setup_ssl_directory()
    
    # Display instructions
    display_setup_instructions()
    
    logger.info("")
    logger.info("📄 Configuration file created:")
    logger.info(f"   {config_file}")
    logger.info("")
    logger.info("📝 Next steps:")
    logger.info("   1. Edit the config file and replace 'yourdomain.com'")
    logger.info("   2. Setup your domain DNS")
    logger.info("   3. Configure router port forwarding")
    logger.info("   4. Generate SSL certificate")
    logger.info("   5. Start nginx: sudo nginx")
    logger.info("")
    logger.info("💡 This is a complex setup. Consider SSH tunnel for simplicity!")

if __name__ == "__main__":
    main()