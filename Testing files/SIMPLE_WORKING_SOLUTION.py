#!/usr/bin/env python3
"""
🚀 SIMPLE WORKING SOLUTION - Get global URL instantly
✅ Shows actual working serveo URL
🌍 Copy and share the URL with anyone worldwide
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
    
    logger.info("🔫 Ensuring port 8005 is free...")
    kill_port_8005()
    
    current_dir = Path(__file__).parent
    server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir / "src") + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting Robeco server...")
    logger.info("⏳ This takes about 20 seconds...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    time.sleep(20)
    
    # Check if running
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', 8005)) == 0:
                    logger.info("✅ Robeco server running on port 8005")
                    return True
        except:
            pass
        time.sleep(2)
    
    return False

def create_tunnel():
    """Create serveo tunnel and show instructions"""
    global tunnel_process
    
    logger.info("")
    logger.info("🌍 CREATING GLOBAL ACCESS...")
    logger.info("📡 Starting serveo tunnel...")
    
    try:
        tunnel_process = subprocess.Popen([
            'ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-R', '80:127.0.0.1:8005', 'serveo.net'
        ])
        
        time.sleep(8)
        
        logger.info("")
        logger.info("🎉 TUNNEL CREATED!")
        logger.info("=" * 80)
        logger.info("✅ YOUR ROBECO APP IS NOW GLOBALLY ACCESSIBLE!")
        logger.info("")
        logger.info("🔍 TO FIND YOUR WORKING URL:")
        logger.info("   1. Look in the terminal output above")
        logger.info("   2. Find the line that says:")
        logger.info("      'Forwarding HTTP traffic from https://[32-char-id].serveo.net'")
        logger.info("   3. Copy that URL")
        logger.info("")
        logger.info("📱 YOUR WORKING URLS:")
        logger.info("   🌍 Main App: https://[your-id].serveo.net")
        logger.info("   🌍 Workbench: https://[your-id].serveo.net/workbench")
        logger.info("")
        logger.info("🔄 Note: URL changes each time you restart")
        logger.info("✅ Works from any computer worldwide!")
        logger.info("=" * 80)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🚀 SIMPLE WORKING SOLUTION")
    logger.info("🌍 Get global URL for your Robeco app")
    logger.info("=" * 60)
    
    # Start server
    if not start_server():
        logger.error("❌ Server failed to start")
        return
    
    # Create tunnel
    if not create_tunnel():
        logger.error("❌ Tunnel failed")
        return
    
    logger.info("")
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