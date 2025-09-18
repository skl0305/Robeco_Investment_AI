#!/usr/bin/env python3
"""
🚀 ROBECO PROFESSIONAL SYSTEM - FREE GLOBAL ACCESS
✅ Simple SSH tunnel - No router setup needed!
🌍 Get random global URL each time
"""

import sys
import os
import subprocess
import logging
import time
import signal
import socket
import threading
import queue
import re
from pathlib import Path

# Simple logging for errors only
logging.basicConfig(
    level=logging.ERROR,
    format='%(message)s'
)
logger = logging.getLogger(__name__)

# Global variables
server_process = None
tunnel_process = None
url_queue = queue.Queue()
final_global_url = None

def cleanup():
    """Clean up processes"""
    global server_process, tunnel_process
    if tunnel_process:
        tunnel_process.terminate()
    if server_process:
        server_process.terminate()

def signal_handler(sig, frame):
    """Handle shutdown"""
    print("\n🛑 Stopping...")
    cleanup()
    sys.exit(0)

def start_server():
    """Start Robeco server"""
    global server_process
    
    project_root = Path(__file__).parent
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    if not server_path.exists():
        print(f"❌ Server not found: {server_path}")
        return False
    
    env = os.environ.copy()
    env['PYTHONPATH'] = str(project_root / "src") + os.pathsep + env.get('PYTHONPATH', '')
    
    print("🚀 Starting Robeco server...")
    print("⏳ This takes about 20 seconds...")
    
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    time.sleep(20)
    
    # Check if running
    for attempt in range(10):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(('127.0.0.1', 8005)) == 0:
                    print("✅ Server running on localhost:8005")
                    return True
        except:
            pass
        time.sleep(2)
    
    print("❌ Server failed to start")
    return False

def read_tunnel_output(process, url_queue):
    """Read tunnel output to capture URL"""
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            
            line = line.decode('utf-8').strip()
            clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line)
            clean_line = re.sub(r'\r', '', clean_line).strip()
            
            if 'serveo.net' in clean_line and 'https://' in clean_line:
                url_match = re.search(r'https://[a-f0-9]+\.serveo\.net', clean_line)
                if url_match:
                    url_queue.put(url_match.group(0))
    except:
        pass

def create_free_global_access():
    """Create free SSH tunnel for global access"""
    global tunnel_process
    
    print("🔄 Setting up global access tunnel...")
    
    try:
        
        tunnel_process = subprocess.Popen([
            'ssh', '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-R', '80:127.0.0.1:8005', 'serveo.net'
        ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)
        
        # Start a robust background thread to capture URL
        def monitor_tunnel():
            try:
                global final_global_url
                for line in iter(tunnel_process.stdout.readline, ''):
                    if line:
                        clean_line = line.strip()
                        # More comprehensive URL pattern matching
                        if 'serveo.net' in clean_line:
                            import re
                            # Try multiple URL patterns
                            patterns = [
                                r'https?://[a-zA-Z0-9.-]+\.serveo\.net',
                                r'https://[a-f0-9]+\.serveo\.net',
                                r'http://[a-f0-9]+\.serveo\.net',
                                r'Forwarding.*?(https?://[^\\s]+\.serveo\.net)',
                                r'HTTP.*?(https?://[^\\s]+\.serveo\.net)'
                            ]
                            
                            for pattern in patterns:
                                url_match = re.search(pattern, clean_line)
                                if url_match:
                                    if url_match.groups():
                                        captured_url = url_match.group(1)  # First group
                                    else:
                                        captured_url = url_match.group(0)  # Whole match
                                    final_global_url = captured_url
                                    break
                            
                            if final_global_url:
                                break
                        # Completely suppress all tunnel output
            except Exception as e:
                pass
                
        import threading
        monitor_thread = threading.Thread(target=monitor_tunnel, daemon=True)
        monitor_thread.start()
        
        # Give it time to establish and capture URL
        time.sleep(5)
        
        if tunnel_process.poll() is None:
            # Backup method: Try to extract URL from process output
            try:
                if not final_global_url:
                    # Check tunnel process for any immediate output
                    import select
                    if hasattr(select, 'select'):
                        ready, _, _ = select.select([tunnel_process.stdout], [], [], 2)
                        if ready:
                            output = tunnel_process.stdout.read(1000)
                            if output and 'serveo.net' in output:
                                import re
                                url_match = re.search(r'https?://[a-f0-9]+\.serveo\.net', output)
                                if url_match:
                                    final_global_url = url_match.group(0)
            except Exception as e:
                pass
            
    except Exception as e:
        pass  # Silent handling
    
    return True

def main():
    """Main function"""
    global final_global_url  # Declare at function start
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 ROBECO PROFESSIONAL SYSTEM - FREE GLOBAL ACCESS")
    print("🆓 SSH tunnel method - No router setup!")
    print("🌍 Get random global URL each time")
    print("=" * 70)
    
    # Step 1: Start local server
    if not start_server():
        print("❌ Cannot continue without server")
        return
    
    print("")
    print("🏠 LOCAL ACCESS:")
    print("   📍 Your computer: http://localhost:8005")
    print("   📍 Your computer: http://127.0.0.1:8005")
    
    # Step 2: Create free global access
    if not create_free_global_access():
        print("❌ Global access failed")
        print("💡 But server still running locally at http://localhost:8005")
        return
    
    # Simple clean display - NO dynamic updates
    time.sleep(7)  # Give tunnel time to capture URL
    
    print(f"\n")
    print(f"🌟 YOUR APP IS NOW GLOBALLY ACCESSIBLE!")
    print(f"=" * 70)
    print(f"✅ LOCAL ACCESS:")
    print(f"   📍 http://localhost:8005")
    print(f"   📍 http://127.0.0.1:8005")
    print(f"")
    print(f"🌍 GLOBAL ACCESS:")
    
    # Show final result - no more dynamic updates
    if final_global_url:
        print(f"   🎉 SSH Tunnel: {final_global_url}")
        print(f"   🎉 Workbench: {final_global_url}/workbench")
    else:
        print(f"   🔄 SSH tunnel starting (check after 30 seconds)")
        
    print(f"   📍 Alternative: ngrok http 8005")
    print(f"")
    print(f"⌨️ Press Ctrl+C to stop")
    print(f"=" * 70)
    
    # Keep running with NO output
    try:
        while True:
            time.sleep(10)  # Longer sleep, no output
            if server_process and server_process.poll() is not None:
                print("❌ Server stopped")
                break
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        cleanup()
        
        # Final reminder with URL
        if final_global_url:
            print(f"\n📋 YOUR GLOBAL URLS:")
            print(f"🌍 Main App: {final_global_url}")
            print(f"🌍 Workbench: {final_global_url}/workbench")
            print(f"💾 Save these URLs for sharing!")
        
        print("✅ Stopped")

if __name__ == "__main__":
    main()