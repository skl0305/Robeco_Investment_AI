#!/usr/bin/env python3
"""
Instant Deploy - Works on ANY Computer, ANY Network
No router setup needed - automatic public URLs
"""

import subprocess
import sys
import os
import time
import logging
import requests
import socket
import json
from pathlib import Path
import threading

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_network_info():
    """Get current network information"""
    try:
        # Get local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
        
        # Get public IP
        try:
            response = requests.get('https://ifconfig.me', timeout=5)
            public_ip = response.text.strip()
        except:
            public_ip = "Unable to detect"
            
        return local_ip, public_ip
    except Exception as e:
        logger.error(f"❌ Network detection failed: {e}")
        return "127.0.0.1", "Unknown"

def check_ngrok():
    """Check if ngrok is installed"""
    try:
        result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✅ ngrok is available")
            return True
    except FileNotFoundError:
        pass
    return False

def install_ngrok():
    """Install ngrok"""
    logger.info("📦 Installing ngrok...")
    
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(['brew', 'install', 'ngrok/ngrok/ngrok'], check=True)
        else:
            logger.info("💡 Please install ngrok manually:")
            logger.info("   Visit: https://ngrok.com/download")
            logger.info("   Download and install ngrok")
            return False
        
        logger.info("✅ ngrok installed successfully")
        return True
        
    except subprocess.CalledProcessError:
        logger.error("❌ ngrok installation failed")
        return False
    except FileNotFoundError:
        logger.error("❌ brew not found - install ngrok manually")
        return False

def setup_ngrok_auth():
    """Setup ngrok authentication (optional but recommended)"""
    logger.info("🔐 Setting up ngrok authentication...")
    logger.info("📋 Get your free auth token:")
    logger.info("   1. Visit: https://dashboard.ngrok.com/get-started/your-authtoken")
    logger.info("   2. Sign up/login (free)")
    logger.info("   3. Copy your authtoken")
    
    token = input("\n🔑 Paste your ngrok authtoken (or press Enter to skip): ").strip()
    
    if token:
        try:
            subprocess.run(['ngrok', 'authtoken', token], check=True)
            logger.info("✅ ngrok authenticated successfully")
            return True
        except subprocess.CalledProcessError:
            logger.error("❌ ngrok authentication failed")
    else:
        logger.info("⚠️  Skipping auth - limited to 2 hour sessions")
    
    return True

def start_ngrok_tunnel():
    """Start ngrok tunnel for port 8005"""
    logger.info("🌐 Creating secure tunnel...")
    
    try:
        # Start ngrok tunnel
        process = subprocess.Popen([
            'ngrok', 'http', '8005', '--log=stdout'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait for tunnel to establish
        time.sleep(3)
        
        # Get tunnel URL from ngrok API
        try:
            response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get('tunnels', [])
                if tunnels:
                    public_url = tunnels[0]['public_url']
                    logger.info("🎉 TUNNEL ESTABLISHED!")
                    logger.info("=" * 80)
                    logger.info("🌍 UNIVERSAL ACCESS URLS - SHARE WITH ANYONE:")
                    logger.info("=" * 80)
                    logger.info(f"📍 Main App: {public_url}/")
                    logger.info(f"📍 Workbench: {public_url}/workbench")
                    logger.info("=" * 80)
                    logger.info("🌐 These URLs work from ANY computer, ANY network!")
                    logger.info("✅ No router configuration needed!")
                    logger.info("📱 Copy and share these URLs worldwide!")
                    logger.info("=" * 80)
                    return process, public_url
        except Exception as e:
            logger.debug(f"API check failed: {e}")
        
        logger.info("🔄 Tunnel started, check http://localhost:4040 for URL")
        return process, None
        
    except Exception as e:
        logger.error(f"❌ Tunnel creation failed: {e}")
        return None, None

def start_robeco_server():
    """Start the Robeco server"""
    logger.info("🚀 Starting Robeco Professional System...")
    
    project_root = Path(__file__).parent
    server_script = project_root / "run_professional_system.py"
    
    try:
        env = os.environ.copy()
        env['PYTHONPATH'] = str(project_root / "src") + os.pathsep + env.get('PYTHONPATH', '')
        
        process = subprocess.Popen([
            sys.executable, str(server_script)
        ], env=env)
        
        # Wait for server to start
        time.sleep(5)
        
        # Check if server is running
        if process.poll() is None:
            logger.info("✅ Robeco server started successfully")
            return process
        else:
            logger.error("❌ Server failed to start")
            return None
            
    except Exception as e:
        logger.error(f"❌ Server startup failed: {e}")
        return None

def main():
    """Main deployment function"""
    logger.info("🚀 Instant Deploy - Universal Access System")
    logger.info("🌍 Works on ANY computer, ANY network, NO router setup!")
    logger.info("=" * 60)
    
    # Get network info
    local_ip, public_ip = get_network_info()
    logger.info(f"📍 Current Local IP: {local_ip}")
    logger.info(f"📍 Current Public IP: {public_ip}")
    logger.info("")
    
    # Check ngrok
    if not check_ngrok():
        logger.info("📦 ngrok not found, installing...")
        if not install_ngrok():
            logger.error("❌ Please install ngrok manually and try again")
            return
    
    # Setup auth (optional)
    if not setup_ngrok_auth():
        return
    
    logger.info("")
    logger.info("🔧 Starting deployment...")
    
    # Start Robeco server
    server_process = start_robeco_server()
    if not server_process:
        return
    
    # Start tunnel
    tunnel_process, public_url = start_ngrok_tunnel()
    if not tunnel_process:
        logger.error("❌ Tunnel failed to start")
        server_process.terminate()
        return
    
    # Display status
    logger.info("")
    logger.info("💡 Deployment Status:")
    logger.info("✅ Robeco Server: Running on port 8005")
    logger.info("✅ Secure Tunnel: Active")
    logger.info(f"📍 Local Access: http://{local_ip}:8005/")
    if public_url:
        logger.info(f"📍 Global Access: {public_url}/")
    logger.info("📊 Tunnel Dashboard: http://localhost:4040")
    logger.info("")
    logger.info("⌨️  Press Ctrl+C to stop all services")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process.poll() is not None:
                logger.error("❌ Server process stopped")
                break
            
            if tunnel_process.poll() is not None:
                logger.error("❌ Tunnel process stopped")
                break
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Shutdown requested...")
    
    finally:
        # Cleanup
        logger.info("🧹 Cleaning up...")
        if tunnel_process:
            tunnel_process.terminate()
        if server_process:
            server_process.terminate()
        logger.info("✅ All services stopped")

if __name__ == "__main__":
    main()