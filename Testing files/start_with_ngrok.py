#!/usr/bin/env python3
"""
Robeco Professional System - NGROK Integration
Provides instant global access using ngrok tunneling
"""

import sys
import os
import subprocess
import logging
import time
import signal
import threading
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for process management
server_process = None
ngrok_url = None

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

def setup_ngrok_tunnel():
    """Setup ngrok tunnel for global access"""
    global ngrok_url
    
    try:
        import ngrok
        
        logger.info("🚀 Setting up ngrok tunnel...")
        
        # Set the authtoken
        authtoken = "32icGzoNAvSORFv3anOyE7Qeon6_6qzfyfbDaCh4AekUVWiZi"
        ngrok.set_auth_token(authtoken)
        
        # Create tunnel to port 8005 - correct API
        listener = ngrok.forward(8005, authtoken=authtoken)
        ngrok_url = listener.url()
        
        logger.info("🎉 NGROK TUNNEL CREATED!")
        logger.info("=" * 80)
        logger.info("🌍 YOUR GLOBAL URL:")
        logger.info(f"🔗 {ngrok_url}")
        logger.info("=" * 80)
        logger.info("✅ Share this URL with ANYONE worldwide!")
        logger.info("✅ No HTTP 502 errors!")
        logger.info("✅ Professional ngrok reliability!")
        logger.info("=" * 80)
        
        return True
        
    except ImportError:
        logger.error("❌ ngrok package not installed. Run: pip install ngrok")
        return False
    except Exception as e:
        logger.error(f"❌ ngrok tunnel failed: {e}")
        logger.info("💡 Let's try alternative ngrok method...")
        
        # Try alternative ngrok approach
        try:
            import ngrok
            # Alternative method
            tunnel = ngrok.connect(8005, auth_token=authtoken)
            ngrok_url = tunnel.public_url
            
            logger.info("🎉 NGROK TUNNEL CREATED (Alternative method)!")
            logger.info("=" * 80)
            logger.info("🌍 YOUR GLOBAL URL:")
            logger.info(f"🔗 {ngrok_url}")
            logger.info("=" * 80)
            logger.info("✅ Share this URL with ANYONE worldwide!")
            logger.info("=" * 80)
            
            return True
        except Exception as e2:
            logger.error(f"❌ Alternative ngrok method also failed: {e2}")
            logger.info("💡 Fallback: Use manual SSH tunnel method")
            return False

def cleanup_processes():
    """Clean up all processes"""
    global server_process
    
    logger.info("🧹 Cleaning up...")
    
    try:
        import ngrok
        ngrok.kill()
        logger.info("✅ ngrok tunnel closed")
    except:
        pass
    
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
    """Launch server with ngrok tunnel"""
    global server_process, ngrok_url
    
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
    logger.info("🌍 GLOBAL ACCESS with NGROK - Enterprise reliability!")
    logger.info("✅ No HTTP 502 errors!")
    logger.info("✅ Professional tunnel solution!")
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
        
        # Verify server is accessible
        import socket
        server_ready = False
        
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
            
            # Verify localhost accessibility
            logger.info("🔍 Verifying server accessibility...")
            try:
                import requests
                response = requests.get('http://127.0.0.1:8005/', timeout=3)
                logger.info("✅ Server confirmed accessible for tunneling")
            except:
                logger.warning("⚠️ Server may have connectivity issues")
            
            # Setup ngrok tunnel
            tunnel_success = setup_ngrok_tunnel()
            
            # Display final access information
            logger.info("")
            logger.info("🎉 SERVER IS RUNNING!")
            logger.info("=" * 80)
            logger.info("📱 ACCESS URLS:")
            logger.info("=" * 80)
            logger.info(f"🏠 Local Access: http://{local_ip}:8005/")
            logger.info(f"🔧 Localhost: http://127.0.0.1:8005/")
            
            if tunnel_success and ngrok_url:
                logger.info(f"🌍 GLOBAL ACCESS: {ngrok_url}")
                logger.info(f"🔧 GLOBAL WORKBENCH: {ngrok_url}/workbench")
                logger.info("✅ ngrok tunnel active - share worldwide!")
            else:
                logger.info("⚠️ ngrok tunnel failed - using local access only")
                logger.info("💡 Manual tunnel: ssh -R 80:127.0.0.1:8005 serveo.net")
            
            logger.info("=" * 80)
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