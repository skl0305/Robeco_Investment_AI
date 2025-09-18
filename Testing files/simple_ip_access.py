#!/usr/bin/env python3
"""
Simple IP Access Setup for Robeco
Makes Robeco accessible via http://138.199.60.185:8080 from ANY computer
"""

import subprocess
import logging
import time
import signal
import sys
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Global process management
server_process = None
proxy_process = None

def cleanup_processes():
    """Clean up all processes"""
    global server_process, proxy_process
    
    logger.info("🧹 Cleaning up processes...")
    
    if proxy_process:
        proxy_process.terminate()
        try:
            proxy_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proxy_process.kill()
    
    if server_process:
        server_process.terminate()
        try:
            server_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            server_process.kill()

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    logger.info("\n🛑 Shutdown requested...")
    cleanup_processes()
    sys.exit(0)

def start_robeco_server():
    """Start the Robeco server"""
    global server_process
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    logger.info("🚀 Starting Robeco server on port 8005...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    # Wait for server to start
    logger.info("⏳ Waiting for server to start...")
    time.sleep(8)
    
    # Verify server is running
    import socket
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', 8005))
                if result == 0:
                    logger.info("✅ Robeco server started successfully on port 8005")
                    return True
        except:
            pass
        time.sleep(1)
    
    logger.error("❌ Failed to start Robeco server")
    return False

def create_simple_proxy():
    """Create a simple HTTP proxy using Python"""
    
    proxy_script = """
import http.server
import socketserver
import urllib.request
import urllib.parse
import urllib.error
from http.server import BaseHTTPRequestHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.proxy_request()
    
    def do_POST(self):
        self.proxy_request()
    
    def do_PUT(self):
        self.proxy_request()
    
    def do_DELETE(self):
        self.proxy_request()
    
    def proxy_request(self):
        try:
            # Build target URL
            target_url = f"http://127.0.0.1:8005{self.path}"
            
            # Create request
            headers = {}
            for header, value in self.headers.items():
                if header.lower() not in ['host', 'connection']:
                    headers[header] = value
            
            # Handle request body for POST/PUT
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            # Make request to Robeco server
            req = urllib.request.Request(target_url, data=body, headers=headers, method=self.command)
            
            with urllib.request.urlopen(req, timeout=30) as response:
                # Send response status
                self.send_response(response.status)
                
                # Send headers
                for header, value in response.headers.items():
                    if header.lower() not in ['connection', 'transfer-encoding']:
                        self.send_header(header, value)
                self.end_headers()
                
                # Send body
                self.wfile.write(response.read())
                
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            logger.error(f"Proxy error: {e}")
            self.send_response(502)
            self.end_headers()
            self.wfile.write(b"Proxy Error")

# Start proxy server
if __name__ == "__main__":
    PORT = 8080
    
    class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
        allow_reuse_address = True
    
    with ThreadedTCPServer(("0.0.0.0", PORT), ProxyHandler) as httpd:
        print(f"🌐 Proxy server running on 0.0.0.0:{PORT}")
        print(f"🎯 Forwarding to Robeco server on 127.0.0.1:8005")
        print(f"🔗 Access via: http://10.7.7.2:{PORT}")
        print(f"🌍 Global access: http://138.199.60.185:{PORT}")
        httpd.serve_forever()
"""
    
    proxy_file = Path(__file__).parent / "proxy_server.py"
    with open(proxy_file, 'w') as f:
        f.write(proxy_script)
    
    return proxy_file

def start_proxy_server():
    """Start the proxy server"""
    global proxy_process
    
    logger.info("🔧 Creating simple HTTP proxy...")
    proxy_file = create_simple_proxy()
    
    logger.info("🌐 Starting proxy server on port 8080...")
    proxy_process = subprocess.Popen([
        sys.executable, str(proxy_file)
    ])
    
    # Wait for proxy to start
    time.sleep(3)
    
    # Test proxy
    import socket
    for attempt in range(5):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', 8080))
                if result == 0:
                    logger.info("✅ Proxy server started successfully on port 8080")
                    return True
        except:
            pass
        time.sleep(1)
    
    logger.error("❌ Failed to start proxy server")
    return False

def test_local_access():
    """Test local access to the proxy"""
    try:
        import requests
        
        # Test localhost
        response = requests.get('http://localhost:8080', timeout=5)
        if response.status_code in [200, 405]:
            logger.info("✅ Localhost access working: http://localhost:8080")
        
        # Test local IP
        response = requests.get('http://10.7.7.2:8080', timeout=5)
        if response.status_code in [200, 405]:
            logger.info("✅ Local network access working: http://10.7.7.2:8080")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Local access test failed: {e}")
        return False

def display_access_info():
    """Display access information"""
    logger.info("")
    logger.info("🎉 ROBECO IP ACCESS SETUP COMPLETE!")
    logger.info("=" * 80)
    logger.info("📱 ACCESS URLS:")
    logger.info("=" * 80)
    logger.info("🏠 Local computer: http://localhost:8080")
    logger.info("🏠 Local network: http://10.7.7.2:8080")
    logger.info("🌍 GLOBAL ACCESS: http://138.199.60.185:8080")
    logger.info("🔧 Workbench: http://138.199.60.185:8080/workbench")
    logger.info("=" * 80)
    logger.info("")
    logger.info("🌐 FOR GLOBAL ACCESS:")
    logger.info("   1. Share this URL: http://138.199.60.185:8080")
    logger.info("   2. Configure router port forwarding:")
    logger.info("      • External Port: 8080")
    logger.info("      • Internal IP: 10.7.7.2")
    logger.info("      • Internal Port: 8080")
    logger.info("      • Protocol: TCP")
    logger.info("")
    logger.info("✅ ANY computer can access via your IP address!")
    logger.info("✅ No domain needed - just your IP!")
    logger.info("✅ Professional fixed URL!")
    logger.info("")
    logger.info("⌨️  Press Ctrl+C to stop servers")
    logger.info("=" * 80)

def main():
    """Main setup function"""
    global server_process, proxy_process
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🌐 Simple IP Access Setup for Robeco")
    logger.info("🎯 Goal: http://138.199.60.185:8080 accessible from ANY computer")
    logger.info("")
    
    # os already imported at top
    
    # Stop any existing nginx
    try:
        subprocess.run(['brew', 'services', 'stop', 'nginx'], check=False)
        subprocess.run(['nginx', '-s', 'quit'], check=False, capture_output=True)
    except:
        pass
    
    # Start Robeco server
    if not start_robeco_server():
        logger.error("❌ Failed to start Robeco server")
        return
    
    # Start proxy server
    if not start_proxy_server():
        logger.error("❌ Failed to start proxy server")
        cleanup_processes()
        return
    
    # Test local access
    time.sleep(2)
    test_local_access()
    
    # Display access information
    display_access_info()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                logger.error("❌ Robeco server stopped")
                break
            
            if proxy_process.poll() is not None:
                logger.error("❌ Proxy server stopped")
                break
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown requested by user...")
    
    finally:
        cleanup_processes()
        logger.info("✅ All services stopped")

if __name__ == "__main__":
    main()