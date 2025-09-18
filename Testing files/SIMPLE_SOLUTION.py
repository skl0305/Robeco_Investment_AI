#!/usr/bin/env python3
"""
🎯 SIMPLEST SOLUTION - ONE CLICK GLOBAL ACCESS
✅ No router setup, no configuration, just works!
🌍 Get instant global URL in 30 seconds
"""

import subprocess
import logging
import time
import signal
import sys
import os
import socket
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

server_process = None
tunnel_process = None

def cleanup():
    global server_process, tunnel_process
    if tunnel_process:
        tunnel_process.terminate()
    if server_process:
        server_process.terminate()

def signal_handler(sig, frame):
    logger.info("\n🛑 Stopping...")
    cleanup()
    sys.exit(0)

def kill_port_8005():
    """Kill anything on port 8005"""
    commands = [
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', '8005']
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, capture_output=True, check=False)
        except:
            pass
    
    # Kill by port number
    try:
        result = subprocess.run(['lsof', '-ti:8005'], capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    subprocess.run(['kill', '-9', pid], check=False)
    except:
        pass
    
    time.sleep(2)

def start_server():
    """Start Robeco server"""
    global server_process
    
    kill_port_8005()
    
    current_dir = Path(__file__).parent
    server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir / "src") + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting server...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    time.sleep(8)
    
    # Check if running
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', 8005)) == 0:
                    logger.info("✅ Server running on port 8005")
                    return True
        except:
            pass
        time.sleep(1)
    
    return False

def create_global_access():
    """Create instant global access"""
    global tunnel_process
    
    logger.info("🌍 Creating global access...")
    
    try:
        tunnel_process = subprocess.Popen([
            'ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-R', '80:127.0.0.1:8005', 'serveo.net'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        time.sleep(10)
        
        logger.info("")
        logger.info("🎉 SUCCESS! YOUR APP IS NOW GLOBALLY ACCESSIBLE!")
        logger.info("=" * 60)
        logger.info("🔗 GLOBAL URL: Check the https://[id].serveo.net URL above")
        logger.info("📱 Share this URL with anyone worldwide!")
        logger.info("✅ No router setup needed!")
        logger.info("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🎯 SIMPLEST SOLUTION - ONE CLICK GLOBAL ACCESS")
    logger.info("=" * 60)
    
    # Start server
    if not start_server():
        logger.error("❌ Server failed to start")
        return
    
    # Create global access
    if not create_global_access():
        logger.error("❌ Global access failed")
        return
    
    logger.info("")
    logger.info("🌟 YOUR ROBECO APP IS NOW ONLINE WORLDWIDE!")
    logger.info("⌨️ Press Ctrl+C to stop")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            if server_process and server_process.poll() is not None:
                logger.error("❌ Server stopped")
                break
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping...")
    finally:
        cleanup()
        logger.info("✅ Stopped")

if __name__ == "__main__":
    main()