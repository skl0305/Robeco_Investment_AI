#!/usr/bin/env python3
"""
Universal Deployment System - Works on ANY Computer
No router configuration needed - automatic internet access
"""

import subprocess
import sys
import os
import time
import logging
import json
import requests
import socket
from pathlib import Path
import threading
import signal

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UniversalDeployment:
    def __init__(self):
        self.server_process = None
        self.tunnel_process = None
        self.public_url = None
        self.local_ip = None
        self.public_ip = None
        
    def get_network_info(self):
        """Get network information"""
        try:
            # Get local IP
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                self.local_ip = s.getsockname()[0]
            
            # Get public IP
            try:
                response = requests.get('https://ifconfig.me', timeout=5)
                self.public_ip = response.text.strip()
            except:
                self.public_ip = "Unable to detect"
                
            logger.info(f"📍 Local IP: {self.local_ip}")
            logger.info(f"📍 Public IP: {self.public_ip}")
            
        except Exception as e:
            logger.error(f"❌ Network detection failed: {e}")
    
    def check_cloudflared(self):
        """Check if cloudflared is available"""
        try:
            result = subprocess.run(['cloudflared', '--version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ Cloudflared is available")
                return True
        except FileNotFoundError:
            pass
        except Exception:
            pass
        return False
    
    def install_cloudflared(self):
        """Install cloudflared tunnel service"""
        logger.info("📦 Installing Cloudflare Tunnel (cloudflared)...")
        
        try:
            # For macOS
            if sys.platform == "darwin":
                subprocess.run(['brew', 'install', 'cloudflared'], check=True)
            # For Linux
            elif sys.platform.startswith("linux"):
                # Download and install cloudflared
                subprocess.run([
                    'wget', 
                    'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64',
                    '-O', '/tmp/cloudflared'
                ], check=True)
                subprocess.run(['chmod', '+x', '/tmp/cloudflared'], check=True)
                subprocess.run(['sudo', 'mv', '/tmp/cloudflared', '/usr/local/bin/'], check=True)
            else:
                logger.error("❌ Unsupported operating system")
                return False
                
            logger.info("✅ Cloudflared installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Installation failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("❌ Package manager not found (brew/wget)")
            return False
    
    def create_tunnel(self):
        """Create a cloudflare tunnel for port 8005"""
        logger.info("🌐 Creating secure tunnel...")
        
        try:
            # Start cloudflared tunnel
            self.tunnel_process = subprocess.Popen([
                'cloudflared', 'tunnel', '--url', 'http://localhost:8005'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait for tunnel to establish and get URL
            time.sleep(5)
            
            # Try to get tunnel info from cloudflared
            try:
                result = subprocess.run([
                    'curl', '-s', 'http://127.0.0.1:44512/metrics'
                ], capture_output=True, text=True, timeout=5)
                
                # Parse metrics for tunnel URL (this is a simplified approach)
                # In reality, we'd monitor the cloudflared output
                logger.info("🔄 Tunnel establishing... checking status...")
                
            except:
                pass
            
            # Check if process is still running
            if self.tunnel_process.poll() is None:
                logger.info("✅ Tunnel process started successfully")
                # For now, we'll use a placeholder URL and monitor output
                logger.info("🔄 Waiting for tunnel URL from cloudflared output...")
                return True
            else:
                logger.error("❌ Tunnel process failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Tunnel creation failed: {e}")
            return False
    
    def monitor_tunnel_output(self):
        """Monitor tunnel output for the public URL"""
        if not self.tunnel_process:
            return
            
        def read_output():
            try:
                for line in iter(self.tunnel_process.stderr.readline, ''):
                    if not line:
                        break
                    line = line.strip()
                    logger.info(f"🔗 Tunnel: {line}")
                    
                    # Look for the tunnel URL in output
                    if 'trycloudflare.com' in line or 'cfargotunnel.com' in line:
                        # Extract URL from cloudflared output
                        import re
                        url_match = re.search(r'https://[a-zA-Z0-9-]+\.trycloudflare\.com', line)
                        if url_match:
                            self.public_url = url_match.group(0)
                            logger.info("🎉 TUNNEL ESTABLISHED!")
                            logger.info("=" * 80)
                            logger.info("🌍 UNIVERSAL ACCESS URLS - WORKS ANYWHERE:")
                            logger.info("=" * 80)
                            logger.info(f"📍 Main App: {self.public_url}/")
                            logger.info(f"📍 Workbench: {self.public_url}/workbench")
                            logger.info("=" * 80)
                            logger.info("🌐 Share these URLs with ANYONE, ANYWHERE!")
                            logger.info("✅ No router configuration needed!")
                            logger.info("=" * 80)
                            break
            except Exception as e:
                logger.debug(f"Output monitoring error: {e}")
        
        # Start monitoring in background thread
        monitor_thread = threading.Thread(target=read_output, daemon=True)
        monitor_thread.start()
    
    def start_server(self):
        """Start the Robeco server"""
        logger.info("🚀 Starting Robeco Professional System...")
        
        project_root = Path(__file__).parent
        server_script = project_root / "run_professional_system.py"
        
        if not server_script.exists():
            logger.error("❌ Server script not found")
            return False
        
        try:
            # Start server in background
            env = os.environ.copy()
            env['PYTHONPATH'] = str(project_root / "src") + os.pathsep + env.get('PYTHONPATH', '')
            
            self.server_process = subprocess.Popen([
                sys.executable, str(server_script)
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for server to start
            time.sleep(3)
            
            # Check if server is running
            if self.server_process.poll() is None:
                logger.info("✅ Robeco server started successfully")
                return True
            else:
                logger.error("❌ Server failed to start")
                return False
                
        except Exception as e:
            logger.error(f"❌ Server startup failed: {e}")
            return False
    
    def cleanup(self):
        """Clean up processes"""
        logger.info("🧹 Cleaning up...")
        
        if self.tunnel_process:
            self.tunnel_process.terminate()
            try:
                self.tunnel_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.tunnel_process.kill()
        
        if self.server_process:
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
    
    def deploy(self):
        """Main deployment function"""
        logger.info("🚀 Universal Deployment - Works on ANY Computer!")
        logger.info("=" * 60)
        
        # Setup signal handler for cleanup
        def signal_handler(sig, frame):
            logger.info("\n🛑 Shutdown requested...")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Get network info
        self.get_network_info()
        
        # Check and install cloudflared if needed
        if not self.check_cloudflared():
            logger.info("📦 Cloudflared not found, installing...")
            if not self.install_cloudflared():
                logger.error("❌ Failed to install tunnel service")
                logger.info("💡 Alternative: Use ngrok or manual router setup")
                return False
        
        # Start server
        if not self.start_server():
            return False
        
        # Wait for server to be ready
        time.sleep(5)
        
        # Create tunnel
        if not self.create_tunnel():
            logger.error("❌ Tunnel creation failed")
            self.cleanup()
            return False
        
        # Monitor tunnel output
        self.monitor_tunnel_output()
        
        # Keep running
        logger.info("\n💡 System Status:")
        logger.info("✅ Server: Running on port 8005")
        logger.info("✅ Tunnel: Active (monitoring for URL)")
        logger.info(f"📍 Local Access: http://{self.local_ip}:8005/")
        logger.info("\n⌨️  Press Ctrl+C to stop all services")
        
        try:
            # Keep the deployment running
            while True:
                time.sleep(1)
                
                # Check if processes are still running
                if self.server_process and self.server_process.poll() is not None:
                    logger.error("❌ Server process died")
                    break
                    
                if self.tunnel_process and self.tunnel_process.poll() is not None:
                    logger.error("❌ Tunnel process died")
                    break
                    
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup()

def main():
    """Main function"""
    deployment = UniversalDeployment()
    deployment.deploy()

if __name__ == "__main__":
    main()