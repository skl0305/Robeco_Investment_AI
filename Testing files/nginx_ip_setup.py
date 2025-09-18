#!/usr/bin/env python3
"""
NGINX + IP Address Setup for Robeco
Access via https://138.199.60.185 directly
"""

import subprocess
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def create_nginx_ip_config():
    """Create nginx configuration for direct IP access"""
    
    config_content = f"""
# Robeco Professional System - IP Access Configuration
# Access via: https://138.199.60.185

server {{
    listen 80;
    server_name 138.199.60.185;
    
    # Redirect HTTP to HTTPS
    return 301 https://138.199.60.185$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name 138.199.60.185;
    
    # SSL Configuration for IP address
    ssl_certificate /opt/homebrew/etc/nginx/ssl/138.199.60.185.crt;
    ssl_certificate_key /opt/homebrew/etc/nginx/ssl/138.199.60.185.key;
    
    # SSL Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    
    # Proxy to Robeco App on port 8005
    location / {{
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }}
    
    # WebSocket Support
    location /ws/ {{
        proxy_pass http://127.0.0.1:8005;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
    
    # API Endpoints
    location /api/ {{
        proxy_pass http://127.0.0.1:8005;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}
}}
"""
    
    # Create config
    config_dir = Path("/opt/homebrew/etc/nginx/servers")
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / "robeco_ip.conf"
    
    try:
        with open(config_file, 'w') as f:
            f.write(config_content)
        logger.info(f"✅ nginx IP configuration created: {config_file}")
        return str(config_file)
    except Exception as e:
        logger.error(f"❌ Failed to create config: {e}")
        return None

def generate_ssl_for_ip():
    """Generate SSL certificate for IP address"""
    
    ssl_dir = Path("/opt/homebrew/etc/nginx/ssl")
    ssl_dir.mkdir(parents=True, exist_ok=True)
    
    cert_file = ssl_dir / "138.199.60.185.crt"
    key_file = ssl_dir / "138.199.60.185.key"
    
    # Generate self-signed certificate for IP
    ssl_command = [
        'openssl', 'req', '-x509', '-nodes', '-days', '365',
        '-newkey', 'rsa:2048',
        '-keyout', str(key_file),
        '-out', str(cert_file),
        '-subj', '/C=US/ST=State/L=City/O=Robeco/CN=138.199.60.185',
        '-addext', 'subjectAltName=IP:138.199.60.185'
    ]
    
    try:
        subprocess.run(ssl_command, check=True, capture_output=True)
        logger.info(f"✅ SSL certificate generated for 138.199.60.185")
        logger.info(f"   Certificate: {cert_file}")
        logger.info(f"   Private key: {key_file}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to generate SSL certificate: {e}")
        return False

def display_setup_instructions():
    """Display setup instructions for IP access"""
    
    logger.info("")
    logger.info("🌐 NGINX + IP SETUP INSTRUCTIONS")
    logger.info("=" * 80)
    logger.info("")
    logger.info("🎯 RESULT: Access via https://138.199.60.185")
    logger.info("")
    logger.info("📋 STEP 1: Router Configuration")
    logger.info("   • Login to router: http://192.168.1.1")
    logger.info("   • Port forwarding: 80 → 10.7.7.2:80")
    logger.info("   • Port forwarding: 443 → 10.7.7.2:443")
    logger.info("   • Save and restart router")
    logger.info("")
    logger.info("📋 STEP 2: Install nginx")
    logger.info("   • brew install nginx")
    logger.info("")
    logger.info("📋 STEP 3: Start Services")
    logger.info("   • Start nginx: sudo nginx")
    logger.info("   • Start Robeco: python run_professional_system.py")
    logger.info("")
    logger.info("📋 STEP 4: Test Access")
    logger.info("   • Local: http://127.0.0.1:8005")
    logger.info("   • Global: https://138.199.60.185")
    logger.info("")
    logger.info("✅ ADVANTAGES:")
    logger.info("   • FREE forever ($0 cost)")
    logger.info("   • Fixed IP URL: https://138.199.60.185")
    logger.info("   • Professional setup")
    logger.info("   • Your own infrastructure")
    logger.info("   • No domain needed")
    logger.info("   • Global access via IP")
    logger.info("")
    logger.info("⚠️  COMPLEXITY: Medium (2-3 hours setup)")
    logger.info("💰 COST: $0 (completely FREE)")
    logger.info("=" * 80)

def main():
    """Main setup function"""
    
    logger.info("🌐 NGINX + IP Address Setup for Robeco")
    logger.info("📍 Target URL: https://138.199.60.185")
    logger.info("")
    
    # Create nginx configuration
    config_file = create_nginx_ip_config()
    if not config_file:
        logger.error("❌ Failed to create nginx configuration")
        return
    
    # Generate SSL certificate
    ssl_success = generate_ssl_for_ip()
    if not ssl_success:
        logger.error("❌ Failed to generate SSL certificate")
        return
    
    # Display instructions
    display_setup_instructions()
    
    logger.info("")
    logger.info("📄 Configuration created successfully!")
    logger.info(f"   Config file: {config_file}")
    logger.info("")
    logger.info("🚀 Next steps:")
    logger.info("   1. Configure router port forwarding")
    logger.info("   2. Install nginx: brew install nginx") 
    logger.info("   3. Start nginx: sudo nginx")
    logger.info("   4. Test: https://138.199.60.185")

if __name__ == "__main__":
    main()