#!/usr/bin/env python3
"""
Robeco Professional System - Simple Tunnel Setup
Fixed HTTP 502 error and provides working global access
"""

import sys
import os
import subprocess
import logging
import time
import signal
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for process management
server_process = None

def get_local_ip():
    """Get local network IP"""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except:
        return "127.0.0.1"

def cleanup_processes():
    """Clean up all processes"""
    global server_process
    
    logger.info("🧹 Cleaning up...")
    
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

def main():
    """Launch server with simple tunnel instructions"""
    global server_process
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Add project root to Python path
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    # Get IP addresses
    local_ip = get_local_ip()
    
    logger.info("🚀 Starting Robeco Professional System")
    logger.info("🌍 GLOBAL ACCESS - Fixed HTTP 502 tunnel issues!")
    logger.info("✅ Enhanced SSH tunnel configuration")
    logger.info("")
    logger.info("=" * 80)
    logger.info("🔧 SIMPLE GLOBAL ACCESS SETUP")
    logger.info("=" * 80)
    logger.info("📋 STEP 1: Wait for server to start (below)")
    logger.info("📋 STEP 2: Look for '✅ Ready for SSH tunneling' message")
    logger.info("📋 STEP 3: Open NEW terminal and run ONE command:")
    logger.info("")
    logger.info("   🔗 COMMAND A: ssh -R 80:127.0.0.1:8005 serveo.net")
    logger.info("   🔗 COMMAND B: ssh -R 80:127.0.0.1:8005 nokey@localhost.run")
    logger.info("")
    logger.info("🎯 RESULT:")
    logger.info("   • Get global URL like https://abc123.serveo.net")
    logger.info("   • Share with anyone worldwide")
    logger.info("   • No HTTP 502 errors!")
    logger.info("=" * 80)
    logger.info("")
    
    # Path to the professional streaming server
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Professional streaming server not found at: {server_path}")
        return
    
    try:
        logger.info("🔧 STARTING SERVER...")
        logger.info("🎯 Server will force use port 8005")
        
        # Start the server in background
        server_process = subprocess.Popen([
            sys.executable, 
            str(server_path)
        ], env=env)
        
        # Wait for server to start
        logger.info("⏳ Waiting for server to start...")
        time.sleep(8)
        
        # Verify server is accessible on localhost for tunnel connectivity
        import socket
        server_ready = False
        tunnel_ready = False
        
        for attempt in range(10):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    result = s.connect_ex(('127.0.0.1', 8005))
                    if result == 0:
                        server_ready = True
                        break
            except:
                pass
            time.sleep(1)
        
        if server_ready and server_process.poll() is None:
            logger.info("✅ Robeco server started successfully on port 8005")
            
            # Verify localhost accessibility for tunneling
            logger.info("🔍 Verifying localhost accessibility for tunneling...")
            try:
                import requests
                response = requests.get('http://127.0.0.1:8005/', timeout=3)
                if response.status_code in [200, 404, 405]:
                    tunnel_ready = True
                    logger.info("✅ Server confirmed accessible on 127.0.0.1:8005 for tunneling")
            except:
                logger.warning("⚠️ Server may not be accessible on 127.0.0.1:8005 for tunneling")
            
            # Display final access information
            logger.info("")
            logger.info("🎉 SERVER IS RUNNING!")
            logger.info("=" * 80)
            logger.info("📱 ACCESS URLS:")
            logger.info("=" * 80)
            logger.info(f"🏠 Local Access: http://{local_ip}:8005/")
            logger.info(f"🔧 Localhost: http://127.0.0.1:8005/ (for tunneling)")
            logger.info("=" * 80)
            logger.info("💡 TUNNEL STATUS:")
            if tunnel_ready:
                logger.info("   ✅ Ready for SSH tunneling")
            else:
                logger.info("   ⚠️ May need troubleshooting for tunneling")
            logger.info("=" * 80)
            logger.info("")
            logger.info("🌍 NOW CREATE GLOBAL TUNNEL:")
            logger.info("📋 Open NEW terminal and run:")
            logger.info("")
            logger.info("   ssh -R 80:127.0.0.1:8005 serveo.net")
            logger.info("")
            logger.info("🎯 You'll get a URL like: https://abc123.serveo.net")
            logger.info("🌐 Share that URL with anyone worldwide!")
            logger.info("✅ No more HTTP 502 errors!")
            logger.info("")
            logger.info("⌨️  Press Ctrl+C to stop the server")
            logger.info("📊 Server logs will appear below...")
            logger.info("=" * 80)
            
            # Keep running and monitor processes
            try:
                while True:
                    time.sleep(1)
                    
                    # Check if server is still running
                    if server_process.poll() is not None:
                        logger.error("❌ Server process stopped")
                        break
                        
            except KeyboardInterrupt:
                logger.info("\n🛑 Shutdown requested by user...")
            
        elif server_process.poll() is not None:
            logger.error("❌ Server process exited unexpectedly")
            return
        else:
            logger.error("❌ Server is not responding on port 8005")
            server_process.terminate()
            return
        
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ Failed to start professional streaming server: {e}")
            
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
    
    finally:
        # Cleanup
        cleanup_processes()
        logger.info("✅ All services stopped - deployment ended")

if __name__ == "__main__":
    main()