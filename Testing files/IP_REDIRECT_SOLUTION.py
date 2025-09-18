#!/usr/bin/env python3
"""
🎯 IP REDIRECT SOLUTION - Fixed IP that auto-redirects to serveo
🔗 Users access: http://138.199.60.185:8005 
🔄 Auto-redirects to current serveo URL
✅ Users always use same IP, system handles changing URLs
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
from flask import Flask, redirect
import re

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

server_process = None
tunnel_process = None
redirect_app = None
redirect_thread = None
current_serveo_url = None
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

def kill_ports():
    """Kill processes on ports 8005 and 8006"""
    commands = [
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', '8005'],
        ['pkill', '-9', '-f', '8006']
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, capture_output=True, check=False)
        except:
            pass
    
    # Kill by port numbers
    for port in [8005, 8006]:
        try:
            result = subprocess.run(['lsof', f'-ti:{port}'], capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid:
                        subprocess.run(['kill', '-9', pid], check=False)
        except:
            pass
    
    time.sleep(2)

def start_robeco_server():
    """Start main Robeco server on port 8005"""
    global server_process
    
    current_dir = Path(__file__).parent
    server_path = current_dir / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(current_dir / "src") + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting Robeco server on port 8005...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    time.sleep(8)
    
    # Check if running
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', 8005)) == 0:
                    logger.info("✅ Robeco server running on port 8005")
                    return True
        except:
            pass
        time.sleep(1)
    
    return False

def read_tunnel_output(process, url_queue):
    """Read tunnel output to capture serveo URL"""
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            line = line.decode('utf-8').strip()
            
            # Look for serveo URL
            if 'https://' in line and 'serveo.net' in line:
                # Extract URL using regex
                url_match = re.search(r'https://[a-f0-9]+\.serveo\.net', line)
                if url_match:
                    url = url_match.group(0)
                    url_queue.put(url)
                        
    except Exception as e:
        logger.info(f"⚠️ Tunnel reader error: {e}")

def create_serveo_tunnel():
    """Create serveo tunnel and capture URL"""
    global tunnel_process, current_serveo_url
    
    logger.info("📡 Creating serveo tunnel...")
    
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
        
        # Wait for URL
        for attempt in range(20):
            try:
                url = url_queue.get(timeout=1)
                current_serveo_url = url
                logger.info(f"✅ Serveo URL captured: {url}")
                return url
            except queue.Empty:
                continue
        
        logger.warning("⚠️ URL not captured automatically")
        return None
        
    except Exception as e:
        logger.error(f"❌ Tunnel failed: {e}")
        return False

def create_redirect_server():
    """Create redirect server on port 8006"""
    global current_serveo_url
    
    app = Flask(__name__)
    
    @app.route('/')
    def redirect_root():
        if current_serveo_url:
            return redirect(current_serveo_url)
        else:
            return f"""
            <h1>🔄 Robeco Redirect Service</h1>
            <p>⏳ Connecting to global server...</p>
            <p>Please wait a moment and refresh this page.</p>
            <script>setTimeout(function(){{location.reload();}}, 3000);</script>
            """
    
    @app.route('/<path:path>')
    def redirect_path(path):
        if current_serveo_url:
            return redirect(f"{current_serveo_url}/{path}")
        else:
            return redirect('/')
    
    # Run on port 8006 (different from main app)
    logger.info("🔄 Starting redirect server on port 8006...")
    
    def run_app():
        app.run(host='0.0.0.0', port=8006, debug=False, use_reloader=False)
    
    redirect_thread = threading.Thread(target=run_app)
    redirect_thread.daemon = True
    redirect_thread.start()
    
    time.sleep(3)
    
    # Test if redirect server is running
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('127.0.0.1', 8006)) == 0:
                logger.info("✅ Redirect server running on port 8006")
                return True
    except:
        pass
    
    return False

def display_access_info():
    """Display access information"""
    logger.info("")
    logger.info("🎉 IP REDIRECT SOLUTION ACTIVE!")
    logger.info("=" * 70)
    logger.info("🎯 FIXED IP ACCESS FOR USERS:")
    logger.info("   📍 Main App: http://138.199.60.185:8006")
    logger.info("   📍 Workbench: http://138.199.60.185:8006/workbench")
    logger.info("")
    logger.info("🔄 DIRECT SERVEO ACCESS:")
    if current_serveo_url:
        logger.info(f"   🌍 Global URL: {current_serveo_url}")
        logger.info(f"   🌍 Workbench: {current_serveo_url}/workbench")
    logger.info("")
    logger.info("✅ HOW IT WORKS:")
    logger.info("   • Users access your IP: http://138.199.60.185:8006")
    logger.info("   • System auto-redirects to current serveo URL")
    logger.info("   • Users always use same IP address")
    logger.info("   • Backend handles changing serveo URLs")
    logger.info("")
    logger.info("📱 SHARE THIS WITH USERS: http://138.199.60.185:8006")
    logger.info("=" * 70)

def main():
    """Main function"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🎯 IP REDIRECT SOLUTION")
    logger.info("🔗 Fixed IP: http://138.199.60.185:8006")
    logger.info("🔄 Auto-redirects to serveo tunnel")
    logger.info("=" * 60)
    
    # Kill existing processes
    kill_ports()
    
    # Start main Robeco server
    if not start_robeco_server():
        logger.error("❌ Robeco server failed to start")
        return
    
    # Create serveo tunnel
    serveo_url = create_serveo_tunnel()
    if not serveo_url:
        logger.error("❌ Serveo tunnel failed")
        return
    
    # Start redirect server
    if not create_redirect_server():
        logger.error("❌ Redirect server failed")
        return
    
    # Display access info
    display_access_info()
    
    logger.info("")
    logger.info("⌨️ Press Ctrl+C to stop all services")
    
    # Keep running
    try:
        while True:
            time.sleep(5)
            
            # Check if processes are still running
            if server_process and server_process.poll() is not None:
                logger.error("❌ Robeco server stopped")
                break
            
            # Monitor for new serveo URLs (in case it changes)
            try:
                new_url = url_queue.get_nowait()
                if new_url != current_serveo_url:
                    current_serveo_url = new_url
                    logger.info(f"🔄 Updated serveo URL: {new_url}")
            except queue.Empty:
                pass
                
    except KeyboardInterrupt:
        logger.info("\n🛑 Stopping all services...")
    finally:
        cleanup()
        logger.info("✅ All services stopped")

if __name__ == "__main__":
    main()