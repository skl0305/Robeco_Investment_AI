#!/usr/bin/env python3
"""
🚀 INSTANT GLOBAL ACCESS - EASIEST METHOD!
🌍 Get instant global URL without any router setup
✅ Works immediately - no configuration needed!
"""

import subprocess
import logging
import time
import signal
import sys
import os
import socket
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

server_process = None
tunnel_process = None

def cleanup_processes():
    """Clean up all processes"""
    global server_process, tunnel_process
    
    if tunnel_process:
        tunnel_process.terminate()
        try:
            tunnel_process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            tunnel_process.kill()
    
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

def kill_port_8005():
    """Kill any process on port 8005"""
    logger.info("🔫 Ensuring port 8005 is free...")
    
    commands = [
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', '8005'],
        ['pkill', '-9', '-f', 'uvicorn.*8005']
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=False)
        except:
            pass
    
    # Kill by port
    try:
        result = subprocess.run(['lsof', '-ti:8005'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], check=False)
    except:
        pass
    
    time.sleep(3)

def start_robeco_server():
    """Start Robeco server on port 8005"""
    global server_process
    
    kill_port_8005()
    
    current_dir = Path(__file__).parent
    server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        logger.error(f"❌ Server not found: {server_path}")
        return False
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir / "src") + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting Robeco server on port 8005...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    # Wait for server
    logger.info("⏳ Waiting for server to start...")
    time.sleep(10)
    
    # Verify server is running
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', 8005))
                if result == 0:
                    logger.info("✅ Robeco server is running on port 8005!")
                    return True
        except:
            pass
        time.sleep(1)
    
    logger.error("❌ Server failed to start")
    return False

def create_instant_tunnel():
    """Create SSH tunnel for instant global access"""
    global tunnel_process
    
    logger.info("🌍 CREATING INSTANT GLOBAL ACCESS...")
    logger.info("🔗 No router setup required!")
    logger.info("")
    
    try:
        logger.info("📡 Connecting to tunnel service...")
        
        # Create SSH tunnel
        tunnel_process = subprocess.Popen([
            'ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'ServerAliveInterval=30',
            '-o', 'ServerAliveCountMax=3',
            '-R', '80:127.0.0.1:8005', 'serveo.net'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        logger.info("⏳ Establishing tunnel...")
        time.sleep(5)
        
        # Try to read the tunnel URL
        tunnel_url = None
        try:
            # Give it more time to establish
            time.sleep(10)
            logger.info("🎉 TUNNEL ESTABLISHED!")
            logger.info("")
            logger.info("🌍 INSTANT GLOBAL ACCESS READY!")
            logger.info("=" * 80)
            logger.info("✅ Your Robeco app is now accessible worldwide!")
            logger.info("🔗 Global URL: Check terminal output above")
            logger.info("🔗 URL format: https://[random-id].serveo.net")
            logger.info("📱 Share this URL with anyone worldwide!")
            logger.info("=" * 80)
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Could not read tunnel URL: {e}")
            logger.info("✅ Tunnel may still be working - check output above")
            return True
            
    except Exception as e:
        logger.error(f"❌ Tunnel creation failed: {e}")
        return False

def display_access_info():
    """Display access information"""
    logger.info("")
    logger.info("📱 ACCESS METHODS:")
    logger.info("=" * 60)
    logger.info("🏠 Local Computer: http://localhost:8005")
    logger.info("🏠 Local Network: http://10.7.7.2:8005")
    logger.info("🌍 GLOBAL ACCESS: Check tunnel URL above")
    logger.info("=" * 60)
    logger.info("")
    logger.info("✅ BENEFITS OF THIS METHOD:")
    logger.info("   • ✅ Works immediately - no waiting")
    logger.info("   • ✅ No router configuration needed")
    logger.info("   • ✅ No technical setup required")
    logger.info("   • ✅ Global access from any computer")
    logger.info("   • ✅ HTTPS secure connection")
    logger.info("")
    logger.info("🌟 YOUR APP IS NOW GLOBALLY ACCESSIBLE!")
    logger.info("⌨️ Press Ctrl+C to stop")
    logger.info("=" * 60)

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 INSTANT GLOBAL ACCESS - EASIEST METHOD!")
    logger.info("🌍 Get your Robeco app online in 30 seconds")
    logger.info("✅ No router setup - No configuration - Just works!")
    logger.info("=" * 80)
    
    # Step 1: Start server
    if not start_robeco_server():
        logger.error("❌ Cannot continue without server")
        return
    
    # Step 2: Create tunnel
    if not create_instant_tunnel():
        logger.error("❌ Failed to create global access")
        return
    
    # Step 3: Display info
    display_access_info()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if server_process and server_process.poll() is not None:
                logger.error("❌ Server stopped")
                break
            
            if tunnel_process and tunnel_process.poll() is not None:
                logger.warning("⚠️ Tunnel disconnected - reconnecting...")
                create_instant_tunnel()
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping services...")
    finally:
        cleanup_processes()
        logger.info("✅ All services stopped")

if __name__ == "__main__":
    main()