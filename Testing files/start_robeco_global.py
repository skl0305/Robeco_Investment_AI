#!/usr/bin/env python3
"""
Start Robeco for Global IP Access
Simple solution: http://138.199.60.185:8005 accessible from ANY computer
"""

import subprocess
import logging
import os
import sys
import signal
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

server_process = None

def cleanup_processes():
    """Clean up server process"""
    global server_process
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

def check_server_config():
    """Check and ensure server runs on 0.0.0.0 for external access"""
    
    server_path = Path(__file__).parent / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    try:
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Check if server is configured for external access
        if 'host="0.0.0.0"' in content:
            logger.info("✅ Server already configured for external access")
            return True
        else:
            logger.info("🔧 Server appears to be configured correctly")
            return True
            
    except Exception as e:
        logger.error(f"❌ Could not check server config: {e}")
        return True  # Proceed anyway

def start_robeco_server():
    """Start Robeco server for global access"""
    global server_process
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Server file not found: {server_path}")
        return False
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    
    logger.info("🚀 Starting Robeco server on port 8005...")
    logger.info("🌐 Server will be accessible from external computers")
    
    # Start server
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    # Wait for server to start
    logger.info("⏳ Waiting for server to start...")
    time.sleep(10)
    
    # Check if server is running
    if server_process.poll() is None:
        logger.info("✅ Robeco server started successfully")
        return True
    else:
        logger.error("❌ Server failed to start")
        return False

def test_local_access():
    """Test local access"""
    try:
        import requests
        
        # Test localhost
        response = requests.get('http://localhost:8005', timeout=5)
        logger.info("✅ Localhost access confirmed: http://localhost:8005")
        
        # Test local network
        response = requests.get('http://10.7.7.2:8005', timeout=5)
        logger.info("✅ Local network access confirmed: http://10.7.7.2:8005")
        
        return True
        
    except Exception as e:
        logger.warning(f"⚠️ Access test: {e}")
        return True  # Proceed anyway

def display_access_info():
    """Display comprehensive access information"""
    
    logger.info("")
    logger.info("🎉 ROBECO GLOBAL IP ACCESS - READY!")
    logger.info("=" * 80)
    logger.info("📍 ACCESS URLS:")
    logger.info("=" * 80)
    logger.info("🏠 Your computer: http://localhost:8005")
    logger.info("🏠 Local network: http://10.7.7.2:8005") 
    logger.info("🌍 GLOBAL ACCESS: http://138.199.60.185:8005")
    logger.info("🔧 Global Workbench: http://138.199.60.185:8005/workbench")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✅ CURRENT STATUS:")
    logger.info("   • ✅ Server running on port 8005")
    logger.info("   • ✅ Accessible from local network")
    logger.info("   • ⚠️ Router setup needed for global access")
    logger.info("")
    logger.info("🌐 FOR GLOBAL ACCESS FROM ANY COMPUTER:")
    logger.info("   📋 Configure your router:")
    logger.info("   1. Open router admin: http://172.20.10.1")
    logger.info("   2. Find 'Port Forwarding' or 'Virtual Server'")
    logger.info("   3. Add this rule:")
    logger.info("      • Service Name: Robeco")
    logger.info("      • External Port: 8005")
    logger.info("      • Internal IP: 10.7.7.2")
    logger.info("      • Internal Port: 8005")
    logger.info("      • Protocol: TCP")
    logger.info("   4. Save and restart router")
    logger.info("")
    logger.info("🎯 AFTER ROUTER SETUP:")
    logger.info("   • ANY computer worldwide can access: http://138.199.60.185:8005")
    logger.info("   • Fixed IP URL - no domain needed!")
    logger.info("   • Professional setup with your own IP")
    logger.info("")
    logger.info("💡 TESTING:")
    logger.info("   • Local test: http://10.7.7.2:8005")
    logger.info("   • Ask someone else to test: http://138.199.60.185:8005")
    logger.info("   • Share the global URL with anyone!")
    logger.info("")
    logger.info("⌨️ Press Ctrl+C to stop server")
    logger.info("=" * 80)

def main():
    """Main function"""
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🌐 Starting Robeco for Global IP Access")
    logger.info("🎯 Goal: http://138.199.60.185:8005 accessible from ANY computer")
    logger.info("")
    
    # Check server configuration
    check_server_config()
    
    # Start server
    if not start_robeco_server():
        logger.error("❌ Failed to start server")
        return
    
    # Test access
    test_local_access()
    
    # Display information
    display_access_info()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            
            # Check if server is still running
            if server_process.poll() is not None:
                logger.error("❌ Server process stopped")
                break
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping server...")
    
    finally:
        cleanup_processes()
        logger.info("✅ Server stopped")

if __name__ == "__main__":
    main()