#!/usr/bin/env python3
"""
🔗 GET REAL URL - Shows the actual working URL
"""

import subprocess
import logging
import time
import signal
import sys
import os
import socket
from pathlib import Path
import threading
import queue

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

server_process = None
tunnel_process = None
url_queue = queue.Queue()

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
    
    kill_port_8005()
    
    current_dir = Path(__file__).parent
    server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir / "src") + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting server...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
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

def read_tunnel_output(process, url_queue):
    """Read tunnel output to capture the real URL"""
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            line = line.decode('utf-8').strip()
            logger.info(f"📡 Tunnel: {line}")
            
            # Look for URLs in the output
            if 'https://' in line and ('serveo.net' in line or 'localhost.run' in line):
                # Extract URL
                parts = line.split()
                for part in parts:
                    if 'https://' in part and ('serveo.net' in part or 'localhost.run' in part):
                        url_queue.put(part)
                        
    except Exception as e:
        logger.info(f"⚠️ Tunnel reader error: {e}")

def create_global_access():
    """Create tunnel and capture the real URL"""
    global tunnel_process
    
    logger.info("🌍 Creating global access...")
    logger.info("⏳ This will show the REAL working URL...")
    
    # Try serveo.net (more reliable for showing URLs)
    try:
        tunnel_process = subprocess.Popen([
            'ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-R', '80:127.0.0.1:8005', 'serveo.net'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        # Start thread to read output
        reader_thread = threading.Thread(target=read_tunnel_output, args=(tunnel_process, url_queue))
        reader_thread.daemon = True
        reader_thread.start()
        
        logger.info("⏳ Waiting for tunnel URL...")
        
        # Wait for URL to appear
        for attempt in range(30):  # 30 seconds
            try:
                url = url_queue.get(timeout=1)
                logger.info("")
                logger.info("🎉 REAL URL FOUND!")
                logger.info("=" * 60)
                logger.info(f"🔗 YOUR WORKING URL: {url}")
                logger.info(f"🔗 WORKBENCH: {url}/workbench")
                logger.info("📱 These URLs work from anywhere in the world!")
                logger.info("=" * 60)
                return url
            except queue.Empty:
                logger.info(f"⏳ Still waiting... ({attempt + 1}/30)")
                continue
        
        logger.info("⚠️ URL not captured, but tunnel may be working")
        logger.info("🔍 Check the output above for https:// URLs")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed: {e}")
        return False

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🔗 GET REAL URL - Shows the actual working URL")
    logger.info("=" * 60)
    
    # Start server
    if not start_server():
        logger.error("❌ Server failed to start")
        return
    
    # Create tunnel and get real URL
    real_url = create_global_access()
    
    if real_url:
        logger.info("")
        logger.info("🌟 YOUR ROBECO APP IS NOW ONLINE!")
        logger.info("📝 Copy the URL above and share it worldwide!")
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
    else:
        logger.error("❌ Failed to get URL")

if __name__ == "__main__":
    main()