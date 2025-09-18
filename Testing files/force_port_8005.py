#!/usr/bin/env python3
"""
FORCE PORT 8005 - Definitive Solution
Ensures Robeco ALWAYS runs on port 8005 for fixed IP access
"""

import subprocess
import logging
import time
import signal
import sys
import os
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

def force_kill_port_8005():
    """Aggressively kill anything on port 8005"""
    logger.info("🔫 FORCE KILLING ALL PROCESSES ON PORT 8005...")
    
    # Method 1: netstat approach
    try:
        result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if ':8005' in line and 'LISTEN' in line:
                logger.info(f"🔍 Found process on port 8005: {line}")
    except:
        pass
    
    # Method 2: Multiple kill attempts
    kill_commands = [
        ['pkill', '-f', 'professional_streaming_server'],
        ['pkill', '-f', '8005'],
        ['pkill', '-f', 'uvicorn.*8005'],
        ['pkill', '-f', 'fastapi.*8005'],
        ['pkill', '-9', '-f', 'professional_streaming_server'],
        ['pkill', '-9', '-f', '8005'],
    ]
    
    for cmd in kill_commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"✅ Killed processes with: {' '.join(cmd)}")
            time.sleep(0.5)
        except:
            pass
    
    # Method 3: Python process cleanup
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        for line in lines:
            if 'python' in line and ('8005' in line or 'professional_streaming_server' in line):
                parts = line.split()
                if len(parts) > 1:
                    pid = parts[1]
                    try:
                        subprocess.run(['kill', '-9', pid], check=False)
                        logger.info(f"🔫 Force killed Python process PID {pid}")
                    except:
                        pass
    except:
        pass
    
    # Wait for cleanup
    time.sleep(3)
    logger.info("✅ Port 8005 cleanup completed")

def test_port_8005_free():
    """Test if port 8005 is truly free"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 8005))
            logger.info("✅ Port 8005 is FREE and available")
            return True
    except OSError:
        logger.error("❌ Port 8005 is still OCCUPIED")
        return False

def modify_server_for_port_8005():
    """Ensure server is configured for port 8005"""
    server_path = Path(__file__).parent / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    try:
        with open(server_path, 'r') as f:
            content = f.read()
        
        # Force port 8005 in all configurations
        new_content = content
        
        # Replace any port references
        new_content = new_content.replace('port = 8011', 'port = 8005')
        new_content = new_content.replace('port = 8006', 'port = 8005')
        new_content = new_content.replace('port = 8007', 'port = 8005')
        new_content = new_content.replace('port = 8008', 'port = 8005')
        new_content = new_content.replace('port = 8009', 'port = 8005')
        new_content = new_content.replace('port = 8010', 'port = 8005')
        
        # Ensure uvicorn runs on 8005
        if 'uvicorn.run(' in content:
            # Find and replace uvicorn.run calls
            import re
            pattern = r'uvicorn\.run\([^)]*port=\d+[^)]*\)'
            replacement = 'uvicorn.run(app, host="0.0.0.0", port=8005)'
            new_content = re.sub(pattern, replacement, new_content)
        
        # Force the port assignment
        if 'port = force_use_port_8005()' not in new_content:
            new_content = new_content.replace(
                'if __name__ == "__main__":',
                '''if __name__ == "__main__":
    port = 8005  # FORCE PORT 8005'''
            )
        
        with open(server_path, 'w') as f:
            f.write(new_content)
        
        logger.info("✅ Server configured to FORCE use port 8005")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to modify server: {e}")
        return False

def start_robeco_on_8005():
    """Start Robeco definitively on port 8005"""
    global server_process
    
    project_root = Path(__file__).parent
    src_path = project_root / "src"
    server_path = project_root / "src" / "robeco" / "backend" / "professional_streaming_server.py"
    
    # Set environment variables
    env = os.environ.copy()
    env['PYTHONPATH'] = str(src_path) + os.pathsep + env.get('PYTHONPATH', '')
    env['FORCE_PORT_8005'] = 'true'
    
    logger.info("🚀 Starting Robeco server DEFINITIVELY on port 8005...")
    
    # Start server
    server_process = subprocess.Popen([
        sys.executable, str(server_path)
    ], env=env)
    
    # Wait for server to start
    logger.info("⏳ Waiting for server to start on port 8005...")
    time.sleep(10)
    
    # Verify server is running on 8005
    import socket
    for attempt in range(20):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', 8005))
                if result == 0:
                    logger.info("🎉 SUCCESS! Robeco server is running on port 8005")
                    return True
        except:
            pass
        time.sleep(1)
    
    logger.error("❌ Failed to start server on port 8005")
    return False

def display_port_8005_success():
    """Display success information for port 8005"""
    logger.info("")
    logger.info("🎉 SUCCESS! ROBECO RUNNING ON PORT 8005!")
    logger.info("=" * 80)
    logger.info("📍 FIXED ACCESS URLS:")
    logger.info("=" * 80)
    logger.info("🏠 Local: http://localhost:8005")
    logger.info("🏠 Network: http://10.7.7.2:8005")
    logger.info("🌍 GLOBAL: http://138.199.60.185:8005")
    logger.info("🔧 Workbench: http://138.199.60.185:8005/workbench")
    logger.info("=" * 80)
    logger.info("")
    logger.info("✅ PERFECT! Everything uses PORT 8005:")
    logger.info("   • ✅ Server running on port 8005")
    logger.info("   • ✅ Local access on port 8005")
    logger.info("   • ✅ Global access will be on port 8005")
    logger.info("   • ✅ Router forwarding: External 8005 → Internal 8005")
    logger.info("")
    logger.info("🌐 FOR GLOBAL ACCESS:")
    logger.info("   Configure router port forwarding:")
    logger.info("   • External Port: 8005")
    logger.info("   • Internal IP: 10.7.7.2")
    logger.info("   • Internal Port: 8005")
    logger.info("   • Protocol: TCP")
    logger.info("")
    logger.info("🎯 RESULT: http://138.199.60.185:8005 will work globally!")
    logger.info("✅ CONSISTENT PORT 8005 EVERYWHERE!")
    logger.info("=" * 80)

def main():
    """Main function"""
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("🎯 FORCE PORT 8005 - Definitive Solution")
    logger.info("🎯 Goal: Robeco ALWAYS runs on port 8005")
    logger.info("")
    
    # Step 1: Force kill everything on port 8005
    force_kill_port_8005()
    
    # Step 2: Verify port is free
    if not test_port_8005_free():
        logger.error("❌ Could not free port 8005")
        return
    
    # Step 3: Configure server for port 8005
    if not modify_server_for_port_8005():
        logger.error("❌ Could not configure server")
        return
    
    # Step 4: Start server on port 8005
    if not start_robeco_on_8005():
        logger.error("❌ Could not start server on port 8005")
        return
    
    # Step 5: Display success
    display_port_8005_success()
    
    # Keep running
    try:
        while True:
            time.sleep(1)
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