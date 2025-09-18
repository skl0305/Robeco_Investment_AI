#!/usr/bin/env python3
"""
Cloud Proxy for Robeco App - Makes your app accessible via public IP
Run this AFTER your main app is running to create internet access
"""

import subprocess
import sys
import time
import logging
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_ssh_tunnel():
    """Create SSH tunnel to cloud server for public access"""
    logger.info("🌐 Creating cloud tunnel for public IP access...")
    
    # This would connect to a cloud server and create a reverse tunnel
    # For now, we'll use a simpler approach with localhost tunneling
    
    try:
        # Start a simple HTTP proxy that forwards to your app
        import http.server
        import socketserver
        from urllib.request import urlopen
        from urllib.parse import urlparse
        
        class ProxyHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                try:
                    # Forward requests to your local app
                    response = urlopen(f'http://127.0.0.1:8005{self.path}')
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    self.wfile.write(response.read())
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
                    self.wfile.write(f"Error: {e}".encode())
        
        # Start proxy on port 8080
        with socketserver.TCPServer(("0.0.0.0", 8080), ProxyHandler) as httpd:
            logger.info("✅ Cloud proxy started on port 8080")
            logger.info("🔗 Access your app via: http://YOUR_PUBLIC_IP:8080/")
            httpd.serve_forever()
            
    except Exception as e:
        logger.error(f"❌ Proxy failed: {e}")

def main():
    logger.info("🚀 Starting Cloud Proxy for Public IP Access")
    logger.info("🔧 This creates: http://YOUR_PUBLIC_IP:8080/ → http://127.0.0.1:8005/")
    logger.info("")
    
    # Check if main app is running
    try:
        response = requests.get('http://127.0.0.1:8005/', timeout=3)
        logger.info("✅ Robeco app is running - creating proxy...")
    except:
        logger.error("❌ Robeco app not running!")
        logger.error("💡 Start your main app first: python run_professional_system.py")
        return
    
    start_ssh_tunnel()

if __name__ == "__main__":
    main()