#!/usr/bin/env python3
"""
Start NGINX with Robeco configuration
Handles proper setup for IP access
"""

import subprocess
import logging
import time
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def stop_existing_nginx():
    """Stop any existing nginx processes"""
    try:
        subprocess.run(['brew', 'services', 'stop', 'nginx'], check=False)
        subprocess.run(['sudo', 'nginx', '-s', 'quit'], check=False, capture_output=True)
        time.sleep(2)
        logger.info("✅ Stopped existing nginx processes")
    except:
        pass

def check_nginx_config():
    """Check nginx configuration"""
    try:
        result = subprocess.run(['nginx', '-t'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ nginx configuration is valid")
            return True
        else:
            logger.error(f"❌ nginx configuration error: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"❌ Failed to test nginx config: {e}")
        return False

def create_simplified_config():
    """Create simplified nginx configuration for testing"""
    
    config_content = """
# Simplified Robeco nginx configuration
events {
    worker_connections 1024;
}

http {
    include       /opt/homebrew/etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    sendfile        on;
    keepalive_timeout  65;
    
    # Test server on port 8080 (no sudo needed)
    server {
        listen 8080;
        server_name localhost 138.199.60.185;
        
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
        }
        
        # WebSocket Support
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
        
        # API Endpoints
        location /api/ {
            proxy_pass http://127.0.0.1:8005;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
"""
    
    config_file = Path("/opt/homebrew/etc/nginx/nginx.conf")
    
    try:
        # Backup original config
        backup_file = config_file.with_suffix('.conf.backup')
        if config_file.exists() and not backup_file.exists():
            subprocess.run(['cp', str(config_file), str(backup_file)])
            logger.info(f"✅ Backed up original config to {backup_file}")
        
        # Write new config
        with open(config_file, 'w') as f:
            f.write(config_content)
        
        logger.info(f"✅ Created simplified nginx config: {config_file}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to create config: {e}")
        return False

def start_nginx():
    """Start nginx with the new configuration"""
    try:
        # Start nginx
        result = subprocess.run(['nginx'], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("✅ nginx started successfully")
            return True
        else:
            logger.error(f"❌ Failed to start nginx: {result.stderr}")
            
            # Try with brew services as fallback
            logger.info("🔄 Trying with brew services...")
            subprocess.run(['brew', 'services', 'start', 'nginx'])
            time.sleep(3)
            return True
            
    except Exception as e:
        logger.error(f"❌ Failed to start nginx: {e}")
        return False

def test_nginx():
    """Test if nginx is working"""
    import requests
    
    try:
        # Test nginx proxy
        response = requests.get('http://localhost:8080', timeout=5)
        if response.status_code in [200, 404, 502]:  # 502 is OK if Robeco isn't running yet
            logger.info("✅ nginx proxy is working")
            return True
        else:
            logger.warning(f"⚠️ Unexpected response: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error("❌ nginx is not responding on port 8080")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def display_test_info():
    """Display testing information"""
    logger.info("")
    logger.info("🎯 NGINX TEST SETUP COMPLETE")
    logger.info("=" * 60)
    logger.info("📍 Test URL: http://localhost:8080")
    logger.info("📍 Test URL: http://10.7.7.2:8080")
    logger.info("📍 Future URL: http://138.199.60.185:8080")
    logger.info("")
    logger.info("🚀 Next steps:")
    logger.info("   1. Start Robeco: python run_professional_system.py")
    logger.info("   2. Test locally: http://localhost:8080")
    logger.info("   3. Configure router for port 8080 → 10.7.7.2:8080")
    logger.info("   4. Test globally: http://138.199.60.185:8080")
    logger.info("")
    logger.info("💡 This avoids needing sudo for ports 80/443")
    logger.info("🎯 After testing works, we can setup proper SSL")
    logger.info("=" * 60)

def main():
    """Main nginx setup function"""
    
    logger.info("🌐 Starting NGINX for Robeco IP Access")
    logger.info("🎯 Setting up test configuration on port 8080")
    logger.info("")
    
    # Stop existing nginx
    stop_existing_nginx()
    
    # Create simplified config
    if not create_simplified_config():
        logger.error("❌ Failed to create nginx configuration")
        return
    
    # Check config
    if not check_nginx_config():
        logger.error("❌ nginx configuration is invalid")
        return
    
    # Start nginx
    if not start_nginx():
        logger.error("❌ Failed to start nginx")
        return
    
    # Test nginx
    time.sleep(2)
    if test_nginx():
        logger.info("🎉 nginx setup successful!")
    else:
        logger.warning("⚠️ nginx may not be working correctly")
    
    # Display information
    display_test_info()

if __name__ == "__main__":
    main()