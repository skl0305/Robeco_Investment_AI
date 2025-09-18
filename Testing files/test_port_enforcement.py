#!/usr/bin/env python3
"""
Test Port 8005 Enforcement
Tests that the server can kill existing processes and claim port 8005
"""

import socket
import subprocess
import time
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def start_dummy_server_on_port_8005():
    """Start a simple HTTP server on port 8005 to simulate occupation"""
    try:
        # Start a simple Python HTTP server on port 8005
        process = subprocess.Popen([
            sys.executable, '-m', 'http.server', '8005'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for it to start
        time.sleep(2)
        
        # Verify it's running
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', 8005))
                if result == 0:
                    logger.info("✅ Dummy server started successfully on port 8005")
                    return process
                else:
                    logger.error("❌ Dummy server failed to start")
                    process.kill()
                    return None
        except Exception as e:
            logger.error(f"❌ Error checking dummy server: {e}")
            process.kill()
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to start dummy server: {e}")
        return None

def test_port_enforcement():
    """Test that our server can kill the dummy server and take port 8005"""
    logger.info("🧪 Testing Port 8005 Enforcement")
    logger.info("=" * 50)
    
    # Step 1: Start dummy server
    logger.info("1️⃣ Starting dummy server on port 8005...")
    dummy_process = start_dummy_server_on_port_8005()
    
    if not dummy_process:
        logger.error("❌ Could not start dummy server for testing")
        return False
    
    # Step 2: Try to start our server (which should kill the dummy)
    logger.info("2️⃣ Starting Robeco server (should kill dummy and claim port)...")
    
    try:
        # Import and test the force_use_port_8005 function
        sys.path.append(str(Path(__file__).parent / "src"))
        from robeco.backend.professional_streaming_server import force_use_port_8005
        
        # This should kill the dummy server and claim port 8005
        port = force_use_port_8005()
        
        if port == 8005:
            logger.info("✅ SUCCESS: Port enforcement worked!")
            logger.info("✅ Dummy server was killed and port 8005 claimed")
            
            # Verify dummy process is dead
            if dummy_process.poll() is not None:
                logger.info("✅ Dummy process confirmed dead")
            else:
                logger.warning("⚠️  Dummy process still alive but port was freed")
                dummy_process.kill()
            
            return True
        else:
            logger.error(f"❌ FAILED: Got port {port} instead of 8005")
            dummy_process.kill()
            return False
            
    except Exception as e:
        logger.error(f"❌ FAILED: Error during test: {e}")
        dummy_process.kill()
        return False

def main():
    """Run the port enforcement test"""
    logger.info("🚀 Port 8005 Enforcement Test")
    logger.info("Testing server's ability to kill existing processes on port 8005")
    logger.info("")
    
    success = test_port_enforcement()
    
    logger.info("")
    logger.info("=" * 50)
    if success:
        logger.info("🎉 TEST PASSED: Port enforcement works correctly!")
        logger.info("✅ Your server will always use port 8005")
    else:
        logger.info("❌ TEST FAILED: Port enforcement needs debugging")
        logger.info("⚠️  Server may not be able to claim port 8005 reliably")
    logger.info("=" * 50)

if __name__ == "__main__":
    main()